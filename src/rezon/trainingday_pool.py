"""VERA::TRAININGDAY: portable, oracle-checked Rezon inference delegation.

Each host invokes its *own* loopback model; a separately authorized transport
(e.g. Executor) moves the exact same job and brings back portable receipts.
Rezon does not open remote host ports, distribute credentials, average weights,
or automatically admit model outputs into a training corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import random
import re
from pathlib import Path
from urllib.parse import urlsplit

from .providers import OpenAICompatibleModel

SCHEMA = "rezon.trainingday.pool.v1"
_WORKER = re.compile(r"[a-z][a-z0-9_]{1,31}\Z")
_INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")


class PoolError(ValueError):
    """Bad pinned task, worker receipt, or training admission boundary."""


def _digest(value: dict) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_json(path: str | Path) -> dict:
    """Decode ordinary UTF-8 and Windows PowerShell UTF-8-BOM JSON alike."""
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json_new(path: str | Path, value: dict) -> None:
    """Create only: never replace existing job, oracle, output or receipt."""
    target = Path(path)
    if not target.parent.is_dir():
        raise PoolError("destination parent does not exist")
    with target.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, sort_keys=True, indent=2, ensure_ascii=False)
        file.write("\n")


def _check_workers(workers: dict) -> None:
    if (type(workers) is not dict or not 2 <= len(workers) <= 8
            or any(type(name) is not str or not _WORKER.fullmatch(name)
                   or type(model) is not str or not 1 <= len(model) <= 180
                   for name, model in workers.items())):
        raise PoolError("workers must be 2..8 unique named local models")


def _calculate(start: int, operations: list[list]) -> int:
    if type(start) is not int or not 2 <= len(operations) <= 5:
        raise PoolError("oracle operations invalid")
    value = start
    for pair in operations:
        if type(pair) is not list or len(pair) != 2 or type(pair[1]) is not int:
            raise PoolError("oracle operation malformed")
        op, operand = pair
        if op == "add":
            value += operand
        elif op == "subtract":
            value -= operand
        elif op == "multiply":
            value *= operand
        else:
            raise PoolError("oracle operation not supported")
    return value


def build_job(*, seed: int, count: int, workers: dict) -> tuple[dict, dict]:
    """Generate bounded ORIGINAL synthetic math; never leak answers to workers."""
    if type(seed) is not int or not 0 <= seed < 2**31:
        raise PoolError("seed must be a nonnegative 31-bit integer")
    if type(count) is not int or not 1 <= count <= 32:
        raise PoolError("count must be 1..32")
    _check_workers(workers)
    rng = random.Random(seed)
    cases, private = [], []
    used = set()
    while len(cases) < count:
        start = rng.randint(-45, 45)
        operations = []
        for _ in range(rng.randint(2, 4)):
            op = rng.choice(("add", "subtract", "multiply"))
            operand = rng.randint(-12, 12) if op != "multiply" else rng.randint(-4, 4)
            operations.append([op, operand])
        segments = [f"Start with the integer {start}."]
        for op, operand in operations:
            segments.append(f"{op} {operand}.")
        prompt = " ".join(segments) + " What is the final integer? Reply with the integer only."
        if prompt in used:
            continue
        used.add(prompt)
        answer = _calculate(start, operations)
        identifier = "case-" + hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:24]
        cases.append({"id": identifier, "prompt": prompt})
        private.append({"id": identifier, "start": start, "operations": operations,
                        "answer": answer, "prompt_sha256": hashlib.sha256(
                            prompt.encode("utf-8")).hexdigest()})
    job = {"schema": SCHEMA, "event_id": "VERA::TRAININGDAY",
           "case_type": "SYNTHETIC_INTEGER_ORACLE", "seed": seed,
           "workers": dict(sorted(workers.items())), "cases": cases}
    job["job_sha256"] = _digest(job)
    oracle = {"schema": SCHEMA + ".oracle", "job_sha256": job["job_sha256"],
              "cases": private, "verification": "INTEGER_ORACLE_REPLAY_ONLY"}
    return job, oracle


def validate_job(job: dict) -> bool:
    if type(job) is not dict or job.get("schema") != SCHEMA:
        raise PoolError("job schema mismatch")
    _check_workers(job.get("workers"))
    cases = job.get("cases")
    if (type(cases) is not list or not 1 <= len(cases) <= 32
            or type(job.get("seed")) is not int):
        raise PoolError("invalid job cases")
    if len({x.get("id") for x in cases if type(x) is dict}) != len(cases):
        raise PoolError("duplicate or invalid case ids")
    for case in cases:
        if (type(case) is not dict or set(case) != {"id", "prompt"}
                or type(case["prompt"]) is not str
                or not 1 <= len(case["prompt"]) <= 1400
                or case["id"] != "case-" + hashlib.sha256(
                    case["prompt"].encode("utf-8")).hexdigest()[:24]):
            raise PoolError("case content/hash invalid")
    claim = job.get("job_sha256")
    if type(claim) is not str or claim != _digest(
        {k: v for k, v in job.items() if k != "job_sha256"}
    ):
        raise PoolError("job digest mismatch")
    return True


def _loopback(base_url: str) -> None:
    try:
        url = urlsplit(base_url)
        local = (url.hostname == "localhost" or (
            url.hostname is not None and ipaddress.ip_address(url.hostname).is_loopback
        ))
        port = url.port
    except (ValueError, AttributeError):
        raise PoolError("model endpoint must be loopback") from None
    if (url.scheme != "http" or not local or not port or url.path.rstrip("/") != "/v1"
            or url.username is not None or url.password is not None
            or url.query or url.fragment):
        raise PoolError("model endpoint must be loopback HTTP /v1")


def _numeric(response: str) -> int | None:
    stripped = response.strip()
    if len(stripped) > 80 or not _INTEGER.fullmatch(stripped):
        return None
    return int(stripped)


def run_worker(job: dict, worker: str, *, base_url: str, model=None) -> dict:
    """One-shot real model inference from worker's localhost, no gateway writes."""
    validate_job(job)
    _loopback(base_url)
    if worker not in job["workers"]:
        raise PoolError("worker not assigned to this job")
    model_id = job["workers"][worker]
    if model is None:
        model = OpenAICompatibleModel(
            agent_id=worker, model=model_id, base_url=base_url,
            api_key="local-loopback-placeholder", timeout_seconds=90,
            max_tokens=32,
        )
    answers = []
    for case in job["cases"]:
        text = model.complete((
            {"role": "system", "content": "Reply with the final integer only. No explanation."},
            {"role": "user", "content": case["prompt"]},
        ))
        if type(text) is not str or len(text) > 2000:
            raise PoolError("unbounded model output")
        answers.append({"id": case["id"], "text": text,
                        "parsed_integer": _numeric(text)})
    receipt = {"schema": SCHEMA + ".worker", "job_sha256": job["job_sha256"],
               "worker": worker, "model_id": model_id,
               "method": "LIVE_LOCAL_MODEL_INFERENCE_UNATTESTED_HOST",
               "answers": answers}
    receipt["receipt_sha256"] = _digest(receipt)
    return receipt


