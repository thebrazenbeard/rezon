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


## Evidence log

### E1 — OpenAI runtime capture

Status: CONFIRMATORY PASS
Run: GitHub Actions 35746266230 / job 106808579975
Subject: openai-agents 0.22.3 + opentelemetry-instrumentation-openai-agents 0.62.3

Observed:
- qualification dependencies installed successfully;
- native OpenAI Agents trace/agent/function span APIs executed without model or
  cloud credentials;
- in-memory OpenTelemetry exporter captured 3 spans;
- emitted GenAI keys included gen_ai.operation.name, gen_ai.agent.name,
  gen_ai.tool.name, gen_ai.tool.type, and gen_ai.provider.name;
- Rezon observed execute_tool and invoke_agent;
- Rezon preserved authority/effect/currentness/independence gaps.

Disposition: H1 confirmed for this exact package pair and credential-free probe.
This does not qualify model-call telemetry or all OpenAI Agents span families.

### E2 — Microsoft first attempt

Status: HARNESS DEAD END / NOT A RUNTIME VERDICT
Run: GitHub Actions 35746266230 / job 106808583722
Subject: agent-framework 1.19.0

Observed:
- package installation succeeded;
- qualification did not execute because importing use_agent_instrumentation from
  package root raised ImportError.

Cause:
The live installed package does not re-export use_agent_instrumentation from
agent_framework.__init__. The current API reference documents the function in
agent_framework.observability while an embedded example still shows a package-
root import.

Pivot P1:
Change only the harness import to agent_framework.observability. Do not change
the hypothesis, expected telemetry, or Rezon acceptance rules.


### E3 — Microsoft second attempt

Status: HARNESS DEAD END / NOT A RUNTIME VERDICT
Run: GitHub Actions 35746495139 / job 106809368121
Subject: agent-framework 1.19.0

Observed:
- package installation again succeeded;
- importing use_agent_instrumentation from agent_framework.observability also
  raised ImportError.

Interpretation:
The installed 1.19.0 subject does not expose the decorator through either import
path shown by the current API documentation examined during this qualification.

Pivot P2:
Remain inside frozen Q2 by using the credential-free workflow observability path
that is present in the current Agent Framework documentation and package:
Executor + WorkflowBuilder + configure_otel_providers. Capture the actual spans
from that workflow. Do not add GenAI attributes. If workflow telemetry contains
no Rezon-consumable gen_ai.operation.name, H2 is falsified for this path.


### E4 — Microsoft documented workflow path

Status: CONFIRMATORY FAIL FOR Q2 DEFAULT CONFIGURATION
Run: GitHub Actions 35746765241 / job 106810294300
Subject: agent-framework 1.19.0

Observed:
- package installation succeeded;
- documented credential-free Executor + WorkflowBuilder path executed correctly;
- workflow output was NOZER OLLEH;
- in-memory OpenTelemetry exporter captured zero spans.

Disposition:
H2 is falsified for the exact Q2 configuration as executed. This is not yet
evidence that Rezon rejects Microsoft telemetry because no telemetry reached the
adapter.

Exploratory diagnostic D1:
Prove the in-memory exporter/provider path with a direct Agent Framework tracer
control span in the same process. If the control span exports, rerun the workflow
and compare. If the framework path still emits no spans, explicitly call the
documented enable_instrumentation() and run once more as an exploratory probe.
Do not promote that exploratory result into the original H2 confirmatory pass.


### E5 — Microsoft diagnostic control failure

Status: HARNESS DEAD END / NOT A RUNTIME VERDICT
Run: GitHub Actions 35747016355 / job 106811137568
Subject: agent-framework 1.19.0

Observed:
- configure_otel_providers(exporters=[InMemorySpanExporter]) completed;
- a control span opened through agent_framework.observability.get_tracer()
  exported zero spans.

Interpretation:
Current documentation says configure_otel_providers creates/configures providers
and custom exporters. Therefore this result does not justify blaming Rezon or
Agent Framework workflow instrumentation. The diagnostic control itself may be
using a tracer obtained through framework helper state that was initialized
before provider configuration.

