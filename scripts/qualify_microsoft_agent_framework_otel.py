from __future__ import annotations

import asyncio
import json
from importlib.metadata import version

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler
from agent_framework.observability import configure_otel_providers
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from typing_extensions import Never

from rezon.otel_genai import inspect_otel_genai_export
from runtime_otel_support import genai_attribute_keys, readable_spans_to_otlp_json


class UpperCaseExecutor(Executor):
    @handler
    async def to_upper_case(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())


class ReverseTextExecutor(Executor):
    @handler
    async def reverse_text(
        self,
        text: str,
        ctx: WorkflowContext[Never, str],
    ) -> None:
        await ctx.yield_output(text[::-1])


async def _run() -> str:
    upper = UpperCaseExecutor(id="upper")
    reverse = ReverseTextExecutor(id="reverse")
    workflow = (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, reverse)
        .build()
    )
    output = None
    async for event in workflow.run("hello rezon", stream=True):
        if event.type == "output":
            output = event.data
    if output is None:
        raise RuntimeError("Agent Framework workflow produced no output")
    return str(output)


def main() -> int:
    exporter = InMemorySpanExporter()
    configure_otel_providers(exporters=[exporter])

    output = asyncio.run(_run())
    spans = exporter.get_finished_spans()
    projected = readable_spans_to_otlp_json(spans)
    report = inspect_otel_genai_export(projected)

    summary = {
        "runtime": "agent-framework",
        "runtime_version": version("agent-framework"),
        "workflow_output": output,
        "captured_span_count": len(spans),
        "captured_span_names": [span.name for span in spans],
        "genai_attribute_keys": list(genai_attribute_keys(spans)),
        "rezon_event_operations": [
            event["operation"] for event in report["events"]
        ],
        "rezon_assurance_gaps": report["assurance_gaps"],
    }

    if not spans:
        summary["qualification"] = "FAIL"
        summary["reason"] = "no_opentelemetry_spans"
        print(json.dumps(summary, sort_keys=True))
        raise RuntimeError("Agent Framework qualification emitted no OpenTelemetry spans")
    if not report["events"]:
        summary["qualification"] = "FAIL"
        summary["reason"] = "no_rezon_consumable_genai_events"
        print(json.dumps(summary, sort_keys=True))
        raise RuntimeError(
            "Agent Framework telemetry contained no Rezon-consumable GenAI events"
        )
    if report["assurance"]["authority"] != "unestablished":
        raise RuntimeError("telemetry improperly promoted authority")
    if report["assurance"]["effect_completion"] != "unestablished":
        raise RuntimeError("telemetry improperly promoted effect completion")

    summary["qualification"] = "PASS"
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
