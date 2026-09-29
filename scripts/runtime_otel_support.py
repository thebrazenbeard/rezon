from __future__ import annotations

import base64
from collections.abc import Mapping, Sequence
from typing import Any


def _plain_string(value: object, name: str) -> str:
    if type(value) is str:
        return value
    if isinstance(value, str):
        enum_value = getattr(value, "value", None)
        if type(enum_value) is str:
            return enum_value
        return str(value)
    raise TypeError(f"{name} must be string-like")


def _otlp_value(value: object) -> dict[str, object]:
    if isinstance(value, str):
        return {"stringValue": _plain_string(value, "attribute value")}
    if type(value) is bool:
        return {"boolValue": value}
    if type(value) is int:
        return {"intValue": str(value)}
    if type(value) is float:
        return {"doubleValue": value}
    if type(value) is bytes:
        return {"bytesValue": base64.b64encode(value).decode("ascii")}
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return {
            "arrayValue": {
                "values": [_otlp_value(item) for item in value]
            }
        }
    if isinstance(value, Mapping):
        return {
            "kvlistValue": {
                "values": [
                    {
                        "key": _plain_string(
                            key,
                            "OpenTelemetry map key",
                        ),
                        "value": _otlp_value(item),
                    }
                    for key, item in value.items()
                ]
            }
        }
    raise TypeError(
        f"unsupported OpenTelemetry attribute value: {type(value).__name__}"
    )


def _attributes(attributes: object) -> list[dict[str, object]]:
    if attributes is None:
        return []
    if not isinstance(attributes, Mapping):
        raise TypeError("OpenTelemetry attributes must be mapping-like")

    projected: list[dict[str, object]] = []
    for key, value in attributes.items():
        if not isinstance(key, str):
            raise TypeError(
                "OpenTelemetry attribute keys must be string-like for OTLP JSON"
            )
        projected.append(
            {
                "key": _plain_string(
                    key,
                    "OpenTelemetry attribute key",
                ),
                "value": _otlp_value(value),
            }
        )
    return projected


def _dropped_attributes(owner: object, attributes: object) -> int:
    direct = getattr(owner, "dropped_attributes", None)
    if direct is not None:
        return int(direct)
    return int(getattr(attributes, "dropped", 0) or 0)


def _hex(value: int, width: int) -> str:
    return f"{value:0{width}x}"


def _trace_state(context: object) -> str | None:
    trace_state = getattr(context, "trace_state", None)
    if trace_state is None:
        return None
    to_header = getattr(trace_state, "to_header", None)
    if not callable(to_header):
        return None
    header = to_header()
    if not header:
        return None
    return _plain_string(header, "OpenTelemetry trace state")


def _status(span: Any) -> dict[str, object]:
    status = getattr(span, "status", None)
    code = getattr(status, "status_code", None)
    name = getattr(code, "name", None)
    if name == "OK":
        numeric = 1
    elif name == "ERROR":
        numeric = 2
    else:
        numeric = 0

    projected: dict[str, object] = {"code": numeric}
    description = getattr(status, "description", None)
    if description:
        projected["message"] = _plain_string(
            description,
            "OpenTelemetry status description",
        )
    return projected


def _span_kind(span: Any) -> int:
    kind = getattr(span, "kind", None)
    if kind is None:
        return 0
    value = getattr(kind, "value", kind)
    if type(value) is not int:
        raise TypeError("OpenTelemetry span kind must expose an integer value")
    return value


def _project_event(event: object) -> dict[str, object]:
    attributes = getattr(event, "attributes", None)
    timestamp = int(getattr(event, "timestamp", 0) or 0)
    return {
        "timeUnixNano": str(timestamp),
        "name": _plain_string(
            getattr(event, "name"),
            "OpenTelemetry event name",
        ),
        "attributes": _attributes(attributes),
        "droppedAttributesCount": _dropped_attributes(
            event,
            attributes,
        ),
    }


def _project_link(link: object) -> dict[str, object]:
    context = getattr(link, "context")
    attributes = getattr(link, "attributes", None)
    projected: dict[str, object] = {
        "traceId": _hex(getattr(context, "trace_id"), 32),
        "spanId": _hex(getattr(context, "span_id"), 16),
        "attributes": _attributes(attributes),
        "droppedAttributesCount": _dropped_attributes(
            link,
            attributes,
        ),
        "flags": int(getattr(context, "trace_flags", 0) or 0),
    }
    trace_state = _trace_state(context)
    if trace_state is not None:
        projected["traceState"] = trace_state
    return projected


