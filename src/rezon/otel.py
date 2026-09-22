from __future__ import annotations

import base64
import binascii
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import math
import re


OTEL_INTAKE_SCHEMA = "rezon.otel-intake.v1"

_TRACE_ID = re.compile(r"^[0-9a-fA-F]{32}$")
_SPAN_ID = re.compile(r"^[0-9a-fA-F]{16}$")
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


def _schema_url(value: object, name: str) -> str | None:
    schema = _optional_string(value, name)
    return schema or None


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


def _integer(
    raw: object,
    name: str,
    *,
    minimum: int,
    maximum: int,
) -> int:
    if type(raw) is bool or raw is None:
        raise OTelIntakeError(
            f"{name} must be an integer-compatible OTLP JSON value"
        )

    if type(raw) is int:
        value = raw
    elif type(raw) is float:
        if not math.isfinite(raw) or not raw.is_integer():
            raise OTelIntakeError(
                f"{name} must be an exact integer"
            )
        value = int(raw)
    elif type(raw) is str and raw:
        try:
            decimal = Decimal(raw)
        except InvalidOperation as exc:
            raise OTelIntakeError(
                f"{name} must be an integer-compatible OTLP JSON value"
            ) from exc
        if (
            not decimal.is_finite()
            or decimal != decimal.to_integral_value()
        ):
            raise OTelIntakeError(
                f"{name} must be an exact integer"
            )
        value = int(decimal)
    else:
        raise OTelIntakeError(
            f"{name} must be an integer-compatible OTLP JSON value"
        )

    if value < minimum or value > maximum:
        raise OTelIntakeError(
            f"{name} is outside the permitted integer range"
        )
    return value


def _uint32(raw: object, name: str) -> int:
    return _integer(raw, name, minimum=0, maximum=(2**32) - 1)


def _uint64(raw: object, name: str) -> int:
    return _integer(raw, name, minimum=0, maximum=(2**64) - 1)


def _int64(raw: object, name: str) -> int:
    return _integer(
        raw,
        name,
        minimum=-(2**63),
        maximum=(2**63) - 1,
    )


def _flags(raw: object, name: str = "span.flags") -> int:
    if raw is None:
        return 0
    return _uint32(raw, name)


def _dropped_attributes_count(raw: object, name: str) -> int:
    if raw is None:
        return 0
    return _uint32(raw, name)


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
        return _int64(raw_value, f"{name}.intValue")

    if kind == "doubleValue":
        if type(raw_value) is bool:
            raise OTelIntakeError(
                f"{name}.doubleValue must be numeric or a supported special value"
            )
        if type(raw_value) in (int, float):
            numeric = float(raw_value)
            if not math.isfinite(numeric):
                raise OTelIntakeError(
                    f"{name}.doubleValue must be finite unless encoded as a supported special string"
                )
            return raw_value
        if raw_value in ("NaN", "Infinity", "-Infinity"):
            return raw_value
        if type(raw_value) is str and raw_value:
            try:
                numeric = float(raw_value)
            except ValueError as exc:
                raise OTelIntakeError(
                    f"{name}.doubleValue must be numeric or a supported special value"
                ) from exc
            if not math.isfinite(numeric):
                raise OTelIntakeError(
                    f"{name}.doubleValue is outside the finite double range"
                )
            return numeric
        raise OTelIntakeError(
            f"{name}.doubleValue must be numeric or a supported special value"
        )

    if kind == "bytesValue":
        if type(raw_value) is not str:
            raise OTelIntakeError(
                f"{name}.bytesValue must be a base64 string"
            )
        try:
            encoded = raw_value.encode("ascii")
            padded = encoded + (b"=" * ((-len(encoded)) % 4))
            base64.b64decode(padded, altchars=b"-_", validate=True)
        except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
            raise OTelIntakeError(
                f"{name}.bytesValue must be valid base64"
            ) from exc
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


