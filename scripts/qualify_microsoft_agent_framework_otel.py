from __future__ import annotations

import asyncio
import json
from importlib.metadata import version

from agent_framework.observability import (
    configure_otel_providers,
    use_agent_instrumentation,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from rezon.otel_genai import inspect_otel_genai_export
from runtime_otel_support import genai_attribute_keys, readable_spans_to_otlp_json


@use_agent_instrumentation
class LocalQualificationAgent:
    AGENT_PROVIDER_NAME = "rezon_qualification"

    def __init__(self) -> None:
        self.id = "rezon-ms-agent"
        self.name = "rezon-ms-agent"
        self.description = "Credential-free telemetry qualification agent"

    async def run(self, messages=None, *, thread=None, **kwargs):
        return "local-result"

    async def run_stream(self, messages=None, *, thread=None, **kwargs):
        if False:
            yield None


async def _run() -> None:
    agent = LocalQualificationAgent()
    await agent.run("credential-free qualification")


def main() -> int:
    exporter = InMemorySpanExporter()
    configure_otel_providers(exporters=[exporter])

    asyncio.run(_run())

    spans = exporter.get_finished_spans()
    projected = readable_spans_to_otlp_json(spans)
    report = inspect_otel_genai_export(projected)

    if not spans:
        raise RuntimeError("Agent Framework qualification emitted no OpenTelemetry spans")
    if not report["events"]:
        raise RuntimeError(
            "Agent Framework telemetry contained no Rezon-consumable GenAI events"
        )
    if report["assurance"]["authority"] != "unestablished":
        raise RuntimeError("telemetry improperly promoted authority")
    if report["assurance"]["effect_completion"] != "unestablished":
        raise RuntimeError("telemetry improperly promoted effect completion")

    print(
        json.dumps(
            {
                "runtime": "agent-framework",
                "runtime_version": version("agent-framework"),
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