def _project_resource(span: Any) -> tuple[dict[str, object] | None, str | None]:
    resource = getattr(span, "resource", None)
    if resource is None:
        return None, None

    attributes = getattr(resource, "attributes", None)
    projected = {
        "attributes": _attributes(attributes),
        "droppedAttributesCount": _dropped_attributes(
            resource,
            attributes,
        ),
    }
    schema_url = getattr(resource, "schema_url", None)
    if schema_url:
        schema_url = _plain_string(
            schema_url,
            "OpenTelemetry resource schema URL",
        )
    else:
        schema_url = None
    return projected, schema_url


def _project_scope(span: Any) -> tuple[dict[str, object] | None, str | None]:
    scope = getattr(span, "instrumentation_scope", None)
    if scope is None:
        return None, None

    attributes = getattr(scope, "attributes", None)
    projected = {
        "name": _plain_string(
            getattr(scope, "name", ""),
            "OpenTelemetry instrumentation scope name",
        ),
        "version": (
            _plain_string(
                getattr(scope, "version"),
                "OpenTelemetry instrumentation scope version",
            )
            if getattr(scope, "version", None) is not None
            else ""
        ),
        "attributes": _attributes(attributes),
        "droppedAttributesCount": _dropped_attributes(
            scope,
            attributes,
        ),
    }
    schema_url = getattr(scope, "schema_url", None)
    if schema_url:
        schema_url = _plain_string(
            schema_url,
            "OpenTelemetry instrumentation scope schema URL",
        )
    else:
        schema_url = None
    return projected, schema_url


def readable_spans_to_otlp_json(
    spans: Sequence[Any],
) -> dict[str, object]:
    """Project actual ReadableSpan fields into OTLP/JSON for qualification.

    The projection serializes runtime-emitted structure only. It never creates
    semantic attributes such as gen_ai.* fields that were not emitted by the
    runtime itself.
    """

    resource_spans: list[dict[str, object]] = []
    for span in spans:
        context = span.context
        parent = span.parent
        attributes = getattr(span, "attributes", None)
        start_time = int(getattr(span, "start_time", 0) or 0)
        end_time = int(getattr(span, "end_time", 0) or 0)

        projected_span: dict[str, object] = {
            "traceId": _hex(context.trace_id, 32),
            "spanId": _hex(context.span_id, 16),
            "name": _plain_string(
                span.name,
                "OpenTelemetry span name",
            ),
            "kind": _span_kind(span),
            "startTimeUnixNano": str(start_time),
            "endTimeUnixNano": str(end_time),
            "status": _status(span),
            "attributes": _attributes(attributes),
            "droppedAttributesCount": _dropped_attributes(
                span,
                attributes,
            ),
            "events": [
                _project_event(event)
                for event in (getattr(span, "events", ()) or ())
            ],
            "droppedEventsCount": int(
                getattr(span, "dropped_events", 0) or 0
            ),
            "links": [
                _project_link(link)
                for link in (getattr(span, "links", ()) or ())
            ],
            "droppedLinksCount": int(
                getattr(span, "dropped_links", 0) or 0
            ),
            "flags": int(
                getattr(context, "trace_flags", 0) or 0
            ),
        }

        if parent is not None and getattr(parent, "span_id", 0):
            projected_span["parentSpanId"] = _hex(
                parent.span_id,
                16,
            )

        trace_state = _trace_state(context)
        if trace_state is not None:
            projected_span["traceState"] = trace_state

        scope, scope_schema = _project_scope(span)
        scope_entry: dict[str, object] = {
            "spans": [projected_span],
        }
        if scope is not None:
            scope_entry["scope"] = scope
        if scope_schema is not None:
            scope_entry["schemaUrl"] = scope_schema

        resource, resource_schema = _project_resource(span)
        resource_entry: dict[str, object] = {
            "scopeSpans": [scope_entry],
        }
        if resource is not None:
            resource_entry["resource"] = resource
        if resource_schema is not None:
            resource_entry["schemaUrl"] = resource_schema
        resource_spans.append(resource_entry)

    return {"resourceSpans": resource_spans}


def genai_attribute_keys(spans: Sequence[Any]) -> tuple[str, ...]:
    keys: list[str] = []
    for span in spans:
        for key in (span.attributes or {}):
            if key.startswith("gen_ai.") and key not in keys:
                keys.append(key)
    return tuple(keys)
