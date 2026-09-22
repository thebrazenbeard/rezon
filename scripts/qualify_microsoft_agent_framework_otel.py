from __future__ import annotations

import asyncio
import json
from importlib.metadata import version

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler
from agent_framework.observability import (
    configure_otel_providers,
    enable_instrumentation,
)
from opentelemetry import trace as otel_trace
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


def _analyze(spans):
    projected = readable_spans_to_otlp_json(spans)
    return inspect_otel_genai_export(projected)


def main() -> int:
    exporter = InMemorySpanExporter()
    configure_otel_providers(exporters=[exporter])

    control_tracer = otel_trace.get_tracer("rezon.qualification.control")
    with control_tracer.start_as_current_span(
        "rezon.qualification.exporter_control"
    ):
        pass
    tracer_provider = otel_trace.get_tracer_provider()
    if not tracer_provider.force_flush():
        raise RuntimeError("Agent Framework tracer provider force_flush failed")
    control_spans = exporter.get_finished_spans()
    if not control_spans:
        raise RuntimeError(
            "Agent Framework qualification exporter/provider control emitted no span"
        )

    before_default = len(control_spans)
    output = asyncio.run(_run())
    if not tracer_provider.force_flush():
        raise RuntimeError("Agent Framework default-path force_flush failed")
    after_default = exporter.get_finished_spans()
    default_runtime_spans = after_default[before_default:]
    default_report = _analyze(default_runtime_spans)

    summary = {
        "runtime": "agent-framework",
        "runtime_version": version("agent-framework"),
        "workflow_output": output,
        "exporter_control_span_count": before_default,
        "default_runtime_span_count": len(default_runtime_spans),
        "default_span_names": [span.name for span in default_runtime_spans],
        "default_genai_attribute_keys": list(
            genai_attribute_keys(default_runtime_spans)
        ),
        "default_rezon_event_operations": [
            event["operation"] for event in default_report["events"]
        ],
    }

    if default_report["events"]:
        summary["qualification"] = "PASS"
        summary["confirmatory"] = True
        print(json.dumps(summary, sort_keys=True))
        return 0

    # Exploratory only after the pre-registered default path failed.
    enable_instrumentation()
    before_explicit = len(exporter.get_finished_spans())
    exploratory_output = asyncio.run(_run())
    if not tracer_provider.force_flush():
        raise RuntimeError("Agent Framework exploratory force_flush failed")
    after_explicit = exporter.get_finished_spans()
    explicit_runtime_spans = after_explicit[before_explicit:]
    explicit_report = _analyze(explicit_runtime_spans)
    summary.update(
        {
            "qualification": "FAIL",
            "confirmatory": True,
            "reason": "default_path_emitted_no_rezon_consumable_genai_events",
            "explicit_enable_probe": {
                "classification": "EXPLORATORY",
                "workflow_output": exploratory_output,
                "runtime_span_count": len(explicit_runtime_spans),
                "span_names": [span.name for span in explicit_runtime_spans],
                "genai_attribute_keys": list(
                    genai_attribute_keys(explicit_runtime_spans)
                ),
                "rezon_event_operations": [
                    event["operation"] for event in explicit_report["events"]
                ],
            },
        }
    )
    print(json.dumps(summary, sort_keys=True))
    raise RuntimeError(
        "Agent Framework default qualification emitted no Rezon-consumable GenAI events"
    )


if __name__ == "__main__":
    raise SystemExit(main())
