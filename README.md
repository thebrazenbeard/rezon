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

The active improvement branch builds from that exact candidate rather than from
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

The highest-value next work is interoperability, not another internal hardening
round for its own sake: define a strict external execution-event adapter
contract, implement one dependency-optional reference adapter, and benchmark
whether Rezon catches correlated consensus, stale evidence, concealed failures,
and authority laundering that simpler trace-only acceptance misses.

No merge or protected runtime effect is implied by this repository state.
