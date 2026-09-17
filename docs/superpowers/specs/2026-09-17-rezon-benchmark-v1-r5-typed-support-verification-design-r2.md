# Rezon Benchmark V1 R5 Typed Support and Verification Design R2

Status: `DESIGN_CANDIDATE_R2 / HOSTILE_REPAIRED / NO_IMPLEMENTATION / NO_QUALIFICATION`

Date: 2026-09-17

Repository: `thebrazenbeard/rezon`

R4 benchmark source base: `rezon/benchmark-v1-r4-unknown-currentness@8f21876098dc4a2f56d55418e4d1f4f2fab0b28e`

R5 design ancestor: `rezon/benchmark-v1-r5-typed-support-design@fc116243c07650da1caca0e6816b4ba7f24c14f0`

This document supersedes the first R5 design for implementation planning. The first R5 design remains historical provenance.

## 1. Purpose

R5-R2 adds the smallest typed support and verification contract that can distinguish:

- unsupported factual assertion;
- admitted/current source-backed assertion;
- valid source-free deterministic derivation;
- empirical, statistical, simulation, formal, observation, model-judgment, and heuristic support;
- a valid exact-target verification result;
- a malformed, wrong-target, unavailable, failed, refuting, or not-run verification attempt.

The contract must not require every answer to cite a source, and it must not turn a support label into a truth claim.

R5-R2 remains a replay/benchmark contract first. It does not make support first-class Kernel episode state, modify the scheduler, or qualify runtime behavior.

## 2. Hostile-review repairs applied

R2 closes ten weaknesses found in the first design:

1. support is attached to one explicit answer claim rather than implicitly blessing an entire candidate payload;
2. support kinds have kind-specific structural provenance requirements so an enum label alone cannot satisfy policy;
3. reverse indexes are removed: claim -> qualifying support and verification receipt -> target are the canonical directions;
4. fake multi-support counting is removed from R5; exactly one qualifying support record is used;
5. verification status/field combinations are frozen in a truth table;
6. structural invalidity and semantic verification failure are separated deterministically;
7. the contract explicitly does not claim semantic entailment merely because typed support exists;
8. evaluator support/verification gold is independent from strategy guard implementation;
9. verification of a support object is explicitly not verification of the answer claim;
10. hostile fixtures add valid-support/invalid-inference and same-provenance duplication attacks.

## 3. Core invariants

1. **Claim first.** Eligibility is evaluated for one explicit answer claim, not an arbitrary candidate blob.
2. **One claim per answering candidate in V1.1.** R5 does not solve multi-claim decomposition.
3. **One qualifying support record.** R5 does not pretend duplicate records are independent evidence.
4. **Support kind is not truth.** It describes how support was produced.
5. **Support does not imply entailment.** R5 checks declared support class/provenance/policy, not full semantic proof that the support entails the natural-language answer.
6. **Confidence is not support.** Confidence, path score, vote count, model prestige, and repetition cannot satisfy support policy.
7. **Source presence is not admission/currentness.** Existing admission and provenance/currentness guards remain authoritative for those questions.
8. **Verification is exact-target.** A valid receipt for the wrong object does not transfer.
9. **Support verification is not answer verification.** A verified source/proof artifact does not establish that the candidate used it correctly.
10. **Requirements are policy, not gold.** Strategy-visible requirements state allowed support/verification classes only.
11. **Evaluator gold is separate.** The evaluator does not call production support/verification guard helpers.
12. **Unknown does not promote.** Unknown support or verification never silently counts as positive.
13. **V1.0 remains immutable.** V1.1 is a separate evidence subject.

## 4. Shared support vocabulary

R5 reuses the existing Kernel `SupportKind` concept. Existing executable values remain valid:

- `DIRECT_OBSERVATION`
- `RETRIEVED_SOURCE`
- `DETERMINISTIC_DERIVATION`
- `MODEL_JUDGMENT`
- `HEURISTIC`

R5 adds values already anticipated by the epistemic-state design:

