# Rezon Benchmark V1 R5 Typed Support and Verification Design — Final Hostile-Repair Candidate

Status: `DESIGN_REVIEW_CANDIDATE / NO_IMPLEMENTATION / NO_QUALIFICATION`

Date: 2026-09-17

Repository: `thebrazenbeard/rezon`

Benchmark source base: `rezon/benchmark-v1-r4-unknown-currentness@8f21876098dc4a2f56d55418e4d1f4f2fab0b28e`

Historical design ancestry: `fc116243...` -> `e22b3c94...` -> `c946ccb8...` -> `f4133f38...`

This document is the only R5 design authority for implementation planning. Earlier R5 design files are historical provenance only.

## 1. Objective

R5 adds a typed support/verification contract to Benchmark V1 that can distinguish unsupportedness, source-backed support, source-free deterministic derivation, empirical/formal/model/heuristic support, and exact-target verification outcomes without collapsing any of those into truth.

R5 is replay-first. It does not yet make support first-class Kernel runtime state.

## 2. Reference architecture

```text
trusted execution profile
  -> answering candidate
  -> one answer claim
  -> one typed support record
  -> existing source-governance guards over that support's source refs
  -> optional exact-target verification receipts
  -> verification-source governance + verifier separation
  -> mandatory verification requirement when present
  -> candidate-local filtering
  -> ambiguity-preserving integration
  -> independent evaluator gold
```

## 3. Invariants

1. Every V1.1 answering candidate has exactly one answer claim.
2. Every answer claim has exactly one support record.
3. Missing support is structural corruption. Semantic unsupportedness is explicit `UNKNOWN` or a policy-disallowed support kind.
4. Support kind must be permitted by trusted execution-profile capability.
5. Verification kind must be permitted by trusted verifier-profile capability.
6. Support kind is not truth and does not imply entailment.
7. Confidence, votes, model prestige, repetition, or path score are not support.
8. Source presence is not admission/currentness.
9. Verification-source refs are provenance and must resolve and pass applicable admission/currentness rules before that receipt can affect candidate eligibility.
10. An attempted verifier execution must be distinct from the execution that produced the target candidate. R5 has no same-execution exception.
11. At most one verification receipt may exist for a given `(target_type, target_id, kind)` tuple.
12. `VERIFIED` is a verifier assertion, not semantic truth. Structural validity, capability, target binding, verifier separation, and source governance are prerequisites; hidden evaluator gold may still mark verification unsatisfied.
13. Verification of a support record is not verification of the answer claim.
14. Unknown states do not promote.
15. Unsolicited or non-required refutations do not gate candidate eligibility in R5.
16. Strategy-visible requirements are task policy, never evaluator gold.
17. Evaluator scoring does not reuse production support/verification satisfaction logic.
18. V1.0 bytes, hashes, strategy-input identity, and semantics remain reproducible.

## 4. Support vocabulary

Reuse Kernel `SupportKind`.

Existing:

```text
DIRECT_OBSERVATION
RETRIEVED_SOURCE
DETERMINISTIC_DERIVATION
MODEL_JUDGMENT
HEURISTIC
```

R5 additions already anticipated by the epistemic design:

```text
STATISTICAL_ESTIMATE
SIMULATION_RESULT
FORMAL_PROOF
FORMAL_COUNTEREXAMPLE
EMPIRICAL_TEST
UNKNOWN
```

This enum extension is vocabulary-only; it does not claim Kernel support storage/admission exists.

## 5. ReplayExecutionProfile

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
- profiles are fixture/runtime metadata, not candidate output;
- IDs are unique;
- permitted kinds are known/unique;
- emitted support/verification kind must be permitted by the referenced profile;
- `DETERMINISTIC_DERIVATION` additionally requires `deterministic = true`;
- capability means permission to emit, not correctness;
- attempted verifier execution must be different from the execution that produced the target candidate; R5 permits no same-execution verification exception;
- distinct execution is a minimum anti-circularity rule, not a claim of statistical or model/provider independence.

Future Kernel authority source: source-bound `NodeDescriptor`/runtime configuration, never worker self-description.

## 6. ReplayAnswerClaim

