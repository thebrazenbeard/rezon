# Rezon Benchmark V1 R5 Typed Support and Verification Design R4

Status: `DESIGN_CANDIDATE_R4 / HOSTILE_REPAIRED / NO_IMPLEMENTATION / NO_QUALIFICATION`

Date: 2026-09-17

Repository: `thebrazenbeard/rezon`

Benchmark source base: `rezon/benchmark-v1-r4-unknown-currentness@8f21876098dc4a2f56d55418e4d1f4f2fab0b28e`

Design ancestry:
- R5 initial: `fc116243c07650da1caca0e6816b4ba7f24c14f0`
- hostile repair R2: `e22b3c943937b5f9369c257aee08e309e51db094`
- hostile repair R3: `c946ccb83b507a5f3f67eb4889df111a15154d19`

This R4 document supersedes the earlier R5 designs for implementation planning. Earlier documents remain provenance only.

## 1. Objective

R5 adds a typed support and verification layer to Benchmark V1 that can distinguish:

- unsupported/unknown support;
- current admitted source support;
- source-free deterministic derivation;
- observation, statistical, simulation, formal, empirical, model-judgment, and heuristic support;
- exact-target verification outcomes;
- structurally valid support that still fails to justify the answer;
- runtime capability metadata from worker self-description.

R5 remains replay-first. It does not yet make support first-class Kernel episode state and does not qualify runtime behavior.

## 2. Architectural thesis

The R5 reference path is intentionally narrow:

```text
trusted execution profile
  -> one answering candidate
  -> one answer claim
  -> exactly one typed support record
  -> optional exact-target verification receipts
  -> mandatory verification requirement when present
  -> candidate-level filtering
  -> ambiguity-preserving integration
  -> independent evaluator gold
```

Capabilities that cannot yet be represented honestly are omitted rather than approximated.

## 3. Trust boundaries

Four classes remain distinct:

1. **candidate output** — what a worker proposed;
2. **execution profile** — frozen runtime/task metadata describing what that execution was permitted to emit;
3. **support/verification records** — typed claims about how the answer was supported or checked;
4. **evaluator gold** — hidden benchmark assessment.

Execution profiles are not worker output. In future Kernel integration they must be source-bound to NodeDescriptor/runtime configuration.

## 4. Core invariants

1. Every V1.1 answering candidate has exactly one answer claim.
2. Every answer claim has exactly one support record.
3. Missing support is structural corruption, not semantic insufficiency.
4. Semantic unsupportedness is represented explicitly by `SupportKind.UNKNOWN` or by a support kind disallowed by policy.
5. Support kind must be permitted by the candidate execution profile.
6. Verification kind must be permitted by the verifier execution profile.
7. Support kind is not truth.
8. Support sufficiency is not semantic entailment.
9. Confidence, path score, repetition, vote count, and model prestige are not support.
10. Source presence is not source admission or currentness.
11. Verification of support is not verification of the answer.
12. Unknown states do not silently promote.
13. Strategy-visible requirements are policy, not evaluator gold.
14. Evaluator scoring does not reuse production guard satisfaction code.
15. V1.0 remains byte-for-byte and digest compatible.

## 5. Support vocabulary

R5 reuses Kernel `SupportKind`.

Existing values:

```text
DIRECT_OBSERVATION
RETRIEVED_SOURCE
DETERMINISTIC_DERIVATION
MODEL_JUDGMENT
HEURISTIC
```

R5 vocabulary additions already anticipated by the frozen epistemic design:

```text
STATISTICAL_ESTIMATE
SIMULATION_RESULT
FORMAL_PROOF
FORMAL_COUNTEREXAMPLE
EMPIRICAL_TEST
UNKNOWN
```

Extending the enum is a vocabulary-only Kernel change. It does not imply Kernel runtime support storage.

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
- every attempted verifier execution has exactly one profile;
- profile IDs are unique;
- `executor_type` is non-empty;
- permitted kind collections contain known unique enum values;
- profile metadata is strategy-visible but candidate-independent;
- support kind must be permitted by producer profile;
- verification kind must be permitted by verifier profile;
- `DETERMINISTIC_DERIVATION` additionally requires `deterministic = true`;
- capability means permission to emit, not correctness.

R5 does not infer capability from provider/model names.

## 7. ReplayAnswerClaim