def _status(raw: object) -> tuple[str, str | None]:
    if raw is None:
        return "unset", None
    status = _require_dict(raw, "span.status")
    code = status.get("code", 0)
    if type(code) is not int or code not in (0, 1, 2):
        raise OTelIntakeError(
            "span.status.code must be an OTLP integer enum value 0, 1, or 2"
        )
    message = _optional_string(
        status.get("message"),
        "span.status.message",
    )
    return (
        {
            0: "unset",
            1: "ok",
            2: "error",
        }[code],
        message,
    )


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
        event_time = _uint64(
            event.get("timeUnixNano", 0),
            f"{span_name}.events[{index}].timeUnixNano",
        )
        events.append(
            {
                "name": name,
                "time_unix_nano": event_time,
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
                "flags": _flags(
                    link.get("flags"),
                    f"{span_name}.links[{index}].flags",
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
    resource_schema_urls: list[str] = []
    span_schema_urls: list[str] = []
    seen_span_ids: set[tuple[str, str]] = set()
    any_dropped_attributes = False
    any_dropped_events = False
    any_dropped_links = False
    any_unbound_timing = False

    for resource_index, raw_resource_spans in enumerate(resource_spans):
        resource_spans_entry = _require_dict(
            raw_resource_spans,
            f"resourceSpans[{resource_index}]",
        )
        resource_schema = _schema_url(
            resource_spans_entry.get("schemaUrl"),
            f"resourceSpans[{resource_index}].schemaUrl",
        )
        if resource_schema is not None:
            if resource_schema not in schema_urls:
                schema_urls.append(resource_schema)
            if resource_schema not in resource_schema_urls:
                resource_schema_urls.append(resource_schema)

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
            scope_schema = _schema_url(
                scope_spans_entry.get("schemaUrl"),
                (
                    f"resourceSpans[{resource_index}]."
                    f"scopeSpans[{scope_index}].schemaUrl"
                ),
            )
            if scope_schema is not None:
                if scope_schema not in schema_urls:
                    schema_urls.append(scope_schema)
                if scope_schema not in span_schema_urls:
                    span_schema_urls.append(scope_schema)

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
                scope_name = _optional_string(
                    scope.get("name"),
                    (
                        f"resourceSpans[{resource_index}]."
                        f"scopeSpans[{scope_index}].scope.name"
                    ),
                )
                scope_version = _optional_string(
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

                start_time = _uint64(
                    span.get("startTimeUnixNano", 0),
                    f"{span_path}.startTimeUnixNano",
                )
                end_time = _uint64(
                    span.get("endTimeUnixNano", 0),
                    f"{span_path}.endTimeUnixNano",
                )
                if start_time and end_time and end_time < start_time:
                    raise OTelIntakeError(
                        f"{span_path}.endTimeUnixNano must be greater than or equal to startTimeUnixNano"
                    )
                any_unbound_timing = (
                    any_unbound_timing
                    or start_time == 0
                    or end_time == 0
                )

                dropped_count = _dropped_attributes_count(
                    span.get("droppedAttributesCount"),
                    f"{span_path}.droppedAttributesCount",
                )
                dropped_events_count = _uint32(
                    span.get("droppedEventsCount", 0),
                    f"{span_path}.droppedEventsCount",
                )
                dropped_links_count = _uint32(
                    span.get("droppedLinksCount", 0),
                    f"{span_path}.droppedLinksCount",
                )
                any_dropped_events = (
                    any_dropped_events or dropped_events_count > 0
                )
                any_dropped_links = (
                    any_dropped_links or dropped_links_count > 0
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

                status, status_message = _status(span.get("status"))
                spans_out.append(
                    {
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "span_name": span_name,
                        "span_kind": _span_kind(span.get("kind")),
                        "start_time_unix_nano": start_time,
                        "end_time_unix_nano": end_time,
                        "trace_state": _optional_string(
                            span.get("traceState"),
                            f"{span_path}.traceState",
                        ),
                        "flags": _flags(span.get("flags")),
                        "status": status,
                        "status_message": status_message,
                        "schema_url": scope_schema,
                        "resource_schema_url": resource_schema,
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
                        "dropped_events_count": dropped_events_count,
                        "dropped_links_count": dropped_links_count,
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
    if any_dropped_events:
        assurance_gaps.append("telemetry_events:dropped")
    if any_dropped_links:
        assurance_gaps.append("telemetry_links:dropped")
    if any_unbound_timing:
        assurance_gaps.append("telemetry_timing:unbound")

    body: dict[str, object] = {
        "schema_version": OTEL_INTAKE_SCHEMA,
        "source_payload_digest": source_payload_digest,
        "schema_urls": schema_urls,
        "resource_schema_urls": resource_schema_urls,
        "span_schema_urls": span_schema_urls,
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
