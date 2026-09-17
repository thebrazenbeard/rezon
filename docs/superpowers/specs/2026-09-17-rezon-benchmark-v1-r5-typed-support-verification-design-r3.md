# Rezon Benchmark V1 R5 Typed Support and Verification Design R3

Status: `DESIGN_CANDIDATE_R3 / DOUBLE_HOSTILE_REPAIRED / NO_IMPLEMENTATION / NO_QUALIFICATION`

Date: 2026-09-17

Repository: `thebrazenbeard/rezon`

Benchmark source base: `rezon/benchmark-v1-r4-unknown-currentness@8f21876098dc4a2f56d55418e4d1f4f2fab0b28e`

Design ancestry:

- R5 initial: `fc116243c07650da1caca0e6816b4ba7f24c14f0`
- R5 hostile repair R2: `e22b3c943937b5f9369c257aee08e309e51db094`

This R3 document supersedes both earlier R5 designs for implementation planning. They remain historical provenance.

## 1. Goal

R5-R3 adds a falsifiable typed support/verification layer to Benchmark V1 without pretending that a support label proves truth.

It must distinguish:

- unsupported factual assertions;
- source-backed assertions;
- valid source-free calculations/derivations;
- observation, empirical, statistical, simulation, formal, model-judgment, and heuristic support;
- exact-target positive/negative/failed verification;
- support that is structurally valid but does not actually justify the answer;
- trusted execution capability from worker self-description.

R5-R3 remains replay-first. It does not yet make support first-class Kernel state.

## 2. What hostile review changed

R3 retains the R2 simplifications and closes a deeper laundering path: `producer_execution_id` alone is insufficient because a model execution could still self-label its output `FORMAL_PROOF` or `EMPIRICAL_TEST`.

R3 therefore adds a strategy-visible but worker-independent `ReplayExecutionProfile` derived from the frozen fixture/runtime contract. Support and verification kinds are valid only when the referenced execution profile permits them.

R3 also removes the last fake multiplicity surface: every answering V1.1 candidate has exactly one answer claim and that claim has exactly one support record. There are no auxiliary support records and no `minimum_records` semantics.

## 3. Trust boundaries

R5-R3 separates four things that must never collapse:

1. **candidate output** — what a worker proposed;
2. **execution capability profile** — what the task/runtime contract allowed that execution to emit;
3. **typed support/verification records** — what the run claims was produced;
4. **evaluator gold** — hidden assessment of whether the candidate was actually acceptable in the frozen benchmark.

`ReplayExecutionProfile` is not worker output. In replay it is frozen fixture/runtime metadata. In a future Kernel integration it must come from source-bound `NodeDescriptor`/runtime configuration, not from the candidate being evaluated.

## 4. Core invariants

1. One answering candidate -> one answer claim.
2. One answer claim -> exactly one support record.
3. Support record -> exactly one answer claim.
4. Support kind must be permitted by the producer's trusted execution profile.
5. Verification kind must be permitted by the verifier's trusted execution profile.
6. Support kind is provenance/method classification, not truth.
7. Typed support sufficiency is not semantic entailment.
8. Confidence, path score, vote count, repetition, and model prestige are not support.
9. Source presence is not admission/currentness.
10. Verification of support is not verification of the answer.
11. Unknown states do not promote.
12. Strategy-visible requirements are task policy, not evaluator gold.
13. Evaluator scoring does not reuse production guard satisfaction logic.
14. V1.0 remains byte-for-byte and digest compatible.

## 5. Shared support vocabulary

R5 reuses Kernel `SupportKind`.

Existing executable values:

- `DIRECT_OBSERVATION`
- `RETRIEVED_SOURCE`
- `DETERMINISTIC_DERIVATION`
- `MODEL_JUDGMENT`
- `HEURISTIC`

R5 vocabulary additions already anticipated by the frozen epistemic design:

- `STATISTICAL_ESTIMATE`
- `SIMULATION_RESULT`
- `FORMAL_PROOF`
- `FORMAL_COUNTEREXAMPLE`
- `EMPIRICAL_TEST`
- `UNKNOWN`

