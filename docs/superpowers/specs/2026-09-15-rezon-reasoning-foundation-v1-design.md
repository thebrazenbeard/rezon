# Rezon Reasoning Foundation V1 Design

Status: `DESIGN_CANDIDATE / NO_RUNTIME / NO_QUALIFICATION`

Date: 2026-09-15

## Purpose

Rezon is an experimental reasoning substrate for representing, inspecting, comparing, and operating on reasoning state without reducing reasoning to either a hidden chain of thought or a flat bag of text chunks.

The V1 thesis is:

> A reasoning state is a typed, multi-view hypergraph of claims, evidence, rules, actions, hypotheses, decisions, participants, and artifacts. Deterministic structure preserves identity, provenance, authority, policy, and currentness. Learned structure may compress, compare, rank, detect anomalies, and suggest missing context.

Rezon is not an authority source merely because it stores or learns from evidence.

## Design goals

1. Represent higher-order reasoning contexts natively instead of forcing every relationship into pairwise edges.
2. Preserve multiple relation semantics as separately inspectable views.
3. Keep deterministic authority/provenance semantics distinct from learned similarity or inference.
4. Make reasoning-state transformations auditable and reproducible.
5. Support structural analogy, anomaly detection, context assembly, contradiction investigation, and hybrid reasoning.
6. Permit multiple reasoning operators without making one retrieval/model architecture universal.
7. Make every learned output traceable to its model/corpus/version and every deterministic output traceable to its source/derivation.
8. Fail closed when identity, provenance, authority class, or required relation semantics are unknown.

## Non-goals for V1

- exposing or reconstructing hidden foundation-model chain of thought,
- replacing Git, databases, or source-specific systems of record,
- treating neural outputs as authorization or truth,
- autonomous protected effects,
- production-scale distributed training,
- universal ontology design,
- importing third-party code simply because it inspired this design.

## Core object model

### ReasoningCase

One bounded reasoning subject.

Examples:

- a technical decision,
- a debugging incident,
- a policy interpretation,
- a research question,
- a system-currentness determination,
- a multi-agent disagreement.

Required fields:

```text
case_id
subject_type
subject_key
created_at
source_set_digest
schema_version
nodes[]
hyperedges[]
receipts[]
```

### ReasoningNode

A first-class object participating in one or more reasoning contexts.

Initial node kinds:

```text
CLAIM
OBSERVATION
SOURCE
RULE
POLICY
HYPOTHESIS
ACTION
DECISION
ARTIFACT
ACTOR
RUNTIME_STATE
MEASUREMENT
QUESTION
RESULT
```

Required fields:

```text
node_id
kind
canonical_label
payload_ref | inline_payload
source_provenance
created_at
valid_time
confidence_class
```

`confidence_class` describes evidentiary confidence; it does not grant authority.

### ReasoningHyperedge

A first-class typed many-to-many context.

Required fields:

```text
hyperedge_id
view
relation_type
members[]
source_provenance
construction_class
valid_time
weight
uncertainty
```

`construction_class` is one of:

```text
EXPLICIT
DETERMINISTIC_DERIVED
LEARNED
HEURISTIC
```

Learned and heuristic hyperedges can never silently cross into explicit or deterministic-derived classes.

## View registry

V1 reserves these relation views:

```text
PROVENANCE
AUTHORITY
SUPPORT
OPPOSITION
CONTRADICTION
TEMPORAL
CAUSAL
DEPENDENCY
SEMANTIC
PARTICIPANT
POLICY
WORKFLOW
```

A hyperedge has exactly one primary view in V1. Cross-view relationships are represented by shared member nodes and explicit linking metadata, not by assigning multiple ambiguous views to one edge.

### Provenance view

Answers: where did this come from, which source objects jointly establish its lineage, and what exact subject was observed?

### Authority view

Answers: which instruction/policy/source has governing authority over a claim, action, or effect?

### Support / opposition views

Represent evidence bundles for or against a hypothesis while preserving dependencies among evidence items.

### Contradiction view

Represents a scoped contradiction. A contradiction edge should include the conflicting propositions and the scope qualifiers needed to determine that the conflict is real.

### Temporal view