```text
ReplayAnswerClaim {
  claim_id
  candidate_id
  statement
}
```

Rules:

- exactly one claim for each candidate with non-null answer;
- no claim for a candidate with null answer;
- candidate V1.1 adds `answer_claim_ref`;
- claim statement equals candidate answer under existing answer normalization;
- fixture authors encode one adjudicable proposition per claim.

R5 does not claim automatic linguistic atomicity detection.

## 7. ReplaySupportRecord

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
- no auxiliary support records in V1.1;
- target claim resolves locally;
- producer execution equals owning candidate execution;
- producer profile permits support kind;
- source refs resolve locally;
- method is audit text, not proof.

Structural minima:

- `RETRIEVED_SOURCE`: at least one source ref;
- `DETERMINISTIC_DERIVATION`: producer profile must be deterministic;
- all other non-UNKNOWN kinds: producer profile must permit kind;
- `UNKNOWN`: representable but never allowed by reference support policy.

## 8. ReplaySupportRequirement

```text
ReplaySupportRequirement {
  requirement_id
  acceptable_kinds[]
}
```

Rules:

- every V1.1 case has exactly one requirement;
- kinds are known, unique, non-empty, OR semantics;
- reference requirements cannot include `UNKNOWN`;
- each candidate's sole support kind must be allowed to satisfy `SUPPORT_SUFFICIENCY`.

R5 has no support count, strength score, confidence score, or pseudo-independence count. Multi-support composition is deferred.

## 9. Version-aware source governance

This is normative and closes the R4->R5 integration gap.

For V1.0:

```text
effective_source_refs(candidate) = candidate.source_refs
```

For V1.1:

```text
effective_source_refs(candidate) = source_refs on the sole support record targeting candidate.answer_claim_ref
```

`ADMISSION_INTEGRITY` and `PROVENANCE_CURRENTNESS` operate over `effective_source_refs`.

Consequences:

- source-backed typed support cannot bypass source governance merely because candidate legacy refs are empty;
- unrelated stale sources elsewhere in the case do not contaminate a source-free deterministic answer;
- V1.1 legacy `candidate.source_refs` cannot expand or substitute for typed support provenance.

Verification provenance is governed separately but by the same source-truth boundary.

For every verification receipt:

- each `source_ref` is unique within the receipt and must resolve to a local `ReplaySource`; dangling verification source refs are structural errors;
- `PROVENANCE_BINDING` and `CURRENTNESS_CHECK` receipts require at least one source ref;
- other verification kinds may be source-free when the verifier execution itself is the relevant artifact;
- when a receipt is applicable to a candidate's mandatory verification requirement, its source refs enter `ADMISSION_INTEGRITY` and `PROVENANCE_CURRENTNESS`;
- an applicable receipt backed by any source that is not explicitly `ADMITTED` and `is_current is True` is not verification-governance-eligible and cannot satisfy or refute the requirement;
- irrelevant, wrong-target, or non-required receipts do not import their source failures into an unrelated candidate.

This prevents stale, retrieved-only, dangling, or otherwise ungoverned verification provenance from laundering a positive receipt.

## 10. Verification vocabulary

```text
VerificationStatus = VERIFIED | REFUTED | ATTEMPTED_UNKNOWN | UNAVAILABLE | FAILED | NOT_RUN
VerificationTargetType = ANSWER_CLAIM | SUPPORT_RECORD
```

Verification kinds:

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

Truth table:

| status | verifier execution | failure | positive |
| --- | --- | --- | --- |
| VERIFIED | required | forbidden | yes |
| REFUTED | required | forbidden | no |
| ATTEMPTED_UNKNOWN | required | optional | no |
| FAILED | required | required | no |
| UNAVAILABLE | forbidden | required | no |
| NOT_RUN | forbidden | forbidden | no |

Attempted verifier execution must have a profile that permits the verification kind. Illegal combinations are structural fixture errors.

Additional structural rules:

