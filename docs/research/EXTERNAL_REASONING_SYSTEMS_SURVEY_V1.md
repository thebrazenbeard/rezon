# External Reasoning Systems Survey V1

Status: `RESEARCH_EVIDENCE / NO_DEPENDENCY_SELECTION`

Date reviewed: 2026-09-15

Purpose: record the external repositories reviewed while forming Rezon's first reasoning architecture. This document is evidence and design input, not an instruction to vendor, fork, import, or depend on any repository listed here.

## Evaluation lens

Each source is evaluated for one or more of these Rezon concerns:

- higher-order relational representation,
- reasoning architecture,
- provenance and auditability,
- retrieval and context assembly,
- ontology/constraint validation,
- agent/tool orchestration,
- multi-view or heterogeneous-state learning,
- contradiction detection,
- licensing/integration risk.

## 1. basiralab/HCAE

Reviewed source subject: `basiralab/HCAE@ed13937a5266aadbfa34cd57e6c9a703470c77e9`.

Source framing: HyperConnectome AutoEncoder for brain-state identification using multi-view hyperconnectomes, hypergraph convolution, reconstruction, and adversarial regularization.

Rezon value: **foundational architectural input**. The important idea is not the medical classifier. It is representing one subject through multiple heterogeneous higher-order relational views, fusing hyperedge families, propagating through a normalized hypergraph operator, and learning a compact representation that can reconstruct relational structure.

Literal Rezon reapplication: reasoning cases become subjects; claims/evidence/rules/actions become vertices; provenance/authority/temporal/causal/semantic/etc. become views; typed reasoning contexts become hyperedges.

Integration posture: reimplement the useful semantics and mathematics in modern maintained code. Do not import the TensorFlow-1-era implementation as production infrastructure.

License: source README states MIT.

See `docs/research/HCAE_SEMANTIC_REAPPLICATION_V1.md`.

## 2. semantica-agi/semantica

Observed repository description: graph-native infrastructure for context and accountable AI systems.

Observed capabilities relevant to Rezon:

- context graphs,
- decision objects,
- deterministic forward chaining / Rete / Datalog / SPARQL,
- conflict detection,
- ontology and SHACL/OWL support,
- W3C PROV-O provenance,
- point-in-time graph snapshots,
- MCP and agent integrations,
- explicit system-level explainability outside the foundation model.

Rezon value: **strong provenance/governance reference**. Particularly useful for representing decision lineage, conflict handling, ontology validation, and auditable context without pretending to expose hidden model reasoning.

Boundary: Semantica-like structures can inform Rezon's deterministic layer. They do not replace Rezon's canonical evidence sources or turn retrieved material into authority.

Observed license: MIT.

## 3. VectifyAI/PageIndex

Observed repository framing: vectorless, reasoning-based RAG using hierarchical document-tree indexes and model-guided navigation rather than standard chunk-and-vector retrieval.

Rezon value: **strong retrieval/context-assembly reference**. Useful for long technical documents, specifications, qualification records, and source corpora where section hierarchy and explicit references matter.

Boundary: retrieval is evidence discovery, not evidence authority. A PageIndex-style navigator may locate relevant source material but cannot decide which source is current or governing.

Observed license: MIT.

## 4. OpenSPG/KAG

Observed framing: Knowledge Augmented Generation using OpenSPG, schema-constrained knowledge construction, graph/text mutual indexing, and logical-form-guided hybrid solving.

Observed reasoning operators include combinations of planning, graph reasoning, exact retrieval, text retrieval, numerical calculation, and language reasoning.

Rezon value: **strong hybrid-reasoning reference**. Especially relevant to preserving both original text and structured graph knowledge and selecting different operators during a solve rather than routing every query through one retrieval mechanism.

Observed license: Apache-2.0.

## 5. ThHanke/ontosphere

Observed framing: browser-based RDF/OWL knowledge-graph editor with client-side reasoning, SHACL validation, reasoner-verified repair, provenance, canonical graph hashing, and MCP tooling.

Observed capabilities relevant to Rezon:

- OWL 2 DL reasoning,
- SHACL validation,
- reasoner-computed contradiction repair,
- PROV-O agent-edit provenance and reversal,
- RDFC-1.0 canonicalization and SHA-256 graph identity,
- MCP tool surface,
- graph visualization and inspection.

Rezon value: **strong inspection/verification reference**. Ontosphere demonstrates a useful separation between agent-authored graph changes and a verification substrate that returns explicit diagnosis rather than silently accepting edits.

