# Reasoning Node Contract V0

Status: DESIGN

## Principle

A reasoning node is a constrained computational capability. The term does not imply an independent mind, persistent identity, or separate consciousness.

## Descriptor

```text
REASONING_NODE_DESCRIPTOR {
  node_id
  version
  capabilities[]
  accepted_input_kinds[]
  emitted_output_kinds[]
  permitted_operations[]
  forbidden_information[]
  executor_type
  deterministic
  cost_model
  latency_model
  reliability_profile
  output_contract
  verification_requirements[]
}
```

Candidate `executor_type` values include:

```text
LLM
SYMBOLIC
NUMERICAL
SIMULATION
RETRIEVAL
SEARCH
CODE_EXECUTION
ONTOLOGY_REASONER
CAUSAL_MODEL
HYPERGRAPH_ENCODER
EXTERNAL_TOOL
```

## Execution request

```text
NODE_EXECUTION_REQUEST {
  execution_id
  episode_id
  node_id
  objective
  visible_proposition_ids[]
  visible_relation_ids[]
  explicit_blindings[]
  resource_budget
  requested_output_kinds[]
}
```

## Execution result

```text
NODE_EXECUTION_RESULT {
  execution_id
  node_id
  started_at
  completed_at
  status
  outputs[]
  evidence_refs[]
  tool_receipts[]
  uncertainty
  resource_usage
  verification_status
  errors[]
}
```

Private model chain-of-thought is not required or presumed available. Rezon records inspectable structured outputs, support, tool effects, and execution metadata.

## Example constraints

### Independent hypothesis generator

Receives observations/evidence and the problem statement. Existing hypotheses and votes are blinded. Emits `HYPOTHESIS` objects and discriminating predictions.

### Falsifier

Receives a target hypothesis and admissible evidence. Supporting argument may be blinded. Emits counterexamples, contradictory evidence, or a bounded `NO_REFUTATION_FOUND` result. Failure to refute is not proof.

### Probabilistic updater

Receives hypothesis IDs plus typed evidence/support. It may update confidence records but may not create new evidence.

### Analogy operator

Emits analogical mappings tagged `HEURISTIC`. An analogy is not promoted to evidence unless an independent operation validates the transferred structure.

### Formal verifier

Receives a formalized proposition and assumptions. It emits proof/refutation/unknown with exact formalization provenance. A proof of the formalized statement does not validate an incorrect translation from natural language.

## Scheduler boundary

The scheduler may select, defer, repeat, isolate, or terminate node executions under budget. It does not rewrite node outputs into stronger epistemic kinds and does not decide truth by vote.
