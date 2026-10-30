"""A Rezon candidate must not enter structural evaluation signatures."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from rezon.trainingday_pool import build_job, _calculate, _render_prompt
from rezon.trainingday_admission import (
    AdmissionGateError, scan_v2_manifest, filter_protected, verify_wave,
)


def _fixture(tmp, *, split, start, ops):
    value = _calculate(start, ops)
    prompt = "Start with " + str(start) + ". " + " ".join(
        f"{name} {v}." for name, v in ops
    ) + " What is the final integer?"
    content = f"Question: {prompt}\nAnswer: {value}"
    digest = hashlib.sha256(content.encode()).hexdigest()
    row = {
        "kind": "verified_reasoning", "verification": "TWO_INTEGER_INTERPRETERS_MATCH",
        "license": "SYNTHETIC_ORIGINAL", "source_repo": "VERA_TRAININGDAY_GENERATOR",
        "source_revision": "vera.trainingday.corpus.v1", "start": start,
        "operations": ops, "answer": value, "prompt": prompt, "text": content,
        "content_sha256": digest, "id": "reasoning-" + digest,
        "source_path": "seed/29034/case/0000000001",
    }
    name = f"{split}/000000.jsonl"
    path = tmp / name
    path.parent.mkdir(exist_ok=True)
    raw = (json.dumps(row) + "\n").encode()
    path.write_bytes(raw)
    return {"split": split, "path": name, "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), "count": 1}


class AdmissionTests(unittest.TestCase):
    def test_v2_manifest_reads_valid_shards_and_does_not_export_eval_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [_fixture(root, split="train", start=1,
                             ops=[["add", 2], ["subtract", 1]]),
                    _fixture(root, split="eval", start=3,
                             ops=[["multiply", 2], ["add", 1]])]
            manifest = {"schema": "vera.trainingday.corpus.v1",
                        "state": "CORPUS_BUILT_NO_MODEL_TRAINING",
                        "seed": 29034, "counts": {"train": 1, "eval": 1},
                        "shards": rows}
            path = root / "manifest.json"
            path.write_text(json.dumps(manifest))
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            train, evaluated, exact, receipt = scan_v2_manifest(path, sha)
            self.assertEqual(len(train), 1)
            self.assertEqual(len(evaluated), 1)
            self.assertEqual(exact["train"].__len__(), 1)
            self.assertNotIn("prompt", json.dumps(receipt))
            with self.assertRaisesRegex(AdmissionGateError, "manifest"):
                scan_v2_manifest(path, "0" * 64)
            (root / rows[1]["path"]).write_text("tampered")
            with self.assertRaisesRegex(AdmissionGateError, "shard"):
                scan_v2_manifest(path, sha)

    def test_protected_signatures_are_rejected_without_consensus(self):
        rows = [
            {"id": "a", "sig": ("add", "multiply"), "exact": (1, (("add", 2), ("multiply", 3))),
             "answer": 9},
            {"id": "b", "sig": ("subtract", "add"), "exact": (4, (("subtract", 1), ("add", 3))),
             "answer": 6},
        ]
        keep, counts = filter_protected(
            rows, train_signatures={("subtract", "add")},
            eval_signatures={("add", "multiply")},
            exact_cases={"train": set(), "eval": set()},
        )
        self.assertEqual([r["id"] for r in keep], ["b"])
        self.assertEqual(counts["excluded_eval_signature"], 1)
        self.assertEqual(counts["kept_not_admitted"], 1)

    def test_replayed_generator_and_candidate_batch_custody(self):
        job, oracle = build_job(seed=29037, count=4, workers={"vn1": "qwen", "vn2": "granite"})
        rows = [{"id": c["id"], "prompt": c["prompt"], "answer": str(o["answer"]),
                 "source": "SYNTHETIC_ORIGINAL_INTEGER_REPLAY_V1",
                 "qualified_for_neural_training": False}
                for c, o in zip(job["cases"], oracle["cases"])]
        result = verify_wave(job, oracle, {"schema": "rezon.trainingday.pool.v1.candidate_batch",
                                           "rows": rows})
        self.assertEqual(len(result), 4)
        rows[0]["answer"] = str(int(rows[0]["answer"]) + 1)
        with self.assertRaisesRegex(AdmissionGateError, "candidate"):
            verify_wave(job, oracle, {"schema": "rezon.trainingday.pool.v1.candidate_batch",
                                      "rows": rows})


    def test_eval_code_row_is_hash_checked_but_not_used_as_math(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            train = _fixture(root, split="train", start=1,
                             ops=[["add", 2], ["subtract", 1]])
            evaluation = _fixture(root, split="eval", start=3,
                                  ops=[["multiply", 2], ["add", 1]])
            file = root / evaluation["path"]
            raw = file.read_bytes() + (json.dumps({
                "kind": "code", "source_repo": "heldout_repo",
                "text": "This is not an arithmetic training example."
            }) + "\n").encode()
            file.write_bytes(raw)
            evaluation["count"] = 2
            evaluation["bytes"] = len(raw)
            evaluation["sha256"] = hashlib.sha256(raw).hexdigest()
            manifest = {"schema": "vera.trainingday.corpus.v1",
                        "state": "CORPUS_BUILT_NO_MODEL_TRAINING",
                        "seed": 29034, "counts": {"train": 1, "eval": 2},
                        "shards": [train, evaluation]}
            path = root / "manifest.json"
            path.write_text(json.dumps(manifest))
            _, _, _, receipt = scan_v2_manifest(
                path, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(receipt["eval_reasoning_rows"], 1)
            self.assertNotIn("heldout_repo", json.dumps(receipt))

    def test_poisoned_manifest_replayed_answer_does_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shard = _fixture(root, split="eval", start=3,
                             ops=[["multiply", 2], ["add", 1]])
            original = json.loads((root / shard["path"]).read_text())
            original["answer"] = 999
            content = (json.dumps(original) + "\n").encode()
            (root / shard["path"]).write_bytes(content)
            shard["sha256"] = hashlib.sha256(content).hexdigest()
            shard["bytes"] = len(content)
            manifest = {"schema": "vera.trainingday.corpus.v1",
                        "state": "CORPUS_BUILT_NO_MODEL_TRAINING", "seed": 29034,
                        "counts": {"train": 0, "eval": 1}, "shards": [shard]}
            path = root / "manifest.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaises(AdmissionGateError):
                scan_v2_manifest(path, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