License note: GitHub repository metadata was observed reporting `NOASSERTION`, while the repository's actual `LICENSE` file contains Apache License 2.0. The file is the stronger source for the repository's stated license.

## 6. acrion/zelph

Observed framing: executable semantic network in which facts, relations, rules, and mathematics are all represented within one graph. The project emphasizes unification, rule execution, derivation/proof chains, contradiction detection, and very large graph workloads.

Rezon value: **high-value conceptual reference** for executable graph semantics, proof-path exposure, and contradiction discovery. The idea that a rule can quantify over relationships represented in the graph itself is particularly relevant to a system that wants first-class reasoning structure rather than opaque procedural glue.

Integration risk: source is AGPL-3.0-or-later with a commercial-license option. Treat as research/reference unless a future explicit dependency/license decision is made.

## 7. sapientinc/HRM

Observed framing: Hierarchical Reasoning Model with two recurrent modules operating at different timescales: a slower high-level planning module and faster low-level computation module.

Rezon value: **reasoning-control research reference**. The key idea is not that Rezon needs this neural model as a dependency; it is that useful reasoning can separate slow abstract state evolution from rapid local computation while allowing the two levels to interact recurrently.

Potential Rezon analogue: hierarchical control plane where a slow planner sets goals/constraints and fast workers perform local evidence, retrieval, calculation, or transformation steps.

Observed license: Apache-2.0.

## 8. MiXaiLL76/n8n-nodes-sgr-tool-calling

Observed framing: schema-guided reasoning agent for n8n with explicit system tools for reasoning, final answer, report creation, clarification, plan creation, and plan adaptation. It also exposes resource limits such as maximum iterations/searches/clarifications.

Rezon value: **agent-loop contract reference**. Explicit tool schemas and bounded loop state are useful patterns for making reasoning execution inspectable rather than letting an agent run an unstructured hidden loop.

License conflict observed: repository metadata and the actual LICENSE file identify GPL-3.0, while the README states AGPL-3.0 and describes AGPL network-service obligations. Do not reuse code until that inconsistency is resolved by authoritative source or maintainer clarification.

## 9. lucasdinnouti/custom-reverse-proxy

Observed framing: heterogeneous load-balancing experiments in Go, with components including proxy, ML proxy, processor, and runner.

Rezon value: **minor routing reference**. Potentially useful as conceptual input if Rezon eventually routes workloads across heterogeneous reasoning nodes. The repository is small and lightly documented; no architectural dependency should be inferred from its presence in this survey.

Observed license: MIT.

## 10. GeorgeVJose/DRISHTE-Public

Observed framing: vehicle detection, tracking, and trajectory analysis for heterogeneous traffic using drone footage, YOLOv5, CSRT/KCF, OpenCV, and associated data-processing tools.

Rezon value: **currently low**. It is useful as an example of multi-stage perception/tracking pipelines but does not presently contribute a distinctive reasoning abstraction needed by Rezon.

Observed repository metadata: no declared GitHub license.

## 11. hvala/Binomial-Heterogenicity

Observed framing: numerical simulation of heterogenic/heterozygote frequencies in a population.

Rezon value: **currently none beyond generic simulation inspiration**. It should not influence Rezon architecture merely because its title contains "heterogenicity."

Observed repository metadata: no declared license.

## Cross-source synthesis

The useful sources do not collapse into one replacement framework. They illuminate different layers:

```text
PageIndex-like navigation
        |
        v
Evidence discovery -----------------------------+
                                                 |
Semantica / Ontosphere-like deterministic       |
context, provenance, ontology, validation       |
        |                                        |
        +-------------------+--------------------+
                            |
                            v
                 Typed multi-view reasoning state
                            |
                HCAE-derived hypergraph encoder
                            |
                 +----------+----------+
                 |                     |
          learned structure       deterministic rules
          anomaly / analogy       authority / provenance
          retrieval ranking       policy / qualification
                 |                     |
                 +----------+----------+
                            |
                            v
                   KAG/Zelph-like hybrid
                    operator composition
                            |
                            v
                       audited result
```

HRM-like hierarchical control can sit above this stack as an execution strategy: slow planning and fast local operations operating against the same explicit reasoning state.

## Non-negotiable boundary

No external model, graph library, retriever, or learned representation becomes truth merely because it produces a score or plausible structure.

Rezon's learned components may discover, rank, compare, compress, predict, and suggest. Authority, provenance, exact identity, currentness, protected effects, and qualification remain explicit deterministic concerns unless a future design deliberately and visibly changes that contract.