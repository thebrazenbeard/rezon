from __future__ import annotations

import json
from importlib.metadata import version

from agents.tracing import agent_span, function_span, set_trace_processors, trace
from opentelemetry import trace as otel_trace
from opentelemetry.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from rezon.otel_genai import inspect_otel_genai_export
from runtime_otel_support import genai_attribute_keys, readable_spans_to_otlp_json


def main() -> int:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    otel_trace.set_tracer_provider(provider)

    # Replace the SDK's default remote processor before creating any trace.
    set_trace_processors([])
    OpenAIAgentsInstrumentor().instrument(tracer_provider=provider)

    with trace("rezon-runtime-qualification"):
        with agent_span("rezon-openai-qualifier", tools=["local_probe"]):
            with function_span(
                "local_probe",
                input='{"value":"fixture"}',
                output='{"status":"ok"}',
            ):
                pass

    provider.force_flush()
    spans = exporter.get_finished_spans()
    projected = readable_spans_to_otlp_json(spans)
    report = inspect_otel_genai_export(projected)

    if not spans:
        raise RuntimeError("OpenAI Agents qualification emitted no OpenTelemetry spans")
    if not report["events"]:
        raise RuntimeError(
            "OpenAI Agents telemetry contained no Rezon-consumable GenAI events"
        )
    if report["assurance"]["authority"] != "unestablished":
        raise RuntimeError("telemetry improperly promoted authority")
    if report["assurance"]["effect_completion"] != "unestablished":
        raise RuntimeError("telemetry improperly promoted effect completion")

    print(
        json.dumps(
            {
                "runtime": "openai-agents",
                "runtime_version": version("openai-agents"),
                "instrumentation_version": version(
                    "opentelemetry-instrumentation-openai-agents"
                ),
                "captured_span_count": len(spans),
                "genai_attribute_keys": list(genai_attribute_keys(spans)),
                "rezon_event_operations": [
                    event["operation"] for event in report["events"]
                ],
                "rezon_assurance_gaps": report["assurance_gaps"],
                "qualification": "PASS",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
