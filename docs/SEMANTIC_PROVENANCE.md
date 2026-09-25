# Semantic Provenance and Verification

## Goal

Rezon should know not only *what* a reasoning node concluded, but how that conclusion relates to explicit concepts, source evidence, constraints, contradictions, and prior decisions.

Several external projects contribute different parts of this problem.

## Semantica

Source: https://github.com/semantica-agi/semantica

Useful transfer:

- context graphs;
- provenance as a first-class structure;
- decision records;
- deterministic reasoning surfaces;
- conflict detection;
- ontology constraints;
- point-in-time snapshots;
- explicit distinction between system-level explainability and inaccessible model-internal reasoning.

Rezon should particularly borrow the idea that a decision is a queryable object with ancestry and downstream effects.

## Ontosphere

Source: https://github.com/ThHanke/ontosphere

Useful transfer:

- OWL 2 DL reasoning;
- SHACL validation;
- reasoner-verified repair suggestions;
- canonical graph hashing;
- edit provenance and reversal;
- MCP tool exposure;
- explicit distinction between asserted and inferred triples.

This suggests a verifier pattern:

```text
candidate semantic state
   -> ontology/profile validation
   -> consistency reasoning
   -> constraint checks
   -> contradiction diagnosis
   -> ranked repair candidates
   -> independent re-verification
```

Rezon should not automatically accept a repair merely because a reasoner says the graph becomes consistent; repair choice can still involve domain intent and authority.

## KAG

Source: https://github.com/OpenSPG/KAG

Useful transfer:

- schema-constrained knowledge construction;
- text/knowledge mutual indexing;
- logical-form-guided reasoning;
- mixing retrieval, knowledge-graph reasoning, language reasoning, and numerical computation;
- explicit domain knowledge boundaries.

## zelph

Source: https://github.com/acrion/zelph

Useful transfer:

- executable graph idea;
- rules represented as graph-native structures;
- deep unification;
- derivation chains / proof-oriented outputs;
- computation as graph rewriting.

Caution: zelph is AGPL-3.0-or-later for open-source use with a commercial licensing option. Rezon should treat it as a conceptual/reference source unless licensing implications are intentionally accepted.

## Proposed Rezon objects

```text
ClaimNode {
  claim_id
  proposition
  proposition_type
  subject
  scope
  status
}

EvidenceEdge {
  evidence_id
  source_ref
  supports_or_conflicts
  admissibility
  temporal_scope
  confidence_or_weight?
}

DecisionNode {
  decision_id
  input_claims[]
  applied_rules[]
  rejected_alternatives[]
  output_claims[]
  receipt_ref
}
```

Some relations should be hyperedges rather than pairwise edges when their semantics depend on a joint configuration.

## Provenance rules

- inferred facts remain distinguishable from asserted facts;
- generated summaries point to their sources;
- transformations have versioned code/model provenance;
- historical state is not silently promoted to current state;
- conflicting evidence is retained rather than overwritten;
- repair changes preserve a diff and previous state;
- externally generated model text is never treated as proof merely because it came from a “reasoning” worker.

## Semantic integrity tests

Rezon should test:

- equivalent paraphrases with different wording;
- same words with different proposition types;
- scope narrowing and broadening;
- relation reversal;
- stale superseded evidence;
- contradictory ontology constraints;
- circular provenance;
- repair that removes the contradiction only by deleting the claim under test;
- inferred-state promotion into asserted state;
- graph equality across different serialization order.