Represents validity, supersession, snapshot identity, sequence, and currentness relationships.

### Causal / dependency views

Represent many-to-many prerequisites, interventions, and consequences without pretending each prerequisite independently causes the result.

### Semantic view

Represents conceptual similarity. This view is advisory and may be model-derived.

### Participant view

Represents actors/models/tools/reviewers and their roles in a reasoning event.

### Policy view

Represents rules, permissions, prohibitions, exceptions, and governed effects.

## Deterministic state compiler

Before any neural model exists, Rezon V1 must compile structured input into a deterministic typed hypergraph.

Pipeline:

```text
source adapters
  -> canonical node identities
  -> explicit relation extraction
  -> deterministic derived relations
  -> view-separated incidence families
  -> canonical serialization
  -> content digest + derivation receipt
```

The compiler is responsible for exact identities and relation classes. It may call external parsers, but every accepted result must become explicit Rezon state with provenance.

## Canonical serialization

The same logically identical deterministic reasoning state should serialize identically inside one schema version.

Canonicalization requirements:

1. stable ordering by canonical identifiers,
2. normalized timestamp representation,
3. normalized member ordering for unordered hyperedges,
4. explicit schema version,
5. explicit construction class,
6. no hidden defaults that alter semantics,
7. SHA-256 digest of canonical bytes.

This digest identifies a Rezon reasoning-state snapshot, not the truth of its contents.

## HCAE-derived learned layer

The learned layer consumes deterministic view-separated incidence families and optional node/hyperedge features.

Baseline mathematical form for each view `v`:

```text
G_v = Dv_v^(-1/2) H_v W_v De_v^(-1) H_v^T Dv_v^(-1/2)
```

A V1 experimental encoder may start with a simple view-specific projection followed by fused hypergraph-convolution blocks.

The design must preserve view identity long enough to support attribution and ablation. Blind concatenation is allowed only as an explicit baseline.

Learned outputs must include:

```text
model_id
model_digest
training_corpus_digest
input_state_digest
output_type
output_payload
view_attribution
created_at
```

Initial output types:

```text
CASE_EMBEDDING
NODE_EMBEDDING
ANOMALY_SCORE
SIMILAR_CASES
MISSING_RELATION_SUGGESTION
STATE_CLASSIFICATION
```

None is authoritative by default.

## Hybrid reasoning operator layer

Rezon should support multiple explicit operator classes rather than one monolithic "reason" function.

Initial operator families:

```text
EXACT_LOOKUP
GRAPH_QUERY
HYPERGRAPH_NEIGHBORHOOD
RULE_EVALUATION
CONTRADICTION_CHECK
TEMPORAL_CURRENTNESS_CHECK
NUMERIC_CALCULATION
SEMANTIC_RETRIEVAL
STRUCTURAL_RETRIEVAL
MODEL_CLASSIFICATION
MODEL_ANOMALY
EXTERNAL_TOOL
```

An execution plan records which operator is chosen and why. Results become new nodes/hyperedges only through an explicit state-transition step with provenance.

## Hierarchical control

Inspired by hierarchical reasoning work such as HRM, Rezon should separate slower problem-level control from faster local operators.

V1 conceptual split:

```text
Strategic controller
  - defines goal
  - selects required evidence classes
  - chooses operator sequence
  - evaluates stop/continue/escalate

Tactical operators
  - retrieve
  - query
  - calculate
  - validate
  - compare
  - classify
  - call tools
```

The strategic controller may be deterministic, model-assisted, or hybrid. Its state transitions must still be recorded explicitly.

## Contradiction semantics

Rezon must not treat `A != B` as a contradiction without scope.

A contradiction check evaluates at least:

```text
subject identity
predicate identity
valid time
branch/version/snapshot
scope
authority class
modality/uncertainty
```

A stale value and a current value may represent supersession rather than contradiction. Two values from different branches may represent divergence. Two uncertain hypotheses may represent alternatives.

The output should therefore classify the relationship, for example:

```text
CONTRADICTION_CONFIRMED
SUPERSESSION
PARALLEL_SCOPE
UNRESOLVED_SCOPE
ALTERNATIVE_HYPOTHESES
NO_CONFLICT
```

