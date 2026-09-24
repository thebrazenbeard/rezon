# Rezon Hostile Exact-Head Review — Project Runner PR #37

Reviewed repository: `thebrazenbeard/project-runner`  
Reviewed pull request: #37  
Reviewed exact head: `90112cd96d11aad9e2845a064941fa5f17f9ba68`  
Reviewed exact base: `d356ff7e49c3426579ad6448faa65a0a0db1ddb2`  
Review class: hostile exact-head source/recovery/fencing review  
Review disposition: **SURVIVES_NARROWED_CLAIM_ONLY**

Lantern note: the required WoWSQL project `bt2-479e4ad9` could not be read because the connector failed internally before project readback. Lantern currentness is therefore **UNKNOWN** and is not substituted by Git, Project prose, or memory. This review is a Git/source/CI review only.

## Exact qualification state

At the reviewed Project Runner head:

- PR #37 is mergeable and remains draft;
- the push CI path completed successfully;
- the pull-request CI path completed successfully;
- the stronger push path passed the test suite, registry validation, live read-only GitHub smoke, recursive restart proof, and live HC→Transcendence proof;
- no merge, deployment, installation, credential/permission change, or backend project effect was performed by this review.

## Claim that survives

PR #37 survives only for:

`BOUND_PLAN_SELECTION -> EXACT_OPERATOR_BINDING -> LIVE_READ_ONLY_HEAD -> DURABLE_CLAIMED_WORK + FRESH_FENCING_TOKEN`

It does not survive as proof of execution readiness, backend authority, protected-effect authority, or runtime effect.

## Hostile findings closed at the reviewed head

### H1 — Crash between root initialization and admission

Initial implementation committed root state and then admitted in a second transaction. A crash between them orphaned a PENDING lineage because replay saw only "root execution state already exists."

**Closed.**

The durable store now has claim-only recovery that verifies the exact immutable root/budget/capability state and resumes admission from the durable PENDING root.

A regression test injects an interruption after root initialization and proves the next invocation recovers the same lineage to fencing token 1 without recreating the root.

### H2 — Crash after admission commit but before receipt

A committed CLAIMED state could previously make replay indistinguishable from duplicate execution.

**Closed for claim-only work.**

For the same holder and an unexpired lease, replay is idempotent and returns the existing exact claim/fence without adding another attempt or consuming budget again.

A different holder cannot steal the active lease.

### H3 — Expired CLAIMED lease / fencing reclaim

The initial bridge had no safe reclaim path for a claim-only lease that expired before any backend execution.

**Closed under the claim-only execution ceiling.**

Re-fencing is permitted only when:

- the exact work operation is `PORTFOLIO_BOUND_CLAIM`;
- `execution_authority=false`;
- `protected_effects_authorized=false`;
- work remained `CLAIMED`;
- the current attempt has no backend result;
- there is no verification or prior reconciliation history;
- lease token, attempt token, budget generation, work generation, and active holder cross-bind.

The expired attempt is recorded as `NO_EFFECT_CONFIRMED` before a new fencing token is issued. Budget is not consumed a second time.

### H4 — Lease and attempt rows independently valid but mutually divergent

A lease row and attempt row could each be structurally valid without being cross-bound.

**Closed.**

Recovery now requires the current lease token to equal the latest attempt token, requires attempt budget/work generations to equal durable generations, and—while held—requires lease holder to equal attempt holder.

A regression test tampers the lease holder and verifies recovery fails closed.

### H5 — `CLAIMED` confused with backend execution authority

A durable claim is a scheduling/fencing state, not permission to execute a backend.

**Closed on the governed Project Runner execution path.**

`execute_admitted()` now refuses any admitted work whose immutable payload explicitly carries `execution_authority=false`. The test backend is not called.

The bridge-created work carries that flag durably.

### H6 — Caller allowlist mislabeled as repository authority

The first bridge wording called a caller-supplied repository list "authority." The code did not prove a credential, principal grant, or repository write permission.

**Closed semantically.**

The interface is now an explicit **claim-scope allowlist** (`--allowed-repository`). Documentation states that it is not proof of repository write authority and cannot authorize protected effects.

The live GitHub action performed by the bridge remains a target-scoped read-only `READ_REF`.

## Remaining limits / unresolved frontiers

### R1 — Currentness may change after claim

The live repository head is read before the local durable claim transaction. The repository can move immediately afterward.

This is acceptable only because PR #37 does not execute the backend.

The exact head stored in the claim is evidence of the read used to form the claim, **not** a guarantee that the branch is still current at later execution time.

A future execution-promotion gate must re-read exact currentness immediately before `CLAIMED -> RUNNING`.

### R2 — Head movement inside the same plan fails closed rather than auto-superseding

If the repository head changes on replay, the exact work fingerprint changes. The existing deterministic plan lineage is not silently rewritten.

The bridge fails closed.

This is safer than replacing the subject, but automatic supersession/migration of the old claim is not implemented.

### R3 — SQLite fencing is only authoritative for actors sharing the same durable store

The fence is durable and transactional inside the exact SQLite state database.

This review does not establish a cross-host/distributed lock for independent databases. Any future multi-host Operator must use one shared transactional authority or an equivalent distributed fencing mechanism.

### R4 — Claim-only no-effect reconciliation depends on the governed execution path

Automatic `NO_EFFECT_CONFIRMED` for an expired claim is justified by:

- work remaining CLAIMED;
- immutable `execution_authority=false`;
- no result/verification history;
- the standard executor refusing that flag.

It cannot prove that arbitrary out-of-contract code with direct external credentials performed no effect. That is outside this source-controlled execution contract.

### R5 — Operator registry binding is source binding, not live external authority

The static Operator binding proves one exact schedulable project/repository/id/visibility mapping in the reviewed source.

It does not establish human authorization for a protected repository mutation. PR #37 performs no such mutation.

## Claim ceiling

`PR37_BOUND_PLAN_TO_DURABLE_CLAIM_SURVIVES__FRESH_FENCE_AND_CRASH_RECOVERY__NO_EXECUTION_READINESS_OR_PROTECTED_EFFECT_AUTHORITY`

## Next frontier

Build a separate **execution-promotion gate** for `CLAIMED -> RUNNING`.

That gate should require, at minimum:

1. exact active lease + current fencing token;
2. exact durable claim/work/attempt cross-binding;
3. a second live repository-head read matching the claim's stored exact head;
4. explicit execution authority distinct from claim scope;
5. effect-class authorization checked independently from execution authority;
6. current reviewer/review-gate evidence where the wave requires it;
7. fail-closed handling when source moved, the lease expired, or review became stale.

Backend execution must remain impossible until that promotion succeeds.
