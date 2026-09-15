# Rezon reasoning-source synthesis — 2026-09-15

Purpose: extract reusable reasoning mechanisms, not copy implementations or claim model-weight changes.

## Mechanisms worth adopting

- **HRM (`sapientinc/HRM`)** — split slow abstract planning from fast detailed computation. Rezon uses this as a two-timescale controller: a high-level goal/state loop delegates bounded low-level operations.
- **HyPER (`ShengxuanQiu/HyPER`)** — treat difficult reasoning as exploration vs. exploitation. Rezon keeps a small hypothesis frontier, expands only plausible branches, scores them against evidence, and prunes aggressively.
- **PageIndex (`VectifyAI/PageIndex`)** — retrieve by a hierarchical tree and contextual relevance rather than flat similarity alone. Rezon searches source/context structure top-down before reading large bodies wholesale.
- **KAG (`OpenSPG/KAG`)** — route each subproblem to the right operator: exact retrieval, graph/logical reasoning, language reasoning, or numerical calculation. Do not force one reasoning style onto every step.
- **Semantica (`semantica-agi/semantica`)** — externalize facts, relations, conflicts, provenance, decisions, and causal ancestry. Rezon treats source-backed claims and decisions as graph-like objects rather than loose prose memory.
- **Ontosphere (`ThHanke/ontosphere`)** — validation and reasoner-verified repair are first-class. Rezon checks contradictions and proposes minimal repair/downgrade rather than silently smoothing conflicts.
- **zelph (`acrion/zelph`)** — rules can live in the same graph as facts and derivations can be exported. Rezon favors explicit rules/constraints and compact proof/evidence paths where deterministic reasoning is possible.
- **SGR tool-calling (`MiXaiLL76/n8n-nodes-sgr-tool-calling`)** — explicit plan/adapt cycles with iteration/search limits. Rezon uses bounded budgets and replans only when new evidence invalidates the current path.
- **ZEEJAI Hyper Chat (`zeeza18/ZEEJAI-Hyper-Chat`)** — separate fast, deep-reasoning, and search modes. Rezon makes depth dynamic rather than always-on.
- **HCAE (`basiralab/HCAE`)** — many-to-many, multi-view relationships matter. Rezon reconciles independent views/sources through a hypergraph-like dependency model instead of reducing everything to pairwise similarity.
- **Hyperbolic reasoning work (`koriavinash1/HyperbolicReasoning`, `deadsmash07/hyperbolic-reasoning-probe`)** — hierarchical reasoning benefits from explicitly tree-like structure. Rezon uses nested hypothesis/context trees and ancestor/descendant distance conceptually; it does not claim to alter the model's embedding geometry.
- **Connectome fingerprint (`yixial-1736/connectome_fingerprint`)** — connection patterns can have different predictive utility. Rezon tracks which evidence paths/operators actually predict successful outcomes and increases their future routing weight.
- **Connectome Matrix (`dakariuishmg/Program_Tool_For_AI_Connectome_Dome`)** — weighted synapses, hierarchy, inferred bridges, and explicit reasons are useful orchestration primitives. Rezon represents cross-node links with type, weight, and rationale.
- **ML reverse proxy (`lucasdinnouti/custom-reverse-proxy`)** — choose a processing target based on expected latency/resource state rather than round-robin. Rezon applies the same idea to tool/model/operator routing: cheapest adequate path first, escalate when needed.
- **DRISHT-E (`GeorgeVJose/DRISHTE-Public`)** — interchangeable trackers trade speed/noise/accuracy. Rezon cross-checks difficult observations with more than one reasoning/retrieval operator when the first is noisy or uncertain.
- **Binomial-Heterogenicity (`hvala/Binomial-Heterogenicity`)** — distribution over repeated simulations is more informative than a single run. Rezon uses perturbation/ensemble checks for fragile conclusions instead of treating one reasoning path as certainty.

## Rejected / bounded interpretations

These sources do **not** let a chat instance permanently alter GPT weights, hidden-state geometry, or native context capacity. Their useful contribution here is architectural: routing, retrieval, decomposition, verification, provenance, and external state.

The target is therefore **effective reasoning gain**: fewer irrelevant tokens, more appropriate operators, broader search only when necessary, explicit contradiction handling, and durable external reasoning state.