```text
ReplayAnswerClaim {
  claim_id
  candidate_id
  statement
}
```

Rules:

- every candidate with `answer != null` has exactly one claim;
- candidates with no answer have no answer claim;
- candidate V1.1 adds `answer_claim_ref`;
- claim ID is unique;
- candidate ownership resolves exactly;
- claim statement matches public candidate answer under existing answer normalization;
- one claim cannot belong to multiple candidates.

R5 cannot mechanically prove linguistic atomicity. Fixture authors must encode one adjudicable proposition per answer claim. Multi-claim/conjunctive smuggling is a fixture-authoring defect for hostile review.

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
- support IDs are unique;
- `target_claim_ref` resolves locally;
- `producer_execution_id` equals the owning candidate execution ID;
- producer profile permits `kind`;
- every `source_ref` resolves to a local source;
- `method` is audit text and never itself establishes sufficiency;
- no auxiliary support records exist in V1.1.

### 8.1 Kind-specific structural minima

| Kind | Additional structural requirement |
| --- | --- |
| `RETRIEVED_SOURCE` | at least one local `source_ref` |
| `DIRECT_OBSERVATION` | permitted producer profile |
| `DETERMINISTIC_DERIVATION` | producer profile `deterministic = true` |
| `STATISTICAL_ESTIMATE` | permitted producer profile |
| `SIMULATION_RESULT` | permitted producer profile |
| `FORMAL_PROOF` | permitted producer profile |
| `FORMAL_COUNTEREXAMPLE` | permitted producer profile |
| `EMPIRICAL_TEST` | permitted producer profile |
| `MODEL_JUDGMENT` | permitted producer profile |
| `HEURISTIC` | permitted producer profile |
| `UNKNOWN` | permitted producer profile; never accepted by reference support policy |

These are structural/provenance minima, not semantic proof.

## 9. ReplaySupportRequirement

```text
ReplaySupportRequirement {
  requirement_id
  acceptable_kinds[]
}
```

Rules:

- every V1.1 case has exactly one support requirement;
- acceptable kinds are non-empty, known, and unique;
- kinds have OR semantics;
- `UNKNOWN` is forbidden in R5 reference requirements;
- each candidate's sole support record must have an allowed kind to satisfy the support guard;
- admission/currentness, authority, failure visibility, and independence remain separate controls.

There is no support count, confidence score, strength score, or prestige score in R5.

Joint/multi-premise support is deferred until Rezon can model provenance-distinct composition honestly, likely with hyperrelations rather than record counting.

## 10. Verification vocabulary

```text
VerificationStatus = {
  VERIFIED,
  REFUTED,
  ATTEMPTED_UNKNOWN,
  UNAVAILABLE,
  FAILED,
  NOT_RUN
}

VerificationKind = {
  PROVENANCE_BINDING,
  CURRENTNESS_CHECK,
  DETERMINISTIC_RECOMPUTATION,
  FORMAL_VERIFICATION,
  EMPIRICAL_REPLICATION,
  TOOL_EFFECT_READBACK,
  CONTRADICTION_CHECK,
  SCHEMA_VALIDATION
}

VerificationTargetType = {
  ANSWER_CLAIM,
  SUPPORT_RECORD
}
```

Only `VERIFIED` is positive.

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

- required IDs/kind/target/status are non-empty;
- target namespace is explicit and resolves locally;
- attempted verifier execution has a profile;
- verifier profile permits receipt kind;
- source refs resolve locally;
- receipt cannot authorize protected effects.

### 11.1 Frozen verification truth table

| Status | verifier execution | failure field | positive? |
| --- | --- | --- | --- |
| `VERIFIED` | required | forbidden | yes |
| `REFUTED` | required | forbidden | no |
| `ATTEMPTED_UNKNOWN` | required | optional | no |
| `FAILED` | required | required | no |
| `UNAVAILABLE` | forbidden | required | no |
| `NOT_RUN` | forbidden | forbidden | no |

Illegal combinations are structural fixture invalidity.

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

- required kinds are non-empty, known, and unique;
- all required kinds use AND semantics;
- answer scope requires exact-target `VERIFIED` receipts for the claim;
- support scope requires exact-target `VERIFIED` receipts for the candidate's sole support record;
- support-level verification does not transfer to answer-level verification;
- answer-level verification does not transfer to support-level verification.