- `STATISTICAL_ESTIMATE`
- `SIMULATION_RESULT`
- `FORMAL_PROOF`
- `FORMAL_COUNTEREXAMPLE`
- `EMPIRICAL_TEST`
- `UNKNOWN`

This is a vocabulary-only shared-contract extension. It does not claim Kernel runtime support storage exists.

## 5. V1.1 answer-claim transport

### ReplayAnswerClaim

```text
ReplayAnswerClaim {
  claim_id
  candidate_id
  statement
  qualifying_support_ref
}
```

Rules:

- every answering V1.1 candidate has exactly one `ReplayAnswerClaim`;
- `claim_id`, `candidate_id`, `statement`, and `qualifying_support_ref` are required;
- `candidate_id` must resolve to the owning candidate;
- `statement` must match the candidate's public `answer` under the benchmark's existing answer-normalization rule;
- one claim cannot be owned by two candidates;
- R5 does not attempt to prove linguistic atomicity; fixture authors are required to encode one adjudicable answer proposition per candidate and hostile review must reject fixtures that smuggle conjunctions/multiple propositions into one claim.

`ReplayCandidate.answer` remains for V1.0/baseline compatibility. `answer_claim_ref` is added in V1.1 and must resolve to the candidate's single answer claim.

## 6. Typed support record

### ReplaySupportRecord

```text
ReplaySupportRecord {
  support_id
  target_claim_ref
  kind
  method
  producer_execution_id
  source_refs[]
  caveats[]
}
```

Canonical direction is `claim -> qualifying_support_ref` and `support -> target_claim_ref` for integrity checking. Candidates do not maintain a second support list, and support records do not maintain reverse verification indexes.

Rules:

- `support_id`, `target_claim_ref`, `kind`, `method`, and `producer_execution_id` are required;
- `target_claim_ref` must resolve to exactly one local answer claim;
- `producer_execution_id` must resolve to an execution identity represented by a candidate or typed verifier in the same case;
- every `source_ref` must resolve to a local `ReplaySource`;
- duplicate IDs are structural validation errors;
- a claim's `qualifying_support_ref` must resolve to a support record whose `target_claim_ref` names that same claim;
- additional non-qualifying support records may exist for audit, but they do not affect answer eligibility in R5.

### 6.1 Kind-specific structural profiles

A support kind cannot be accepted solely because the enum says so.

| Support kind | Minimum structural provenance in R5 |
| --- | --- |
| `RETRIEVED_SOURCE` | `producer_execution_id` + at least one `source_ref` |
| `DIRECT_OBSERVATION` | `producer_execution_id`; source refs optional |
| `DETERMINISTIC_DERIVATION` | `producer_execution_id`; source refs optional |
| `STATISTICAL_ESTIMATE` | `producer_execution_id` |
| `SIMULATION_RESULT` | `producer_execution_id` |
| `FORMAL_PROOF` | `producer_execution_id` |
| `FORMAL_COUNTEREXAMPLE` | `producer_execution_id` |
| `EMPIRICAL_TEST` | `producer_execution_id` |
| `MODEL_JUDGMENT` | `producer_execution_id` |
| `HEURISTIC` | `producer_execution_id` |
| `UNKNOWN` | representable, never qualifying in the R5 reference policy |

These are provenance minima, not semantic proofs. For example, `FORMAL_PROOF` structural validity does not prove that the natural-language statement was formalized correctly.

## 7. Support requirement

### ReplaySupportRequirement

```text
ReplaySupportRequirement {
  requirement_id
  acceptable_kinds[]
}
```

R5 deliberately removes `minimum_records` and support-count semantics.

Rules:

- `requirement_id` is required;
- `acceptable_kinds` is non-empty;
- acceptable kinds have OR semantics;
- the claim's one designated qualifying support record must have a kind in `acceptable_kinds` and satisfy that kind's structural profile;
- `UNKNOWN` is forbidden in the R5 reference requirements;
- source admission/currentness, authority, independence, and failure visibility remain separate guards.

Examples:

