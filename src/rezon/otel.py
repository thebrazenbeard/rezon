from __future__ import annotations

from hashlib import sha256
import json
import re


OTEL_INTAKE_SCHEMA = "rezon.otel-intake.v1"

_TRACE_ID = re.compile(r"^[0-9a-fA-F]{32}$")
_SPAN_ID = re.compile(r"^[0-9a-fA-F]{16}$")
_INT = re.compile(r"^-?[0-9]+$")
_ANY_VALUE_KINDS = {
    "stringValue",
    "boolValue",
    "intValue",
    "doubleValue",
    "bytesValue",
    "arrayValue",
    "kvlistValue",
}


class OTelIntakeError(ValueError):
    pass


def canonical_json_digest(value: object) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise OTelIntakeError(
            "OTLP assurance input must be canonically JSON-serializable"
        ) from exc
    return sha256(encoded).hexdigest()


def _require_dict(value: object, name: str) -> dict[str, object]:
    if type(value) is not dict:
        raise OTelIntakeError(f"{name} must be an exact object")
    return value


def _require_list(value: object, name: str) -> list[object]:
    if type(value) is not list:
        raise OTelIntakeError(f"{name} must be an exact list")
    return value


def _optional_nonempty_string(value: object, name: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str or not value:
        raise OTelIntakeError(f"{name} must be a non-empty string when present")
    return value


def _optional_string(value: object, name: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise OTelIntakeError(f"{name} must be a string when present")
    return value


def _valid_trace_id(value: object) -> bool:
    return (
        type(value) is str
        and _TRACE_ID.fullmatch(value) is not None
        and int(value, 16) != 0
    )


def _valid_span_id(value: object) -> bool:
    return (
        type(value) is str
        and _SPAN_ID.fullmatch(value) is not None
        and int(value, 16) != 0
    )


def _flags(raw: object) -> int:
    if raw is None:
        return 0
    if type(raw) is not int or raw < 0 or raw > 0xFFFFFFFF:
        raise OTelIntakeError(
            "span.flags must be an unsigned 32-bit integer when present"
        )
    return raw


def _dropped_attributes_count(raw: object, name: str) -> int:
    if raw is None:
        return 0
    if type(raw) is not int or raw < 0:
        raise OTelIntakeError(
            f"{name} must be a non-negative exact integer"
        )
    return raw


def _decode_any_value(raw: object, name: str) -> object:
    value = _require_dict(raw, name)
    present = [key for key in _ANY_VALUE_KINDS if key in value]
    if len(present) != 1:
        raise OTelIntakeError(
            f"{name} must contain exactly one OTLP value kind"
        )

    kind = present[0]
    raw_value = value[kind]

    if kind == "stringValue":
        if type(raw_value) is not str:
            raise OTelIntakeError(f"{name}.stringValue must be a string")
        return raw_value

    if kind == "boolValue":
        if type(raw_value) is not bool:
            raise OTelIntakeError(f"{name}.boolValue must be a boolean")
        return raw_value

    if kind == "intValue":
        if type(raw_value) is int:
            return raw_value
        if type(raw_value) is str and _INT.fullmatch(raw_value):
            return int(raw_value)
        raise OTelIntakeError(
            f"{name}.intValue must be an integer or decimal integer string"
        )

    if kind == "doubleValue":
        if type(raw_value) in (int, float):
            return raw_value
        if raw_value in ("NaN", "Infinity", "-Infinity"):
            return raw_value
        raise OTelIntakeError(
            f"{name}.doubleValue must be numeric or a supported special value"
        )

    if kind == "bytesValue":
        if type(raw_value) is not str:
            raise OTelIntakeError(
                f"{name}.bytesValue must be a base64 string"
            )
        return {"bytes_base64": raw_value}

    if kind == "arrayValue":
        array = _require_dict(raw_value, f"{name}.arrayValue")
        values = _require_list(
            array.get("values", []),
            f"{name}.arrayValue.values",
        )
        return [
            _decode_any_value(item, f"{name}.arrayValue.values[{index}]")
            for index, item in enumerate(values)
        ]

    kvlist = _require_dict(raw_value, f"{name}.kvlistValue")
    return _decode_attributes(
        kvlist.get("values", []),
        f"{name}.kvlistValue.values",
    )


def _decode_attributes(raw: object, name: str) -> dict[str, object]:
    values: dict[str, object] = {}
    for index, raw_attribute in enumerate(_require_list(raw, name)):
        attribute = _require_dict(raw_attribute, f"{name}[{index}]")
        key = _optional_nonempty_string(
            attribute.get("key"),
            f"{name}[{index}].key",
        )
        if key is None:
            raise OTelIntakeError(f"{name}[{index}].key is required")
        if key in values:
            raise OTelIntakeError(
                f"{name} contains duplicate attribute key: {key}"
            )
        values[key] = _decode_any_value(
            attribute.get("value"),
            f"{name}[{index}].value",
        )
    return values


def _status(raw: object) -> str:
    if raw is None:
        return "unset"
    status = _require_dict(raw, "span.status")
    code = status.get("code", 0)
    if type(code) is not int or code not in (0, 1, 2):
        raise OTelIntakeError(
            "span.status.code must be an OTLP integer enum value 0, 1, or 2"
        )
    return {
        0: "unset",
        1: "ok",
        2: "error",
    }[code]


def _span_kind(raw: object) -> int | None:
    if raw is None:
        return None
    if type(raw) is not int or raw not in (0, 1, 2, 3, 4, 5):
        raise OTelIntakeError(
            "span.kind must be an OTLP integer enum value from 0 through 5"
        )
    return raw


def _events(raw: object, span_name: str) -> tuple[list[dict[str, object]], bool]:
    events: list[dict[str, object]] = []
    dropped = False
    for index, raw_event in enumerate(
        _require_list(raw, f"{span_name}.events")
    ):
        event = _require_dict(
            raw_event,
            f"{span_name}.events[{index}]",
        )
        name = _optional_nonempty_string(
            event.get("name"),
            f"{span_name}.events[{index}].name",
        )
        if name is None:
            raise OTelIntakeError(
                f"{span_name}.events[{index}].name is required"
            )
        dropped_count = _dropped_attributes_count(
            event.get("droppedAttributesCount"),
            f"{span_name}.events[{index}].droppedAttributesCount",
        )
        dropped = dropped or dropped_count > 0
        events.append(
            {
                "name": name,
                "attributes": _decode_attributes(
                    event.get("attributes", []),
                    f"{span_name}.events[{index}].attributes",
                ),
                "dropped_attributes_count": dropped_count,
            }
        )
    return events, dropped


def _links(raw: object, span_name: str) -> tuple[list[dict[str, object]], bool]:
    links: list[dict[str, object]] = []
    dropped = False
    for index, raw_link in enumerate(
        _require_list(raw, f"{span_name}.links")
    ):
        link = _require_dict(
            raw_link,
            f"{span_name}.links[{index}]",
        )
        trace_id = link.get("traceId")
        span_id = link.get("spanId")
        if not _valid_trace_id(trace_id):
            raise OTelIntakeError(
                f"{span_name}.links[{index}].traceId must be a non-zero 32-character hex ID"
            )
        if not _valid_span_id(span_id):
            raise OTelIntakeError(
                f"{span_name}.links[{index}].spanId must be a non-zero 16-character hex ID"
            )
        dropped_count = _dropped_attributes_count(
            link.get("droppedAttributesCount"),
            f"{span_name}.links[{index}].droppedAttributesCount",
        )
        dropped = dropped or dropped_count > 0
        links.append(
            {
                "trace_id": trace_id,
                "span_id": span_id,
                "trace_state": _optional_string(
                    link.get("traceState"),
                    f"{span_name}.links[{index}].traceState",
                ),
                "attributes": _decode_attributes(
                    link.get("attributes", []),
                    f"{span_name}.links[{index}].attributes",
                ),
                "dropped_attributes_count": dropped_count,
            }
        )
    return links, dropped


def inspect_otel_export(payload: object) -> dict[str, object]:
    """Inspect generic OTLP/JSON traces without assigning semantic meaning."""

    root = _require_dict(payload, "OTLP export")
    if "resourceSpans" not in root:
        raise OTelIntakeError("OTLP export requires resourceSpans")
    resource_spans = _require_list(root["resourceSpans"], "resourceSpans")
    source_payload_digest = canonical_json_digest(root)

    spans_out: list[dict[str, object]] = []
    trace_ids: list[str] = []
    schema_urls: list[str] = []
    seen_span_ids: set[tuple[str, str]] = set()
    any_dropped_attributes = False

    for resource_index, raw_resource_spans in enumerate(resource_spans):
        resource_spans_entry = _require_dict(
            raw_resource_spans,
            f"resourceSpans[{resource_index}]",
        )
        resource_schema = _optional_nonempty_string(
            resource_spans_entry.get("schemaUrl"),
            f"resourceSpans[{resource_index}].schemaUrl",
        )
        if resource_schema is not None and resource_schema not in schema_urls:
            schema_urls.append(resource_schema)

        raw_resource = resource_spans_entry.get("resource")
        if raw_resource is None:
            resource_attributes: dict[str, object] = {}
            resource_dropped = 0
        else:
            resource = _require_dict(
                raw_resource,
                f"resourceSpans[{resource_index}].resource",
            )
            resource_attributes = _decode_attributes(
                resource.get("attributes", []),
                f"resourceSpans[{resource_index}].resource.attributes",
            )
            resource_dropped = _dropped_attributes_count(
                resource.get("droppedAttributesCount"),
                f"resourceSpans[{resource_index}].resource.droppedAttributesCount",
            )
            any_dropped_attributes = (
                any_dropped_attributes or resource_dropped > 0
            )

        scope_spans = _require_list(
            resource_spans_entry.get("scopeSpans", []),
            f"resourceSpans[{resource_index}].scopeSpans",
        )
        for scope_index, raw_scope_spans in enumerate(scope_spans):
            scope_spans_entry = _require_dict(
                raw_scope_spans,
                (
                    f"resourceSpans[{resource_index}]."
                    f"scopeSpans[{scope_index}]"
                ),
            )
            scope_schema = _optional_nonempty_string(
                scope_spans_entry.get("schemaUrl"),
                (
                    f"resourceSpans[{resource_index}]."
                    f"scopeSpans[{scope_index}].schemaUrl"
                ),
            )
            if scope_schema is not None and scope_schema not in schema_urls:
                schema_urls.append(scope_schema)

            raw_scope = scope_spans_entry.get("scope")
            if raw_scope is None:
                scope_name = None
                scope_version = None
                scope_attributes: dict[str, object] = {}
                scope_dropped = 0
            else:
                scope = _require_dict(
                    raw_scope,
                    (
                        f"resourceSpans[{resource_index}]."
                        f"scopeSpans[{scope_index}].scope"
                    ),
                )
                scope_name = _optional_nonempty_string(
                    scope.get("name"),
                    (
                        f"resourceSpans[{resource_index}]."
                        f"scopeSpans[{scope_index}].scope.name"
                    ),
                )
                scope_version = _optional_nonempty_string(
                    scope.get("version"),
                    (
                        f"resourceSpans[{resource_index}]."
                        f"scopeSpans[{scope_index}].scope.version"
                    ),
                )
                scope_attributes = _decode_attributes(
                    scope.get("attributes", []),
                    (
                        f"resourceSpans[{resource_index}]."
                        f"scopeSpans[{scope_index}].scope.attributes"
                    ),
                )
                scope_dropped = _dropped_attributes_count(
                    scope.get("droppedAttributesCount"),
                    (
                        f"resourceSpans[{resource_index}]."
                        f"scopeSpans[{scope_index}].scope.droppedAttributesCount"
                    ),
                )
                any_dropped_attributes = (
                    any_dropped_attributes or scope_dropped > 0
                )

            raw_spans = _require_list(
                scope_spans_entry.get("spans", []),
                (
                    f"resourceSpans[{resource_index}]."
                    f"scopeSpans[{scope_index}].spans"
                ),
            )
            for span_index, raw_span in enumerate(raw_spans):
                span_path = (
                    f"resourceSpans[{resource_index}]."
                    f"scopeSpans[{scope_index}].spans[{span_index}]"
                )
                span = _require_dict(raw_span, span_path)
                trace_id = span.get("traceId")
                span_id = span.get("spanId")
                if not _valid_trace_id(trace_id):
                    raise OTelIntakeError(
                        "traceId must be a non-zero 32-character hex ID"
                    )
                if not _valid_span_id(span_id):
                    raise OTelIntakeError(
                        "spanId must be a non-zero 16-character hex ID"
                    )

                identity = (trace_id.lower(), span_id.lower())
                if identity in seen_span_ids:
                    raise OTelIntakeError(
                        "duplicate span identity within OTLP export"
                    )
                seen_span_ids.add(identity)

                parent_span_id = span.get("parentSpanId")
                if parent_span_id in (None, ""):
                    parent_span_id = None
                elif (
                    not _valid_span_id(parent_span_id)
                ):
                    raise OTelIntakeError(
                        "parentSpanId must be exactly 16 hex characters when present"
                    )

                span_name = _optional_nonempty_string(
                    span.get("name"),
                    f"{span_path}.name",
                )
                if span_name is None:
                    raise OTelIntakeError(f"{span_path}.name is required")

                dropped_count = _dropped_attributes_count(
                    span.get("droppedAttributesCount"),
                    f"{span_path}.droppedAttributesCount",
                )
                events, events_dropped = _events(
                    span.get("events", []),
                    span_path,
                )
                links, links_dropped = _links(
                    span.get("links", []),
                    span_path,
                )
                any_dropped_attributes = (
                    any_dropped_attributes
                    or dropped_count > 0
                    or events_dropped
                    or links_dropped
                )

                if trace_id not in trace_ids:
                    trace_ids.append(trace_id)

                spans_out.append(
                    {
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "span_name": span_name,
                        "span_kind": _span_kind(span.get("kind")),
                        "trace_state": _optional_string(
                            span.get("traceState"),
                            f"{span_path}.traceState",
                        ),
                        "flags": _flags(span.get("flags")),
                        "status": _status(span.get("status")),
                        "schema_url": scope_schema or resource_schema,
                        "resource_attributes": dict(resource_attributes),
                        "resource_dropped_attributes_count": resource_dropped,
                        "instrumentation_scope": {
                            "name": scope_name,
                            "version": scope_version,
                            "attributes": dict(scope_attributes),
                            "dropped_attributes_count": scope_dropped,
                        },
                        "attributes": _decode_attributes(
                            span.get("attributes", []),
                            f"{span_path}.attributes",
                        ),
                        "events": events,
                        "links": links,
                        "dropped_attributes_count": dropped_count,
                        "semantic_classification": "unclassified",
                    }
                )

    assurance_gaps = [
        "semantic_meaning:not_established_by_otel",
        "provenance:not_established_by_otel",
        "source_currentness:not_established_by_otel",
        "worker_independence:not_established_by_otel",
        "authority:not_established_by_otel",
        "effect_completion:not_established_by_otel",
    ]
    if not spans_out or any(span["schema_url"] is None for span in spans_out):
        assurance_gaps.append("telemetry_schema:unbound")
    if any_dropped_attributes:
        assurance_gaps.append("telemetry_attributes:dropped")

    body: dict[str, object] = {
        "schema_version": OTEL_INTAKE_SCHEMA,
        "source_payload_digest": source_payload_digest,
        "schema_urls": schema_urls,
        "trace_ids": trace_ids,
        "span_count": len(spans_out),
        "spans": spans_out,
        "assurance": {
            "telemetry_structure": "observed",
            "semantic_meaning": "unestablished",
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
        "intake_digest": canonical_json_digest(body),
    }
