# Hierarchical Distributed Reasoning

## Core idea

A reasoning system should not assume one reasoning tempo, one worker type, or one representation.

The strongest structural inspiration here is HRM’s separation between a slower, abstract high-level module and a faster, detailed low-level module. Rezon should not copy HRM’s trained recurrent architecture literally; it should transfer the systems principle into an orchestrated reasoning runtime.

Source: https://github.com/sapientinc/HRM

## Rezon tiers

### Strategic / slow tier
Responsibilities:

- establish the literal proposition;
- decompose the problem;
- select reasoning operators;
- allocate resources;
- decide which evidence is missing;
- determine when independent opposition is required;
- integrate results across nodes;
- decide whether to continue, reconcile, or stop unresolved.

### Tactical / fast tier
Responsibilities:

- bounded retrieval;
- calculations;
- constraint solving;
- local search;
- document extraction;
- code/test execution;
- graph queries;
- proposition checks;
- specialized model calls;
- deterministic validation.

A node can be computationally expensive without being strategic. “Slow” and “fast” describe role/timescale, not necessarily model size.

## Heterogeneous operator topology

KAG supplies another important principle: one problem-solving process can combine planning, retrieval, knowledge-graph reasoning, language reasoning, and numerical calculation under a common plan.

Source: https://github.com/OpenSPG/KAG

Rezon should support nodes with explicit operator types, for example:

```text
RETRIEVAL
DEDUCTION
ABDUCTION
CAUSAL
COUNTERFACTUAL
NUMERICAL
SYMBOLIC
CONSTRAINT
SEARCH
SIMULATION
GRAPH
HYPERGRAPH
SEMANTIC
PRAGMATIC
OPPOSITION
VERIFICATION
INTEGRATION
```

Provider/model is a property of a node, not its semantic role.

## Proposed orchestration model

```text
TaskEnvelope
   |
   v
Proposition/Scope Parser
   |
   v
Strategic Planner
   |
   +----------+----------+-----------+---------+
   v          v          v           v         v
Retrieve   Symbolic   Numeric     Model     Simulate
   |          |          |           |         |
   +----------+----------+-----------+---------+
                         |
                         v
                    Opposition
                         |
                         v
                    Verification
                         |
                         v
                     Integrator
```

The graph should support loops. A failed verification can create a new evidence request or revised decomposition rather than merely lowering confidence.

## Independence requirements

Multiple nodes are not automatically independent. Rezon should record:

- model/provider identity;
- prompt/instruction lineage;
- shared context sources;
- shared random seed where relevant;
- whether one node saw another node’s result before answering;
- whether two “reviewers” are actually reruns of one deterministic process.

Consensus from correlated workers is weaker than consensus from genuinely independent methods.

## Resource scheduling

Each node invocation should expose estimates or bounds for:

- cost;
- latency;
- reasoning depth;
- context size;
- tool requirements;
- provider availability;
- concurrency class;
- expected information gain.

A scheduler can route simple subtasks to cheap deterministic workers and reserve high-cost models for genuinely hard integration or hostile review.

## Failure semantics

A node should end in explicit states such as:

```text
SUCCESS
NO_RESULT
INSUFFICIENT_EVIDENCE
CONFLICT
UNAVAILABLE
TIMEOUT
RESOURCE_LIMIT
INVALID_INPUT
VERIFICATION_FAILED
ATTEMPTED_UNKNOWN
```

The integrator must not silently convert unavailable or conflicting branches into agreement.