- `verification_id` values are unique;
- `target_id` resolves to the declared target type;
- `source_refs` are unique and resolve locally;
- there is at most one receipt for each `(target_type, target_id, kind)` tuple; a VERIFIED/REFUTED pair for the same tuple is structurally invalid rather than order-resolved;
- every attempted verifier execution has a trusted execution profile, permits the verification kind, and is distinct from the target candidate's execution;
- `PROVENANCE_BINDING` and `CURRENTNESS_CHECK` require at least one source ref.

A structurally valid `VERIFIED` status remains only a positive verifier assertion. It becomes usable by `VERIFICATION_INTEGRITY` only after target binding, verifier separation, capability, and applicable verification-source governance pass.

## 12. ReplayVerificationRequirement

```text
ReplayVerificationRequirement {
  requirement_id
  required_kinds[]
  target_scope
}
```

Presence means mandatory. Absence means no verification gate.

`target_scope` is `ANSWER_CLAIM` or `QUALIFYING_SUPPORT`.

All listed kinds use AND semantics and require exact-target `VERIFIED` receipts.

Support-level verification never satisfies answer-level verification, and vice versa.

If no verification requirement exists, verification receipts are diagnostic only and cannot block or promote candidate eligibility. If a requirement exists, only receipts whose kind is listed in that requirement and whose target exactly matches the candidate's required target are eligibility-relevant.

## 13. Candidate-local verification semantics

- unsatisfied mandatory verification blocks only the affected candidate;
- only exact-target receipts for required verification kinds are eligibility-relevant;
- an applicable receipt whose verification-source provenance fails admission/currentness is non-satisfying and non-refuting;
- an exact-target `REFUTED` receipt blocks the candidate only when its kind is required and the receipt is verification-governance-eligible;
- a legal wrong-target receipt is non-satisfying;
- a REFUTED receipt is diagnostic only when no verification requirement exists or when its kind is not required; it does not create candidate-local denial of service;
- conflicting receipts for one target/kind tuple never reach strategy semantics because tuple duplication is structural invalidity;
- one broken candidate cannot globally poison a separately verified candidate;
- if at least one candidate survives mandatory verification, integration continues;
- if answering candidates exist but none survive mandatory verification, final disposition is `FAIL_CLOSED`.

## 14. Structural invalidity vs semantic governance

Structural invalidity -> harness error before strategy:

- missing/duplicate/dangling IDs;
- missing required execution profile;
- profile lacks claimed support/verification capability;
- deterministic derivation from non-deterministic profile;
- answering candidate without exactly one claim;
- non-answer candidate with claim;
- claim/answer mismatch;
- answer claim with zero or multiple support records;
- support producer not owning candidate execution;
- retrieved-source support without source refs;
- illegal verification status fields;
- nonexistent verification target;
- dangling verification source ref;
- duplicate verification `(target_type, target_id, kind)` tuple;
- attempted self-verification where verifier execution equals the target candidate execution;
- source-required verification kind without source refs;
- unknown enum;
- mixed fixture versions.

Semantic governance failure -> structurally valid input reaches strategy:

- explicit `UNKNOWN` or disallowed support kind;
- stale/retrieved-only source-backed support;
- valid receipt targets another existing object than required;
- required verification non-positive/missing;
- applicable exact-target VERIFIED receipt backed by stale/retrieved-only verification source provenance;
- advisory confidence/path score tries to replace support;
- correlated consensus;
- structurally valid support accompanies an evaluator-invalid inference.

## 15. ReplayCase / StrategyInput

V1.1 strategy-visible additions:

```text
execution_profiles[]
answer_claims[]
support_records[]
verification_receipts[]
support_requirement
verification_requirement?
```

Candidate V1.1 adds `answer_claim_ref?`.

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

- exactly one gold assessment per answering candidate;
- none for non-answer candidates;
- `verification_satisfied` required iff verification requirement exists;
- hidden gold never enters StrategyInput or its digest;
- `support_sufficient=true` may coexist with `inference_valid=false` to test support-vs-entailment separation;
- `verification_satisfied=false` may coexist with a structurally valid exact-target `VERIFIED` receipt when independent evidence such as stale verification provenance makes the assertion unusable;
- receipt status never writes, derives, or determines evaluator gold.

Existing gold disposition/answer/expected violations remain evaluator-only.

