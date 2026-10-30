"""Read-only protected V2 structural gate for Rezon synthetic candidates.

Evaluator-only source scan; no heldout prompt or answer is exported to a
trainer. Passing this gate DOES NOT grant neural-training admission.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from .trainingday_pool import (
    SCHEMA, _calculate, _render_prompt, build_job, load_json,
    save_json_new, validate_job,
)


class AdmissionGateError(ValueError):
    pass


def _require(ok, message):
    if not ok:
        raise AdmissionGateError(message)


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _source_row(row, seed):
    if row.get("kind") == "code":
        return None
    _require(row.get("kind") == "verified_reasoning" and
             row.get("verification") == "TWO_INTEGER_INTERPRETERS_MATCH" and
             row.get("license") == "SYNTHETIC_ORIGINAL" and
             row.get("source_repo") == "VERA_TRAININGDAY_GENERATOR" and
             row.get("source_revision") == "vera.trainingday.corpus.v1",
             "invalid source reasoning")
    start, ops, answer = row.get("start"), row.get("operations"), row.get("answer")
    _require(type(start) is int and type(answer) is int and
             type(ops) is list and 2 <= len(ops) <= 5, "source arithmetic malformed")
    for op in ops:
        _require(type(op) is list and len(op) == 2 and
                 op[0] in ("add", "subtract", "multiply") and
                 type(op[1]) is int and -15 <= op[1] <= 15,
                 "source operation invalid")
    _require(_calculate(start, ops) == answer, "source integer oracle mismatch")
    prompt = ("Start with " + str(start) + ". " +
              " ".join(f"{op} {value}." for op, value in ops) +
              " What is the final integer?")
    content = f"Question: {prompt}\nAnswer: {answer}"
    digest = _hash(content.encode())
    _require(row.get("prompt") == prompt and row.get("text") == content and
             row.get("content_sha256") == digest and
             row.get("id") == "reasoning-" + digest and
             re.fullmatch(rf"seed/{seed}/case/[0-9]{{10}}",
                          str(row.get("source_path", ""))) is not None,
             "source prompt/hash/provenance mismatch")
    return (tuple(pair[0] for pair in ops),
            (start, tuple((pair[0], pair[1]) for pair in ops)))


def scan_v2_manifest(manifest_path, expected_sha):
    path = Path(manifest_path)
    _require(path.is_file() and not path.is_symlink(), "manifest missing")
    _require(re.fullmatch("[a-f0-9]{64}", str(expected_sha)) is not None and
             _hash(path.read_bytes()) == expected_sha, "manifest SHA mismatch")
    root = path.parent
    _require(not root.is_symlink(), "manifest directory linked")
    manifest = load_json(path)
    _require(manifest.get("schema") == "vera.trainingday.corpus.v1" and
             manifest.get("state") == "CORPUS_BUILT_NO_MODEL_TRAINING" and
             type(manifest.get("seed")) is int, "manifest schema/state invalid")
    shards = manifest.get("shards")
    _require(type(shards) is list and 1 <= len(shards) <= 100000,
             "shard list invalid")
    structures = {"train": set(), "eval": set()}
    exact = {"train": set(), "eval": set()}
    counts = Counter()
    shard_rows = Counter()
    seen_paths = set()
    for shard in shards:
        _require(type(shard) is dict and
                 shard.get("split") in structures and
                 type(shard.get("path")) is str, "shard spec invalid")
        split, name = shard["split"], shard["path"]
        _require(re.fullmatch(rf"{split}/[0-9]{{6}}\.jsonl", name) is not None
                 and name not in seen_paths, "shard path unsafe/duplicate")
        seen_paths.add(name)
        file = root / split / name.rsplit("/", 1)[1]
        _require(file.is_file() and not file.is_symlink() and
                 not file.parent.is_symlink(), "shard absent/symlinked")
        raw = file.read_bytes()
        _require(_hash(raw) == shard.get("sha256") and
                 len(raw) == shard.get("bytes"), "shard hash/size mismatch")
        lines = raw.splitlines()
        _require(len(lines) == shard.get("count"), "shard row count mismatch")
        shard_rows[split] += len(lines)
        for line in lines:
            try:
                row = json.loads(line.decode("utf-8"))
            except (ValueError, UnicodeDecodeError) as exc:
                raise AdmissionGateError("invalid shard JSON") from exc
            _require(type(row) is dict, "shard row invalid")
            if row.get("kind") == "code":
                # Source-code rows in either split are hashed and counted,
                # but never parsed as arithmetic or sent to the trainer.
                continue
            signature, key = _source_row(row, manifest["seed"])
            structures[split].add(signature)
            exact[split].add(key)
            counts[split] += 1
    _require(dict(shard_rows) == manifest.get("counts") and
             all(counts.get(split, 0) > 0 for split in structures) and
             not (structures["train"] & structures["eval"]),
             "shard counts / structural split invalid")
    return structures["train"], structures["eval"], exact, {
        "status": "V2_SHARDS_VERIFIED_NO_EVAL_CONTENT_EXPORTED",
        "manifest_sha256": expected_sha,
        "train_reasoning_rows": counts["train"], "eval_reasoning_rows": counts["eval"],
        "train_structures": len(structures["train"]),
        "eval_structures": len(structures["eval"]),
    }


def verify_wave(job, oracle, batch):
    validate_job(job)
    regen_job, regen_oracle = build_job(
        seed=job["seed"], count=len(job["cases"]), workers=job["workers"])
    _require(job == regen_job and oracle == regen_oracle,
             "wave generator/oracle differs from pinned deterministic source")
    _require(type(batch) is dict and
             batch.get("schema") == SCHEMA + ".candidate_batch" and
             type(batch.get("rows")) is list and
             len(batch["rows"]) == len(job["cases"]),
             "candidate batch malformed")
    cases = []
    for public, secret, row in zip(job["cases"], oracle["cases"], batch["rows"]):
        _require(type(row) is dict and row.get("id") == public["id"] and
                 row.get("prompt") == public["prompt"] and
                 row.get("answer") == str(secret["answer"]) and
                 row.get("source") == "SYNTHETIC_ORIGINAL_INTEGER_REPLAY_V1" and
                 row.get("qualified_for_neural_training") is False,
                 "candidate batch/answer mismatch")
        ops = secret["operations"]
        _require(public["prompt"] == _render_prompt(secret["start"], ops) and
                 secret["answer"] == _calculate(secret["start"], ops),
                 "candidate question/answer oracle mismatch")
        cases.append({
            "id": public["id"], "prompt": public["prompt"],
            "answer": str(secret["answer"]),
            "sig": tuple(op[0] for op in ops),
            "exact": (secret["start"], tuple((op[0], op[1]) for op in ops)),
        })
    return cases


def filter_protected(rows, *, train_signatures, eval_signatures, exact_cases):
    counts = Counter()
    kept = []
    seen = set()
    for row in rows:
        _require(row["id"] not in seen, "duplicate candidate case id")
        seen.add(row["id"])
        if row["sig"] in eval_signatures or row["exact"] in exact_cases["eval"]:
            counts["excluded_eval_signature"] += 1
        elif row["exact"] in exact_cases["train"]:
            counts["excluded_train_duplicate"] += 1
        elif row["sig"] not in train_signatures:
            counts["excluded_unassigned_structure"] += 1
        else:
            kept.append(row)
            counts["kept_not_admitted"] += 1
    counts["reviewed"] = len(rows)
    return kept, dict(counts)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--wave", type=Path, action="append", required=True)
    p.add_argument("--batch", type=Path, action="append", required=True)
    p.add_argument("--batch-sha256", action="append", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    a = p.parse_args()
    _require(len(a.wave) == len(a.batch) == len(a.batch_sha256),
             "wave/batch argument count mismatch")
    train_sigs, eval_sigs, exact, source_receipt = scan_v2_manifest(
        a.manifest, a.manifest_sha256)
    proposed, jobs = [], []
    for wave, batch_file, expected_sha in zip(a.wave, a.batch, a.batch_sha256):
        _require(batch_file.is_file() and not batch_file.is_symlink() and
                 _hash(batch_file.read_bytes()) == expected_sha,
                 "candidate batch SHA mismatch")
        job = load_json(wave / "job.json")
        proposed.extend(verify_wave(job, load_json(wave / "oracle.private.json"),
                                    load_json(batch_file)))
        jobs.append(job["job_sha256"])
    survivors, counts = filter_protected(
        proposed, train_signatures=train_sigs, eval_signatures=eval_sigs,
        exact_cases=exact)
    batch = {
        "schema": "rezon.trainingday.train_structure_quarantine.v1",
        "state": "NOT_ADMITTED_TO_NEURAL_TRAINING",
        "manifest_sha256": source_receipt["manifest_sha256"],
        "source_jobs": jobs,
        "rows": [
            {"id": c["id"], "prompt": c["prompt"], "answer": c["answer"],
             "source": "SYNTHETIC_ORIGINAL_INTEGER_REPLAY_V1",
             "verification": "INDEPENDENT_INTEGER_ORACLE_REPLAY",
             "qualified_for_neural_training": False}
            for c in survivors],
    }
    receipt = {**source_receipt, **counts,
               "status": "TRAIN_SIDE_QUARANTINE_ONLY", "rows": len(survivors),
               "neural_optimizer_steps": 0, "eval_contents_exported": False,
               "neural_admitted": False}
    _require(a.output != a.receipt and not a.output.exists() and
             not a.receipt.exists(), "output path occupied")
    save_json_new(a.output, batch)
    save_json_new(a.receipt, receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