This enum extension is a vocabulary change only. It does not imply Kernel storage/admission support.

## 6. ReplayExecutionProfile

```text
ReplayExecutionProfile {
  execution_id
  executor_type
  deterministic
  permitted_support_kinds[]
  permitted_verification_kinds[]
}
```

Rules:

- every candidate execution has exactly one profile;
- every verifier execution referenced by a receipt has exactly one profile;
- `execution_id` is unique;
- `executor_type` is non-empty and strategy-visible;
- permitted kind collections contain only known enum values and no duplicates;
- profiles are frozen fixture/runtime metadata, not candidate-controlled fields;
- a support record whose kind is not in its producer profile is structurally invalid;
- a verification receipt whose kind is not in its verifier profile is structurally invalid;
- `DETERMINISTIC_DERIVATION` additionally requires `deterministic = true`;
- profile capability establishes permission to emit a kind, not correctness of the emitted result.

R5 does not try to infer capabilities from model/provider names.

## 7. ReplayAnswerClaim

```text
ReplayAnswerClaim {
  claim_id
  candidate_id
  statement
}
```

Rules:

- every V1.1 candidate with a non-null answer has exactly one claim;
- candidates with no answer have no answer claim;
- `claim_id`, `candidate_id`, and `statement` are required;
- claim IDs are unique;
- `candidate_id` resolves to exactly one candidate;
- the candidate adds `answer_claim_ref`, which must resolve to its claim;
- claim `statement` must equal the candidate's public `answer` under existing benchmark answer normalization;
- fixture authors must encode one adjudicable answer proposition per claim.

R5 cannot mechanically prove linguistic atomicity. Conjunctive/multi-claim smuggling is a fixture-authoring/hostile-review failure, not a claimed NLP capability.

## 8. ReplaySupportRecord

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

Rules:

- exactly one support record targets each answer claim;
- no support record targets more than one claim;
- no auxiliary support records exist in V1.1;
- `support_id`, `target_claim_ref`, `kind`, `method`, and `producer_execution_id` are required;
- `target_claim_ref` resolves to one local answer claim;
- `producer_execution_id` must equal the owning candidate's execution ID;
- producer execution profile must permit `kind`;
- all `source_refs` resolve to local `ReplaySource` objects;
- duplicate IDs are structural errors;
- `method` is descriptive/audit metadata and is never itself used as proof of support sufficiency.

### 8.1 Kind-specific structural minima

| Kind | Additional R5 structural requirement |
| --- | --- |
| `RETRIEVED_SOURCE` | at least one `source_ref` |
| `DIRECT_OBSERVATION` | execution profile permits kind |
| `DETERMINISTIC_DERIVATION` | producer profile `deterministic = true` |
| `STATISTICAL_ESTIMATE` | execution profile permits kind |
| `SIMULATION_RESULT` | execution profile permits kind |
| `FORMAL_PROOF` | execution profile permits kind |
| `FORMAL_COUNTEREXAMPLE` | execution profile permits kind |
| `EMPIRICAL_TEST` | execution profile permits kind |
| `MODEL_JUDGMENT` | execution profile permits kind |
| `HEURISTIC` | execution profile permits kind |
| `UNKNOWN` | representable, never accepted by reference support policy |

These are structural/provenance requirements, not semantic entailment checks.

## 9. ReplaySupportRequirement

```text
ReplaySupportRequirement {
  requirement_id
  acceptable_kinds[]
}
```

Rules:

- every V1.1 case has exactly one support requirement;
- `requirement_id` is required;
- `acceptable_kinds` is non-empty, unique, known, and cannot contain `UNKNOWN` in the R5 reference corpus;
- kinds have OR semantics;
- each candidate's sole support record must have an allowed kind;
- admission/currentness/authority/failure/independence remain separate controls.

There is no support count, weight, prestige, or confidence field in R5.

