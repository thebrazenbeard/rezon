# Rezon

Rezon is an executable multi-faceted reasoning project: a place to study, formalize, test, and eventually run heterogeneous reasoning as a coordinated system rather than treating one model invocation as the whole reasoning process.

The project deliberately separates four things that are often collapsed together:

1. **Reasoning methods** — deduction, induction, abduction, causality, counterfactuals, planning, analogy, probabilistic inference, semantic reasoning, adversarial challenge, and more.
2. **Reasoning topology** — how several reasoning processes cooperate, oppose, verify, retrieve, route, and integrate.
3. **State and identity** — what subject is being reasoned about, what changed, what persisted, and what evidence supports continuity.
4. **Execution** — provider/model adapters, worker routing, receipts, provenance, resource constraints, and runtime behavior.

Rezon is intended to become runnable from the beginning, but the first population is knowledge-first: the architecture is being made explicit before implementation hardens accidental assumptions into interfaces.

## Core direction

A working Rezon system should eventually support a flow like:

```text
TaskEnvelope
  -> Decomposer / Planner
  -> Heterogeneous Reasoning Nodes
  -> Opposition / Falsification Lane
  -> Retrieval + Semantic / Provenance Verification
  -> Integrator
  -> ResultReceipt
```

Cross-cutting state substrates:

```text
Persistent Subject / Identity Track
Multi-View State Graph / Hypergraph
Evidence + Provenance Ledger
```

A stronger model is never automatically an authority source. A reasoning node may be more capable, more expensive, or more specialized without being entitled to promote identity, consent, facts, deployment state, or governance claims.

## Documents

- `docs/FOUNDATION.md` — project principles and scope
- `docs/REASONING_TAXONOMY.md` — reasoning families worth modeling
- `docs/HUMAN_AI_REASONING_SYNTHESIS.md` — transferable human/AI reasoning mechanisms
- `docs/IDENTITY_TRACKING.md` — persistent identity under discontinuous observations
- `docs/MULTIVIEW_HYPERGRAPH_STATE.md` — many-to-many, multi-view state representation
- `docs/HIERARCHICAL_DISTRIBUTED_REASONING.md` — slow/fast and heterogeneous worker topology
- `docs/ADVERSARIAL_COLLABORATION.md` — literal-proposition hostile review method
- `docs/RETRIEVAL_CONTEXT.md` — reasoning-based retrieval and context selection
- `docs/SEMANTIC_PROVENANCE.md` — knowledge graphs, ontologies, provenance, repair
- `docs/WORKER_ROUTING_ULTRA.md` — optional high-reasoning worker routing
- `docs/EVALUATION_AND_FALSIFICATION.md` — how Rezon should try to prove itself wrong
- `docs/SOURCE_TRANSFER_MATRIX.md` — source-by-source transfer analysis
- `docs/EXECUTABLE_FRAMEWORK_DIRECTION.md` — runnable system direction
- `docs/VERA_ADOPTION_CANDIDATES.md` — mechanisms that may be promoted into Vera later

## Current status

`work/rezon-kernel-v0-r3-mune` contains the current R3 provider-independent Kernel V0 repair candidate. Executable payload `2cf746779a5f755d4e7fe57df1c811baeb2ef764` passed the hosted Python 3.12 qualification surface with **66/66 tests passing**, including Masa's R1 and R2 hostile artifacts, Mune-derived R3 regressions, and additional adversarial regressions. See `docs/qualification/KERNEL_V0_ACCEPTANCE.md`.

Masa's R1 and R2 `CHANGES_REQUESTED` dispositions and Mune's R2 `CHANGES_REQUESTED` disposition remain preserved as historical exact-subject evidence. R3 repairs those known executable/source blockers but does **not** self-award independent R3 qualification. Fresh exact-head Mune and Masa rereview is required before R3 is promoted into the P0 integration subject or PR #8 is advanced.

This remains source/build/test candidate evidence only. It does not establish reasoning superiority, live-provider/tool correctness, deployment, installation, activation, or downstream behavioral qualification.
