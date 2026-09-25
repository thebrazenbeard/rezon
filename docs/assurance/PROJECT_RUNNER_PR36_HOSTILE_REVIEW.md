# Rezon Hostile Exact-Head Review — Project Runner PR #36

Reviewed repository: `thebrazenbeard/project-runner`  
Reviewed pull request: #36  
Reviewed exact head: `d356ff7e49c3426579ad6448faa65a0a0db1ddb2`  
Reviewed logical wave base: `e09f10c57f50fe39ccef25d398ff15a8fee8c2e5`  
Review class: hostile exact-head source review  
Review disposition: **SURVIVES_SOURCE_ADMISSION_REVIEW**

This disposition is limited to PR #36's declared claim: deterministic, bounded, source-only admission planning with immutable wave/plan bindings. It is **not** an approval to treat the planner's occupancy claims as durable lease/fencing authority.

## What survives

1. **Explicit budgets.** Global, per-identity, and per-family limits are caller-supplied and fail closed on invalid values.
2. **Deterministic ordering.** Selection order is stable for the same wave, occupied-key set, and budget tuple.
3. **Concrete collision exclusion.** Repository/workstream durable surfaces are converted into deterministic collision keys; occupied keys are checked before softer capacity limits.
4. **No-effect suppression.** HELD / preserve-only / NO_EFFECT subjects are not admitted.
5. **Effect ceiling.** Admission rejects anything above `SOURCE_ONLY`.
6. **No authority laundering.** CLI output explicitly states that it grants neither execution authority nor protected-effect authority.
7. **Family coupling is explicit.** Related repositories can be serialized through `max_per_family` without pretending family membership is equivalent to one durable resource.
8. **Live regression repair.** The same head also repairs the HC→Transcendence live proof so it snapshots the live HC head before exact-currentness verification rather than freezing a stale source fixture.

At the refreshed reviewed head, Project Runner test workflow `36061039190` completed successfully after the 67-repository / 51-public-subject wave update. The admission-budget, collision, source-only ceiling, and recursive qualification paths remain green.

## Hostile findings

### H1 — CLOSED at reviewed head: immutable wave/plan binding

The reviewed head now emits SHA-256 of the exact wave bytes, wave/corpus binding metadata, and a canonical plan digest over the complete admission payload. Integration tests recompute both digests independently.

### H2 — CLOSED at reviewed head: selected-item review/effect binding

Selected entries now bind reviewer identities, review gate, effect ceiling, action/activity state, frontier, source status, and collision keys inside the canonical plan digest.

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

`PR36_BOUND_SOURCE_ADMISSION_SURVIVES__OPERATOR_HANDOFF_REQUIRES_DURABLE_FENCE_REACQUISITION_AND_FRESH_CURRENTNESS`

## Next frontier

Bridge only the bound plan into Operator's durable admission path. The bridge must verify both digests, revalidate exact source/currentness and target authority, and acquire a fresh durable lease/fencing token rather than inheriting planner occupancy claims.


## 67-repository refresh delta

The admission planner was requalified after the public corpus grew from 48 to 49
repositories. The new `sql-connectome` subject is admitted through the same
deterministic budget/collision path and does not change the mechanical claim
ceiling.

No new dispatch authority is inferred from the refreshed head. Occupied collision
keys remain planning inputs rather than durable fences, and exact target
currentness/authority must still be reacquired by the Operator path.
