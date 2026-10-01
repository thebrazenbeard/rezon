# Hostile Exact-Head Review — DriftGuard PR #40 Effect Reservation Fence

Reviewed repository: `thebrazenbeard/driftguard`  
Reviewed PR: #40  
Reviewed exact head: `33b75523a1130c614c270f3de45417e1acf4e32b`  
Reviewed exact base: `52fa829c629fa0f3e729204912db9f9f783f322a`

Review class: source-recorded hostile exact-head review. This does not claim a separately executed external-model review.

## Disposition

`SURVIVES_NARROWED`

The candidate survives as a local durable reservation/fence mechanism only. It does not establish provider-effect authority, provider I/O, distributed coordination, retry authority, deployment, runtime activation, behavioral recovery, or external currentness.

## Mechanical invariants reviewed

### 1. Reservation currentness and reservation write are atomic

`reserve_effect_attempt(...)` opens one SQLite connection, executes `BEGIN IMMEDIATE`, validates the exact session/evaluation/state/generation/subject currentness inside that transaction, rejects reused attempt IDs and an existing unresolved session fence, then writes both `effect_attempts` and `effect_fences` before returning the receipt.

The public wrapper `reserve_reload_effect_attempt(...)` first validates the exact `ReloadDirective` / `SaveState` / monitored-subject static binding and passes `directive.digest` into the ledger reservation. The ledger is therefore not being handed an unrelated caller-provided label by the supported wrapper.

### 2. One unresolved fence per session is enforced twice

The code checks for an existing fence before insert, and the schema also makes `effect_fences.session_id` the primary key. `attempt_id` is unique as well. SQLite foreign keys are explicitly enabled on every connection.

### 3. Cancellation is pre-dispatch only

`cancel_effect_attempt(...)` requires status `RESERVED`, verifies exact fence ownership, performs a compare-and-swap to `CANCELLED_BEFORE_DISPATCH`, and deletes the matching fence in the same immediate transaction.

Once an attempt has left `RESERVED`, this cancellation path cannot release the fence.

### 4. Dispatch claim is single-use and fence-preserving

`claim_effect_dispatch(...)` requires the exact active fence and atomically changes only:

`RESERVED -> DISPATCH_UNCERTAIN`

A second claim fails because the status is no longer `RESERVED`. The fence is intentionally retained.

That means a crash after the durable claim does not recreate retry authority. The trade-off is deliberate fail-closed liveness loss until a later effect-aware reconciliation path exists.

### 5. Generic acknowledgement cannot bypass the unresolved fence

`acknowledge_reload(...)` runs under `BEGIN IMMEDIATE` and rejects any session with an active effect fence before advancing generation.

The ordinary acknowledgement route therefore cannot skip around an unresolved protected-effect attempt.

## Exact-head executable evidence

On `33b75523a1130c614c270f3de45417e1acf4e32b`:

- `tests` run `35940813596`: PASS
- `action-smoke` run `35940813553`: PASS
- `CodeQL Advanced` run `35940813564`: PASS

The changed paths are limited to:

- `docs/EFFECT_RESERVATION_FENCE_V1.md`
- `src/driftguard/external_boundary.py`
- `src/driftguard/ledger.py`
- `tests/test_effect_fence.py`

## Hostile challenges

> Does possession of `EffectDispatchPermit` prove protected-effect authority?

No. The permit is an in-process mechanical token guarded by a module-private object, not a cryptographic or cross-process capability. Python private/module internals are not a security boundary. The code and documentation correctly narrow its claim to `MECHANICAL_SINGLE_USE_DISPATCH_PERMIT_ONLY`. A future provider adapter must separately verify current protected-effect authority.

> Does `DISPATCH_UNCERTAIN` prove an effect occurred?

No. It means the local dispatch claim was durably consumed. It deliberately says nothing about provider receipt, provider honesty, network delivery, idempotency, or applied state.

> Can the system recover automatically after a crash in `DISPATCH_UNCERTAIN`?

Not in this slice. The retained fence intentionally blocks ordinary acknowledgement and retry. Future provider readback/reconciliation is required before safe fence release. This is a liveness limitation, but it is fail-closed rather than an authority escalation.

> Is SQLite locking a distributed lock?

No. `BEGIN IMMEDIATE` plus the schema constraints provide local database serialization for this ledger. No distributed-locking claim survives this review.

## Remaining limits

1. No provider network adapter is implemented here.
2. No protected-effect authority verifier is implemented here.
3. No authenticated provider outcome/readback path is implemented here.
4. No post-dispatch resolution states such as VERIFIED_APPLIED, VERIFIED_NOT_APPLIED, or QUARANTINED_UNRESOLVED are implemented.
5. No retry authorization exists.
6. No deployment/runtime effect is established.
7. The in-process permit must never be promoted into a trust root by downstream adapters.

## Claim ceiling

`DRIFTGUARD_PR40_33B75523_SURVIVES_NARROWED__LOCAL_DURABLE_EFFECT_RESERVATION_AND_SINGLE_USE_DISPATCH_FENCE_ONLY__NO_PROVIDER_AUTHORITY__NO_RUNTIME_EFFECT`