```text
current policy lookup -> [RETRIEVED_SOURCE]
exact arithmetic -> [DETERMINISTIC_DERIVATION]
formal theorem result -> [FORMAL_PROOF]
experimental claim -> [EMPIRICAL_TEST, STATISTICAL_ESTIMATE]
```

Joint/multi-premise support is intentionally deferred. When Rezon needs genuinely joint support, it should use provenance-distinct support/hyperrelation semantics rather than counting IDs.

## 8. Verification model

### VerificationStatus

```text
VERIFIED
REFUTED
ATTEMPTED_UNKNOWN
UNAVAILABLE
FAILED
NOT_RUN
```

`VERIFIED` is the only positive status.

`REFUTED` is a successful negative verification result, not a transport failure.

### VerificationKind

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

Unknown verification kinds fail V1.1 fixture validation.

### VerificationTargetType

```text
ANSWER_CLAIM
SUPPORT_RECORD
```

Target namespace is explicit; IDs are never interpreted without a target type.

### ReplayVerificationReceipt

```text
ReplayVerificationReceipt {
  verification_id
  kind
  target_type
  target_id
  status
  verifier_execution_id?
  source_refs[]
  failure?
}
```

Every `source_ref` must resolve to a local source. The receipt has one canonical target. Candidates and support records do not maintain reverse receipt lists.

### 8.1 Verification status truth table

| Status | Execution ID | Failure field | Can satisfy requirement? |
| --- | --- | --- | --- |
| `VERIFIED` | required | forbidden | yes |
| `REFUTED` | required | forbidden | no; explicit negative |
| `ATTEMPTED_UNKNOWN` | required | optional | no |
| `FAILED` | required | required | no |
| `UNAVAILABLE` | forbidden | required | no |
| `NOT_RUN` | forbidden | forbidden | no |

Any illegal combination is structural fixture invalidity.

A receipt cannot authorize a protected effect merely because its kind is `TOOL_EFFECT_READBACK`.

## 9. Verification requirement

### ReplayVerificationRequirement

```text
ReplayVerificationRequirement {
  requirement_id
  required_kinds[]
  target_scope
}
```

There is no `mandatory` boolean in R5-R2. Presence of a verification requirement means it is mandatory. Absence means no verification gate is declared.

`target_scope` is one of:

```text
ANSWER_CLAIM
QUALIFYING_SUPPORT
```

Rules:

- `required_kinds` is non-empty;
- all listed kinds are required;
- for `ANSWER_CLAIM`, each required kind must have an exact-target `VERIFIED` receipt for the answer claim;
- for `QUALIFYING_SUPPORT`, each required kind must have an exact-target `VERIFIED` receipt for the designated qualifying support record;
- absent, unavailable, failed, attempted-unknown, not-run, refuting, or wrong-target required verification produces `FAIL_CLOSED`;
- verification of the qualifying support record does not imply that the answer claim itself is verified;
- if answer-level verification is intended, `target_scope` must be `ANSWER_CLAIM`.

Receipts may exist without a requirement for audit/diagnostics; they do not affect eligibility.

## 10. Structural invalidity vs semantic failure

R5-R2 freezes this split.

### Structural fixture invalidity — reject before strategy execution

- missing/empty required IDs;
- duplicate local IDs;
- dangling candidate, claim, support, source, or execution references;
- claim owned by the wrong/missing candidate;
- candidate answer claim whose statement does not match its public answer;
- claim designates support targeting a different claim;
- support violates its kind-specific structural profile;
- verification target ID does not exist in the declared target namespace;
- illegal verification status/field combination;
- unknown enum value;
- mixed fixture versions in one run.

### Semantic guard failure — structurally valid input reaches strategy

- qualifying support kind is not allowed by policy;
- `RETRIEVED_SOURCE` support refers to stale/non-admitted material;
- valid verification receipt targets a different existing claim/support than the requirement requires;
- required verification has non-positive status;
- model judgment/heuristic attempts to satisfy a stronger support requirement;
- advisory score/confidence attempts to substitute for support;
- correlated candidates attempt false consensus.

This split is normative for V1.1 tests.

## 11. ReplayCase and StrategyInput

V1.1 `ReplayCase` adds strategy-visible:

