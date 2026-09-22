from __future__ import annotations

from hashlib import sha256
import json
import re


OTEL_GENAI_INTAKE_SCHEMA = "rezon.otel-genai-intake.v1"
_SUPPORTED_OPERATIONS = {
    "invoke_workflow",
    "invoke_agent",
    "plan",
    "execute_tool",
}
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
    for index, raw_attribute in enumerate(_require_list(raw, name)):
        attribute = _require_dict(raw_attribute, f"{name}[{index}]")
        key = _optional_nonempty_string(
            attribute.get("key"),
            f"{name}[{index}].key",
        )
        if key is None:
            raise OTelGenAIIntakeError(f"{name}[{index}].key is required")
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
                if operation not in _SUPPORTED_OPERATIONS:
                    ignored_span_count += 1
                    continue

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
    if not schema_urls:
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