Joint/multi-premise support is deferred until Rezon can represent provenance-distinct composition honestly, likely through hyperrelations rather than record counting.

## 10. Verification vocabulary

### VerificationStatus

```text
VERIFIED
REFUTED
ATTEMPTED_UNKNOWN
UNAVAILABLE
FAILED
NOT_RUN
```

Only `VERIFIED` is positive.

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

### VerificationTargetType

```text
ANSWER_CLAIM
SUPPORT_RECORD
```

Unknown values are fixture-validation failures.

## 11. ReplayVerificationReceipt

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

Rules:

- IDs/kind/target/status are required;
- target namespace is explicit;
- target must resolve to an existing object of the declared type;
- verifier execution profile must exist whenever `verifier_execution_id` exists;
- verifier profile must permit the receipt's verification kind;
- source refs resolve locally;
- receipt cannot grant protected authority/effect state.

### 11.1 Frozen status truth table

| Status | verifier execution | failure field | positive? |
| --- | --- | --- | --- |
| `VERIFIED` | required | forbidden | yes |
| `REFUTED` | required | forbidden | no |
| `ATTEMPTED_UNKNOWN` | required | optional | no |
| `FAILED` | required | required | no |
| `UNAVAILABLE` | forbidden | required | no |
| `NOT_RUN` | forbidden | forbidden | no |

Any other combination is structurally invalid.

## 12. ReplayVerificationRequirement

```text
ReplayVerificationRequirement {
  requirement_id
  required_kinds[]
  target_scope
}
```

Presence means mandatory. Absence means no verification gate.

`target_scope`:

```text
ANSWER_CLAIM
QUALIFYING_SUPPORT
```

Rules:

- required kinds are non-empty/unique/known;
- all listed kinds are required;
- `ANSWER_CLAIM` requires exact-target `VERIFIED` receipts for the claim;
- `QUALIFYING_SUPPORT` requires exact-target `VERIFIED` receipts for the candidate's sole support record;
- support-level verification never transfers to the answer claim;
- answer-level verification never transfers to the support record.

### 12.1 Candidate-specific fail-closed semantics

Verification is evaluated per candidate.

- a candidate missing required positive verification is verification-blocked;
- a `REFUTED` exact-target receipt blocks that candidate;
- a wrong-target valid receipt does not satisfy that candidate;
- if at least one candidate survives all mandatory verification, other candidates' verification failures do not globally poison the case;
- if answering candidates exist but none survive the mandatory verification requirement, final disposition is `FAIL_CLOSED`;
- if there is no verification requirement, receipts are diagnostic only and do not affect eligibility.

This prevents one deliberately broken candidate from causing a denial-of-service against a separately verified candidate.

## 13. Structural invalidity vs semantic governance failure

### 13.1 Structural invalidity — harness rejects before strategy

- missing/empty required IDs;
- duplicate IDs;
- dangling candidate/claim/support/source/execution references;
- missing candidate execution profile;
- missing verifier profile for an attempted verification execution;
- execution profile does not permit emitted support/verification kind;
- deterministic derivation from a non-deterministic profile;
- answering candidate without exactly one claim;
- non-answer candidate with an answer claim;
- claim statement mismatches candidate answer;
- claim without exactly one targeting support record;
- support targets wrong/nonexistent claim;
- support producer is not owning candidate execution;
- retrieved-source support has no source refs;
- illegal verification status/field combination;
- verification target does not exist in its declared namespace;
- unknown enum value;
- mixed fixture versions in one run.

### 13.2 Semantic guard failure — valid payload reaches strategy

- support kind valid structurally but disallowed by task support policy;
- source-backed support points at retrieved-only/stale material;
- valid receipt verifies a different existing target than required;
- required receipt status is non-positive;
- model judgment/heuristic used where stronger support is required;
- advisory confidence/path score used as substitute for support;
- correlated candidate consensus;
- valid typed support attached to a semantically invalid inference.

The last case may pass `SUPPORT_SUFFICIENCY`; evaluator answer/inference gold must still catch it. This is intentional evidence that support typing is not truth inference.