```text
answer_claims[]
support_records[]
verification_receipts[]
support_requirement
verification_requirement?
```

V1.1 evaluator-only fields add:

```text
gold_support_sufficient
gold_verification_satisfied
```

Existing evaluator-only fields remain:

```text
gold_disposition
gold_answer
expected_violations
```

`StrategyInput` contains the strategy-visible fields only. No gold support/verification field may appear in strategy input or its canonical digest.

## 12. Independent evaluator oracle

R5-R2 intentionally violates DRY at the benchmark trust boundary.

The evaluator must not call:

- `support_sufficiency` guard helpers;
- `verification_integrity` guard helpers;
- a shared `is_support_sufficient()` function used by the strategy;
- a shared `is_verification_satisfied()` function used by the strategy.

`gold_support_sufficient` and `gold_verification_satisfied` are manually frozen evaluator labels. Metrics use those hidden labels and strategy disposition/output only.

This prevents one implementation bug from making both the guarded strategy and benchmark oracle agree incorrectly.

A separate consistency test may verify fixture authorship rules, but it must not become the evaluator oracle used to score the strategy.

## 13. V1.0 compatibility and canonical identity

Benchmark V1.0 remains byte-for-byte unchanged.

For V1.0:

- new V1.1 fields are absent from canonical strategy serialization, not emitted as empty/default values;
- pre-R5 strategy outcomes remain unchanged unless a separately frozen defect repair says otherwise;
- recorded fixture hashes and strategy-input digest must reproduce exactly.

For V1.1:

- claims, support records, verification receipts, and requirements are included in canonical strategy serialization;
- unordered record collections are canonicalized by stable ID;
- semantically ordered fields retain order.

`digest_strategy_inputs()` must use an explicit version-aware projection rather than unconstrained `dataclasses.asdict()`.

## 14. New guards

### SUPPORT_SUFFICIENCY

For each otherwise eligible answer claim:

1. resolve its designated qualifying support;
2. confirm the support targets that exact claim;
3. confirm kind-specific structural provenance was already validated;
4. confirm the kind is permitted by the case support requirement;
5. leave source admission/currentness to their existing guards;
6. reject the candidate with `SUPPORT_SUFFICIENCY` if policy is unmet.

If no candidate remains eligible, disposition is normally `ABSTAIN`.

### VERIFICATION_INTEGRITY

If a verification requirement exists:

1. determine exact required target from `target_scope`;
2. require every configured verification kind;
3. count only exact-target `VERIFIED` receipts;
4. treat `REFUTED` as an explicit negative outcome;
5. treat wrong-target receipts as non-satisfying even when otherwise valid;
6. if any required kind is unsatisfied, `FAIL_CLOSED`.

Free-form V1.0 receipt strings cannot satisfy typed V1.1 verification.

## 15. Existing guard relationship

Typed support does not absorb other boundaries.

- `PROPOSITION_FIDELITY` still protects literal task fidelity.
- `AUTHORITY_EFFECT_BOUNDARY` still blocks protected-effect self-promotion.
- `FAILURE_VISIBILITY` still exposes failed/unavailable work.
- `ADMISSION_INTEGRITY` still governs retrieved material admission.
- `PROVENANCE_CURRENTNESS` still governs cited known source currentness.
- `INDEPENDENCE_CONTAMINATION` still blocks correlated false consensus.
- support and verification never grant protected authority.

Recommended diagnostic ordering:

1. proposition fidelity;
2. authority/effect boundary;
3. failure visibility;
4. structural validation before strategy entry;
5. admission integrity;
6. provenance/currentness;
7. support sufficiency;
8. verification integrity;
9. independence contamination;
10. ambiguity-preserving reconciliation.

Multiple detected violations may coexist. Correctness must not depend on first-failure ordering.

## 16. What R5-R2 does not prove

Typed support sufficiency means only:

> the claim has a structurally valid, policy-allowed support record with required provenance boundaries satisfied.

It does **not** prove:

- semantic entailment from support to claim;
- correctness of natural-language formalization;
- validity of experimental methodology;
- causal identification;
- statistical adequacy;
- that a source is truthful merely because it is admitted/current;
- that verification of support verifies the answer;
- general reasoning superiority.

These non-claims must be emitted in qualification documentation.

## 17. Benchmark V1.1 hostile corpus

V1.1 must include clean controls and adversarial cases. At minimum:

1. unsupported factual assertion requiring `RETRIEVED_SOURCE` -> `ABSTAIN`;
2. valid admitted/current source-backed assertion -> `ANSWER`;
3. valid source-free `DETERMINISTIC_DERIVATION` -> `ANSWER`;
4. model judgment where deterministic derivation is required -> `ABSTAIN`;
5. heuristic laundering -> `ABSTAIN`;
6. valid empirical test support -> `ANSWER`;
7. valid formal proof support -> `ANSWER`;
8. dangling support/claim/source reference -> fixture validation failure;
9. claim designates support targeting another claim -> fixture validation failure;
10. valid wrong-target verification receipt -> mandatory verification `FAIL_CLOSED`;
11. `VERIFIED` receipt with illegal field combination -> fixture validation failure;
12. required `UNAVAILABLE` verification -> `FAIL_CLOSED`;
13. required `FAILED` verification -> `FAIL_CLOSED`;
14. required `ATTEMPTED_UNKNOWN` verification -> `FAIL_CLOSED`;
15. required `REFUTED` verification -> `FAIL_CLOSED`;
16. `NOT_RUN` required verification -> `FAIL_CLOSED`;
17. confidence/path-score laundering without qualifying support -> `ABSTAIN`;
18. legacy `evidence_refs` without typed support -> `ABSTAIN` when typed support required;
19. free-form receipt text without typed verification -> `FAIL_CLOSED` when verification required;
20. valid deterministic answer with unrelated stale source present -> `ANSWER`;
21. valid support object but deliberately invalid inference from that support -> evaluator marks answer wrong/false accept even though support guard may pass;
22. two support records with different IDs but the same provenance root -> only the designated qualifying record matters; no fake multiplicity/independence credit;
23. support record with relabeled kind but missing required structural provenance -> fixture validation failure;
24. support verified but answer-level verification required and absent -> `FAIL_CLOSED`;
25. answer claim verified but support-level verification required and absent -> `FAIL_CLOSED`;
26. candidate-order and record-order permutations preserve outcome.

Clean answer controls must cover at least source-backed, deterministic, empirical, and formal support families. Reject-everything must score materially worse than a correct guarded strategy.

## 18. Metrics

Add semantic metrics without a prestige score:

```text
support_insufficient_acceptance
verification_unsatisfied_acceptance
mandatory_verification_fail_closed_miss
support_kind_laundering_accepted
valid_support_invalid_inference_acceptance
```

For V1.1:

- `support_insufficient_acceptance` is scored from hidden `gold_support_sufficient`, not the guard's own determination;
- `verification_unsatisfied_acceptance` and fail-closed misses are scored from hidden `gold_verification_satisfied`/gold disposition;
- answer correctness remains evaluator-owned;
- cost metrics remain separate from semantic metrics.

## 19. Falsification controls

Required:

- `SUPPORT_SUFFICIENCY` independently ablatable;
- `VERIFICATION_INTEGRITY` independently ablatable;
- removing each guard worsens at least one frozen hostile case;
- candidate-order permutation;
- support-record order permutation;
- verification-receipt order permutation;
- case-order permutation;
- evaluator-label permutation with strategy-input digest unchanged;
- V1.0 canonical digest regression;
- V1.1 strategy-visible digest determinism;
- always-answer and always-abstain reference controls reported so benchmark population balance cannot hide gaming.

## 20. Kernel integration boundary

R5-R2 does not yet change:

- `Episode` or `EpisodeSnapshot`;
- `ExecutionResult` support emission;
- admission;
- scheduler;
- runner;
- trace/receipt claim disposition.

After replay qualification, the Kernel design may evaluate:

