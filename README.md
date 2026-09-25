> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

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

`work/rezon-kernel-v0-r5-independence` contains the current provider-independent Kernel V0 R5 candidate. Executable payload `d32cca38606e767813d9e0797681d1ab00e0b0b8`, tree `fbe4a4eca7251144306b4ba301fd7f3c9d9d9f8f`, passed the hosted Python 3.12 qualification surface with **91/91 tests passing** after a test-first repair of Mune's exact-head R4 pairwise-independence blocker.

R5 preserves all R4 controls and additionally rejects strong pairwise-independence claims when workers share any executor, model, provider, prompt lineage, context lineage, or declared common evidence. Exact RED head `289e89b8a2be526349aba893c09fa301f41011d4` reproduced **3 failed / 88 passed** before the repair, matching the three R4 correlation bypasses identified by Mune. See `docs/qualification/KERNEL_V0_ACCEPTANCE.md`.

Masa's R1/R2 `CHANGES_REQUESTED` dispositions and Mune's R2/R3/R4 `CHANGES_REQUESTED` dispositions remain preserved as historical exact-subject evidence. R5 repairs the currently known executable/source blockers but does **not** self-award independent R5 qualification. Fresh exact-head Mune and Masa rereview is required before R5 is promoted into the P0 integration subject or predecessor PRs are advanced.

This remains source/build/test candidate evidence only. It does not establish reasoning superiority, live-provider/tool correctness, deployment, installation, activation, or downstream behavioral qualification.