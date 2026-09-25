# Epistemic State Contract V0

Status: DESIGN

## Purpose

This contract prevents semantic collapse inside Rezon. Different kinds of epistemic material remain distinguishable even when represented by the same underlying software type.

## Proposition record

```text
PROPOSITION {
  proposition_id
  episode_id
  kind
  content
  normalized_form?
  created_at
  valid_from?
  valid_to?
  status
  confidence?
  source_refs[]
  producer_execution_id?
  provenance
  tags[]
}
```

`kind` is one of:

```text
OBSERVATION
EVIDENCE
CLAIM
HYPOTHESIS
ASSUMPTION
QUESTION
PREDICTION
TEST
TEST_RESULT
DECISION
```

## Semantic invariants

1. A `HYPOTHESIS` does not become `EVIDENCE` because multiple nodes repeat it.
2. `CONFIDENCE` is not evidence strength, truth, node health, priority, or authorization.
3. A retrieved statement is not automatically true; retrieval establishes source presence, not correctness.
4. A model-generated statement has producer provenance but no external evidentiary authority merely because a model emitted it.
5. An `ASSUMPTION` must remain inspectable as an assumption until independently supported or explicitly discharged.
6. A `TEST_RESULT` records what a test established under its exact conditions. It must not silently generalize beyond those conditions.
7. A `DECISION` records an action-selection result. Selection does not make its premises true.
8. Retraction or correction creates new temporal state; history is preserved.

## Hyperrelation record

```text
HYPERRELATION {
  relation_id
  episode_id
  relation_type
  participants[] {
    proposition_id
    role
  }
  directionality
  support
  provenance
  created_at
  valid_from?
  valid_to?
  status
}
```

A hyperrelation can represent genuinely joint support, such as three observations plus one assumption jointly supporting one inference, without inventing a serial order.

## Support record

```text
SUPPORT {
  support_kind
  strength?
  method
  source_refs[]
  execution_refs[]
  caveats[]
}
```

Candidate `support_kind` values:

```text
DIRECT_OBSERVATION
SOURCE_ATTESTATION
DEDUCTIVE_DERIVATION
STATISTICAL_ESTIMATE
SIMULATION_RESULT
FORMAL_PROOF
FORMAL_COUNTEREXAMPLE
EMPIRICAL_TEST
MODEL_JUDGMENT
HEURISTIC
UNKNOWN
```

Support kinds must not be flattened into a single score without retaining the original typed record.

## Contradiction

Contradiction is first-class state. Conflicting propositions may coexist. Rezon should not resolve them by overwrite.

A contradiction record should capture the competing proposition IDs, relation or rule under which they conflict, discovery execution, and resolution status.

## Provenance minimum

Every durable proposition or relation must be attributable to one or more of:

```text
user input
external source
retrieval result
reasoning-node execution
numerical/symbolic computation
simulation
human/system decision
```

Unknown provenance is representable but should be visibly degraded rather than fabricated.