## 16. Evaluator independence

The evaluator intentionally does not DRY semantic satisfaction with the strategy.

It must not import/call production:

- support-satisfaction helpers;
- verification-satisfaction helpers;
- candidate-eligibility helpers.

Scoring uses frozen candidate gold assessments plus existing gold disposition/answer.

The hostile population must contain at least one structurally valid exact-target `VERIFIED` receipt whose hidden evaluator assessment is `verification_satisfied=false` for a reason independently encoded outside the production verification-satisfaction helper (for example stale verification provenance). This is the anti-oracle control proving that "receipt says VERIFIED" is not the evaluator's truth rule.

Structural parser/shape validation may be shared; semantic scoring may not.

## 17. Guard semantics

`SUPPORT_SUFFICIENCY`:

- uses sole typed support record;
- requires kind allowed by case support policy;
- leaves source admission/currentness to those guards via `effective_source_refs`;
- unmet support normally rejects candidate and contributes `ABSTAIN` if no ordinary candidate survives.

`VERIFICATION_INTEGRITY`:

- computes the exact required target per candidate;
- requires every configured verification kind;
- considers only receipts for required kinds and the exact required target;
- counts a `VERIFIED` receipt only when its verifier execution is trusted/permitted, distinct from the target candidate execution, and its applicable verification-source refs pass admission/currentness;
- a source-governance-ineligible `VERIFIED` receipt is non-satisfying and records the corresponding source-governance failure;
- an exact-target `REFUTED` receipt blocks only when its kind is required and its verification provenance is governance-eligible;
- wrong-target, non-required, or unsolicited receipts cannot satisfy or block eligibility;
- blocks candidate on missing/non-positive/otherwise unsatisfied required verification;
- if no answering candidate survives mandatory verification, disposition is `FAIL_CLOSED`.

Receipt status alone is never sufficient authority for verification truth.

Free-form V1.0 evidence/receipt strings cannot satisfy V1.1 typed requirements.

## 18. Disposition precedence

1. structural invalidity -> harness error;
2. ordinary governance/support filters candidates;
3. mandatory verification blocks candidates;
4. unsolicited/non-required verification receipts remain diagnostic and do not alter eligibility;
5. surviving candidates proceed to ambiguity-preserving integration;
6. no survivors + at least one verification-blocked answering candidate -> `FAIL_CLOSED`;
7. no survivors only from ordinary support/governance insufficiency -> `ABSTAIN`;
8. surviving answer tie -> `ABSTAIN`.

R5 does not silently redefine separately documented failure-visibility behavior.

## 19. V1.0 compatibility

- V1.0 fixtures stay byte-identical;
- historical hashes and strategy-input digest reproduce exactly;
- new fields are omitted from V1.0 canonical projection, not serialized as defaults;
- V1.0 guard/baseline behavior remains unchanged except separately frozen earlier defects;
- V1.1 canonical projection includes profiles/claims/support/verification/requirements;
- unordered collections canonicalize by stable IDs;
- mixed fixture versions in one run are invalid.

`digest_strategy_inputs()` becomes explicitly version-aware instead of relying on unconstrained `dataclasses.asdict()`.

## 20. Explicit non-claims

Passing R5 guards does not prove:

- semantic entailment;
- correct formalization;
- experimental validity;
- statistical adequacy;
- causal identification;
- source truthfulness;
- answer validity from support-level verification;
- runtime qualification;
- general reasoning superiority.

## 21. Minimum V1.1 hostile population

Include frozen cases for:

1. `UNKNOWN` support under source requirement -> ABSTAIN;
2. admitted/current source support -> ANSWER;
3. source-free deterministic derivation -> ANSWER;
4. model judgment under deterministic requirement -> ABSTAIN;
5. heuristic laundering -> ABSTAIN;
6. empirical clean control -> ANSWER;
7. formal clean control -> ANSWER;
8. profile permits model judgment but support claims formal proof -> structural error;
9. verifier profile lacks receipt kind -> structural error;
10. deterministic derivation from non-deterministic profile -> structural error;
11. missing claim/support -> structural error;
12. multiple support records for claim -> structural error;
13. support producer ownership mismatch -> structural error;
14. retrieved-source support without source refs -> structural error;
15. stale/retrieved-only typed source support -> reject;
16. legacy candidate source refs cannot rescue stale/empty typed source support;
17. unrelated stale source does not contaminate source-free deterministic support;
18. wrong support kind -> reject;
19. legal wrong-target verification -> block candidate;
20. illegal VERIFIED receipt fields -> structural error;
21. UNAVAILABLE/FAILED/ATTEMPTED_UNKNOWN/REFUTED/NOT_RUN required verification -> block candidate;
22. legacy evidence refs + UNKNOWN support cannot satisfy typed support;
23. free-form receipt text cannot satisfy typed verification;
24. confidence/path score cannot satisfy support;
25. valid typed support + evaluator-invalid inference -> counted as invalid inference;
26. support verification cannot substitute for answer verification;
27. answer verification cannot substitute for support verification;
28. one bad candidate + one fully verified candidate -> good candidate may answer;
29. all candidates verification-blocked -> FAIL_CLOSED;
30. candidate/profile/claim/support/receipt/case order permutations preserve outcome;
31. evaluator-label permutation leaves strategy-visible digest unchanged;
32. exact-target VERIFIED receipt backed by stale verification source -> verification unsatisfied and currentness violation;
33. exact-target VERIFIED receipt backed by retrieved-only verification source -> verification unsatisfied and admission violation;
34. dangling verification source ref -> structural error;
35. verifier execution equals target candidate execution -> structural error;
36. same `(target_type, target_id, kind)` with VERIFIED and REFUTED receipts -> structural error;
37. exact-target VERIFIED receipt with hidden `verification_satisfied=false` due stale verification provenance -> counted as a false-VERIFIED hostile oracle unless blocked;
38. unsolicited exact-target REFUTED receipt with no verification requirement -> diagnostic only, clean candidate may still answer;
39. REFUTED receipt for a non-required kind -> diagnostic only and cannot candidate-local DoS.

Clean controls span source-backed, deterministic, empirical, and formal support. Always-abstain must be visibly worse than a correct guarded strategy.

## 22. Metrics

Add separate metrics:

```text
support_insufficient_acceptance
verification_unsatisfied_acceptance
mandatory_verification_fail_closed_miss
support_kind_capability_laundering
invalid_inference_acceptance
verification_source_governance_acceptance
false_verified_acceptance
unsolicited_refutation_false_block
```

Metrics use hidden candidate gold, never the production guard's own determination.

Cost remains separate from semantic metrics.

## 23. Falsification controls

Required:

- independently ablate SUPPORT_SUFFICIENCY;
- independently ablate VERIFICATION_INTEGRITY;
- each ablation worsens frozen hostile cases;
- order permutations across candidates/profiles/claims/support/receipts/cases;
- receipt-status conflict fixture proving duplicate target/kind tuples fail structurally rather than order-resolve;
- self-verifier fixture proving execution separation is enforced;
- false-VERIFIED fixture scored only from hidden evaluator gold plus independent failure evidence;
- unsolicited/non-required REFUTED fixtures proving no candidate-local denial of service;
- evaluator-label permutation;
- V1.0 digest regression;
- V1.1 digest determinism;
- always-answer reference;
- always-abstain reference;
- population disposition balance report.

## 24. Kernel boundary

R5 may extend executable `SupportKind` vocabulary only.

It does not modify Episode, ExecutionResult, NodeDescriptor runtime behavior, admission, scheduler, runner, trace, or ResultReceipt semantics.

After replay qualification, a separate Kernel design must bind execution profiles to source-controlled NodeDescriptor/runtime authority and add first-class support admission/storage.

## 25. Acceptance criteria

One exact implementation subject must prove:

