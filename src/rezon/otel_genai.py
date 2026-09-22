from __future__ import annotations

from hashlib import sha256
import json
import re

from .audit import verify_run_evidence
from .interop import RunEvidenceError


OTEL_GENAI_INTAKE_SCHEMA = "rezon.otel-genai-intake.v1"
_TRACE_ID = re.compile(r"^[0-9a-fA-F]{32}$")
_SPAN_ID = re.compile(r"^[0-9a-fA-F]{16}$")


class OTelGenAIIntakeError(ValueError):
    pass


def _require_dict(value: object, name: str) -> dict[str, object]:
    if type(value) is not dict:
        raise OTelGenAIIntakeError(f"{name} must be an exact object")
    return value


def _require_list(value: object, name: str) -> list[object]:
    if type(value) is not list:
        raise OTelGenAIIntakeError(f"{name} must be an exact list")
    return value


def _optional_nonempty_string(value: object, name: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str or not value:
        raise OTelGenAIIntakeError(f"{name} must be a non-empty string when present")
    return value


def _attributes(raw: object, name: str) -> dict[str, str]:
    values: dict[str, str] = {}
    seen_keys: set[str] = set()
    for index, raw_attribute in enumerate(_require_list(raw, name)):
        attribute = _require_dict(raw_attribute, f"{name}[{index}]")
        key = _optional_nonempty_string(
            attribute.get("key"),
            f"{name}[{index}].key",
        )
        if key is None:
            raise OTelGenAIIntakeError(f"{name}[{index}].key is required")
        if key in seen_keys:
            raise OTelGenAIIntakeError(
                f"{name} contains duplicate attribute key: {key}"
            )
        seen_keys.add(key)
        raw_value = _require_dict(
            attribute.get("value"),
            f"{name}[{index}].value",
        )
        value = raw_value.get("stringValue")
        if type(value) is str:
            values[key] = value
    return values


def _status(raw: object) -> str:
    if raw is None:
        return "unset"
    status = _require_dict(raw, "span.status")
    code = status.get("code", 0)
    if code in (1, "STATUS_CODE_OK", "OK"):
        return "ok"
    if code in (2, "STATUS_CODE_ERROR", "ERROR"):
        return "error"
    return "unset"


def _subject_name(operation: str, attributes: dict[str, str]) -> str | None:
    key_by_operation = {
        "invoke_workflow": "gen_ai.workflow.name",
        "invoke_agent": "gen_ai.agent.name",
        "execute_tool": "gen_ai.tool.name",
    }
    key = key_by_operation.get(operation)
    return attributes.get(key) if key is not None else None


def _canonical_digest(body: dict[str, object]) -> str:
    encoded = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def inspect_otel_genai_export(payload: object) -> dict[str, object]:
    """Inspect OTLP/JSON GenAI spans without promoting telemetry into authority."""

    root = _require_dict(payload, "OTLP export")
    if "resourceSpans" not in root:
        raise OTelGenAIIntakeError("OTLP export requires resourceSpans")
    resource_spans = _require_list(root["resourceSpans"], "resourceSpans")

    events: list[dict[str, object]] = []
    ignored_span_count = 0
    trace_ids: list[str] = []
    schema_urls: list[str] = []
    seen_span_ids: set[tuple[str, str]] = set()

    for resource_index, raw_resource in enumerate(resource_spans):
        resource = _require_dict(
            raw_resource,
            f"resourceSpans[{resource_index}]",
        )
        resource_schema = _optional_nonempty_string(
            resource.get("schemaUrl"),
            f"resourceSpans[{resource_index}].schemaUrl",
        )
        if resource_schema is not None and resource_schema not in schema_urls:
            schema_urls.append(resource_schema)

        scope_spans = _require_list(
            resource.get("scopeSpans", []),
            f"resourceSpans[{resource_index}].scopeSpans",
        )
        for scope_index, raw_scope in enumerate(scope_spans):
            scope = _require_dict(
                raw_scope,
                f"resourceSpans[{resource_index}].scopeSpans[{scope_index}]",
            )
            scope_schema = _optional_nonempty_string(
                scope.get("schemaUrl"),
                (
                    f"resourceSpans[{resource_index}]."
                    f"scopeSpans[{scope_index}].schemaUrl"
                ),
            )
            if scope_schema is not None and scope_schema not in schema_urls:
                schema_urls.append(scope_schema)

            spans = _require_list(
                scope.get("spans", []),
                (
                    f"resourceSpans[{resource_index}]."
                    f"scopeSpans[{scope_index}].spans"
                ),
            )
            for span_index, raw_span in enumerate(spans):
                span = _require_dict(
                    raw_span,
                    (
                        f"resourceSpans[{resource_index}]."
                        f"scopeSpans[{scope_index}].spans[{span_index}]"
                    ),
                )
                trace_id = span.get("traceId")
                span_id = span.get("spanId")
                if type(trace_id) is not str or not _TRACE_ID.fullmatch(trace_id):
                    raise OTelGenAIIntakeError("traceId must be exactly 32 hex characters")
                if type(span_id) is not str or not _SPAN_ID.fullmatch(span_id):
                    raise OTelGenAIIntakeError("spanId must be exactly 16 hex characters")
                identity = (trace_id.lower(), span_id.lower())
                if identity in seen_span_ids:
                    raise OTelGenAIIntakeError(
                        "duplicate span identity within OTLP export"
                    )
                seen_span_ids.add(identity)

                parent_span_id = span.get("parentSpanId")
                if parent_span_id in (None, ""):
                    parent_span_id = None
                elif (
                    type(parent_span_id) is not str
                    or not _SPAN_ID.fullmatch(parent_span_id)
                ):
                    raise OTelGenAIIntakeError(
                        "parentSpanId must be exactly 16 hex characters when present"
                    )

                attributes = _attributes(
                    span.get("attributes", []),
                    "span.attributes",
                )
                operation = attributes.get("gen_ai.operation.name")
                if operation is None:
                    ignored_span_count += 1
                    continue
                if type(operation) is not str or not operation:
                    raise OTelGenAIIntakeError(
                        "gen_ai.operation.name must be a non-empty string"
                    )

                if trace_id not in trace_ids:
                    trace_ids.append(trace_id)

                name = span.get("name")
                if type(name) is not str or not name:
                    raise OTelGenAIIntakeError(
                        "GenAI span name must be a non-empty string"
                    )

                events.append(
                    {
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "span_name": name,
                        "operation": operation,
                        "subject_name": _subject_name(operation, attributes),
                        "provider_name": attributes.get("gen_ai.provider.name"),
                        "schema_url": scope_schema or resource_schema,
                        "run_evidence_digest": attributes.get("rezon.run_evidence.digest"),
                        "run_evidence_schema_version": attributes.get(
                            "rezon.run_evidence.schema_version"
                        ),
                        "status": _status(span.get("status")),
                        "execution_observed": True,
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

    body: dict[str, object] = {
        "schema_version": OTEL_GENAI_INTAKE_SCHEMA,
        "semconv_stability": "development",
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
    if type(anchor_digest) is not str or not re.fullmatch(r"[0-9a-fA-F]{64}", anchor_digest):
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
        "trace_ids": intake["trace_ids"],
        "workflow_span_id": anchor["span_id"],
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
