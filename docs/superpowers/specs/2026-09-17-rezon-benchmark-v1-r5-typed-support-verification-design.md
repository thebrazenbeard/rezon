# Rezon Benchmark V1 R5 Typed Support and Verification Design

Status: `DESIGN_CANDIDATE / NO_IMPLEMENTATION / NO_QUALIFICATION`

Date: 2026-09-17

Repository: `thebrazenbeard/rezon`

Design base: `rezon/benchmark-v1-r4-unknown-currentness@8f21876098dc4a2f56d55418e4d1f4f2fab0b28e`

## Purpose

R5 adds a typed support and verification contract to Benchmark V1 so Rezon can distinguish:

- an unsupported factual assertion;
- a source-backed factual assertion;
- a deterministic calculation or derivation that legitimately needs no external source;
- an empirical or simulation result;
- a formal proof or formal counterexample;
- a model judgment or heuristic that must not be promoted into stronger evidence merely because confidence is high;
- a valid verification receipt;
- a malformed, unavailable, wrong-target, or otherwise insufficient verification attempt.

The objective is not to make every answer cite a source. The objective is to make the required support class explicit and machine-checkable.

R5 is a benchmark/replay contract extension first. It does not yet modify Kernel episode storage, node execution, admission, or runtime scheduling. If the contract survives replay qualification, the same vocabulary can then be integrated into Kernel without inventing a second epistemic ontology.

## Architectural decision

Use one shared support vocabulary, with replay-specific transport records and task-visible requirements.

R5 does **not** create a replay-only evidence ontology. It reuses the existing Kernel `SupportKind` concept and extends it only where the current executable enum is narrower than the frozen epistemic-state design.

The current executable Kernel values remain valid:

- `DIRECT_OBSERVATION`
- `RETRIEVED_SOURCE`
- `DETERMINISTIC_DERIVATION`
- `MODEL_JUDGMENT`
- `HEURISTIC`

R5 adds the missing support classes already anticipated by the design contract:

- `STATISTICAL_ESTIMATE`
- `SIMULATION_RESULT`
- `FORMAL_PROOF`
- `FORMAL_COUNTEREXAMPLE`
- `EMPIRICAL_TEST`
- `UNKNOWN`

R5 does not rename `RETRIEVED_SOURCE` to `SOURCE_ATTESTATION` in executable code. The design documents use both concepts historically; the R5 implementation preserves the existing enum value to avoid a needless compatibility migration. A future version may introduce an alias or versioned rename if that improves the public API.

## Design invariants

1. **Support kind is not truth.** A typed support record says how an answer is supported, not that the answer is correct.
2. **Confidence is not support.** Confidence, path score, model prestige, repetition, and consensus cannot satisfy a support requirement by themselves.
3. **Source presence is not source admission.** Source-backed support remains subject to the existing admission and currentness guards.
4. **No blanket source requirement.** A deterministic calculation, formal derivation, empirical test, simulation, or other qualified non-source support may satisfy an answer requirement without an external source when the task contract allows it.
5. **Verification is target-bound.** A verification receipt without an exact target cannot satisfy a verification requirement.
6. **Verification is status-bound.** `VERIFIED` is different from `UNKNOWN`, `UNAVAILABLE`, `FAILED`, `REFUTED`, and `NOT_RUN`.
7. **Mandatory verification fails closed when unavailable or semantically invalid.** Optional verification may leave the answer unresolved or unsupported according to the task requirement.
8. **Model judgment cannot self-promote.** `MODEL_JUDGMENT` and `HEURISTIC` are never implicitly equivalent to `DIRECT_OBSERVATION`, `RETRIEVED_SOURCE`, `DETERMINISTIC_DERIVATION`, `FORMAL_PROOF`, `EMPIRICAL_TEST`, or other stronger support classes.
9. **Replay gold remains evaluator-only.** Support and verification requirements are strategy-visible policy, not hidden gold labels.
10. **Benchmark V1.0 stays immutable.** R5 adds a V1.1 typed-support corpus instead of rewriting the frozen V1.0/R2/R3/R4 evidence population.

## Data model

### SupportKind

R5 uses the shared Kernel support vocabulary described above.

### ReplaySupportRecord

A support record is candidate-scoped and strategy-visible.

```text
ReplaySupportRecord {
  support_id
  candidate_id
  kind
  method
  source_refs[]
  evidence_refs[]
  execution_refs[]
  verification_receipt_refs[]
  caveats[]
}
```

Rules:

