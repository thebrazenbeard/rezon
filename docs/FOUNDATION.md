# Foundation

## Purpose

Rezon exists to make reasoning composable, inspectable, falsifiable, and provider-independent. The central premise is that “reasoning” is not one monolithic operation. Different problems benefit from different inference modes, representations, search strategies, critics, retrieval methods, and verification surfaces.

Rezon should therefore treat a reasoning run as a structured process with typed inputs, typed intermediate claims, explicit provenance, independent challenge, and a receipt describing what was actually established.

## Foundational separations

### Claim vs evidence
A claim is not promoted because it is repeated, confidently stated, emitted by a stronger model, or stored in a trusted repository. Evidence has source, scope, time, subject, and an admissibility rule.

### Subject vs observation
An observation of a subject is not the subject itself. This matters for persistent identity, long-running projects, distributed agents, and any state reconstructed across discontinuous runtimes.

### Reasoning method vs authority
Deduction, retrieval, graph reasoning, model confidence, or an “Ultra” worker can improve epistemic quality without granting operational or governance authority.

### Reasoning quality vs runtime effect
A correct plan is not deployment. A source candidate is not an installed runtime. A behavioral test is not provider activation. Rezon receipts should preserve these distinctions.

### Representation vs reality
Embeddings, latent states, graphs, hypergraphs, ontologies, and summaries are representations. They can help detect structure and drift but must not silently become the thing represented.

## Design principles

1. **Literal proposition first.** Before improving a proposal, identify and test the proposition actually made.
2. **Falsification before promotion.** Important conclusions should survive an opposition lane designed to find counterexamples, scope errors, and stronger alternative explanations.
3. **Heterogeneous nodes.** Different reasoning nodes may use different models, algorithms, symbolic engines, retrieval systems, simulations, or deterministic code.
4. **Provider independence.** The core graph should run with deterministic/mock workers; providers are adapters.
5. **Typed state.** Fact, hypothesis, preference, intent, authority, identity, desire, consent, runtime state, and effect evidence are not interchangeable.
6. **Provenance first-class.** Every material claim should be traceable to its sources and transformations.
7. **Ambiguity is a state.** Unknown, unresolved, conflicting, unavailable, attempted-unknown, and verified are distinct states.
8. **No hidden continuity assumption.** Longitudinal identity requires association evidence, not merely similarity or naming.
9. **Resource-aware orchestration.** Reasoning depth, latency, cost, and scarce workers are scheduling inputs.
10. **Small executable spine.** Rezon should resist framework inflation; mechanisms earn promotion by surviving tests and demonstrating a consumer.

## Candidate runtime spine

```text
TaskEnvelope
    |
    v
Semantic Parser / Proposition Typing
    |
    v
Decomposer / Planner
    |
    +--> Retrieval Node(s)
    +--> Deductive / Symbolic Node(s)
    +--> Probabilistic / Causal Node(s)
    +--> Analogical / Generative Node(s)
    +--> Simulation / Search Node(s)
    +--> Specialist Model Node(s)
    |
    v
Opposition / Hostile Review
    |
    v
Semantic + Provenance Reconciliation
    |
    v
Integrator
    |
    v
ResultReceipt
```

The topology is a proposal, not yet an executable implementation.