1. V1.0 bytes/hashes/digest/replay unchanged;
2. V1.1 structural-invalidity table enforced;
3. trusted profiles gate every support/verification kind;
4. every answering candidate has exactly one claim/support;
5. explicit UNKNOWN/disallowed kind represents semantic unsupportedness;
6. version-aware source governance uses typed support refs in V1.1;
7. applicable verification-source refs resolve and cannot satisfy/refute through stale, retrieved-only, or unknown currentness/admission state;
8. source-required verification kinds cannot omit their source refs;
9. source-backed and source-free clean controls pass;
10. model judgment/heuristic/unknown cannot satisfy stronger policy;
11. verification truth table enforced structurally;
12. verifier execution is distinct from the target candidate execution for every attempted verification;
13. duplicate `(target_type, target_id, kind)` receipts are structural errors, so VERIFIED/REFUTED conflicts cannot order-resolve;
14. wrong-target valid verification reaches strategy and blocks only the affected candidate when the required exact target remains unsatisfied;
15. support/answer verification scopes never substitute;
16. unsolicited or non-required REFUTED receipts cannot block an otherwise eligible candidate;
17. a structurally valid exact-target VERIFIED receipt can still be rejected by independent source-governance evidence and hidden evaluator gold;
18. legacy strings cannot satisfy typed policy;
19. one bad candidate cannot globally poison a separately verified candidate;
20. no mandatory-verification survivor -> FAIL_CLOSED;
21. evaluator semantic scoring shares no production satisfaction helpers;
22. false-VERIFIED and invalid-inference cases are caught without importing production satisfaction helpers into evaluator scoring;
23. new guards are independently ablatable;
24. order permutations preserve outcomes;
25. hidden gold absent from StrategyInput/digest;
26. always-answer/always-abstain controls reported;
27. clean checkout passes full tests, compile, V1.0 replay, V1.1 replay, diff-check;
28. independent hostile review attacks capability laundering, support/verification source-governance bypass, circular verification, receipt conflict handling, target confusion, oracle coupling, unsolicited-refutation DoS, inference gaps, false abstention, and version boundaries.

## 26. Hostile roles for One

- **Capability Launderer** — emit kinds outside execution-profile authority.
- **Source-Governance Bypass Adversary** — exploit differences between legacy candidate refs and typed support refs.
- **Claim Scope Attacker** — support theft, claim smuggling, ownership mismatch.
- **Verification Target Confuser** — support/answer substitution, wrong-target receipts, receipt reuse, candidate-local DoS.
- **Verification Source Launderer** — stale/retrieved-only/dangling verification provenance behind a positive receipt.
- **Circular Verifier** — candidate self-verification and verifier/target execution aliasing.
- **Receipt Conflict Injector** — VERIFIED/REFUTED collisions for one target/kind tuple.
- **Receipt Label Oracle Attacker** — exact-target VERIFIED labels that hidden evaluator gold says are unsatisfied.
- **Unsolicited Refutation Attacker** — non-required REFUTED receipts used to try candidate-local denial of service.
- **Oracle Coupling Auditor** — find shared semantic helpers between evaluator and strategy.
- **Inference Gap Adversary** — valid typed support that does not justify the answer.
- **Reject-Everything Prosecutor** — compare to always-abstain/fail-closed and clean controls.
- **Version Boundary Adversary** — attack V1.0 identity/mixed-version/default leakage.
- **Descriptor Trust Adversary** — prove whether execution profiles can be candidate-controlled and define the future Kernel authority source.

## 27. Decision record

Chosen final design:

**trusted execution profile -> one answer claim -> one typed support record -> version-aware support-source governance -> exact-target receipts with governed verification provenance + distinct verifier execution + unique target/kind tuple -> mandatory verification requirement when present -> requirement-scoped refutation -> candidate-local filtering -> independent evaluator gold**.

Deferred intentionally:

- multi-claim candidates;
- multiple/joint support;
- semantic entailment engine;
- Kernel support state/admission;
- learned support scoring;
- live provider reasoning.

Rejected:

- missing support as a normal semantic state;
- support counts without provenance independence;
- worker-self-declared support authority;
- bidirectional support/receipt indexes;
- free-form verification parsing;
- shared evaluator/strategy semantic oracle;
- global fail-closed caused by one broken peer when another verified candidate survives;
- treating support verification as answer verification.

This final design is intentionally smaller than the original R5 proposal. It removes mechanisms that could not yet be represented honestly and closes the cross-layer source-governance gap before implementation.