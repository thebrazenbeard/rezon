# Roadmap

Rezon’s goal is a runnable reasoning framework, but promotion from research to runtime should be evidence-driven.

## Phase 0 — knowledge foundation

Current pass.

Deliverables:

- reasoning taxonomy;
- human/AI mechanism synthesis;
- identity-track model;
- multi-view hypergraph-state model;
- hierarchical/multi-node reasoning topology;
- adversarial collaboration method;
- retrieval/context strategy;
- semantic/provenance verification strategy;
- worker-routing/Ultra research boundary;
- source transfer matrix;
- evaluation/falsification principles;
- Vera adoption candidates.

Success: repository contains enough explicit architecture that first code is constrained by semantics rather than improvisation.

## Phase 1 — executable core

Build the smallest provider-independent runtime with:

- TaskEnvelope;
- Proposition typing;
- ReasoningNode interface;
- deterministic/mock workers;
- planner/decomposer;
- opposition node;
- integrator;
- ResultReceipt;
- hostile tests.

No external model dependency is required to pass the core suite.

## Phase 2 — evidence and retrieval

Add:

- source/provenance objects;
- structural/tree retrieval;
- exact retrieval;
- semantic retrieval adapter;
- evidence conflict handling;
- source-version pinning.

Prototype PageIndex-style hierarchical retrieval on a real technical corpus.

## Phase 3 — persistent subject state

Add:

- subject track;
- observation epochs;
- hard/soft association evidence;
- ambiguity/conflict states;
- state trajectory;
- multi-view graph/hypergraph representation.

Do not add learned identity scoring until hard association semantics are already tested.

## Phase 4 — heterogeneous reasoning adapters

Add bounded adapters for:

- deterministic numerical/symbolic operations;
- graph/ontology reasoning;
- simulation;
- one or more LLM providers;
- optional local models.

Use capability discovery rather than hardcoding model prestige into routing.

## Phase 5 — semantic verifier

Prototype:

- canonical graph identity;
- constraint/ontology validation;
- contradiction diagnosis;
- asserted vs inferred state;
- repair candidates + independent re-verification.

## Phase 6 — resource-aware distributed scheduling

Add:

- concurrency/dependency graph;
- resource leases;
- parent/child budget inheritance;
- idempotent invocation IDs;
- ambiguous completion reconciliation;
- cost/latency/information-gain routing.

## Phase 7 — optional high-reasoning workers

If supported callable surfaces exist, integrate high-cost workers (including any future verified Ultra path) as optional specialists.

Requirements:

- no runtime dependency on undocumented provider internals;
- no authority promotion by model rank;
- exact capability/readback evidence;
- resource and privacy limits;
- independent verification of important outputs.

## Phase 8 — Vera integration candidates

Promote only mechanisms that have survived Rezon prototypes and hostile tests. Likely candidates are listed in `VERA_ADOPTION_CANDIDATES.md`.

Each Vera integration is separately governed and must distinguish source, installation, runtime consumption, effect, and qualification.

## Continuous research questions

- What is the minimal useful representation for a reasoning graph?
- When is a hyperedge materially better than explicit n-ary relation objects?
- How should worker independence be quantified?
- How can expected information gain be estimated cheaply enough for scheduling?
- Which reasoning operations are best deterministic vs model-based?
- How can semantic equivalence tests resist lexical bypasses?
- How should persistent subject tracks represent branching/merging histories?
- Which state dimensions should remain hard symbolic facts and which benefit from learned latent representations?
- What provider capability discovery can be made portable across model vendors?