Receipts may exist without a requirement for audit, but do not affect eligibility.

## 13. Candidate-specific verification semantics

Verification is evaluated per candidate.

- candidate missing required positive verification is verification-blocked;
- exact-target `REFUTED` blocks that candidate;
- wrong-target receipt does not satisfy that candidate;
- one broken candidate does not globally poison another candidate that independently satisfies support and verification;
- if at least one candidate survives all mandatory verification, integration may continue;
- if answering candidates exist but none survive mandatory verification, final disposition is `FAIL_CLOSED`.

This prevents denial-of-service via an intentionally broken peer candidate.

## 14. Structural invalidity vs semantic governance failure

### 14.1 Structural invalidity — reject before strategy execution

- missing/empty required IDs;
- duplicate IDs;
- dangling candidate/claim/support/source/execution references;
- missing execution profile;
- profile does not permit emitted support/verification kind;
- deterministic derivation from `deterministic = false` profile;
- answering candidate without exactly one claim;
- non-answer candidate with a claim;
- claim statement mismatches candidate answer;
- claim without exactly one targeting support record;
- support targets wrong/nonexistent claim;
- support producer differs from owning candidate execution;
- retrieved-source support has no source refs;
- illegal verification status/field combination;
- verification target absent from declared namespace;
- unknown enum value;
- mixed fixture versions in one run.

### 14.2 Semantic governance failure — structurally valid payload reaches strategy

- support kind disallowed by task policy;
- explicit `UNKNOWN` support under a stronger requirement;
- source-backed support references stale/non-admitted source;
- valid receipt targets another existing object than the requirement target;
- required verification has non-positive status;
- advisory confidence/path score attempts to substitute for support;
- correlated candidate consensus;
- structurally valid support is attached to an inference the evaluator deems invalid.

The last case may pass `SUPPORT_SUFFICIENCY`; evaluator gold must still catch it. That is intentional.

## 15. ReplayCase and StrategyInput

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

- every answering candidate has exactly one hidden gold assessment;
- non-answer candidates have no support/verification gold assessment;
- `verification_satisfied` is required when a verification requirement exists and absent otherwise;
- hidden gold never appears in StrategyInput or strategy-input digest;
- support/inference gold may disagree intentionally to test support-vs-entailment separation.

Existing `gold_disposition`, `gold_answer`, and `expected_violations` remain evaluator-only.

## 16. Independent evaluator oracle

The benchmark intentionally avoids DRY at the trust boundary.

Evaluator scoring must not call/import:

- production support guard helpers;
- production verification guard helpers;
- shared candidate-eligibility functions;
- shared support/verification satisfaction functions.

Metrics use manually frozen candidate gold assessments, gold disposition, and gold answer.

Fixture structural validators may be shared for parsing/shape safety, but semantic scoring is independent.

## 17. Guard semantics

### SUPPORT_SUFFICIENCY

For each otherwise eligible answering candidate:

1. resolve its claim;
2. resolve the sole support targeting that claim;
3. rely on structural validation for capability/profile shape;
4. require support kind in case `acceptable_kinds`;
5. leave source admission/currentness to existing guards;
6. reject candidate with `SUPPORT_SUFFICIENCY` when policy is unmet.

Unsupportedness in valid V1.1 data is represented by `UNKNOWN` or another disallowed support kind. A missing support record is structural invalidity.

If no candidate survives ordinary support/governance filters, final disposition is normally `ABSTAIN`.

### VERIFICATION_INTEGRITY

If requirement exists, per candidate:

1. compute exact required target;
2. require each configured verification kind;
3. count only exact-target `VERIFIED` receipts;
4. block candidate for missing/wrong-target/non-positive required verification;
5. if no answering candidate survives mandatory verification, `FAIL_CLOSED`.

Free-form V1.0 receipt strings cannot satisfy V1.1 verification.

## 18. Final disposition precedence

1. Structural invalidity -> harness error, no strategy result.
2. Ordinary candidate governance/support filters reject candidates.
3. Mandatory verification blocks candidates.
4. If candidates survive, integrate remaining answers.
5. If none survive and at least one answering candidate was verification-blocked -> `FAIL_CLOSED`.
6. If none survive only through ordinary governance/support insufficiency -> `ABSTAIN`.
7. Tie among surviving answers -> `ABSTAIN`.

Existing independently documented failure-visibility behavior is not silently redefined by R5.

