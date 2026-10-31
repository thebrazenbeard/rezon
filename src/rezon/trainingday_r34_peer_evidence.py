"""Public synthetic peer-challenge ledger grounded in a deterministic oracle.

Unlike vote/consensus selectors, this ledger discloses per-case corrections and
regressions separately. It neither takes hidden evaluation data nor provides an
authority path to neural training, host execution, or model release.
"""

from __future__ import annotations

import hashlib
import json

from .trainingday_pool import PoolError, collect_reviews
from .trainingday_r29_interop import (
    MAX_INPUT_BYTES, InteropScenarioError, _clone_exact_json_tree,
)


SCHEMA = "rezon.trainingday.r34-peer-evidence.v1"
_ORACLE_FIELDS = frozenset(("schema", "job_sha256", "cases", "verification"))
_ORACLE_CASE_FIELDS = frozenset(("id", "start", "operations", "answer",
                                 "prompt_sha256"))


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":")).encode("ascii")


def _require_exact_oracle_shape(oracle: dict) -> None:
    """Refuse ambiguous oracle metadata before delegating to replay checks.

    The original replay validates arithmetic, but its oracle rows are assumed
    to be mappings; a malformed row can otherwise escape as AttributeError.
    Inspect the detached plain-JSON snapshot, never the caller-owned object.
    """
    if (type(oracle) is not dict or set(oracle) != _ORACLE_FIELDS
            or oracle["verification"] != "INTEGER_ORACLE_REPLAY_ONLY"
            or type(oracle["cases"]) is not list):
        raise PoolError("invalid peer evidence oracle fields")
    for row in oracle["cases"]:
        if (type(row) is not dict or set(row) != _ORACLE_CASE_FIELDS
                or type(row["id"]) is not str
                or type(row["prompt_sha256"]) is not str
                or type(row["start"]) is not int
                or type(row["answer"]) is not int
                or type(row["operations"]) is not list):
            raise PoolError("invalid peer evidence oracle case")
        if (not 2 <= len(row["operations"]) <= 5
                or any(type(op) is not list or len(op) != 2
                       or type(op[0]) is not str or type(op[1]) is not int
                       for op in row["operations"])):
            raise PoolError("invalid peer evidence oracle operations")


def _freeze(job: dict, oracle: dict, first: list, reviews: list) -> dict:
    """Detach all untrusted input exactly once before any validation code.

    No caller-owned object is passed to downstream receipt checks or reread to
    calculate provenance. This rejects dict/list subclasses with custom hooks.
    """
    if (type(job) is not dict or type(oracle) is not dict
            or type(first) is not list or type(reviews) is not list):
        raise PoolError("peer evidence requires exact JSON containers")
    try:
        frozen = _clone_exact_json_tree({
            "job": job, "oracle": oracle, "first": first, "reviews": reviews,
        })
        if len(_canonical(frozen)) > MAX_INPUT_BYTES:
            raise PoolError("oversized peer evidence fixture")
        _require_exact_oracle_shape(frozen["oracle"])
    except (InteropScenarioError, OverflowError, RecursionError, ValueError,
            TypeError) as exc:
        if isinstance(exc, PoolError):
            raise
        raise PoolError("invalid or oversized peer evidence fixture") from exc
    return frozen


def _consensus(votes: dict[str, int], truth: int) -> str:
    if len(set(votes.values())) > 1:
        return "DISAGREEMENT"
    return ("UNANIMOUS_CORRECT" if next(iter(votes.values())) == truth
            else "UNANIMOUS_WRONG")


def assess_peer_outcomes(job: dict, oracle: dict, first: list[dict],
                         reviews: list[dict]) -> dict:
    """Assess frozen, signed-by-digest *synthetic* receipts, never peer truth.

    `collect_reviews` first validates the actual prompt/answer arithmetic from
    the deterministic integer replay, all receipt-to-job bindings, worker IDs,
    peer snapshot digests, complete rounds and duplicate deliveries. Only then
    does this additional ledger compare the same cases across rounds.

    Self-hashes are source-level tamper indicators, not cryptographic host
    identity attestation or evidence of independent model execution.
    """
    frozen = _freeze(job, oracle, first, reviews)
    source = frozen["job"]
    summary, candidates = collect_reviews(
        source, frozen["oracle"], frozen["first"], frozen["reviews"])
    workers = sorted(source["workers"])
    # Duplicate byte-identical transport deliveries have already passed
    # collect_reviews' idempotent replay rules; one worker remains one vote.
    first_by_worker = {r["worker"]: r for r in frozen["first"]}
    review_by_worker = {r["worker"]: r for r in frozen["reviews"]}
    cases = []
    first_total = reviewed_total = corrections = regressions = 0
    for index, candidate in enumerate(candidates):
        truth = int(candidate["answer"])
        first_votes = {w: first_by_worker[w]["answers"][index]["parsed_integer"]
                       for w in workers}
        review_votes = {w: review_by_worker[w]["answers"][index]["parsed_integer"]
                        for w in workers}
        first_exact = sum(v == truth for v in first_votes.values())
        review_exact = sum(v == truth for v in review_votes.values())
        fixed = [w for w in workers
                 if first_votes[w] != truth and review_votes[w] == truth]
        regressed = [w for w in workers
                     if first_votes[w] == truth and review_votes[w] != truth]
        first_total += first_exact
        reviewed_total += review_exact
        corrections += len(fixed)
        regressions += len(regressed)
        cases.append({
            "id": candidate["id"],
            "first_exact_votes": first_exact,
            "review_exact_votes": review_exact,
            "first_consensus": _consensus(first_votes, truth),
            "review_consensus": _consensus(review_votes, truth),
            "corrected_workers": fixed,
            "regressed_workers": regressed,
            "changed_workers": [w for w in workers
                                if first_votes[w] != review_votes[w]],
            "qualified_for_neural_training": False,
        })
    outcome = {
        "schema": SCHEMA,
        "status": "SOURCE_ONLY_HOLD",
        "job_sha256": source["job_sha256"],
        "peer_receipts_sha256": summary["peer_receipts_sha256"],
        "first_receipts": {w: first_by_worker[w]["receipt_sha256"] for w in workers},
        "review_receipts": {w: review_by_worker[w]["receipt_sha256"] for w in workers},
        "workers": workers,
        "cases_count": len(cases),
        "first_exact_total": first_total,
        "review_exact_total": reviewed_total,
        "corrected_votes": corrections,
        "regressed_votes": regressions,
        "net_exact_delta": reviewed_total - first_total,
        "case_dispositions": cases,
        "oracle_scope": "PUBLIC_DETERMINISTIC_INTEGER_REPLAY",
        "host_identity_attested": False,
        "physical_inference_verified": False,
        "neural_weight_update_verified": False,
        "authorizes_optimizer_start": False,
        "authorizes_model_release": False,
        "distributed_gradients_proven": False,
    }
    outcome["assessment_sha256"] = hashlib.sha256(_canonical(outcome)).hexdigest()
    return outcome
