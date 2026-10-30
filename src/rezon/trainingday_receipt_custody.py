"""Source-only custody checks for three TrainingDay inference worker receipts.

The caller supplies job, route, and receipt declarations. No OS principal,
signature key, transport, host lease, corpus rights, or model weights are
authenticated by this module. Even a complete synthetic chain is a HOLD,
never authorization to dispatch, train, or pool gradients.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Callable

from .trainingday_pool import PoolError, _digest, validate_job
from .trainingday_routing import _valid_device


SCHEMA = "rezon.trainingday.receipt-custody.v1"
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_NONCE = re.compile(r"[A-Za-z0-9_-]{8,64}\Z")
_MAX_AGE_SECONDS = 30
_MAX_DELIVERIES = 4
_EXPECTED_SYNTHETIC_DEVICES = frozenset(("lappy", "vn1", "vn2"))


def _valid_sha(value: object) -> bool:
    return type(value) is str and len(value) == 64 and _SHA.fullmatch(value) is not None


def _valid_time(value: object) -> bool:
    return type(value) is int and 0 <= value < 2**63


def _canonical_claim_bytes(value: object) -> bytes:
    """Snapshot ordinary JSON values before untrusted verification callbacks."""
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise PoolError("custody input declarations not canonical JSON") from exc


def build_synthetic_corpus_claim(job: dict) -> dict:
    """Bind public job examples, not assert legal/training-corpus admission."""
    validate_job(job)
    claim = {
        "schema": SCHEMA + ".corpus",
        "job_sha256": job["job_sha256"],
        "case_handles": [{
            "id": row["id"],
            "prompt_sha256": hashlib.sha256(row["prompt"].encode("utf-8")).hexdigest(),
        } for row in job["cases"]],
        # The job's synthetic case_type is itself caller-asserted. A hash
        # cannot prove the content is public, licensed, or training-admitted.
        "rights_status": "UNVERIFIED_NO_TRAINING_ADMISSION",
    }
    claim["corpus_sha256"] = _digest(claim)
    return claim


def signing_payload_digest(receipt: dict) -> bytes:
    """Canonical claimed bytes; a hash alone is not an authenticated signature."""
    return _digest({key: value for key, value in receipt.items()
                    if key not in ("signature", "receipt_sha256")}).encode("ascii")


def _validate_receipt_shape(receipt: dict) -> None:
    fields = {
        "schema", "job_sha256", "corpus_sha256", "worker", "device",
        "model_id", "kind", "issued_at_unix", "nonce", "output_sha256",
        "signature", "receipt_sha256",
    }
    if (type(receipt) is not dict or set(receipt) != fields
            or receipt["schema"] != SCHEMA + ".inference"
            or receipt["kind"] != "INFERENCE_RESULT_CLAIM"
            or any(not _valid_sha(receipt[k]) for k in (
                "job_sha256", "corpus_sha256", "output_sha256", "receipt_sha256"
            ))
            or type(receipt["worker"]) is not str
            or not 1 <= len(receipt["worker"]) <= 32
            or not _valid_device(receipt["device"])
            or type(receipt["model_id"]) is not str
            or not 1 <= len(receipt["model_id"]) <= 180
            or not _valid_time(receipt["issued_at_unix"])
            or type(receipt["nonce"]) is not str
            or _NONCE.fullmatch(receipt["nonce"]) is None
            or not _valid_sha(receipt["signature"])):
        raise PoolError("inference receipt declaration malformed")
    if receipt["receipt_sha256"] != _digest({
        key: value for key, value in receipt.items() if key != "receipt_sha256"
    }):
        raise PoolError("inference receipt content digest mismatch")


def assess_synthetic_three_node_chain(
    job: dict,
    corpus_claim: dict,
    routes: dict,
    receipts: list,
    *,
    now_unix: int,
    verify_claim: Callable[[bytes, str, str], bool] | None = None,
) -> dict:
    """Assess untrusted continuity and synthetic signatures, never issue auth.

    Identical retries are counted once, but marked as replay evidence. A
    conflicting retry is rejected. A signer callback supplied by the same
    coordinator cannot prove real device or host identity.
    """
    # Cheap bounded structural admission MUST precede deep JSON snapshot.
    # A malformed gigantic receipt list cannot consume unbounded copy/encode
    # work merely to discover afterward that it exceeds the replay limit.
    validate_job(job)
    if not _valid_time(now_unix):
        raise PoolError("custody assessment clock invalid")
    if len(job["workers"]) != 3:
        raise PoolError("exactly three worker identities required for this fixture")
    if (type(routes) is not dict or len(routes) != 3
            or set(routes) != set(job["workers"])
            or any(not _valid_device(device) for device in routes.values())
            or set(routes.values()) != _EXPECTED_SYNTHETIC_DEVICES):
        raise PoolError("synthetic three-node route declaration invalid")
    if type(corpus_claim) is not dict or corpus_claim != build_synthetic_corpus_claim(job):
        raise PoolError("synthetic corpus content-addressed claim mismatch")
    if type(receipts) is not list or len(receipts) > 3 * _MAX_DELIVERIES:
        raise PoolError("three-node receipt list malformed or unbounded")
    for receipt in receipts:
        _validate_receipt_shape(receipt)

    # Isolate all mutable caller-owned collections before invoking the
    # caller-supplied verifier. Otherwise a verifier can mutate a previously
    # checked worker/job/route/receipt after its hash has been accepted.
    original_claims = {"job": job, "corpus_claim": corpus_claim,
                       "routes": routes, "receipts": receipts}
    frozen_bytes = _canonical_claim_bytes(original_claims)
    frozen = json.loads(frozen_bytes)
    job = frozen["job"]
    corpus_claim = frozen["corpus_claim"]
    routes = frozen["routes"]
    receipts = frozen["receipts"]
    validate_job(job)
    if not _valid_time(now_unix):
        raise PoolError("custody assessment clock invalid")
    if len(job["workers"]) != 3:
        raise PoolError("exactly three worker identities required for this fixture")
    if (type(routes) is not dict or set(routes) != set(job["workers"])
            or any(not _valid_device(device) for device in routes.values())
            or set(routes.values()) != _EXPECTED_SYNTHETIC_DEVICES):
        raise PoolError("synthetic three-node route declaration invalid")
    expected_corpus = build_synthetic_corpus_claim(job)
    if type(corpus_claim) is not dict or corpus_claim != expected_corpus:
        raise PoolError("synthetic corpus content-addressed claim mismatch")
    if type(receipts) is not list or len(receipts) > 3 * _MAX_DELIVERIES:
        raise PoolError("three-node receipt list malformed or unbounded")

    seen: dict[str, dict] = {}
    count: dict[str, int] = {}
    blockers: set[str] = set()
    duplicates = 0
    nonce_owners: dict[tuple[str, str], str] = {}
    for receipt in receipts:
        _validate_receipt_shape(receipt)
        worker = receipt["worker"]
        if (worker not in job["workers"] or receipt["device"] != routes[worker]
                or receipt["model_id"] != job["workers"][worker]
                or receipt["job_sha256"] != job["job_sha256"]
                or receipt["corpus_sha256"] != corpus_claim["corpus_sha256"]):
            raise PoolError("receipt worker/job/corpus binding mismatch")
        count[worker] = count.get(worker, 0) + 1
        if count[worker] > _MAX_DELIVERIES:
            raise PoolError("worker receipt replay limit exceeded")
        nonce_key = (worker, receipt["nonce"])
        prior = nonce_owners.setdefault(nonce_key, receipt["receipt_sha256"])
        if prior != receipt["receipt_sha256"]:
            raise PoolError("conflicting receipt nonce reuse")
        if worker in seen:
            if seen[worker] != receipt:
                raise PoolError("conflicting duplicate worker receipt")
            duplicates += 1
            blockers.add("REPLAYED_RECEIPT_COLLAPSED")
        else:
            seen[worker] = receipt
        if not 0 <= now_unix - receipt["issued_at_unix"] <= _MAX_AGE_SECONDS:
            blockers.add("STALE_OR_FUTURE_RECEIPT")
        if verify_claim is None:
            blockers.add("NO_EXTERNAL_SIGNATURE_VERIFIER")
        else:
            try:
                valid = verify_claim(signing_payload_digest(receipt),
                                     receipt["signature"], worker)
            except Exception:
                valid = False
            if valid is not True:
                blockers.add("SYNTHETIC_SIGNATURE_CLAIM_INVALID")
    missing = sorted(set(job["workers"]) - set(seen))
    if missing:
        blockers.add("INCOMPLETE_THREE_NODE_RECEIPTS")
    # Source-level TOCTOU sentinel: never report a complete chain when a
    # mutable input was changed by a callback during this assessment. The
    # frozen copy still determines the exact bytes that were checked.
    try:
        unchanged = _canonical_claim_bytes(original_claims) == frozen_bytes
    except PoolError:
        unchanged = False
    if not unchanged:
        blockers.add("INPUT_CHANGED_DURING_VERIFICATION")

    receipt_digests = [receipt["receipt_sha256"] for receipt in receipts]
    summary = {
        "schema": SCHEMA + ".assessment",
        "job_sha256": job["job_sha256"],
        "corpus_sha256": corpus_claim["corpus_sha256"],
        # Bind frozen values but normalize receipt transport order, otherwise
        # the same delivered evidence appears different after a network retry.
        "frozen_input_claim_sha256": _digest({
            "job": job, "corpus_claim": corpus_claim, "routes": routes,
            "receipts": sorted(receipts, key=lambda row: row["receipt_sha256"]),
        }),
        "assessed_at_unix": now_unix,
        "status": "HOLD_SYNTHETIC_CHAIN",
        "blockers": sorted(blockers),
        "missing_workers": missing,
        "unique_worker_receipts": len(seen),
        "delivery_count": len(receipts),
        "duplicate_deliveries_collapsed": duplicates,
        "worker_to_device_claims": dict(sorted(routes.items())),
        "receipt_sha256_list": sorted(receipt_digests),
        "corpus_content_continuity_check": True,
        "corpus_rights_or_training_admission_verified": False,
        "source_level_chain_complete": not missing and not blockers,
        "host_identity_authenticated": False,
        "signature_trust_anchor_authenticated": False,
        "host_lease_authenticated": False,
        "dispatch_authorized": False,
        "training_candidate_admitted": False,
        "shared_gradient_computation_proven": False,
    }
    summary["assessment_sha256"] = _digest(summary)
    return summary