## Retrieval design

Rezon should support at least four retrieval modes:

1. exact identity retrieval,
2. semantic retrieval,
3. structural/hypergraph retrieval,
4. hierarchical document navigation.

The system should be able to compose them. Example:

```text
semantic search finds candidate concept
-> hierarchical navigator locates exact section
-> provenance view finds exact source lineage
-> authority/currentness check determines whether it may govern
-> structural retrieval finds analogous resolved cases
```

Retrieval results remain references to evidence; retrieval rank is not authority.

## Provenance and receipts

Every state transition needs a receipt containing:

```text
receipt_id
input_state_digest
operation
operator_version
parameters_digest
source_refs[]
output_state_digest | output_ref
timestamp
actor/tool identity
```

Learned operations additionally include model and corpus digests.

A Rezon result that cannot identify its input snapshot or generating operator is unqualified.

## Failure behavior

Fail closed on:

- unknown required node identity,
- missing source provenance for deterministic claims,
- unknown construction class,
- invalid cross-view coercion,
- authority decision based solely on learned/heuristic relations,
- model output without model/corpus/input digests,
- non-reproducible deterministic state serialization,
- contradiction claims with unresolved scope when scope is required.

Learned model failure should degrade to deterministic reasoning where possible rather than block exact queries.

## First executable proof

The first implementation should use a synthetic corpus, not production project state.

Views:

```text
PROVENANCE
AUTHORITY
TEMPORAL
SUPPORT
SEMANTIC
```

Synthetic case families:

1. complete qualified decision,
2. missing provenance,
3. stale source incorrectly semantically matched,
4. authority conflict,
5. legitimate supersession,
6. unresolved contradiction,
7. structurally analogous case with different vocabulary.

Required baselines:

```text
semantic embedding retrieval only
pairwise graph representation
flattened feature vector
explicit deterministic hypergraph query
HCAE-derived multi-view representation
```

Required measurements:

- structural-analogy retrieval accuracy,
- stale/current discrimination,
- missing-relation detection precision/recall,
- anomaly separation,
- cross-view ablation,
- deterministic digest reproducibility.

No model is selected as superior until the exact frozen evaluation set and metrics support that claim.

## Repository structure target

```text
rezon/
  README.md
  docs/
    research/
      HCAE_SEMANTIC_REAPPLICATION_V1.md
      EXTERNAL_REASONING_SYSTEMS_SURVEY_V1.md
    examples/
      MULTIVIEW_REASONING_CASE_V1.md
    superpowers/
      specs/
        2026-09-15-rezon-reasoning-foundation-v1-design.md
      plans/
        2026-09-15-rezon-reasoning-foundation-v1.md
  src/rezon/
    model.py
    canonical.py
    hypergraph.py
    compiler.py
    operators.py
    receipts.py
  tests/
    test_model.py
    test_canonical.py
    test_hypergraph.py
    test_compiler.py
    test_operators.py
    fixtures/
```

The `src/` and `tests/` paths above are implementation targets, not claims that the files already exist.

## Acceptance gates

### Design acceptance

- object model is explicit,
- views are semantically distinct,
- HCAE reapplication is source-grounded,
- learned/deterministic authority boundary is explicit,
- external inspirations and license risks are recorded.

### Compiler acceptance

- deterministic state round-trips,
- canonical digest is reproducible,
- invalid provenance/construction classes fail closed,
- view membership is explicit and inspectable.

### Learned-layer acceptance

- exact model/corpus/input digests recorded,
- held-out cases used,
- baselines run on the same frozen subjects,
- view ablation performed,
- no authority classification inferred from semantic similarity alone.

### System acceptance

- one reasoning case can be compiled, queried, structurally retrieved, checked for contradictions/currentness, and fully traced back to source relations and operation receipts.

## Design boundary

Rezon V1 should be ambitious about representation and conservative about authority.

The system is allowed to say:

> "This state resembles prior authority-conflict cases and appears to be missing a provenance relation."

It is not allowed to turn that into:

> "Therefore the claim is false" or "therefore this action is authorized."

Those conclusions require explicit deterministic evidence and policy.