## 19. Existing boundaries remain separate

R5 does not absorb:

- proposition fidelity;
- authority/effect boundary;
- failure visibility;
- admission integrity;
- provenance/currentness;
- independence contamination;
- ambiguity preservation.

Typed support or verification never grants protected-effect authority.

## 20. V1.0 compatibility and version identity

V1.0 fixtures remain byte-for-byte unchanged.

For V1.0:

- V1.1 fields are omitted from canonical serialization;
- recorded fixture hashes and strategy-input digest must reproduce exactly;
- existing strategy semantics remain unchanged except separately frozen historical defect repairs.

For V1.1:

- profiles/claims/support/receipts/requirements are strategy-visible and canonicalized;
- unordered records are sorted by stable ID;
- semantic sequence fields retain defined order.

`digest_strategy_inputs()` must use an explicit version-aware projection, not raw unconstrained `dataclasses.asdict()`.

Mixed fixture versions in one run are invalid.

## 21. Explicit non-claims

Passing R5 support/verification guards does not prove:

- semantic entailment;
- correct formalization;
- experimental validity;
- statistical adequacy;
- causal identification;
- source truthfulness;
- that support-level verification validates the answer;
- runtime/production qualification;
- general reasoning superiority.

Qualification artifacts must preserve these non-claims.

## 22. V1.1 hostile corpus

Freeze at least these cases:

1. `UNKNOWN` support under `RETRIEVED_SOURCE` requirement -> `ABSTAIN`;
2. admitted/current retrieved-source support -> `ANSWER`;
3. valid source-free deterministic derivation -> `ANSWER`;
4. model judgment where deterministic derivation required -> `ABSTAIN`;
5. heuristic laundering -> `ABSTAIN`;
6. empirical clean control -> `ANSWER`;
7. formal proof clean control -> `ANSWER`;
8. execution profile permits only model judgment while support claims formal proof -> structural failure;
9. verifier profile does not permit verification kind -> structural failure;
10. deterministic derivation from non-deterministic profile -> structural failure;
11. answering candidate missing claim -> structural failure;
12. claim missing support -> structural failure;
13. claim has two support records -> structural failure;
14. support producer differs from owning candidate execution -> structural failure;
15. retrieved-source support has no source refs -> structural failure;
16. stale/retrieved-only source-backed support -> candidate rejected;
17. disallowed support kind -> candidate rejected;
18. legal wrong-target verification -> candidate blocked;
19. illegal VERIFIED field combination -> structural failure;
20. required `UNAVAILABLE` -> candidate blocked;
21. required `FAILED` -> candidate blocked;
22. required `ATTEMPTED_UNKNOWN` -> candidate blocked;
23. required `REFUTED` -> candidate blocked;
24. required `NOT_RUN` -> candidate blocked;
25. legacy `evidence_refs` plus `UNKNOWN` support -> cannot satisfy stronger support;
26. free-form receipt text without typed verification -> cannot satisfy requirement;
27. confidence/path-score plus `UNKNOWN` support -> cannot satisfy stronger support;
28. valid deterministic support with unrelated stale source present -> `ANSWER`;
29. valid typed support but evaluator-invalid inference -> acceptance counted as invalid inference;
30. support verified while answer verification required -> candidate blocked;
31. answer verified while support verification required -> candidate blocked;
32. one unverified candidate plus one fully verified candidate -> verified candidate may answer;
33. all answering candidates verification-blocked -> `FAIL_CLOSED`;
34. candidate/profile/claim/support/receipt ordering permutations preserve outcome;
35. evaluator-label permutation leaves strategy-visible digest unchanged.

Clean answer controls must span source-backed, deterministic, empirical, and formal families. Always-abstain must not look competitive through population skew.

## 23. Metrics

Add separate semantic metrics:

```text
support_insufficient_acceptance
verification_unsatisfied_acceptance
mandatory_verification_fail_closed_miss
support_kind_capability_laundering
invalid_inference_acceptance
```

Scoring uses hidden candidate gold assessments rather than production guard determinations.

- accepted candidate with `support_sufficient=false` increments support-insufficient acceptance;
- accepted candidate with required verification and `verification_satisfied=false` increments verification-unsatisfied acceptance;
- accepted candidate with `inference_valid=false` increments invalid-inference acceptance;
- answer correctness remains separate;
- cost remains separate.