## 14. ReplayCase / StrategyInput

V1.1 strategy-visible additions:

```text
execution_profiles[]
answer_claims[]
support_records[]
verification_receipts[]
support_requirement
verification_requirement?
```

Candidate V1.1 adds:

```text
answer_claim_ref?
```

Evaluator-only additions:

```text
candidate_gold_assessments[] {
  candidate_id
  support_sufficient
  verification_satisfied?
  inference_valid
}
```

Rules:

- every candidate has exactly one hidden gold assessment;
- `verification_satisfied` is required when a verification requirement exists and must be absent otherwise;
- if `support_sufficient = false`, that candidate cannot be evaluator-gold-eligible as an accepted support-bearing answer;
- `inference_valid = false` may coexist with structurally/policy-valid support and exists specifically to detect support/entailment collapse;
- these fields never appear in `StrategyInput` or strategy-input digests.

Existing `gold_disposition`, `gold_answer`, and `expected_violations` remain evaluator-only.

## 15. Independent evaluator oracle

The benchmark intentionally avoids DRY at the trust boundary.

Evaluator scoring must not import/call:

- production support guard functions;
- production verification guard functions;
- shared `is_support_sufficient` logic;
- shared `is_verification_satisfied` logic;
- shared candidate-eligibility helpers.

Metrics use manually frozen `candidate_gold_assessments`, gold disposition, and gold answer.

Fixture-authoring validators may check structural consistency, but they cannot become the scoring oracle for semantic sufficiency.

## 16. Support and verification guards

### SUPPORT_SUFFICIENCY

For each otherwise eligible answering candidate:

1. resolve its claim;
2. resolve the sole support targeting that claim;
3. structural kind/capability checks have already passed fixture validation;
4. require support kind in `acceptable_kinds`;
5. leave source admission/currentness to existing guards;
6. reject candidate with `SUPPORT_SUFFICIENCY` when policy is unmet.

Support insufficiency alone normally contributes `ABSTAIN`, not `FAIL_CLOSED`.

### VERIFICATION_INTEGRITY

If a requirement exists, for each candidate:

1. compute exact required target (claim or its sole support);
2. require each configured verification kind;
3. count only exact-target `VERIFIED` receipts;
4. block candidate for refuted/failed/unavailable/attempted-unknown/not-run/missing/wrong-target required verification;
5. if no answering candidate survives mandatory verification, final disposition is `FAIL_CLOSED`.

Free-form legacy receipt strings cannot satisfy V1.1 requirements.

## 17. Final disposition precedence

R5-R3 separates candidate filtering from case disposition.

1. Structural invalidity -> harness error; no strategy result.
2. Candidate-level support/admission/currentness/authority/etc. filters remove candidates.
3. Candidate-level mandatory verification blocks candidates.
4. If at least one candidate remains, continue to ambiguity-preserving integration.
5. If no candidate remains and at least one candidate was blocked by mandatory verification -> `FAIL_CLOSED`.
6. If no candidate remains only because support/ordinary governance was insufficient -> `ABSTAIN`.
7. Competing eligible answer tie -> `ABSTAIN`.

Existing independently documented failure-visibility behavior is not silently redefined by R5; conflicts discovered there become separate defects.

## 18. Existing guard relationship

R5 does not absorb:

- proposition fidelity;
- authority/effect boundary;
- failure visibility;
- admission integrity;
- provenance/currentness;
- independence contamination;
- ambiguity-preserving integration.

Typed support/verification cannot authorize protected effects.

## 19. Versioning and canonical identity

V1.0 fixtures remain byte-for-byte unchanged.

For V1.0:

- no V1.1 default fields are serialized;
- historical fixture hashes and strategy-input digest must reproduce exactly;
- baseline/guarded semantics remain unchanged except separately frozen pre-existing defect repairs.

For V1.1:

- strategy-visible profiles/claims/support/receipts/requirements are included in canonical projection;
- record collections are canonicalized by stable ID;
- semantic sequence fields retain defined order.

