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