## 24. Falsification controls

Required:

- independent ablation of `SUPPORT_SUFFICIENCY`;
- independent ablation of `VERIFICATION_INTEGRITY`;
- each ablation worsens at least one frozen hostile case;
- candidate/profile/claim/support/receipt/case order permutations;
- evaluator-label permutation;
- V1.0 digest regression;
- V1.1 digest determinism;
- always-answer control;
- always-abstain control;
- population disposition balance report.

## 25. Kernel integration boundary

R5 may extend executable `SupportKind` vocabulary only.

It does not modify:

- Episode/EpisodeSnapshot;
- ExecutionResult support emission;
- NodeDescriptor runtime capabilities;
- admission;
- scheduler;
- runner;
- trace/receipt semantics.

After replay qualification, a separate Kernel design should source execution profiles from trusted NodeDescriptor/runtime state and add first-class support admission/storage.

## 26. Expected implementation surface

Subject to a later implementation plan/TDD:

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

## 27. Acceptance criteria

One exact implementation subject must prove:

1. V1.0 fixture bytes/hashes unchanged;
2. V1.0 strategy-input digest unchanged;
3. V1.0 replay reproduces;
4. V1.1 structural-invalidity table is enforced;
5. each candidate/verifier execution has trusted profile when applicable;
6. profile capability gates support/verification kinds;
7. every answering candidate has one claim and one support;
8. semantic unsupportedness uses `UNKNOWN`/disallowed kind, not missing support;
9. source-backed and source-free clean controls pass;
10. model judgment/heuristic/unknown cannot satisfy stronger policy;
11. illegal verification truth-table combinations fail structurally;
12. legal wrong-target verification reaches strategy and blocks only the affected candidate;
13. support verification cannot substitute for answer verification or vice versa;
14. legacy text/evidence fields cannot satisfy typed policy;
15. one bad candidate cannot globally poison a separately verified candidate;
16. no surviving mandatory-verification candidate -> fail closed;
17. evaluator scoring shares no production semantic satisfaction helpers;
18. invalid-inference case is caught even when support guard passes;
19. new guards are independently ablatable;
20. order permutations preserve outcomes;
21. hidden gold is absent from strategy input/digest;
22. always-answer/always-abstain controls are reported;
23. full tests, compile, V1.0 replay, V1.1 replay, and diff-check pass from clean checkout;
24. independent hostile review attacks capability laundering, target confusion, oracle coupling, inference gaps, false abstention, and version boundaries.

## 28. Hostile roles for One

### Capability Launderer
Try to emit support/verification kinds outside execution-profile authority.

### Claim Scope Attacker
Try support theft, multi-claim smuggling, support duplication, or mismatched ownership.

### Verification Target Confuser
Try answer/support substitution, valid wrong-target receipts, receipt reuse, and per-candidate denial-of-service.

### Oracle Coupling Auditor
Trace imports/helpers/defaults for strategy/evaluator semantic coupling.

### Inference Gap Adversary
Supply structurally valid support that does not justify the answer; benchmark must still score the acceptance as bad.

### Reject-Everything Prosecutor
Compare against always-abstain/fail-closed and clean answer controls.

### Version Boundary Adversary
Attack V1.0 digest stability, mixed versions, default leakage, and old-fixture reinterpretation.

### Descriptor Trust Adversary
Verify execution profiles cannot be candidate-supplied and identify the exact future Kernel authority source.

## 29. Decision record

Chosen architecture:

**trusted execution profile -> one answer claim -> one typed support record -> optional exact-target verification receipts -> mandatory verification requirement when present -> candidate-local filtering -> independent evaluator gold**.

Deferred intentionally:

- multi-claim candidates;
- multiple/joint support composition;
- semantic entailment engine;
- full Kernel support state/admission;
- learned support scoring;
- live provider calls.

Rejected:

- support counts without provenance independence;
- worker-self-declared support authority;
- missing-support-as-normal semantic state;
- bidirectional support/receipt indexes;
- free-form verification parsing;
- shared evaluator/strategy semantic oracle;
- global fail-closed caused by one broken peer while another verified candidate survives;
- treating support verification as answer verification.

R5-R4 is intentionally narrow. It removes mechanisms that cannot yet be represented honestly and makes unsupportedness, capability authority, target semantics, and evaluator independence explicit.