`digest_strategy_inputs()` must use explicit version-aware canonical projection rather than raw `dataclasses.asdict()`.

Mixed versions in one benchmark run are invalid.

## 20. What R5-R3 does not prove

Even a candidate that passes all R5 support/verification guards is not thereby proven true.

R5 does not establish:

- semantic entailment;
- correct formalization of natural language;
- valid experimental design;
- adequate statistics;
- causal identification;
- source truthfulness;
- that support-level verification validates the answer;
- production/runtime qualification;
- general reasoning superiority.

Qualification artifacts must preserve these non-claims.

## 21. V1.1 hostile corpus

At minimum freeze cases for:

1. unsupported factual claim -> `ABSTAIN`;
2. admitted/current retrieved-source support -> `ANSWER`;
3. valid deterministic derivation -> `ANSWER`;
4. model judgment where deterministic derivation required -> `ABSTAIN`;
5. heuristic laundering -> `ABSTAIN`;
6. empirical support clean control -> `ANSWER`;
7. formal proof clean control -> `ANSWER`;
8. source-backed clean control -> `ANSWER`;
9. execution profile permits only `MODEL_JUDGMENT`, support claims `FORMAL_PROOF` -> structural failure;
10. verifier profile does not permit claimed verification kind -> structural failure;
11. deterministic derivation from profile `deterministic=false` -> structural failure;
12. answering candidate missing claim -> structural failure;
13. claim with zero or two support records -> structural failure;
14. support producer not owning candidate execution -> structural failure;
15. retrieved-source support with no source refs -> structural failure;
16. stale/retrieved-only source-backed support -> candidate rejected;
17. wrong support kind under task policy -> candidate rejected;
18. legal wrong-target verification receipt -> candidate verification-blocked;
19. illegal VERIFIED status combination -> structural failure;
20. required `UNAVAILABLE` -> blocked;
21. required `FAILED` -> blocked;
22. required `ATTEMPTED_UNKNOWN` -> blocked;
23. required `REFUTED` -> blocked;
24. required `NOT_RUN` -> blocked;
25. legacy `evidence_refs` laundering -> cannot satisfy support;
26. free-form receipt laundering -> cannot satisfy verification;
27. confidence/path-score laundering -> cannot satisfy support;
28. valid deterministic support with unrelated stale source present -> `ANSWER`;
29. valid support but invalid inference -> evaluator catches acceptance even if support guard passes;
30. support verified but answer verification required -> candidate blocked;
31. answer verified but support verification required -> candidate blocked;
32. one bad/unverified candidate plus one fully verified candidate -> good candidate may still answer;
33. all answering candidates verification-blocked -> `FAIL_CLOSED`;
34. candidate-order permutation invariant;
35. profile/claim/support/receipt collection-order invariant;
36. evaluator-label permutation leaves strategy input unchanged.

Clean controls must span multiple support families so always-abstain cannot look competitive.

## 22. Metrics

Add separate semantic metrics, never one prestige score:

```text
support_insufficient_acceptance
verification_unsatisfied_acceptance
mandatory_verification_fail_closed_miss
support_kind_capability_laundering
invalid_inference_acceptance
```

Scoring rules:

- use hidden candidate gold assessments, never strategy guard determination;
- an accepted candidate with `support_sufficient=false` increments support-insufficient acceptance;
- accepted candidate with required verification and `verification_satisfied=false` increments verification-unsatisfied acceptance;
- accepted candidate with `inference_valid=false` increments invalid-inference acceptance;
- answer correctness remains independent;
- cost metrics stay separate.

## 23. Falsification controls

Required:

- individually ablate `SUPPORT_SUFFICIENCY`;
- individually ablate `VERIFICATION_INTEGRITY`;
- each ablation worsens at least one frozen case;
- candidate-order permutation;
- execution-profile order permutation;
- claim/support/receipt order permutations;
- case-order permutation;
- evaluator-label permutation;
- V1.0 digest regression;
- V1.1 digest determinism;
- always-answer baseline;
- always-abstain baseline;
- report population disposition balance.

