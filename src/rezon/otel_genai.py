from __future__ import annotations

import re

from .audit import verify_run_evidence
from .interop import RunEvidenceError
from .otel import (
    OTelIntakeError,
    canonical_json_digest,
    inspect_otel_export,
)


OTEL_GENAI_INTAKE_SCHEMA = "rezon.otel-genai-intake.v1"
_STRING_ATTRIBUTE_KEYS = {
    "gen_ai.operation.name",
    "gen_ai.workflow.name",
    "gen_ai.agent.name",
    "gen_ai.tool.name",
    "gen_ai.provider.name",
    "rezon.run_evidence.digest",
    "rezon.run_evidence.schema_version",
}


class OTelGenAIIntakeError(ValueError):
    pass


def _canonical_digest(value: object) -> str:
    try:
        return canonical_json_digest(value)
    except OTelIntakeError as exc:
        raise OTelGenAIIntakeError(str(exc)) from exc


def _string_attribute(
    attributes: dict[str, object],
    key: str,
) -> str | None:
    value = attributes.get(key)
    if value is None:
        return None
    if type(value) is not str:
        raise OTelGenAIIntakeError(
            f"{key} must use an OTLP stringValue"
        )
    if not value:
        raise OTelGenAIIntakeError(
            f"{key} must be a non-empty string"
        )
    return value


def _subject_name(
    operation: str,
    attributes: dict[str, object],
) -> str | None:
    key_by_operation = {
        "invoke_workflow": "gen_ai.workflow.name",
        "invoke_agent": "gen_ai.agent.name",
        "execute_tool": "gen_ai.tool.name",
    }
    key = key_by_operation.get(operation)
    return _string_attribute(attributes, key) if key is not None else None


def inspect_otel_genai_export(payload: object) -> dict[str, object]:
    """Derive a GenAI semantic view from structurally validated OTLP/JSON."""

    try:
        generic = inspect_otel_export(payload)
    except OTelIntakeError as exc:
        raise OTelGenAIIntakeError(str(exc)) from exc

    events: list[dict[str, object]] = []
    trace_ids: list[str] = []
    schema_urls: list[str] = []
    ignored_span_count = 0

    for span in generic["spans"]:
        attributes = span["attributes"]
        if type(attributes) is not dict:
            raise OTelGenAIIntakeError(
                "generic OTLP intake produced invalid span attributes"
            )

        operation = _string_attribute(
            attributes,
            "gen_ai.operation.name",
        )
        if operation is None:
            ignored_span_count += 1
            continue

        for key in _STRING_ATTRIBUTE_KEYS - {"gen_ai.operation.name"}:
            if key in attributes:
                _string_attribute(attributes, key)

        trace_id = span["trace_id"]
        if trace_id not in trace_ids:
            trace_ids.append(trace_id)

        schema_url = span["schema_url"]
        if schema_url is not None and schema_url not in schema_urls:
            schema_urls.append(schema_url)

        events.append(
            {
                "trace_id": trace_id,
                "span_id": span["span_id"],
                "parent_span_id": span["parent_span_id"],
                "span_name": span["span_name"],
                "operation": operation,
                "subject_name": _subject_name(operation, attributes),
                "provider_name": _string_attribute(
                    attributes,
                    "gen_ai.provider.name",
                ),
                "schema_url": schema_url,
                "run_evidence_digest": _string_attribute(
                    attributes,
                    "rezon.run_evidence.digest",
                ),
                "run_evidence_schema_version": _string_attribute(
                    attributes,
                    "rezon.run_evidence.schema_version",
                ),
                "status": span["status"],
                "execution_observed": True,
                "dropped_attributes_count": span[
                    "dropped_attributes_count"
                ],
            }
        )

    assurance_gaps = [
        "provenance:not_established_by_otel",
        "source_currentness:not_established_by_otel",
        "worker_independence:not_established_by_otel",
        "authority:not_established_by_otel",
        "effect_completion:not_established_by_otel",
    ]
    if not events or any(event["schema_url"] is None for event in events):
        assurance_gaps.append("semantic_convention_version:unbound")
    if any(event["dropped_attributes_count"] > 0 for event in events):
        assurance_gaps.append("telemetry_attributes:dropped")

    body: dict[str, object] = {
        "schema_version": OTEL_GENAI_INTAKE_SCHEMA,
        "semconv_stability": "development",
        "source_payload_digest": generic["source_payload_digest"],
        "schema_urls": schema_urls,
        "trace_ids": trace_ids,
        "events": events,
        "ignored_span_count": ignored_span_count,
        "assurance": {
            "telemetry_structure": "observed",
            "provenance": "unestablished",
            "source_currentness": "unestablished",
            "worker_independence": "unestablished",
            "authority": "unestablished",
            "effect_completion": "unestablished",
        },
        "assurance_gaps": assurance_gaps,
    }
    return {
        **body,
        "intake_digest": _canonical_digest(body),
    }