- `support_id`, `candidate_id`, `kind`, and `method` are required.
- `candidate_id` must name a candidate in the same replay case.
- all referenced sources, evidence objects, executions, and verification receipts must either resolve inside the case transport or be explicitly represented as external opaque references under a future versioned contract; R5 V1.1 does not silently accept dangling local references;
- `UNKNOWN` is representable but never satisfies a support requirement unless the requirement explicitly permits `UNKNOWN`, which the R5 reference corpus will not do;
- a `MODEL_JUDGMENT` or `HEURISTIC` record remains advisory even if it contains many references.

### ReplaySupportRequirement

A support requirement says what classes of support are acceptable for a final answer.

```text
ReplaySupportRequirement {
  requirement_id
  acceptable_kinds[]
  minimum_records
  require_distinct_support_ids
}
```

R5 defaults:

- `minimum_records >= 1` when a requirement exists;
- `acceptable_kinds` must be non-empty;
- `require_distinct_support_ids = true` prevents one support object from being counted multiple times;
- multiple accepted kinds mean logical OR across kinds unless `minimum_records > 1`, in which case the candidate must satisfy the count with distinct qualifying support records.

The requirement does not duplicate source currentness, source admission, independence, or authority policy. Those remain separate guards.

Examples:

```text
current policy lookup:
  acceptable_kinds = [RETRIEVED_SOURCE]
  minimum_records = 1

exact arithmetic:
  acceptable_kinds = [DETERMINISTIC_DERIVATION]
  minimum_records = 1

formal theorem claim:
  acceptable_kinds = [FORMAL_PROOF]
  minimum_records = 1

experimental claim:
  acceptable_kinds = [EMPIRICAL_TEST, STATISTICAL_ESTIMATE]
  minimum_records = 1
```

### VerificationStatus

```text
VERIFIED
REFUTED
UNKNOWN
UNAVAILABLE
FAILED
NOT_RUN
```

`VERIFIED` is the only positive status. `REFUTED` is an explicit negative result, not a failed verification transport. `UNKNOWN`, `UNAVAILABLE`, `FAILED`, and `NOT_RUN` are all non-positive and remain distinguishable.

### VerificationKind

R5 introduces a compact typed verification vocabulary:

```text
PROVENANCE_BINDING
CURRENTNESS_CHECK
DETERMINISTIC_RECOMPUTATION
FORMAL_VERIFICATION
EMPIRICAL_REPLICATION
TOOL_EFFECT_READBACK
CONTRADICTION_CHECK
SCHEMA_VALIDATION
```

The vocabulary may be extended in future fixture versions, but R5 implementations fail closed on unknown enum values rather than silently treating them as valid verification.

### ReplayVerificationReceipt

```text
ReplayVerificationReceipt {
  verification_id
  kind
  target_ref
  status
  verifier_execution_id
  support_refs[]
  source_refs[]
  failure?
}
```

Rules:

- `verification_id`, `kind`, `target_ref`, `status`, and `verifier_execution_id` are required;
- `target_ref` must name the candidate, support record, or other explicitly allowed local target identified by the corresponding requirement;
- `VERIFIED` requires a non-empty target and verifier execution identity;
- `REFUTED` is valid and causes the targeted positive requirement to fail;
- `UNAVAILABLE`, `FAILED`, `UNKNOWN`, and `NOT_RUN` cannot satisfy a mandatory verification requirement;
- free-form `receipt_claims` remain supported only for V1.0 backward compatibility and do not satisfy a V1.1 typed verification requirement.

### ReplayVerificationRequirement

```text
ReplayVerificationRequirement {
  requirement_id
  required_kinds[]
  target_scope
  minimum_verified
  mandatory
}
```

`target_scope` is one of:

```text
ANSWER_CANDIDATE
QUALIFYING_SUPPORT
```

Rules:

- `required_kinds` is non-empty;
- `minimum_verified >= 1`;
- a receipt counts only if its kind is required, its target matches `target_scope`, and its status is `VERIFIED`;
- if `mandatory = true`, an unavailable, malformed, wrong-target, failed, unknown, refuted, or absent required verification produces `FAIL_CLOSED`;
- if `mandatory = false`, missing positive verification prevents verification-dependent support from being considered sufficient but does not itself force `FAIL_CLOSED`.

## Replay transport changes

### ReplayCandidate

R5 V1.1 adds:

```text
support_refs[]
verification_receipt_refs[]
```

The candidate refers to typed records by ID rather than embedding them. Existing `source_refs`, `evidence_refs`, and `receipt_claims` remain for V1.0 compatibility and for provenance surfaces that are not themselves typed support.

### ReplayCase

R5 V1.1 adds strategy-visible fields:

```text
support_records[]
verification_receipts[]
support_requirement?
verification_requirement?
```

