# Source Transfer Matrix

This document classifies external repositories by the computation or architecture Rezon can literally transfer from them. “Transfer” means mechanism, test idea, data model, or architectural pattern unless code reuse is explicitly appropriate and license-compatible.

| Source | Advertised domain | Transferable mechanism for Rezon | Directness | Cautions |
|---|---|---|---|---|
| `GeorgeVJose/DRISHTE-Public` | drone traffic detection/tracking | persistent identity as a track across transient observations; detection vs identity hypothesis; trajectory continuity under noise/occlusion | High conceptually | public repo redacts much implementation; do not invent its re-identification algorithm |
| `basiralab/HCAE` | multi-view brain-state classification | multi-view relational matrices -> hypergraphs -> fused many-to-many state representation -> compressed embedding | High | old TensorFlow stack; learned embedding must never become identity/authority oracle |
| `sapientinc/HRM` | hierarchical neural reasoning | slow abstract/high-level reasoning coordinating fast/detailed computation | High architectural | trained recurrent model is not an agent router; transfer principle, not literal architecture |
| `OpenSPG/KAG` | knowledge augmented generation | heterogeneous operators: planning, retrieval, graph reasoning, language reasoning, numerical calculation; logical-form guidance | High | heavyweight deployment; borrow interfaces and solver ideas first |
| `VectifyAI/PageIndex` | reasoning-based RAG | hierarchical tree indexing; reasoning-guided relevance retrieval; traceable context selection | High | retrieval claims/benchmarks need independent evaluation for our corpus |
| `semantica-agi/semantica` | context/knowledge graph + accountable AI | provenance, context graphs, decision objects, deterministic rules, conflicts, snapshots, ontology governance | High | do not replace Vera/Rezon governance wholesale without gap analysis |
| `ThHanke/ontosphere` | RDF/OWL editor + MCP | OWL reasoning, SHACL validation, reasoner-verified repairs, canonical graph hashing, edit provenance/reversal | High for verifier | distinguish consistency repair from correct-domain repair |
| `acrion/zelph` | executable semantic network/reasoning engine | graph-native rules, deep unification, derivation chains, graph rewriting | Medium/High research | AGPL/commercial license; experimental fit; avoid premature runtime dependency |
| `MiXaiLL76/n8n-nodes-sgr-tool-calling` | n8n research agent | bounded planning/adaptation loop, tool inventory, MCP integration, clarification state, iteration budgets | Medium/High | AGPL/commercial license; orchestration reference rather than direct import initially |
| `lucasdinnouti/custom-reverse-proxy` | ML-selected reverse proxy | dynamic backend selection based on observed/predicted resource metrics | Medium/High | toy/research implementation; extract routing pattern, not security posture |
| `hvala/Binomial-Heterogenicity` | population genetics simulation | Monte Carlo / generational simulation as an example of repeated stochastic model evaluation | Low/Medium | domain code itself is unrelated; do not force relevance |

## Detailed transfer notes

### DRISHT-E

The most important semantic transfer is:

```text
observation_t != identity
```

A tracker maintains a longitudinal hypothesis while detections are transient evidence. For Rezon, this supports subject tracks across discontinuous chats, runtimes, provider readbacks, or distributed workers. Hard provenance/admission evidence determines association eligibility; soft state similarity can help rank or flag drift.

### HCAE

The important transfer is not “brain-like AI.” HCAE literally consumes relational matrices for one subject, supports multiple views, constructs hypergraphs, combines hyperedges, and learns a representation. This supports a Rezon state substrate where several evidence planes describe one subject and where meaningful relations can involve more than two nodes at once.

### HRM

The architectural transfer is multi-timescale reasoning. A strategic node can reason slowly about decomposition, operator choice, and integration while tactical workers execute bounded detail tasks.

### KAG

KAG supports the idea that reasoning is an operator graph, not merely natural-language continuation. Rezon should be able to call exact retrieval, numerical calculation, symbolic/graph reasoning, and language-model reasoning in one planned solution.

### PageIndex

PageIndex challenges “embedding similarity = relevance.” Rezon should preserve hierarchical/structural retrieval and let the reasoner navigate evidence trees, especially for long project histories and technical corpora.

### Semantica

The strongest transfer is accountable state: decisions and facts remain linked to provenance, conflict, causal/semantic relations, policies, and point-in-time structure.

### Ontosphere

The strongest transfer is a verifier that can explain inconsistency and propose repairs that are rechecked rather than merely generated. Canonical RDF hashing is also attractive for semantic state identity.

### zelph

The executable-graph concept is worth studying for reasoning programs that are themselves inspectable graph state rather than opaque orchestration code.

### SGR tool calling

The useful pattern is explicit bounded agency: reason, plan, adapt, clarify, use tools, stop under limits, and produce structured final state.

### ML reverse proxy

Rezon can generalize predicted-latency routing into capability-aware reasoning-worker selection, while adding hard eligibility gates that a simple reverse proxy does not provide.

### Binomial-Heterogenicity

The literal code is not a Rezon component. Its relevance is methodological: repeated simulation over generations/distributions and explicit output suitable for statistical analysis. Keep as a weak research reference, not an architecture dependency.

## Rejected transfer behavior

Rezon should not collect repositories merely because their vocabulary sounds cognitively interesting. A source earns architectural influence only when a literal mechanism can be stated, tested, and assigned to a concrete consumer in the system.
