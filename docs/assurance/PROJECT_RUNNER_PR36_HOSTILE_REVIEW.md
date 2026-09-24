# Rezon Hostile Exact-Head Review — Project Runner PR #36

Reviewed repository: `thebrazenbeard/project-runner`  
Reviewed pull request: #36  
Reviewed exact head: `a1aa682510b1f4029bad9d89328f0e0f65af114e`  
Reviewed base: `4f43e594b6cb57ce1c8820fd4fafff11e0e11641`  
Review class: hostile exact-head source review  
Review disposition: **SURVIVES_NARROWED**

This disposition is limited to PR #36's declared claim: deterministic, bounded, source-only admission planning. It is **not** an approval to feed the current CLI output directly into durable Operator dispatch.

## What survives

1. **Explicit budgets.** Global, per-identity, and per-family limits are caller-supplied and fail closed on invalid values.
2. **Deterministic ordering.** Selection order is stable for the same wave, occupied-key set, and budget tuple.
3. **Concrete collision exclusion.** Repository/workstream durable surfaces are converted into deterministic collision keys; occupied keys are checked before softer capacity limits.
4. **No-effect suppression.** HELD / preserve-only / NO_EFFECT subjects are not admitted.
5. **Effect ceiling.** Admission rejects anything above `SOURCE_ONLY`.
6. **No authority laundering.** CLI output explicitly states that it grants neither execution authority nor protected-effect authority.
7. **Family coupling is explicit.** Related repositories can be serialized through `max_per_family` without pretending family membership is equivalent to one durable resource.
8. **Live regression repair.** The same head also repairs the HC→Transcendence live proof so it snapshots the live HC head before exact-currentness verification rather than freezing a stale source fixture.

At the reviewed head, Project Runner's branch test path passed 241 tests, registry validation, GitHub read smoke, recursive restart proof, and the live HC→Transcendence proof.

## Hostile findings

### H1 — Admission output is not immutably bound to its source wave

The CLI emits selected/deferred subjects and budgets, but it does not emit a digest of the exact wave bytes or a canonical plan digest.

Consequence: a durable consumer cannot independently prove that a later admission record came from the same wave bytes that were reviewed.

Required before Operator handoff:
- exact wave SHA-256;
- wave id / generated-at / corpus binding;
- deterministic plan digest over all selected/deferred entries plus budget and occupied-key inputs.

### H2 — Selected entries omit review/effect handoff metadata

Selected entries currently omit:
- `reviewer_identities`;
- `review_gate`;
- `effect_ceiling`;
- `frontier`;
- `source_status`.

Consequence: a durable consumer would need to reload mutable source context to reconstruct why a subject was admissible and what review/effect ceiling applies.

Required before Operator handoff: bind these fields into each admitted item or into a canonical selected-item fingerprint.

### H3 — Occupied collision keys are claims, not durable fences

The planner accepts `--occupied-collision-key` strings but does not establish their owner, generation, lease expiry, or fencing token.

This is acceptable for planning only. It is insufficient for dispatch.

Required Operator rule: the durable dispatch path must independently acquire/verify the lease and fencing token; it must never infer ownership from planner occupancy input.

### H4 — Planner currentness is intentionally incomplete

The planner does not independently revalidate:
- repository exact head;
- branch/ref authority;
- reviewer freshness;
- provider/runtime effect authority.

This is consistent with the documented claim ceiling, but it is a hard boundary.

Required Operator rule: selected status is only a scheduling disposition. Exact currentness and target authority must be re-established immediately before durable claim/admission.

### H5 — Surface classification is intentionally heuristic

Collision-key classification treats strings shaped like `owner/repo` as repository keys and other strings as generic surfaces.

This survives for the current public corpus because its durable surfaces use the expected forms. It is not a general typed-resource parser.

Required future hardening if new surface types are admitted: introduce explicit durable-surface kinds rather than extending string heuristics.

## Claim ceiling

`PR36_DETERMINISTIC_BOUNDED_SOURCE_ADMISSION_SURVIVES__OPERATOR_HANDOFF_REQUIRES_IMMUTABLE_PLAN_BINDING_AND_DURABLE_FENCE_REACQUISITION`

## Next frontier

Harden Project Runner's admission output with immutable wave/plan bindings and selected-item review/effect metadata. Then bridge only that bound plan into Operator's durable admission path, where leases/fencing/currentness/authority are re-established rather than inherited from the planner.