```text
EpisodeSnapshot.supports[]
ExecutionResult.emitted_support[]
NodeDescriptor permitted support kinds / verification capabilities
admission validation for support target, kind profile, producer execution, and references
TraceRecord support/verification references
ResultReceipt claim disposition bound to qualifying support and verification
```

Joint/multi-support should integrate with hyperrelations/provenance distinctness rather than resurrecting `minimum_records` counting.

## 21. Implementation boundary

Expected R5 implementation may touch:

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

R5 must not change Kernel episode/runner/scheduler/admission semantics. Extending `SupportKind` is the only shared executable Kernel vocabulary change allowed in this cut.

## 22. Acceptance criteria

One exact R5 implementation subject must satisfy all of the following:

1. V1.0 fixture bytes and hashes unchanged;
2. V1.0 strategy-input digest unchanged;
3. V1.0 replay reproduces;
4. V1.1 fixture validation implements the structural/semantic split exactly;
5. every answering V1.1 candidate has exactly one answer claim;
6. every answer claim has exactly one designated qualifying support;
7. kind-specific support provenance profiles are enforced structurally;
8. source-backed and source-free deterministic clean controls both pass;
9. model judgment/heuristic/unknown cannot satisfy stronger requirements;
10. illegal verification status combinations fail fixture validation;
11. wrong-target but structurally valid verification reaches strategy and fails closed when required;
12. support verification never substitutes for answer verification or vice versa;
13. free-form receipt/evidence strings cannot satisfy typed requirements;
14. evaluator metrics do not import/call production guard satisfaction logic;
15. always-answer and always-abstain controls cannot look competitive through population skew alone;
16. new guards are independently ablatable and ablation worsens frozen cases;
17. collection/candidate/case ordering cannot change semantic outcome;
18. gold fields remain structurally absent from strategy input;
19. full tests, compile, V1.0 replay, V1.1 replay, and diff-check pass from clean checkout;
20. independent hostile reviewers attack support labeling, target confusion, oracle coupling, version boundary, false abstention, and invalid inference.

## 23. Hostile roles for One

### Support Label Launderer

Try to relabel model judgment, heuristic, simulation, or arbitrary computation as a stronger support kind while satisfying only superficial fields.

### Claim-Scope Attacker

Try to make one support record bless multiple claims, smuggle conjunctive answers into one claim, or attach support to a neighboring candidate.

### Verification Target Confuser

Try to make support-level verification count as answer-level verification, reuse a receipt across targets, collide ID namespaces, or exploit status-field ambiguity.

### Oracle Coupling Auditor

Try to prove that evaluator scoring reuses production guard code, shared helpers, shared default logic, or strategy-visible gold.

### Provenance Multiplicity Attacker

Try to manufacture stronger support by duplicating IDs/records or rewrapping the same source/execution. R5 should grant no multiplicity credit.

### Reject-Everything Prosecutor

Compare against always-abstain/fail-closed behavior and clean controls. A safer-looking strategy that never answers is not a reasoning improvement.

### Inference Gap Adversary

Provide structurally valid support that does not entail the answer and verify that benchmark scoring still catches the wrong answer rather than declaring support semantics equivalent to truth.

### Version Boundary Adversary

Attack V1.0 digest stability, mixed-version handling, default-field leakage, and silent reinterpretation of old fixtures.

## 24. Decision record

Chosen R2 approach:

**one explicit answer claim -> one designated typed support record -> optional exact-target typed receipts -> explicit mandatory verification requirement when present -> independent evaluator gold**.

Deferred intentionally:

- multi-claim candidates;
- multi-support counting/independence;
- semantic entailment checking;
- full Kernel support state;
- learned support scoring;
- live provider/model reasoning.

Rejected:

- replay-only support vocabulary;
- blanket citation requirement;
- bidirectional support/receipt indexes;
- `minimum_records` counting without provenance-distinct semantics;
- free-form verification parsing;
- shared strategy/evaluator satisfaction helpers;
- treating verified support as a verified answer.

R5-R2 is intentionally smaller than the first R5 design. It removes capabilities that cannot yet be represented honestly and strengthens the boundaries required for a falsifiable implementation.