def bind_otel_genai_to_run_evidence(
    otel_payload: object,
    evidence_payload: object,
) -> dict[str, object]:
    """Cross-bind an OTLP GenAI workflow span to verified Rezon run evidence."""

    intake = inspect_otel_genai_export(otel_payload)
    if len(intake["trace_ids"]) != 1:
        raise OTelGenAIIntakeError(
            "OTLP evidence binding requires exactly one GenAI trace"
        )
    anchored = [
        event
        for event in intake["events"]
        if event["operation"] == "invoke_workflow"
        and (
            event["run_evidence_digest"] is not None
            or event["run_evidence_schema_version"] is not None
        )
    ]
    if not anchored:
        raise OTelGenAIIntakeError("OTLP workflow has no Rezon evidence anchor")
    if len(anchored) != 1:
        raise OTelGenAIIntakeError(
            "OTLP workflow must contain exactly one Rezon evidence anchor"
        )

    anchor = anchored[0]
    anchor_digest = anchor["run_evidence_digest"]
    anchor_schema = anchor["run_evidence_schema_version"]
    if type(anchor_digest) is not str or not re.fullmatch(
        r"[0-9a-fA-F]{64}",
        anchor_digest,
    ):
        raise OTelGenAIIntakeError(
            "Rezon evidence anchor digest must be exactly 64 hex characters"
        )
    if type(anchor_schema) is not str or not anchor_schema:
        raise OTelGenAIIntakeError(
            "Rezon evidence anchor schema must be a non-empty string"
        )

    try:
        evidence = verify_run_evidence(evidence_payload)
    except RunEvidenceError as exc:
        raise OTelGenAIIntakeError(
            f"Rezon run evidence verification failed: {exc}"
        ) from exc

    if anchor_digest != evidence["evidence_digest"]:
        raise OTelGenAIIntakeError(
            "OTLP Rezon evidence digest does not match verified artifact"
        )
    if anchor_schema != evidence["schema_version"]:
        raise OTelGenAIIntakeError(
            "OTLP Rezon evidence schema does not match verified artifact"
        )

    body: dict[str, object] = {
        "binding_schema_version": "rezon.otel-run-evidence-binding.v1",
        "binding_status": "verified",
        "binding_scope": "trace_to_verified_artifact",
        "trace_ids": intake["trace_ids"],
        "workflow_span_id": anchor["span_id"],
        "telemetry_source_payload_digest": intake["source_payload_digest"],
        "telemetry_intake_digest": intake["intake_digest"],
        "telemetry_assurance_gaps": list(intake["assurance_gaps"]),
        "evidence_digest": evidence["evidence_digest"],
        "evidence_schema_version": evidence["schema_version"],
        "evidence_effect_state": evidence["effect_state"],
        "authority": "unestablished",
        "effect_completion": "unestablished",
    }
    return {
        **body,
        "binding_digest": _canonical_digest(body),
    }