Gold fields remain evaluator-only:

```text
gold_disposition
gold_answer
expected_violations
```

### StrategyInput

V1.1 `StrategyInput` carries the same typed support and verification fields as the strategy-visible portion of `ReplayCase`.

No gold field is introduced into `StrategyInput`.

## Versioning and digest compatibility

Benchmark V1.0 evidence must remain reproducible.

R5 therefore makes strategy-input canonicalization fixture-version aware.

For `benchmark-v1.0`:

- canonical strategy serialization remains byte-for-byte equivalent to the pre-R5 V1.0 strategy-visible structure;
- V1.1 extension fields are omitted, not serialized as empty arrays or `null` values;
- the existing V1.0 strategy-input digest must remain unchanged under regression test.

For `benchmark-v1.1`:

- typed support records, verification receipts, support requirements, and verification requirements are included in canonical strategy serialization;
- ordering is deterministic by stable IDs where the transport semantics treat collections as sets;
- semantic sequence fields retain sequence order where order is meaningful.

`digest_strategy_inputs()` should stop relying directly on unconstrained `dataclasses.asdict()` for versioned public digest identity. It should call a version-aware canonical projection function.

## Guard changes

R5 adds two independently ablatable guards to `rezon_guarded`.

### SUPPORT_SUFFICIENCY

The guard evaluates only candidates that otherwise remain eligible.

For each candidate:

1. resolve the candidate's `support_refs`;
2. reject dangling, duplicate-as-counted, malformed, or candidate-mismatched support records;
3. filter support records to the case's `acceptable_kinds`;
4. require at least `minimum_records` distinct qualifying records;
5. for source-backed qualifying support, leave source admission/currentness enforcement to the existing guards rather than duplicating those policies;
6. if the requirement cannot be satisfied, reject the candidate with `SUPPORT_SUFFICIENCY` and normally produce `ABSTAIN` if no eligible answer remains.

A support record of kind `MODEL_JUDGMENT`, `HEURISTIC`, or `UNKNOWN` cannot satisfy a requirement for a stronger class.

### VERIFICATION_INTEGRITY

For each candidate subject to a verification requirement:

1. resolve candidate-referenced verification receipts;
2. reject malformed or dangling receipts;
3. require the configured verification kind(s);
4. validate the exact target scope;
5. count only `VERIFIED` receipts toward `minimum_verified`;
6. surface `REFUTED` distinctly from unavailable/failed/unknown;
7. when the requirement is mandatory and the requirement is not met, produce `FAIL_CLOSED` rather than `ABSTAIN`;
8. when the requirement is optional and unmet, the candidate cannot rely on the missing verification to satisfy support, but the transport failure alone does not force `FAIL_CLOSED`.

Free-form V1.0 receipt strings do not satisfy this guard.

## Guard ordering

Recommended R5 order:

1. proposition fidelity;
2. authority/effect boundary;
3. failure visibility;
4. admission integrity;
5. provenance/currentness;
6. support sufficiency;
7. verification integrity;
8. independence contamination;
9. answer reconciliation / ambiguity preservation.

This ordering is diagnostic rather than epistemically authoritative. Multiple violations may be retained in the outcome. The implementation should not make correctness depend on only the first failing guard.

## Disposition semantics

R5 keeps the existing three dispositions:

- `ANSWER`
- `ABSTAIN`
- `FAIL_CLOSED`

New mapping:

- insufficient or wrong support class -> `ABSTAIN` when no candidate remains eligible;
- malformed typed verification receipt -> `FAIL_CLOSED` if verification is mandatory, otherwise candidate rejection / `ABSTAIN`;
- required verification unavailable -> `FAIL_CLOSED`;
- required verification `REFUTED` -> `FAIL_CLOSED` for that candidate's proposed answer;
- optional verification absent/unknown/failed -> candidate may remain only if its support requirement does not depend on that verification;
- competing eligible answer tie -> preserve R3 behavior and `ABSTAIN`.

## Relationship to existing guards

Typed support does not absorb other trust boundaries.

- `ADMISSION_INTEGRITY` still decides whether referenced retrieved material was admitted.
- `PROVENANCE_CURRENTNESS` still decides whether cited known sources are explicitly current where currentness matters.
- `INDEPENDENCE_CONTAMINATION` still prevents correlated outputs from becoming false independent consensus.
- `FAILURE_VISIBILITY` still exposes unavailable/failed work.
- `AUTHORITY_EFFECT_BOUNDARY` still prevents reasoning outputs from self-promoting runtime/effect state.
- support and verification records cannot authorize protected effects.