def collect(job: dict, oracle: dict, receipts: list[dict]) -> tuple[dict, list[dict]]:
    """Replay integer oracle; model agreement alone NEVER certifies correctness."""
    validate_job(job)
    if (type(oracle) is not dict or oracle.get("schema") != SCHEMA + ".oracle"
            or oracle.get("job_sha256") != job["job_sha256"]
            or type(oracle.get("cases")) is not list
            or len(oracle["cases"]) != len(job["cases"])):
        raise PoolError("oracle job mismatch")
    truth = {}
    for public, secret in zip(job["cases"], oracle["cases"]):
        if (secret.get("id") != public["id"]
                or secret.get("prompt_sha256") != hashlib.sha256(
                    public["prompt"].encode("utf-8")).hexdigest()
                or type(secret.get("answer")) is not int
                or secret["answer"] != _calculate(secret.get("start"), secret.get("operations"))):
            raise PoolError("oracle mismatch or invalid answer")
        truth[public["id"]] = secret["answer"]
    seen = {}
    for receipt in receipts:
        if (type(receipt) is not dict or receipt.get("schema") != SCHEMA + ".worker"
                or receipt.get("job_sha256") != job["job_sha256"]):
            raise PoolError("worker job mismatch")
        worker = receipt.get("worker")
        if worker in seen:
            raise PoolError("duplicate worker receipt")
        if (worker not in job["workers"]
                or receipt.get("model_id") != job["workers"][worker]):
            raise PoolError("worker model mismatch")
        if receipt.get("receipt_sha256") != _digest({
            k: v for k, v in receipt.items() if k != "receipt_sha256"
        }):
            raise PoolError("worker receipt digest mismatch")
        answers = receipt.get("answers")
        if (type(answers) is not list or len(answers) != len(job["cases"])
                or [x.get("id") for x in answers] != [x["id"] for x in job["cases"]]):
            raise PoolError("answer IDs/order mismatch")
        for row in answers:
            if type(row.get("text")) is not str or row.get("parsed_integer") != _numeric(row["text"]):
                raise PoolError("worker answer parsing mismatch")
        seen[worker] = receipt
    if set(seen) != set(job["workers"]):
        return ({"status": "PARTIAL_WORKER_EVIDENCE_NOT_ADMITTED",
                 "job_sha256": job["job_sha256"],
                 "workers_completed": len(seen), "workers_required": len(job["workers"])}, [])
    accurate = {w: 0 for w in seen}
    candidates = []
    for case in job["cases"]:
        outputs = {w: next(x for x in receipt["answers"] if x["id"] == case["id"])
                   for w, receipt in seen.items()}
        for worker, answer in outputs.items():
            accurate[worker] += int(answer["parsed_integer"] == truth[case["id"]])
        candidate = {"schema": SCHEMA + ".candidate",
                     "id": case["id"], "prompt": case["prompt"],
                     "answer": str(truth[case["id"]]),
                     "source": "SYNTHETIC_ORIGINAL_TWO_PATH_INTEGER_ORACLE",
                     "verification": "DETERMINISTIC_ORACLE_REPLAY",
                     "model_exact_votes": sum(
                         output["parsed_integer"] == truth[case["id"]]
                         for output in outputs.values()),
                     "models_checked": len(outputs),
                     "qualified_for_neural_training": False,
                     "reason": "REQUIRES_DATASET_ADMISSION_AND_DEDUP_REVIEW"}
        candidates.append(candidate)
    summary = {"schema": SCHEMA + ".summary",
               "status": "REPLAYED_ORACLE_NOT_MODEL_CONSENSUS",
               "job_sha256": job["job_sha256"],
               "workers_completed": len(seen), "candidate_rows": len(candidates),
               "model_exact_total": sum(accurate.values()),
               "exact_by_worker": dict(sorted(accurate.items())),
               "oracle_verification": "INTEGER_ARITHMETIC_ONLY",
               "host_identity_attested": False,
               "neural_weight_update": False,
               "source_provenance": "SYNTHETIC_GENERATED_NO_PRIVATE_DATA"}
    return summary, candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Rezon bounded multi-host training inference exchange")
    sub = parser.add_subparsers(dest="op", required=True)
    create = sub.add_parser("create")
    create.add_argument("--workers-json", type=Path, required=True)
    create.add_argument("--job", type=Path, required=True)
    create.add_argument("--oracle", type=Path, required=True)
    create.add_argument("--seed", type=int, default=29037)
    create.add_argument("--cases", type=int, default=12)
    worker = sub.add_parser("worker")
    worker.add_argument("--job", type=Path, required=True)
    worker.add_argument("--worker", required=True)
    worker.add_argument("--model-url", required=True)
    worker.add_argument("--output", type=Path, required=True)
    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--job", type=Path, required=True)
    aggregate.add_argument("--oracle", type=Path, required=True)
    aggregate.add_argument("--receipt", type=Path, action="append", required=True)
    aggregate.add_argument("--summary", type=Path, required=True)
    aggregate.add_argument("--candidates", type=Path, required=True)
    args = parser.parse_args()
    if args.op == "create":
        job, oracle = build_job(seed=args.seed, count=args.cases,
                                workers=load_json(args.workers_json))
        save_json_new(args.job, job)
        save_json_new(args.oracle, oracle)
        print(json.dumps({"job_sha256": job["job_sha256"], "cases": len(job["cases"]),
                          "workers": sorted(job["workers"]), "status": "PACKAGED_NO_INFERENCE"}))
    elif args.op == "worker":
        receipt = run_worker(load_json(args.job),
                             args.worker, base_url=args.model_url)
        save_json_new(args.output, receipt)
        print(json.dumps({"receipt_sha256": receipt["receipt_sha256"],
                          "worker": receipt["worker"], "count": len(receipt["answers"]),
                          "status": "LOCAL_MODEL_RESPONSES_UNATTESTED"}))
    else:
        summary, candidates = collect(
            load_json(args.job),
            load_json(args.oracle),
            [load_json(p) for p in args.receipt],
        )
        if summary["status"] != "REPLAYED_ORACLE_NOT_MODEL_CONSENSUS":
            raise PoolError("all workers required before training candidates export")
        save_json_new(args.summary, summary)
        save_json_new(args.candidates, {"schema": SCHEMA + ".candidate_batch", "rows": candidates})
        print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