Pivot P3:
After configure_otel_providers(), create the control tracer through the standard
opentelemetry.trace.get_tracer API. This directly tests the installed global
provider/exporter pipeline. Only if that control exports may the workflow-span
result be interpreted.


### E6 — Microsoft batch-export diagnosis

Status: HARNESS DEFECT CONFIRMED / NOT A RUNTIME VERDICT
Subject: agent-framework 1.19.0 observability provider wiring

Source inspection established that configure_otel_providers() installs a
TracerProvider and attaches custom SpanExporter instances through
BatchSpanProcessor. The prior diagnostics read InMemorySpanExporter immediately
after span completion without forcing the provider to flush.

Root cause:
The qualification harness treated an asynchronous batch exporter as if it were
a synchronous simple exporter.

Pivot P4:
Call the installed tracer provider's force_flush() before every exporter
readback. No qualification hypothesis or Rezon acceptance rule changes.


### E7 — Microsoft string-enum attribute key boundary

Status: QUALIFICATION PROJECTION DEFECT / NOT A RUNTIME VERDICT
Run: GitHub Actions 35748467846 / job 106816056155
Subject: agent-framework 1.19.0

Observed:
- the batch-export flush defect was repaired;
- the control span exported, so provider/exporter wiring was proven live;
- workflow telemetry reached the Rezon qualification projection;
- Rezon rejected projected attribute key type OtelAttr because the projection
  preserved the Python str-Enum object instead of emitting its JSON string value.

Source inspection:
agent_framework.observability.OtelAttr subclasses str and Enum and defines
__str__ to return the canonical attribute value (for example workflow.id).

Pivot P5:
The qualification projection will accept only isinstance(key, str) keys and
serialize str(key). Non-string keys still fail. Rezon's OTLP/JSON parser remains
strict and unchanged.


### E8 — Final V1 real-runtime result

Status: QUALIFICATION COMPLETE
Run: GitHub Actions 35748734429
Head: 2dd9ebfa46df69b5a6a719400b34e84adc6d4f63 plus the
batch-flush and string-enum projection repairs exercised in the run lineage.

H1 — OpenAI Agents SDK: CONFIRMED.
The pinned OpenAI Agents 0.22.3 lane repeatedly emitted real OpenTelemetry GenAI
spans consumable by Rezon without model credentials. Observed operations included
execute_tool and invoke_agent. Rezon retained its authority/effect/currentness/
independence gaps.

H2 — Microsoft Agent Framework workflow: FALSIFIED FOR THE TESTED PATH.
The exporter control succeeded and the credential-free workflow completed with
output NOZER OLLEH. Seven native Agent Framework spans were captured:

- workflow.build
- edge_group.process InternalEdgeGroup
- message.send
- executor.process upper
- edge_group.process SingleEdgeGroup
- executor.process reverse
- workflow.run

None of those seven spans carried gen_ai.* attributes, and therefore the current
generic Rezon GenAI intake observed zero events. Calling enable_instrumentation()
explicitly produced the same seven spans and the same zero GenAI attributes.

This is a compatibility gap, not evidence that either runtime failed to emit
telemetry. Microsoft Agent Framework emitted native workflow telemetry that the
generic GenAI adapter intentionally did not reinterpret.

Corroboration:
Microsoft issue #6626 reports that native workflow spans use workflow.*,
executor.*, and message attributes without gen_ai.operation.name=invoke_workflow.

H3 — No trust promotion: CONFIRMED on the OpenAI consumable path. The Microsoft
path never reached a Rezon GenAI event and therefore cannot be counted as a
second H3 runtime confirmation.

## V1 conclusion

The claim "provider-neutral OTLP/JSON GenAI intake works unchanged across both
tested runtimes" is REJECTED.

