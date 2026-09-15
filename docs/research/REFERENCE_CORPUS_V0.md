# Rezon Reference Corpus V0

Status: RESEARCH NOTES

These repositories are architectural references, not dependencies. No source code from them is copied into Rezon by this document.

## `basiralab/HCAE`

Literal value: multi-view hyperconnectome construction, normalized hypergraph propagation, hypergraph convolution, per-subject encoding, structural compression/reconstruction. Rezon candidate use: transient per-episode structural encoder over several compatible relational views of the same proposition set.

## `sapientinc/HRM`

Value: hierarchical and multi-timescale reasoning, coupling slow abstract processing with faster detailed computation. Rezon should test fast/slow execution regimes and allocate slow reasoning selectively. Rezon does not assume HRM's neural implementation is required.

## `VectifyAI/PageIndex`

Value: hierarchical reasoning-based retrieval. Retrieval can be a search/planning operation over explicit structure rather than similarity-only nearest-neighbor lookup. Rezon should permit retrieval nodes to traverse structured indexes and preserve why a region was selected.

## `OpenSPG/KAG`

Value: hybrid problem solving under logical forms with planning, reasoning, retrieval, language reasoning, knowledge-graph reasoning, and numerical operators. This strongly supports Rezon's heterogeneous-operator model.

## `semantica-agi/semantica`

Value: explicit context/knowledge graphs, provenance, decision records, conflict detection, ontology constraints, deterministic rule engines, and system-level explainability around opaque foundation models. Rezon similarly needs explainability of supplied context, structured operations, support paths, and effects rather than pretending to expose hidden model internals.

## `ThHanke/ontosphere`

Value: separate AI proposal from deterministic ontology reasoning/validation; verified repair; provenance and reversibility of agent edits. Rezon should preserve a verifier boundary where generative proposals can be checked by stronger formal substrates.

## `acrion/zelph`

Value: executable semantic graph in which rules can themselves be graph-native structures. Rezon should leave room for rules/operators to be represented as data and reasoned about, not only hard-coded behind APIs. Licensing requires care before any code reuse.

## `lucasdinnouti/custom-reverse-proxy`

Value: several routing strategies including a learned selector that considers request type and live CPU/memory conditions. Rezon scheduler analogy: route by task/operator compatibility plus live resource/health state, rather than static role labels.

## `GeorgeVJose/DRISHTE-Public`

Value: heterogeneous specialist algorithms can be interchanged to balance processing speed, noise, and accuracy. This is an orchestration analogy, not a reasoning framework.

## `hvala/Binomial-Heterogenicity`

Value: repeated simulation over changing distributions. Rezon should treat Monte Carlo simulation as a genuine evidence-generating computational operator where appropriate instead of asking a language model to intuit quantitative distributions.

## `MiXaiLL76/n8n-nodes-sgr-tool-calling`

Value: explicit reasoning/tool/final-answer operations and hard iteration/search/clarification budgets. Rezon needs first-class resource budgets and terminal conditions. Licensing requires care before any code reuse.

## Synthesis

The strongest combined lesson is:

> Build heterogeneous computation around structured, provenance-bearing semantic state; route operations according to task and runtime conditions; preserve deterministic verification where available; use learned latent structure as an aid rather than an authority; and measure whether added reasoning actually improves outcomes.
