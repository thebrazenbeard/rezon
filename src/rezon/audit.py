from __future__ import annotations

from hashlib import sha256
import json

from .interop import RUN_EVIDENCE_SCHEMA, RunEvidenceError
from .provenance import canonical_producer_execution_id
from .receipts import FailureState


_EVIDENCE_KEYS = {"schema_version", "receipt", "executions", "evidence_digest"}
_RECEIPT_KEYS = {
    "task_id", "episode_version", "accepted_claim_ids", "rejected_claim_ids",
    "unresolved", "failures", "effect_state", "source_versions",
    "execution_ids", "execution_output_digests", "execution_producer_ids",
    "task_envelope_digest", "claim_disposition_complete",
}
_RECORD_KEYS = {
    "execution_id", "node_id", "episode_version", "visible_proposition_ids",
    "blinded_proposition_ids", "visible_relation_ids", "blinded_relation_ids",
    "emitted_proposition_ids", "independence_demonstrated",
    "task_envelope_digest", "executor_task_specification_digest",
    "executor_episode_version", "canonical_producer_execution_id",
    "canonical_episode_snapshot_digest", "canonical_output_digest",
    "source_refs", "source_versions", "reported_source_refs",
    "reported_source_versions", "failures",
}
_KNOWN_FAILURES = {failure.value for failure in FailureState}


def _require_dict(value: object, name: str) -> dict[str, object]:
    if type(value) is not dict:
        raise RunEvidenceError(f"{name} must be an exact object")
    return value


def _require_keys(value: dict[str, object], expected: set[str], name: str) -> None:
    if set(value) != expected:
        raise RunEvidenceError(f"{name} fields do not match the v1 schema")


def _require_string(value: object, name: str) -> str:
    if type(value) is not str or not value:
        raise RunEvidenceError(f"{name} must be a non-empty exact string")
    return value


def _optional_string(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, name)


def _string_list(value: object, name: str) -> tuple[str, ...]:
    if type(value) is not list:
        raise RunEvidenceError(f"{name} must be an exact list")
    if any(type(item) is not str or not item for item in value):
        raise RunEvidenceError(f"{name} must contain non-empty exact strings")
    return tuple(value)


def _pairs(value: object, name: str) -> tuple[tuple[str, str], ...]:
    if type(value) is not list:
        raise RunEvidenceError(f"{name} must be an exact list")
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for item in value:
        if (
            type(item) is not list
            or len(item) != 2
            or any(type(part) is not str or not part for part in item)
        ):
            raise RunEvidenceError(f"{name} must contain two-string lists")
        left, right = item
        if left in seen:
            raise RunEvidenceError(f"{name} cannot duplicate execution ids")
        seen.add(left)
        pairs.append((left, right))
    return tuple(pairs)


