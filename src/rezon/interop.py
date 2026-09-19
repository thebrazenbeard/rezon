from __future__ import annotations

from hashlib import sha256
import json

from .receipts import EffectState
from .runner import RunOutcome


RUN_EVIDENCE_SCHEMA = "rezon.run-evidence.v1"


def _receipt_payload(outcome: RunOutcome) -> dict[str, object]:
    if type(outcome) is not RunOutcome:
        raise TypeError("run evidence requires exact RunOutcome")

    receipt = outcome.receipt
    if receipt.effect_state is not EffectState.PLAN:
        raise ValueError("run evidence may export PLAN receipts only")

    return {
        "task_id": receipt.task_id,
        "episode_version": receipt.episode_version,
        "accepted_claim_ids": list(receipt.accepted_claim_ids),
        "rejected_claim_ids": list(receipt.rejected_claim_ids),
        "unresolved": list(receipt.unresolved),
        "failures": [failure.value for failure in receipt.failures],
        "effect_state": receipt.effect_state.value,
        "source_versions": list(receipt.source_versions),
        "execution_ids": list(receipt.execution_ids),
        "execution_output_digests": [
            list(binding) for binding in receipt.execution_output_digests
        ],
        "execution_producer_ids": [
            list(binding) for binding in receipt.execution_producer_ids
        ],
        "task_envelope_digest": receipt.task_envelope_digest,
        "claim_disposition_complete": receipt.claim_disposition_complete,
    }


def export_run_evidence(outcome: RunOutcome) -> dict[str, object]:
    """Return deterministic, JSON-safe, non-promotional Rezon run evidence."""

    body: dict[str, object] = {
        "schema_version": RUN_EVIDENCE_SCHEMA,
        "receipt": _receipt_payload(outcome),
    }
    encoded = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return {
        **body,
        "evidence_digest": sha256(encoded).hexdigest(),
    }
