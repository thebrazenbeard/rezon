import importlib.util
import json
from enum import Enum
from pathlib import Path
from types import SimpleNamespace


def _load_projection():
    path = Path(__file__).parents[1] / "scripts" / "runtime_otel_support.py"
    spec = importlib.util.spec_from_file_location("runtime_otel_support", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.readable_spans_to_otlp_json


readable_spans_to_otlp_json = _load_projection()


class SpanName(str, Enum):
    WORKFLOW_RUN = "workflow.run"


def test_runtime_projection_emits_plain_otlp_json_primitives():
    context = SimpleNamespace(
        trace_id=int("12" * 16, 16),
        span_id=int("34" * 8, 16),
        trace_flags=1,
        trace_state=SimpleNamespace(to_header=lambda: "vendor=value"),
    )
    status = SimpleNamespace(
        status_code=SimpleNamespace(name="OK"),
    )
    scope = SimpleNamespace(schema_url=None)
    span = SimpleNamespace(
        context=context,
        parent=None,
        name=SpanName.WORKFLOW_RUN,
        status=status,
        attributes={"workflow.id": "wf-1"},
        dropped_attributes=0,
        instrumentation_scope=scope,
    )

    payload = readable_spans_to_otlp_json([span])
    projected = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]

    assert type(projected["name"]) is str
    assert projected["name"] == "workflow.run"
    assert projected["status"]["code"] == 1
    assert type(projected["status"]["code"]) is int
    assert projected["traceState"] == "vendor=value"
    assert projected["flags"] == 1

    json.dumps(payload)



def test_runtime_projection_preserves_readable_span_structure():
    parent_context = SimpleNamespace(
        trace_id=int("56" * 16, 16),
        span_id=int("78" * 8, 16),
        trace_flags=1,
        trace_state=SimpleNamespace(to_header=lambda: "parent=v"),
    )
    context = SimpleNamespace(
        trace_id=int("12" * 16, 16),
        span_id=int("34" * 8, 16),
        trace_flags=1,
        trace_state=SimpleNamespace(to_header=lambda: "vendor=value"),
    )
    link_context = SimpleNamespace(
        trace_id=int("9a" * 16, 16),
        span_id=int("bc" * 8, 16),
        trace_flags=1,
        trace_state=SimpleNamespace(to_header=lambda: "link=v"),
    )
    event_attributes = {"event.count": 2}
    event = SimpleNamespace(
        name="workflow.started",
        timestamp=150,
        attributes=event_attributes,
        dropped_attributes=1,
    )
    link_attributes = {"link.role": "dependency"}
    link = SimpleNamespace(
        context=link_context,
        attributes=link_attributes,
        dropped_attributes=2,
    )
    resource = SimpleNamespace(
        attributes={"service.name": "runtime-probe"},
        schema_url="https://example.test/resource-schema",
    )
    scope_attributes = {"scope.role": "qualification"}
    scope = SimpleNamespace(
        name="runtime.instrumentation",
        version="1.2.3",
        schema_url="https://example.test/span-schema",
        attributes=scope_attributes,
    )
    status = SimpleNamespace(
        status_code=SimpleNamespace(name="OK"),
        description="completed",
    )
    span = SimpleNamespace(
        context=context,
        parent=parent_context,
        name=SpanName.WORKFLOW_RUN,
        kind=SimpleNamespace(value=1),
        status=status,
        attributes={"workflow.id": "wf-1"},
        dropped_attributes=3,
        dropped_events=4,
        dropped_links=5,
        start_time=100,
        end_time=200,
        events=[event],
        links=[link],
        resource=resource,
        instrumentation_scope=scope,
    )

    payload = readable_spans_to_otlp_json([span])
    resource_spans = payload["resourceSpans"][0]
    scope_spans = resource_spans["scopeSpans"][0]
    projected = scope_spans["spans"][0]

    assert resource_spans["schemaUrl"] == "https://example.test/resource-schema"
    assert resource_spans["resource"]["attributes"] == [
        {
            "key": "service.name",
            "value": {"stringValue": "runtime-probe"},
        }
    ]
    assert scope_spans["schemaUrl"] == "https://example.test/span-schema"
    assert scope_spans["scope"] == {
        "name": "runtime.instrumentation",
        "version": "1.2.3",
        "attributes": [
            {
                "key": "scope.role",
                "value": {"stringValue": "qualification"},
            }
        ],
        "droppedAttributesCount": 0,
    }

    assert projected["kind"] == 1
    assert projected["startTimeUnixNano"] == "100"
    assert projected["endTimeUnixNano"] == "200"
    assert projected["droppedAttributesCount"] == 3
    assert projected["droppedEventsCount"] == 4
    assert projected["droppedLinksCount"] == 5
    assert projected["status"] == {"code": 1, "message": "completed"}
    assert projected["events"] == [
        {
            "timeUnixNano": "150",
            "name": "workflow.started",
            "attributes": [
                {
                    "key": "event.count",
                    "value": {"intValue": "2"},
                }
            ],
            "droppedAttributesCount": 1,
        }
    ]
    assert projected["links"] == [
        {
            "traceId": "9a" * 16,
            "spanId": "bc" * 8,
            "traceState": "link=v",
            "attributes": [
                {
                    "key": "link.role",
                    "value": {"stringValue": "dependency"},
                }
            ],
            "droppedAttributesCount": 2,
            "flags": 1,
        }
    ]

    json.dumps(payload)
