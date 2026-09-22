# Real-Runtime OTLP Qualification V1

Status: PRE-REGISTERED / RESULTS NOT YET KNOWN
Date: 2026-09-22
Base: feature/otel-genai-intake-v1-20260922@cb0e7b056aa6eda423bfab221e85e29e7f5157f1

## Question

Can the current Rezon OTLP/JSON GenAI intake consume telemetry actually emitted
by two independent agent runtimes without synthesizing missing GenAI semantic
attributes or using model/cloud credentials?

## Frozen hypotheses

H1 — OpenAI Agents SDK compatibility.

Prediction: OpenAI Agents SDK 0.22.3, observed through its OpenTelemetry
instrumentation, emits at least one span carrying a non-empty
gen_ai.operation.name when exercised through native trace/agent/tool span APIs.

Falsifier: the installed runtime/instrumentor cannot execute credential-free, or
the captured spans contain no gen_ai.operation.name consumable by Rezon.

H2 — Microsoft Agent Framework compatibility.

Prediction: Agent Framework 1.19.0, using its native instrumentation with an
in-memory OpenTelemetry exporter and a deterministic local agent/workflow path,
emits at least one span carrying a non-empty gen_ai.operation.name consumable by
Rezon.

Falsifier: the installed runtime cannot execute credential-free, instrumentation
cannot be captured locally, or the captured spans contain no consumable
gen_ai.operation.name.

H3 — No trust promotion.

Prediction: for both runtimes, successful Rezon intake continues to report
authority and effect completion as unestablished.

Falsifier: either runtime's telemetry causes Rezon to promote authority or effect
completion merely because telemetry reports successful execution.

## Methods

Q1 OPENAI_RUNTIME_CAPTURE — confirmatory.
Install pinned OpenAI Agents SDK 0.22.3, OpenTelemetry SDK, and the current
OpenAI-Agents OTel instrumentation used by the qualification job. Disable the
SDK's default remote trace exporter, attach an in-memory OTel exporter, create a
native SDK trace with agent/tool spans, then serialize captured ReadableSpan
objects into a qualification OTLP/JSON projection without adding semantic
attributes.

Q2 MICROSOFT_RUNTIME_CAPTURE — confirmatory.
Install pinned Agent Framework 1.19.0 and OpenTelemetry SDK. Attach an in-memory
exporter through framework-supported observability configuration, execute a
credential-free deterministic instrumented path, then serialize captured
ReadableSpan objects into the same qualification projection without adding
semantic attributes.

Q3 REZON_INGEST — confirmatory for each Q1/Q2 result.
Feed the qualification projection into inspect_otel_genai_export. Require at
least one observed GenAI event and require authority/effect completion to remain
unestablished.

## Projection boundary

The qualification harness may serialize actual OpenTelemetry ReadableSpan
identity, parent identity, name, status, instrumentation-scope schema URL,
dropped-attribute count, and emitted attributes into OTLP/JSON shape.

It MUST NOT invent or rewrite gen_ai.* attributes to make Rezon accept a
runtime. Failure to emit usable GenAI semantics is a qualification failure.

The projection is not claimed to be byte-for-byte exporter output.

## Stopping rules

- PASS for a runtime requires its pinned package to install, the credential-free
  runtime exercise to complete, actual emitted spans to be captured, and Rezon
  intake to observe at least one GenAI event without semantic synthesis.
- FAIL is retained as evidence; do not normalize around it in the same run.
- If package/API drift prevents the documented route from executing, record the
  exact failure and stop that runtime lane.
- No cloud credentials, provider calls, deployment, or paid service are allowed.

## External version bindings

- OpenAI Agents SDK: 0.22.3 (PyPI release 2026-09-17).
- Microsoft Agent Framework: 1.19.0 (PyPI release 2026-09-18).
- OpenTelemetry OpenAI Agents instrumentation route is version-pinned in the CI
  workflow and remains qualification-only, not a Rezon runtime dependency.
