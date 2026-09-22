# Portable Assurance Layer

## Position

Rezon should not compete with general agent orchestration frameworks for handoffs,
tool calling, sessions, workflow hosting, or provider-specific model loops.

Its strongest current asset is narrower: a provider-independent epistemic kernel
that can make reasoning runs inspectable and fail closed when provenance,
currentness, independence, failure reporting, or authority boundaries do not bind.

## Native run-evidence verification

A Rezon run can be exported as deterministic rezon.run-evidence.v1 JSON.
The portable verifier validates that artifact without rerunning the reasoning job.

    rezon verify-evidence run-evidence.json

Verification covers:

- canonical body digest integrity;
- exact receipt-to-trace execution coverage;
- source-version ordered binding;
- trace-failure visibility in the receipt;
- output-digest binding;
- canonical producer identity recomputation;
- task-envelope digest consistency;
- the non-promotional PLAN ceiling.

A valid artifact proves internal structural consistency of that Rezon evidence
artifact. It does not prove semantic truth, source authenticity outside the
recorded bindings, external authority, deployment state, or reasoning superiority.

## OpenTelemetry GenAI reference intake

The first dependency-free external intake accepts OTLP/JSON GenAI traces:

    rezon inspect-otel-genai trace.json

The intake:

- validates OTLP trace/span identities used by the adapter;
- rejects duplicate attribute keys instead of applying ambiguous last-value wins;
- preserves every non-empty gen_ai.operation.name, including custom operations,
  rather than silently dropping operations the adapter does not recognize;
- records effective per-event schema URLs using scope-over-resource precedence;
- reports unbound semantic-convention versions per observed GenAI event;
- reports dropped span attributes as an assurance gap;
- records workflow, agent, tool, provider, status, and hierarchy fields used by
  the current assurance boundary;
- emits a canonical digest of the complete parsed OTLP JSON payload plus a
  deterministic digest of the normalized assurance intake;
- does not promote successful telemetry into provenance, source currentness,
  worker independence, authority, or completed external effect.

The OpenTelemetry GenAI conventions remain a developing surface. The adapter
therefore preserves the emitted schema binding when available rather than
assuming the vocabulary is timeless.

Relevant upstream contracts:

- https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/
- https://opentelemetry.io/docs/specs/otel/schemas/
- https://opentelemetry.io/docs/specs/otel/common/
- https://opentelemetry.io/docs/specs/semconv/general/naming/

## Trace-to-evidence binding

An external workflow span may carry application-specific Rezon anchors:

- rezon.run_evidence.digest
- rezon.run_evidence.schema_version

OpenTelemetry recommends application-specific namespacing for attributes that
are not part of an existing semantic convention; these anchors deliberately use
the Rezon namespace rather than pretending to be OpenTelemetry-standard fields.

Bind a trace to an evidence artifact with:

    rezon bind-otel-evidence trace.json run-evidence.json

Binding requires exactly one GenAI trace and exactly one anchored
invoke_workflow span, independently verifies the Rezon evidence artifact, and
checks exact schema and digest agreement. The binding digest incorporates both
the canonical complete OTLP JSON payload digest and the normalized assurance
intake digest. Changes to payload content therefore change the binding even when
trace IDs and the Rezon evidence artifact remain unchanged. JSON formatting and
object-key order are normalized before hashing.

A successful binding has scope trace_to_verified_artifact. It explicitly carries
the unresolved telemetry assurance gaps and still does not prove:

- that the telemetry or artifact came from the actor they claim to represent;
- semantic truth of model or tool outputs;
- provenance/currentness not independently established by Rezon evidence;
- worker independence not independently established by Rezon evidence;
- authorization for an external action;
- durable completion of an external action.

The source-payload digest establishes content binding, not producer
authenticity. Mutual consistency is not authenticity.

## Integration direction

External runtimes should remain responsible for orchestration and execution.
Rezon should consume or cross-bind their evidence without becoming another
provider-specific workflow engine.

OTLP/JSON is the first reference intake because it provides a provider-neutral
trace substrate. Runtime-specific exporters or adapters should preserve their
native identity and effect receipts, then map into this boundary without
flattening them into generic text.

## Next executable frontier

1. Exercise the OTLP intake against real traces from at least two independent
   agent/workflow runtimes.
2. Add held-out adversarial fixtures where ordinary telemetry looks successful
   but evidence is stale, correlated, incomplete, substituted, or unauthorized.
3. Compare Rezon against trace-only acceptance baselines on detection accuracy,
   false blocks, runtime overhead, and evidence size.
4. Only then decide whether an MCP-facing hosted assurance service is justified.