def _body_digest(
    schema_version: str,
    receipt: dict[str, object],
    executions: list[object],
) -> str:
    body = {
        "schema_version": schema_version,
        "receipt": receipt,
        "executions": executions,
    }
    encoded = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def verify_run_evidence(payload: object) -> dict[str, object]:
    """Verify a serialized rezon.run-evidence.v1 artifact without executing it."""

    evidence = _require_dict(payload, "run evidence")
    _require_keys(evidence, _EVIDENCE_KEYS, "run evidence")

    schema_version = _require_string(evidence["schema_version"], "schema_version")
    if schema_version != RUN_EVIDENCE_SCHEMA:
        raise RunEvidenceError(f"unsupported run evidence schema: {schema_version}")

    receipt = _require_dict(evidence["receipt"], "receipt")
    _require_keys(receipt, _RECEIPT_KEYS, "receipt")
    executions_raw = evidence["executions"]
    if type(executions_raw) is not list:
        raise RunEvidenceError("executions must be an exact list")

    supplied_digest = _require_string(evidence["evidence_digest"], "evidence_digest")
    expected_digest = _body_digest(schema_version, receipt, executions_raw)
    if supplied_digest != expected_digest:
        raise RunEvidenceError("evidence digest does not match canonical body")

    _require_string(receipt["task_id"], "receipt.task_id")
    _require_string(receipt["episode_version"], "receipt.episode_version")
    if receipt["accepted_claim_ids"] != [] or receipt["rejected_claim_ids"] != []:
        raise RunEvidenceError("portable run evidence cannot assert claim disposition")
    unresolved = _string_list(receipt["unresolved"], "receipt.unresolved")
    receipt_failures = _string_list(receipt["failures"], "receipt.failures")
    if any(failure not in _KNOWN_FAILURES for failure in receipt_failures):
        raise RunEvidenceError("receipt contains an unknown failure state")
    if receipt["effect_state"] != "plan":
        raise RunEvidenceError("portable run evidence may report PLAN only")
    receipt_sources = _string_list(receipt["source_versions"], "receipt.source_versions")
    receipt_execution_ids = _string_list(receipt["execution_ids"], "receipt.execution_ids")
    if len(set(receipt_execution_ids)) != len(receipt_execution_ids):
        raise RunEvidenceError("receipt execution ids must be unique")
    receipt_outputs = _pairs(
        receipt["execution_output_digests"],
        "receipt.execution_output_digests",
    )
    receipt_producers = _pairs(
        receipt["execution_producer_ids"],
        "receipt.execution_producer_ids",
    )
    receipt_task_digest = _optional_string(
        receipt["task_envelope_digest"],
        "receipt.task_envelope_digest",
    )
    if receipt["claim_disposition_complete"] is not False:
        raise RunEvidenceError("portable run evidence cannot claim disposition completeness")

    execution_ids: list[str] = []
    source_versions: list[str] = []
    trace_failures: list[str] = []
    expected_outputs: list[tuple[str, str]] = []
    expected_producers: list[tuple[str, str]] = []

    for index, raw_record in enumerate(executions_raw):
        record = _require_dict(raw_record, f"executions[{index}]")
        _require_keys(record, _RECORD_KEYS, f"executions[{index}]")
        execution_id = _require_string(
            record["execution_id"],
            f"executions[{index}].execution_id",
        )
        node_id = _require_string(record["node_id"], f"executions[{index}].node_id")
        _require_string(
            record["episode_version"],
            f"executions[{index}].episode_version",
        )
        for field in (
            "visible_proposition_ids",
            "blinded_proposition_ids",
            "visible_relation_ids",
            "blinded_relation_ids",
            "emitted_proposition_ids",
            "source_refs",
            "source_versions",
            "reported_source_refs",
            "reported_source_versions",
        ):
            values = _string_list(record[field], f"executions[{index}].{field}")
            if field == "source_versions":
                for value in values:
                    if value not in source_versions:
                        source_versions.append(value)

        if type(record["independence_demonstrated"]) is not bool:
            raise RunEvidenceError(
                f"executions[{index}].independence_demonstrated must be boolean"
            )
        record_task_digest = _optional_string(
            record["task_envelope_digest"],
            f"executions[{index}].task_envelope_digest",
        )
        task_spec_digest = _optional_string(
            record["executor_task_specification_digest"],
            f"executions[{index}].executor_task_specification_digest",
        )
        _optional_string(
            record["executor_episode_version"],
            f"executions[{index}].executor_episode_version",
        )
        producer_id = _optional_string(
            record["canonical_producer_execution_id"],
            f"executions[{index}].canonical_producer_execution_id",
        )
        snapshot_digest = _optional_string(
            record["canonical_episode_snapshot_digest"],
            f"executions[{index}].canonical_episode_snapshot_digest",
        )
        output_digest = _optional_string(
            record["canonical_output_digest"],
            f"executions[{index}].canonical_output_digest",
        )
        failures = _string_list(record["failures"], f"executions[{index}].failures")
        if any(failure not in _KNOWN_FAILURES for failure in failures):
            raise RunEvidenceError("execution contains an unknown failure state")

        execution_ids.append(execution_id)
        for failure in failures:
            if failure not in trace_failures:
                trace_failures.append(failure)
        if output_digest is not None:
            expected_outputs.append((execution_id, output_digest))
        if producer_id is not None:
            if snapshot_digest is None or output_digest is None:
                raise RunEvidenceError(
                    "canonical producer binding requires snapshot and output digests"
                )
            recomputed = canonical_producer_execution_id(
                node_id,
                snapshot_digest,
                task_spec_digest,
                output_digest,
            )
            if producer_id != recomputed:
                raise RunEvidenceError("canonical producer identity does not recompute")
            expected_producers.append((execution_id, producer_id))
        if record_task_digest != receipt_task_digest:
            raise RunEvidenceError("receipt task envelope digest does not match trace")

    if len(set(execution_ids)) != len(execution_ids):
        raise RunEvidenceError("trace execution ids must be unique")
    if tuple(execution_ids) != receipt_execution_ids:
        raise RunEvidenceError("receipt execution ids do not match trace")
    if tuple(source_versions) != receipt_sources:
        raise RunEvidenceError("receipt source versions do not match trace")
    if any(failure not in receipt_failures for failure in trace_failures):
        raise RunEvidenceError("receipt failure summary does not cover trace failures")
    if tuple(expected_outputs) != receipt_outputs:
        raise RunEvidenceError("receipt output bindings do not match trace")
    if tuple(expected_producers) != receipt_producers:
        raise RunEvidenceError("receipt producer bindings do not match trace")

    return {
        "valid": True,
        "schema_version": schema_version,
        "evidence_digest": supplied_digest,
        "execution_count": len(execution_ids),
        "failure_count": len(receipt_failures),
        "unresolved_count": len(unresolved),
        "effect_state": "plan",
    }
