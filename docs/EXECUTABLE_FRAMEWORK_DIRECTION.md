# Executable Framework Direction

## Product posture

Rezon is intended to become a runnable reasoning framework, not only a research archive. The framework should remain small enough that its abstractions can still be falsified and changed.

The first implementation should be provider-agnostic and executable with deterministic/mock workers. External model providers, Work/Ultra, local models, symbolic engines, retrieval systems, and graph stores should enter through adapters.

## Candidate core interfaces

### TaskEnvelope

Carries the user/problem proposition without prematurely decomposing it.

```text
TaskEnvelope {
  task_id
  literal_request
  subject_refs[]
  constraints[]
  available_authority[]?
  privacy_scope?
  resource_budget?
  context_refs[]
}
```

### Proposition

```text
Proposition {
  proposition_id
  text_or_structure
  type
  referent
  scope
  modality
  temporal_scope
  status
}
```

### ReasoningNode

```text
ReasoningNode {
  node_id
  operator_type
  worker_descriptor
  input_contract
  output_contract
  independence_metadata
}
```

### ReasoningResult

```text
ReasoningResult {
  node_id
  subject
  claims[]
  evidence_refs[]
  assumptions[]
  unresolved[]
  confidence?
  execution_receipt
}
```

### OppositionResult

See `ADVERSARIAL_COLLABORATION.md`.

### ResultReceipt

```text
ResultReceipt {
  task_id
  exact_graph_version
  worker_runs[]
  source_versions[]
  accepted_claims[]
  rejected_claims[]
  conflicts[]
  unresolved[]
  effect_state
  resource_settlement
}
```

## Proposed modules

```text
rezon/
  core/
    envelopes
    propositions
    claims
    receipts
  planning/
    decomposer
    scheduler
  nodes/
    base
    deterministic
    model_adapter
    retrieval
    symbolic
    simulation
    opposition
    verifier
  state/
    identity_track
    epoch
    graph
    hypergraph
    provenance
  integration/
    reconciler
    integrator
  providers/
    mock
    openai?
    local?
  evaluation/
    harness
    hostile_cases
```

This is a direction, not a frozen directory contract.

## Execution lifecycle

```text
INGEST
  -> TYPE_PROPOSITIONS
  -> PLAN
  -> RESERVE_RESOURCES
  -> EXECUTE_NODES
  -> OPPOSE
  -> VERIFY
  -> RECONCILE
  -> INTEGRATE
  -> SETTLE
  -> RECEIPT
```

Loops are allowed between VERIFY/RECONCILE and PLAN when new evidence or a revised subproblem is needed.

## State and identity integration

Reasoning tasks can optionally bind to a persistent subject track. A run then receives a current state epoch and may produce a proposed next epoch. State promotion occurs only through the subject’s association/admission rules and provenance constraints.

This prevents a worker from changing persistent identity/state simply by emitting a plausible narrative.

## Concurrency

Parallelism should require explicit independence and data-dependency analysis. A scheduler should distinguish:

- independent parallel tasks;
- shared-read tasks;
- tasks that require a predecessor result;
- mutually exclusive mutations;
- redundant reviewers intended for independent verification.

## Resource leases

Resource use should eventually support leases/reservations for scarce model/provider capacity. Child work inherits bounded resource authority rather than implicitly getting a new budget.

## Error model

Errors should remain typed. Exceptions are implementation details; system state should expose semantics such as `UNAVAILABLE`, `CONFLICT`, `INVALID_SUBJECT`, `INSUFFICIENT_EVIDENCE`, `RESOURCE_LIMIT`, and `ATTEMPTED_UNKNOWN`.

## Non-goals for the first executable version

- no universal autonomous agent;
- no requirement for a graph database;
- no requirement for distributed network services;
- no dependency on an internal Ultra worker;
- no neural embedding required for identity;
- no claim of human-like consciousness or continuous subjective state;
- no large plugin ecosystem before the core receipts and tests work.

## Promotion rule

A mechanism moves from research note to core interface only when:

1. a concrete consumer exists;
2. a minimal implementation can be tested;
3. hostile cases exist;
4. the abstraction reduces rather than increases semantic ambiguity;
5. an alternate implementation can satisfy the same interface.
