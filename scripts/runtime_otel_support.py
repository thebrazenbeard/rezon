from __future__ import annotations

import base64
from collections.abc import Mapping, Sequence
from typing import Any


def _otlp_value(value: object) -> dict[str, object]:
    if type(value) is str:
        return {"stringValue": value}
    if type(value) is bool:
        return {"boolValue": value}
    if type(value) is int:
        return {"intValue": str(value)}
    if type(value) is float:
        return {"doubleValue": value}
    if type(value) is bytes:
        return {"bytesValue": base64.b64encode(value).decode("ascii")}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return {"arrayValue": {"values": [_otlp_value(item) for item in value]}}
    if isinstance(value, Mapping):
        return {
            "kvlistValue": {
                "values": [
                    {"key": str(key), "value": _otlp_value(item)}
                    for key, item in value.items()
                ]
            }
        }
    raise TypeError(f"unsupported OpenTelemetry attribute value: {type(value).__name__}")


def _hex(value: int, width: int) -> str:
    return f"{value:0{width}x}"


def _status_code(span: Any) -> str:
    status = getattr(span, "status", None)
    code = getattr(status, "status_code", None)
    name = getattr(code, "name", None)
    if name == "OK":
        return "STATUS_CODE_OK"
    if name == "ERROR":
        return "STATUS_CODE_ERROR"
    return "STATUS_CODE_UNSET"


def readable_spans_to_otlp_json(spans: Sequence[Any]) -> dict[str, object]:
    """Serialize actual ReadableSpan fields into a qualification OTLP/JSON projection.

    This helper does not add or rewrite semantic attributes.
    """

    scope_spans: list[dict[str, object]] = []
    for span in spans:
        context = span.context
        parent = span.parent
        attributes = [
            {"key": key, "value": _otlp_value(value)}
            for key, value in (span.attributes or {}).items()
        ]
        projected: dict[str, object] = {
            "traceId": _hex(context.trace_id, 32),
            "spanId": _hex(context.span_id, 16),
            "name": span.name,
            "status": {"code": _status_code(span)},
            "attributes": attributes,
            "droppedAttributesCount": int(getattr(span, "dropped_attributes", 0) or 0),
        }
        if parent is not None and getattr(parent, "span_id", 0):
            projected["parentSpanId"] = _hex(parent.span_id, 16)

        scope = getattr(span, "instrumentation_scope", None)
        schema_url = getattr(scope, "schema_url", None)
        scope_entry: dict[str, object] = {"spans": [projected]}
        if schema_url:
            scope_entry["schemaUrl"] = schema_url
        scope_spans.append(scope_entry)

    return {"resourceSpans": [{"scopeSpans": scope_spans}]}


def genai_attribute_keys(spans: Sequence[Any]) -> tuple[str, ...]:
    keys: list[str] = []
    for span in spans:
        for key in (span.attributes or {}):
            if key.startswith("gen_ai.") and key not in keys:
                keys.append(key)
    return tuple(keys)