A candidate can therefore have a valid `RETRIEVED_SOURCE` support record and still be rejected because the referenced source is stale or merely retrieved-only.

## Benchmark V1.1 hostile corpus

R5 introduces a new fixture version and does not rewrite V1.0.

The initial V1.1 population must include at least these classes:

1. **Unsupported factual assertion** — factual/current claim, no support records, requires `RETRIEVED_SOURCE`; must abstain.
2. **Valid source-backed assertion** — admitted/current source plus `RETRIEVED_SOURCE`; may answer.
3. **Valid deterministic derivation** — zero source refs, `DETERMINISTIC_DERIVATION`, deterministic method/execution; may answer.
4. **Wrong support class** — high-confidence `MODEL_JUDGMENT` where `DETERMINISTIC_DERIVATION` is required; must abstain.
5. **Heuristic laundering** — `HEURISTIC` presented as if it were empirical/formal support; must abstain.
6. **Valid empirical support** — `EMPIRICAL_TEST` satisfies an empirical requirement; may answer.
7. **Valid formal proof** — `FORMAL_PROOF` satisfies a formal requirement; may answer.
8. **Dangling support reference** — candidate names missing support ID; fail closed at fixture validation or candidate rejection according to transport location.
9. **Cross-candidate support theft** — candidate references support whose `candidate_id` names another candidate; must reject.
10. **Malformed VERIFIED receipt** — `VERIFIED` with empty/wrong target; mandatory verification -> fail closed.
11. **Wrong-target valid receipt** — syntactically valid receipt verifies a different candidate/support object; mandatory verification -> fail closed.
12. **Unavailable mandatory verifier** — mandatory verification receipt/status unavailable; fail closed.
13. **Refuted verification** — exact target receipt status `REFUTED`; fail closed for positive answer.
14. **Unknown/NOT_RUN verification** — cannot satisfy mandatory verification.
15. **Advisory-score laundering** — confidence/path score without typed qualifying support; must abstain.
16. **Valid source-free calculation with irrelevant stale source present** — deterministic support remains valid; stale unrelated source must not contaminate the calculation merely by existing in the case.

The V1.1 population should include clean answer controls in each major support family so reject-everything remains penalized.

## Metrics and evaluator changes

R5 extends metrics without creating a prestige score.

New semantic metrics:

```text
support_sufficiency_accepted
verification_integrity_accepted
mandatory_verification_fail_closed_miss
support_kind_laundering_accepted
```

Existing `unsupported_acceptance` remains but becomes grounded in typed support requirements for V1.1 rather than only evaluator violation labels.

Evaluator gold remains independent of strategy-visible support requirements. A case may expose that a source-backed answer is required without exposing whether the candidate actually satisfies that requirement.

## Ablation and falsification controls

`SUPPORT_SUFFICIENCY` and `VERIFICATION_INTEGRITY` must be individually ablatable.

Required controls:

- removing `SUPPORT_SUFFICIENCY` must expose at least one frozen unsupported/wrong-kind case;
- removing `VERIFICATION_INTEGRITY` must expose at least one frozen malformed/wrong-target mandatory-verification case;
- label permutation remains evaluator-side only;
- case-order permutation remains deterministic;
- add candidate-order permutations for V1.1 multi-candidate cases so support resolution cannot depend on tuple order;
- support-record and verification-receipt collection ordering must not change strategy outcome when IDs and semantics are unchanged.

## Kernel integration boundary

R5 does not yet make `Support` first-class runtime state.

The existing Kernel currently has:

- a `SupportKind` enum;
- a `Support` dataclass;
- propositions and relations stored in `Episode`;
- `ExecutionResult` with propositions/relations/failures/source refs;
- admission checks for emitted propositions and relations.

The existing `Support` object is not yet stored in `EpisodeSnapshot`, emitted by `ExecutionResult`, or validated by admission.

That is intentionally deferred.

After R5 replay qualification, the next Kernel design should evaluate:

```text
EpisodeSnapshot.supports[]
ExecutionResult.emitted_support[]
NodeDescriptor permitted support kinds / verification capabilities
admission validation for support ownership, references, producer execution, and semantic promotion
TraceRecord support/verification refs
ResultReceipt claim disposition tied to qualifying support and verification
```

Replay qualification must not be described as Kernel integration or runtime qualification.

## Backward compatibility

R5 must preserve:

- all existing Benchmark V1.0 fixtures byte-for-byte;
- all V1.0 evaluator gold;
- all pre-R5 strategy outcomes on the V1.0 corpus unless an independently documented pre-existing defect is intentionally fixed in a separately frozen regression;
- the V1.0 strategy-input digest;
- baseline strategy semantics;
- R3 ambiguity behavior;
- R4 unknown-currentness behavior.