A narrower claim survives:
Rezon consumes standards-shaped GenAI telemetry from the tested OpenAI Agents
instrumentation, while Microsoft Agent Framework 1.19.0 native workflow telemetry
requires an explicit framework-native compatibility adapter if Rezon is to
preserve those workflow/executor/message observations without fabricating GenAI
semantic attributes.

Next production frontier:
Implement a Microsoft Agent Framework native-workflow adapter with an explicit
source-semantics label. It must not synthesize gen_ai.operation.name or imply
OpenTelemetry GenAI conformance that the source runtime did not emit.


### E9 — Qualification-monitor pipeline-status defect

Status: MONITOR HARNESS DEFECT / QUALIFICATION RESULT REPRODUCED
Run: GitHub Actions 35749057711 / job 106818076971

Observed:
- Microsoft qualification reproduced the exact recorded FAIL:
  exporter control = 1, native workflow spans = 7, GenAI keys = none,
  Rezon GenAI events = none;
- the observation step used a shell pipeline to tee JSON output;
- without pipefail, the successful tee process masked the Python probe's non-zero
  exit and GitHub exposed the step outcome as success;
- the following assertion correctly rejected that inconsistent monitor state.

Pivot P6:
Enable shell pipefail for the observation pipeline. No runtime result, adapter
behavior, or compatibility claim changes.


### E5 — Microsoft zero-span diagnostic correction

Status: HARNESS DEFECT IDENTIFIED / E4 ZERO-SPAN INTERPRETATION SUPERSEDED
Evidence: exact Agent Framework observability source inspected after E4.

Finding:
configure_otel_providers() constructs an OpenTelemetry TracerProvider and attaches
BatchSpanProcessor instances to custom span exporters. The qualification probe
read InMemorySpanExporter immediately after span end without forcing the provider
to flush. Therefore E4's zero-span observation cannot be treated as a framework
non-emission result.

Correction P3:
Force-flush the configured tracer provider before every exporter read. Preserve
the same credential-free workflow and the same no-semantic-synthesis acceptance
criterion. E4 remains durable as a harness failure record but is not evidence
against H2.


### E6 — Microsoft monitor pipeline defect

Status: MONITOR HARNESS DEFECT / QUALIFICATION RESULT UNAFFECTED
Run: GitHub Actions 35770468175 / job 106890581894

Observed qualification result after batch flush:
- exporter/provider control span: 1;
- native Agent Framework workflow spans: 7;
- span names included workflow.build, executor.process, message.send,
  edge_group.process, and workflow.run;
- default gen_ai attribute keys: none;
- default Rezon event operations: none;
- explicit enable_instrumentation exploratory probe produced the same 7 native
  spans and still no GenAI semantics;
- qualification reason:
  default_path_emitted_no_rezon_consumable_genai_events.

Monitor defect:
The observation shell piped the deliberately nonzero qualification probe through
tee without pipefail, causing the GitHub step outcome to be reported as success.
The subsequent monitor correctly rejected that inconsistent step outcome even
though the JSON result reproduced the expected Microsoft FAIL.

Correction P4:
Enable shell pipefail for the observation pipeline. Do not change the
qualification expectation or Microsoft compatibility verdict.


## Engineering repair gate — generic OTLP intake

Classification: POST-RESULT ENGINEERING QUALIFICATION, not a new confirmatory
test of H2.

The Microsoft Agent Framework result showed a real provider-neutral boundary:
the framework emitted native OpenTelemetry workflow spans but no GenAI semantic
attributes on the credential-free workflow path. Rezon must not synthesize
gen_ai.* fields merely to make that path pass.

Repair criterion:
- feed the exact captured Agent Framework spans into the generic Rezon OTLP
  structural intake;
- require every captured runtime span to survive normalization;
- preserve trace hierarchy and emitted native attributes;
- keep semantic meaning, provenance/currentness, independence, authority, and
  external effect completion unestablished;
- simultaneously preserve the original GenAI qualification FAIL when no
  gen_ai.operation.name exists.

A PASS here means Rezon can observe the runtime structurally without falsely
classifying its telemetry as GenAI evidence. It does not retroactively turn H2
into a PASS.
