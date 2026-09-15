# Multi-Node Reasoning Topology

## Why multiple nodes

Multiple reasoning nodes are useful only when their separation creates a real epistemic or computational benefit. Spawning several copies of the same model with the same context can create the appearance of consensus without meaningful independence.

## Topology patterns

### Pipeline

```text
parse -> retrieve -> reason -> verify -> integrate
```

Useful when stages have clear dependencies.

### Fan-out / fan-in

```text
             -> deductive --
problem ----> causal -------> integrator
             -> analogical --
             -> opponent ----
```

Useful for independent methods over one proposition.

### Debate / dialectic

```text
proponent <-> opponent
       \       /
        verifier
           |
        integrator
```

Useful when assumptions are contestable. Must avoid endless rhetorical loops and shared-premise blind spots.

### Hierarchical tree

```text
strategic planner
  |- subproblem A -> workers
  |- subproblem B -> workers
  `- subproblem C -> workers
```

Useful for complex decomposable tasks.

### Blackboard / shared evidence graph

Nodes publish typed claims/evidence to a shared structure. Other nodes subscribe to unresolved or relevant items. Powerful, but requires strict provenance and mutation semantics.

### Market / bidding router

Eligible workers estimate cost, latency, confidence, or expected information gain. A scheduler assigns tasks under hard constraints. Useful with heterogeneous providers.

## Roles

Candidate roles are semantic, not identities:

- coordinator;
- proposition parser;
- decomposer;
- retriever;
- domain specialist;
- symbolic solver;
- simulator;
- causal analyst;
- adversarial reviewer;
- verifier;
- provenance auditor;
- integrator;
- resource scheduler.

One worker can implement several roles, but roles should remain separable in receipts.

## Shared-state hazards

### Premature contamination
If an “independent” reviewer sees the candidate’s rationale first, it may anchor on the same assumptions.

### Stale frontier
A worker can review an old subject while the candidate changes underneath it.

### Consensus inflation
Five correlated workers do not equal five independent sources.

### Authority propagation
Delegating a task must not silently delegate protected authority beyond the task’s exact scope.

### Write collisions
Multiple workers mutating one branch/state require CAS, transactions, or isolation + reconciliation.

## Independence metadata

Every important review node should record:

```text
IndependenceMetadata {
  worker_model
  worker_provider
  prompt_lineage
  source_context_digest
  saw_candidate_rationale
  saw_peer_outputs
  randomization_or_seed?
  execution_subject
}
```

## Integration rule

The integrator should aggregate **arguments and evidence**, not votes.

A minority node with a valid counterexample beats a majority of unsupported approvals.

## Stopping conditions

A reasoning graph should stop when one of these applies:

- success criteria are verified;
- remaining uncertainty is explicitly acceptable;
- a real external dependency blocks progress;
- resource budget is exhausted;
- evidence conflict cannot be resolved from available sources;
- continuation has low expected information gain.

Stopping is part of reasoning, not merely a timeout.