V1.1 cases may use the new fields. V1.0 cases may not be silently reinterpreted as if they contained typed support requirements.

## Implementation shape

Expected implementation files after planning, subject to TDD:

```text
src/rezon/epistemics.py
src/rezon/replay.py
src/rezon/replay_strategies.py
src/rezon/replay_metrics.py
src/rezon/replay_experiments.py
scripts/run_benchmark_v1.py

tests/test_replay_contracts.py
tests/test_rezon_guarded_replay.py
tests/test_replay_metrics.py
tests/test_replay_experiments.py
tests/test_benchmark_v1_r5_support_verification.py
tests/fixtures/benchmark_v1_1_typed_support.json
```

R5 should avoid changes to Kernel `Episode`, runner, scheduler, and admission unless implementation proves a minimal shared enum import requires a narrowly scoped compatibility edit. Any broader Kernel change becomes a separate design subject.

## Acceptance criteria

R5 design/implementation is not accepted until all of the following are true on one exact subject:

1. V1.0 fixture bytes and their recorded digests remain unchanged.
2. The V1.0 strategy-input digest remains unchanged.
3. V1.0 reference replay remains reproducible.
4. V1.1 typed-support fixtures validate deterministically and fail closed on malformed references.
5. A source-backed factual answer can pass with valid admitted/current source support.
6. A source-free deterministic derivation can pass when deterministic support is the declared requirement.
7. `MODEL_JUDGMENT`, `HEURISTIC`, and `UNKNOWN` cannot satisfy stronger requirements.
8. Mandatory verification cannot be satisfied by free-form receipt strings.
9. Mandatory `UNAVAILABLE`, `FAILED`, `UNKNOWN`, `NOT_RUN`, `REFUTED`, malformed, or wrong-target verification does not answer; the required fail-closed semantics are preserved.
10. Both new guards are independently ablatable and their hostile cases worsen when removed.
11. Candidate/support/verification collection-order permutations do not change outcomes.
12. Gold fields remain structurally absent from strategy inputs.
13. Full repository tests, compile, reference V1.0 replay, V1.1 replay, and diff-check pass from a clean checkout.
14. Independent hostile review attacks support laundering, wrong-target verification, dangling references, old-version reinterpretation, and benchmark leakage.

## Non-goals

R5 does not:

- claim that typed support proves truth;
- require citations for every answer;
- infer support requirements from natural-language wording with an LLM;
- introduce live model/provider calls;
- add HCAE, HyPER, hyperbolic routing, or learned support scoring;
- make support a first-class Kernel runtime object yet;
- establish deployment, installation, activation, effect, or behavioral qualification;
- merge any branch;
- claim general reasoning superiority.

## Hostile review roles for this design

One may assign independent workers to these focused attacks:

### Support Laundering Adversary

Try to satisfy a strong requirement with model judgment, heuristic, duplicate support IDs, dangling refs, cross-candidate support, stale/retrieved-only sources, or high-confidence advisory signals.

### Verification Forgery Adversary

Try to produce `VERIFIED` without an exact target, with the wrong target, wrong kind, missing verifier execution, stale support, free-form receipt text, unavailable verifier, or a receipt copied from another candidate.

### Version Boundary Adversary

Try to change V1.0 strategy-input identity, reinterpret old fixtures using V1.1 defaults, leak new fields into old digests, or make mixed fixture versions silently comparable.

### Reject-Everything Prosecutor

Ensure typed support policy does not make guarded integration appear successful merely by abstaining/failing closed on everything. Attack clean controls in every support family.

### Support-Type Semantics Adversary

Challenge whether a declared support kind actually matches what the method established. A deterministic method should not be relabeled empirical; a simulation should not become observation; a proof receipt should not validate an incorrect natural-language formalization.

## Decision record

Chosen approach: **shared support vocabulary + replay-specific typed transport + explicit strategy-visible requirements, replay first, Kernel integration later**.

Rejected alternatives:

- replay-only support enums: rejected because they create semantic drift from Kernel;
- immediate full Kernel support integration: rejected because the runtime blast radius is too large while support semantics are still being qualified in replay;
- blanket source-reference requirement: rejected because it incorrectly rejects valid calculations, proofs, tests, simulations, and other non-source support classes;
- free-form receipt parsing: rejected because it cannot provide exact target/status semantics and is vulnerable to receipt laundering.

This design deliberately prefers semantic precision over a smaller patch because the observed R4 gaps are consequences of a missing abstraction, not two unrelated predicates.
