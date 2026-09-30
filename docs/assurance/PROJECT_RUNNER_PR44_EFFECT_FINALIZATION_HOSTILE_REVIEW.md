# Rezon Hostile Exact-Head Review — Project Runner PR #44

Reviewed repository: `thebrazenbeard/project-runner`  
Reviewed pull request: #44  
Reviewed exact head: `6c8e6827a204380b40b7c7fa07d785ca53cec136`  
Reviewed exact base: `848c2172e6fa98cdab722b43d1ff4817990c5968`  
Disposition: **SURVIVES_NARROWED_EFFECT_CONFIRMED_FINALIZATION**

WoWSQL is retired under current live project authority and is not consulted or treated as a fallback.

## Exact qualification

- PR #44 is draft, mergeable, and exactly stacked on PR #43.
- Push and pull-request CI pass.
- **317 tests pass.**
- Registry validation passes.
- Exact-head GitHub read smoke passes.
- Read-only GitHub SOURCE_WRITE route qualification passes with `write_exercised=false`.
- Recursive restart proof passes.
- Live HC -> Transcendence proof passes.
- No live source write, merge, deployment, installation, release, credential/permission mutation, or other protected effect was performed.

## Surviving claim

`DURABLE EFFECT_CONFIRMED + EXACT PROMOTION/REQUEST/FENCE + TWO-STAGE CURRENT CANDIDATE READBACK -> VERIFYING -> COMPLETE`

with no backend replay.

## Hostile findings

### H1 — EFFECT_CONFIRMED alone could be treated as terminal verification

**Closed.**

The finalizer independently revalidates the promotion/request/result/reconciliation/fence and re-reads the exact candidate commit/blob/content.

### H2 — RUNNING could jump directly to COMPLETE

**Closed.**

Project Runner's lifecycle invariant is preserved:

`RUNNING gN -> VERIFYING gN+1 -> COMPLETE gN+2`.

The first implementation attempt correctly failed CI on the invalid direct transition and was repaired without weakening the state machine.

### H3 — The source could move after entering VERIFYING

**Closed.**

A second independent stable candidate readback occurs after the durable VERIFYING checkpoint. Head, blob, or content drift prevents COMPLETE.

### H4 — Fence could expire during verification

**Closed.**

The active exact lease is checked before readback, again before entering VERIFYING, again after the second readback, and inside the terminal SQLite transaction.

### H5 — Lost response after RUNNING -> VERIFYING could cause a duplicate execution

**Closed.**

`begin_verification()` is idempotent only for the exact work already at the one expected successor generation under the same active fence. Resume performs readback/finalization only; the backend is never replayed.

### H6 — Lost response after COMPLETE could make a finished effect operationally ambiguous

**Closed.**

Terminal replay reconstructs the receipt only when all of these still cross-bind:

- exact completed generation;
- exact completed holder/fencing token;
- validated terminal verification digest/status/reason;
- promotion;
- execution request;
- EFFECT_CONFIRMED reconciliation.

The returned receipt is marked `finalization_replayed=true`, performs no GitHub read, and performs no backend effect.

This replay is historical/idempotent and is not a claim that the candidate remains current at replay time.

### H7 — Reconciliation journal tampering could authorize completion

**Closed against tamper-without-digest-rewrite corruption.**

The latest reconciliation is loaded through validated canonical digest verification before its outcome is accepted.

### H8 — Original OUTCOME_UNKNOWN backend result could be rewritten into success

**Closed.**

The original result remains `OUTCOME_UNKNOWN`. Terminal COMPLETE is justified by the separate conclusive reconciliation plus two-stage independent verification, not by rewriting execution history.

### H9 — Repository source completion could be laundered into deployment/install completion

**Closed by claim ceiling.**

Terminal verification is scoped to the exact GitHub source effect only. No downstream deployment, installation, activation, release, webhook, credential, or permission effect is claimed.

## Remaining limits

1. A later source movement after terminal verification does not invalidate the historical terminal receipt; currentness must be checked separately.
2. SQLite fencing remains scoped to actors sharing the same durable database.
3. HMAC authority-key custody/revocation remains outside this layer.
4. The live GitHub write path itself is still not effect-qualified on a disposable target; this stack qualifies source logic and read-only runtime visibility.
5. Terminal source verification does not prove every downstream consumer observed the source change.

## Claim ceiling

`PR44_EFFECT_CONFIRMED_FINALIZATION_SURVIVES__TWO_STAGE_EXACT_READBACK_FENCE_AND_REPLAY_SAFE__SOURCE_EFFECT_ONLY`

## Next portfolio frontier

Return to the Project Runner portfolio wave and advance live P0 subjects from current source evidence, beginning with independent families where possible. BT2's current live frontier is no longer WoWSQL resilience: PR #49 proposes the source transition from retired WoWSQL to PostgreSQL V4 and must be reviewed as a source/runtime-contract migration, not treated as installed effect.