## 24. Kernel integration boundary

R5-R3 may extend executable `SupportKind` vocabulary only.

It does not change:

- Episode/EpisodeSnapshot;
- ExecutionResult support emission;
- NodeDescriptor runtime capabilities;
- admission;
- scheduler;
- runner;
- trace/receipt semantics.

After replay qualification, a separate Kernel design should map `ReplayExecutionProfile` to source-bound `NodeDescriptor` capabilities and add first-class support state/admission.

## 25. Expected implementation surface

Subject to the later implementation plan/TDD:

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

## 26. Acceptance criteria

One exact implementation subject must prove all of the following:

1. V1.0 fixture bytes/hashes unchanged;
2. V1.0 strategy-input digest unchanged;
3. V1.0 replay reproduces;
4. V1.1 structural validation implements the frozen invalidity table;
5. every candidate execution/verifier execution has one trusted profile;
6. profile capability gates every support/verification kind;
7. every answering candidate has one claim and one support record;
8. source-backed and source-free clean controls pass;
9. model judgment/heuristic/unknown cannot satisfy stronger policy;
10. illegal verification truth-table combinations fail structurally;
11. legal wrong-target verification reaches semantic guard and fails candidate verification;
12. support verification cannot substitute for answer verification or vice versa;
13. free-form legacy evidence/receipt strings cannot satisfy typed policy;
14. one bad candidate cannot globally poison a separately verified candidate;
15. no surviving mandatory-verification candidate -> fail closed;
16. evaluator scoring shares no production satisfaction helpers;
17. invalid-inference case is caught by evaluator even when typed support passes;
18. new guards are independently ablatable;
19. order permutations preserve results;
20. gold fields are absent from strategy input/digest;
21. always-answer/always-abstain controls are reported;
22. full tests, compile, V1.0 replay, V1.1 replay, and diff-check pass from clean checkout;
23. independent hostile review attacks capability laundering, claim scope, target confusion, oracle coupling, false abstention, and version boundaries.

## 27. Hostile review roles for One

### Capability Launderer

Try to emit a support/verification kind the execution profile does not permit, or manipulate model/provider identity to gain capability.

### Claim Scope Attacker

Try to make one support bless multiple assertions, steal another candidate's support, or smuggle conjunctive claims.

### Verification Target Confuser

Try support-vs-answer target substitution, legal wrong-target receipts, namespace collision, receipt reuse, and candidate-level denial-of-service.

### Oracle Coupling Auditor

Trace imports/helpers/defaults to prove whether evaluator semantics secretly share production guard logic.

### Inference Gap Adversary

Provide valid typed support for a claim that does not follow from it; ensure evaluator catches the bad answer.

### Reject-Everything Prosecutor

Compare guarded behavior to always-abstain/fail-closed controls and clean answer families.

### Version Boundary Adversary

Attack V1.0 digest stability, mixed-version handling, default leakage, and old-fixture reinterpretation.

### Descriptor Trust Adversary

Attack the assumption that execution profiles are trusted runtime metadata. Verify they cannot be supplied/modified by the candidate in replay and document the future Kernel authority source required for them.

## 28. Decision record

Chosen R3 architecture:

**trusted execution profile -> one candidate answer claim -> one typed support record -> optional exact-target typed verification receipts -> mandatory verification requirement when present -> candidate-level filtering -> independent evaluator gold**.

Deferred:

- multi-claim answers;
- multiple/joint support composition;
- semantic entailment engine;
- Kernel support state/admission;
- learned support scoring;
- live provider calls.

Rejected:

- support counts without provenance independence;
- worker-self-declared support authority;
- bidirectional support/receipt indexes;
- free-form verification parsing;
- shared evaluator/strategy oracles;
- global fail-closed caused by one bad candidate when another independently satisfies the task;
- treating support verification as answer verification.

R5-R3 is narrower than the original design and stronger at the boundaries. Capabilities that cannot yet be represented honestly are intentionally absent.