# Rezon

Rezon is a provider-independent epistemic reasoning kernel and assurance layer.

Its purpose is not to replace general agent runtimes. Agent SDKs and workflow
frameworks already handle model loops, tools, handoffs, sessions, persistence,
and orchestration well. Rezon focuses on the harder boundary they do not make
true merely by executing successfully: what evidence was actually available,
which sources and versions were consumed, whether supposedly independent
reasoners were actually independent, which failures occurred, and whether a
reasoning result is being mistaken for authority or an external effect.

## Core model

Rezon separates:

1. reasoning methods — deduction, induction, abduction, causality,
   counterfactuals, planning, analogy, probabilistic inference, falsification;
2. reasoning topology — heterogeneous workers, opposition, verification,
   retrieval, scheduling, and integration;
3. epistemic state — propositions, relations, provenance, currentness,
   disagreement, source versions, and persistent subject identity;
4. execution evidence — task envelopes, execution traces, output digests,
   producer identities, failures, receipts, and effect ceilings.

A capable model is never automatically an authority source. Agreement among
multiple workers is never automatically independent confirmation.

## Current source state

The default branch is still the one-commit bootstrap. Draft PR #80,
'estate/rezon-canonical-baseline-v1-20260920', is the current repository
canonicalization candidate at exact head
'90140fa109bdfe5bd5aba24dec4afab799b25848'.

That candidate composes the R51 kernel lineage, accepted Benchmark R4, and the
reviewed canonical Episode-method binding. Its recorded exact-subject evidence
is 337/337 tests passing on Python 3.12, plus benchmark replay, install,
compileall, and diff-check passes. Those are source/build/test claims only; PR
#80 is not merged and does not establish deployment, installation, live-provider
behavior, semantic truth, or reasoning superiority.

The active improvement stack builds from that exact candidate rather than from
the obsolete default branch.

## Portable run assurance

Rezon can export a deterministic 'rezon.run-evidence.v1' artifact. The portable
verifier checks that artifact without rerunning the reasoning job:

    rezon verify-evidence run-evidence.json

Verification covers canonical body integrity, receipt-to-trace execution
coverage, ordered source-version binding, failure visibility, output-digest
binding, canonical producer identity recomputation, task-envelope consistency,
and the non-promotional PLAN ceiling.

A successful verification establishes structural consistency of that artifact.
It does not prove that the underlying claims are true or that an external action
was authorized or completed.

## External consultation intake

Rezon can inspect a multi-model consultation report without promoting reported
agreement into independent evidence:

    rezon inspect-consultation consultation.json

The intake preserves reported synthesis, convergence/confidence signals,
provider/model identities, failures, costs, latency, and optional raw-output
bindings. It explicitly leaves the original prompt/configuration, worker
independence, semantic truth, evidence status, and authority unestablished when
the artifact does not bind them.

The first adversarial reference specimen is
`anywave/lattice-consult-mcp@675faae4d8ebd32071b656a2344fbd54843c8295`.
Its heuristic synthesis is treated as reported advisory output rather than a
truth or authority signal.

See `docs/ENSEMBLE_CONSULTATION_INTAKE.md`.

## External telemetry intake

Rezon has a dependency-free structural intake for generic OpenTelemetry
OTLP/JSON traces:

    rezon inspect-otel trace.json

That layer preserves typed attributes, resource/instrumentation-scope identity,
trace hierarchy, events, links, schema visibility, dropped-attribute gaps, and
a canonical full-payload binding. It deliberately classifies semantic meaning,
provenance/currentness, independence, authority, and external effect completion
as unestablished.

GenAI inspection is a semantic projection over that structural layer rather
than a second parser:

    rezon inspect-otel-genai trace.json

A GenAI workflow span can bind itself to a Rezon evidence artifact with
application-specific Rezon digest/schema attributes:

    rezon bind-otel-evidence trace.json run-evidence.json

The binding requires one GenAI trace per operation, verifies structural
consistency and exact payload-to-artifact agreement, and preserves unresolved
telemetry gaps. It does not authenticate
the producer, establish semantic truth, grant authority, or prove external
effect completion.

See 'docs/PORTABLE_ASSURANCE_LAYER.md'.

## Architecture flow

    TaskEnvelope
      -> governed scheduling
      -> heterogeneous reasoning nodes
      -> opposition / falsification
      -> retrieval + provenance controls
      -> canonical Episode admission
      -> ResultReceipt + ExecutionTrace
      -> deterministic run-evidence artifact
      -> independent verification
      -> optional external telemetry cross-binding

## Key documents

- 'docs/FOUNDATION.md' — principles and scope
- 'docs/REASONING_TAXONOMY.md' — reasoning families
- 'docs/MULTIVIEW_HYPERGRAPH_STATE.md' — multi-view state representation
- 'docs/HIERARCHICAL_DISTRIBUTED_REASONING.md' — worker topology
- 'docs/ADVERSARIAL_COLLABORATION.md' — hostile review method
- 'docs/RETRIEVAL_CONTEXT.md' — retrieval and context selection
- 'docs/SEMANTIC_PROVENANCE.md' — provenance and semantic repair
- 'docs/EVALUATION_AND_FALSIFICATION.md' — falsification discipline
- 'docs/architecture/PROJECT_RUNNER_OUTER_ORCHESTRATION_BOUNDARY.md' — runtime boundary
- 'docs/PORTABLE_ASSURANCE_LAYER.md' — current integration direction
- 'architecture/REPOSITORY_RECONCILIATION_V1.json' — exact estate reconciliation

## Near-term direction

The external boundary has now been exercised against two independent runtime
subjects. OpenAI Agents SDK telemetry produced consumable GenAI operations.
Microsoft Agent Framework's credential-free workflow path produced native
OpenTelemetry workflow spans but no gen_ai.* operation semantics; those spans
are now consumable through the generic structural intake without being
misclassified as GenAI evidence.

The next useful work is adversarial cross-runtime measurement: determine whether
Rezon catches stale, correlated, incomplete, substituted, or unauthorized
evidence that simpler trace-only acceptance misses.

No merge or protected runtime effect is implied by this repository state.
