# Rezon Hostile Exact-Head Review — Project Runner PR #41

Reviewed repository: `thebrazenbeard/project-runner`  
Reviewed pull request: #41  
Reviewed exact head: `11bdeae62d645c6bd0ad6e2be96b03efa149e452`  
Reviewed exact base: `90112cd96d11aad9e2845a064941fa5f17f9ba68`  
Review class: hostile exact-head promotion / authority / fencing / execution review  
Review disposition: **SURVIVES_NARROWED_EXECUTION_PROMOTION_GATE**

Lantern note: the required WoWSQL project `bt2-479e4ad9` remained unavailable because the connector failed internally before project readback. Lantern currentness is therefore **UNKNOWN** and is not replaced by Git, Project prose, or memory. This review is source/CI evidence only.

## Exact qualification state

At the reviewed Project Runner head:

- PR #41 is draft and mergeable;
- its base exactly equals current PR #37 head `90112cd96d11aad9e2845a064941fa5f17f9ba68`;
- both push and pull-request CI paths completed successfully;
- the stronger push path passed **280 tests**;
- registry validation passed;
- exact-head GitHub read smoke passed and returned the reviewed head;
- the recursive restart proof passed;
- the live HC -> Transcendence proof passed;
- no merge, deployment, installation, credential/permission mutation, or protected runtime effect was performed.

## Claim that survives

PR #41 survives only for the following governed path:

`EXACT CLAIMED WORK + ACTIVE FENCE + FRESH EXACT REVIEW + EXPLICIT EXECUTION AUTHORITY [+ SEPARATE EFFECT AUTHORITY] + LIVE EXACT HEAD -> DURABLE RUNNING PROMOTION`

and, for a promoted execution backend:

`DURABLE PROMOTION + RECHECKED FENCE/EXPIRIES/LIVE HEAD -> BACKEND CALL`

This does **not** establish that any current user or runtime has a real execution grant, protected-effect grant, authority-key custody, deployment authority, or effect completion.

## Hostile findings closed at the reviewed head

### H1 — CLAIMED was not execution authority

A claim/fence alone must not be promotable to backend execution.

**Closed.**

The claim continues to carry `execution_authority=false`. Promotion requires a separate HMAC-authenticated execution-authority document bound to the exact lineage, work fingerprint, fence, repository/ref/head, operation, and validity interval.

The generic admitted-work executor continues to reject claim work carrying `execution_authority=false`.

### H2 — Protected-effect authority could have been conflated with execution authority

A valid execution grant must not implicitly authorize source mutation, deployment, installation, credentials, or destructive effects.

**Closed.**

Execution and protected-effect authority are separate document schemas verified with separate keys:

- `PROJECT_RUNNER_EXECUTION_AUTHORITY_KEY`;
- `PROJECT_RUNNER_PROTECTED_EFFECT_AUTHORITY_KEY`.

A protected-effect grant cannot substitute for execution authority. An execution grant cannot authorize a protected effect by itself.

Hostile tests explicitly verify cross-key substitution fails.

### H3 — A syntactically valid effect grant could exceed the wave ceiling

The source wave is itself a hard effect ceiling.

**Closed.**

V1 cross-binds the selected wave metadata and enforces:

- `NO_EFFECT` -> `NO_PROTECTED_EFFECT` only;
- `SOURCE_ONLY` -> `NO_PROTECTED_EFFECT` or `SOURCE_WRITE`.

A signed `DEPLOY` grant still fails under a `SOURCE_ONLY` claim.

### H4 — Execution operation could diverge from the admitted wave action

Separate authority must not change what work was admitted.

**Closed.**

The execution grant's operation must exactly equal the bound selected item's wave `action`. The hostile suite signs a different operation and confirms promotion fails.

### H5 — Historical/favorable review could be reused after it became stale

Review presence is not review currentness.

**Closed.**

Promotion requires HMAC-authenticated review evidence that:

- binds exact subject/repository/ref/head/plan/work fingerprint;
- names a reviewer identity listed in the claim;
- matches the exact claim review gate;
- carries `EXECUTION_PROMOTION_REVIEWED`;
- has an active freshness interval.

Execution rechecks the durable review expiry again before backend invocation.

### H6 — Fence could expire or be replaced after claim

Promotion must use the exact currently active fence.

**Closed.**

Promotion verifies holder, current fencing token, incomplete lease, active expiry, attempt holder, and attempt/work generation before the live source read and again inside the promotion transaction.

Execution revalidates the durable fence and lease expiry before the backend call.

### H7 — Source could become stale between claim and promotion

The claim's stored head cannot be assumed current.

**Closed to the available external-read ceiling.**

Promotion performs a live read-only repository-head read and requires it to equal the stored exact commit.

The hostile suite moves the branch after claim and proves promotion remains `CLAIMED`.

### H8 — Source/review/fence could become stale after promotion but before execution

Promotion itself must not be a timeless backend pass.

**Closed to the available external-read ceiling.**

`execute_promoted()` rechecks:

- durable promotion integrity;
- exact RUNNING generation;
- exact holder/fence;
- lease expiry;
- review expiry;
- execution-authority expiry;
- protected-effect-authority expiry when required;
- live repository head.

Hostile tests prove the backend is not called when the head, fence, or review is stale.

### H9 — Promotion receipt could be forged by changing returned fields while keeping an old digest

A caller-supplied receipt must exactly reproduce durable state.

**Closed.**

The durable row's canonical digest is recomputed, a durable receipt is reconstructed, and the supplied receipt must equal it field-for-field.

The hostile suite extends a returned review expiry while retaining the old promotion digest and proves execution fails.

### H10 — Durable promotion row could be tampered

A modified SQLite promotion row must not silently authorize execution.

**Closed against accidental/tamper-without-digest-rewrite corruption.**

The promotion row carries a canonical SHA-256. A changed exact head without matching digest fails before backend invocation.

This is integrity evidence, not protection against an actor already authorized to rewrite the database and all associated state.

### H11 — Lost response after successful promotion could strand RUNNING work

A committed promotion must be reconstructible.

**Closed.**

Promotion replay detects existing RUNNING state, reconstructs and validates the durable promotion receipt, rechecks exact signed review/authority documents, active lease, and live head, then returns the same receipt.

Changed execution authority or a moved live head fails replay.

### H12 — Missing key custody could degrade into unsigned acceptance

**Closed.**

The CLI fails closed when required review or execution authority verification keys are absent. Protected-effect executions additionally require their distinct effect-authority key.

This PR does not create or configure those keys.

## Remaining limits / unresolved frontiers

### R1 — External branch movement remains non-atomic with local promotion/execution

There is no transaction spanning Git hosting and local SQLite.

The gate performs a live read immediately before promotion and again before backend invocation. A branch can still move after the final read.

Therefore any mutating backend must use the promoted exact head as its own compare-and-swap/precondition. Project Runner's GitHub backend supports exact-head mutation preconditions; future promoted adapters must preserve that property.

### R2 — Authority-key custody is outside this PR

HMAC verification proves possession of the configured key, not why that holder is authorized.

PR #41 establishes the software gate and key separation. It does not establish:

- who controls the keys;
- key rotation policy;
- revocation infrastructure;
- hardware-backed custody;
- identity-to-key governance.

No live execution-authority claim should be made until those are governed separately.

### R3 — Review signer identity is certified by the review-evidence key, not independently cryptographic per reviewer

The review document names one reviewer required by the claim, and the trusted review-evidence key authenticates the document.

V1 does not maintain distinct cryptographic keys per REZON/VOSS/ACHILLES identity.

That is acceptable for the current central review-evidence authority model but is not equivalent to independent per-reviewer signatures.

### R4 — No immediate grant revocation list

Authority and review are invalidated by expiry, key replacement/rotation, or failure of later state checks.

There is no durable grant-id revocation registry checked on every execution in V1.

Short-lived grants reduce but do not eliminate this limitation.

### R5 — SQLite fence scope remains one durable database

The exact fence is authoritative for actors sharing the same SQLite state database.

This review does not establish distributed exclusion among independent state databases or hosts. A multi-host runtime requires one shared transactional fencing authority or an equivalent distributed mechanism.

### R6 — Promoted backend contract is now explicit but real protected backend adapters remain separately qualifiable

The hostile suite uses a spy promoted backend to prove call/no-call behavior.

PR #41 does not qualify a real source-writing promoted adapter, merge adapter, deployment adapter, or credential adapter. Each such backend must preserve exact-head/effect-class authority semantics and independent readback.

### R7 — Review freshness uses issuer-declared time windows

The gate validates `reviewed_at` and `valid_until` against the runtime clock.

It does not provide an independent trusted timestamp service.

### R8 — Successful RUNNING promotion is not effect completion

A promotion receipt proves that execution preconditions passed at a specific moment.

It is not:

- backend success;
- verification success;
- merge;
- deployment;
- installation;
- runtime effect;
- terminal qualification.

Existing result/verification/reconciliation machinery remains responsible for later states.

## Claim ceiling

`PR41_CLAIMED_TO_RUNNING_GATE_SURVIVES__EXACT_FENCE_HEAD_FRESH_REVIEW_AND_SEPARATED_AUTHORITY__NO_LIVE_AUTHORITY_KEY_OR_EFFECT_QUALIFICATION`

## Next frontier

The next bounded frontier is **real promoted-backend qualification** for one explicitly chosen low-risk effect class.

The smallest defensible candidate is a source-only GitHub mutation adapter that:

1. receives `PromotedExecution`;
2. rejects any effect class except `SOURCE_WRITE`;
3. binds the exact repository/ref/head from the promotion receipt;
4. uses GitHub exact-head/blob compare-and-swap;
5. performs independent readback;
6. returns a result bound to the original work fingerprint and fencing token;
7. remains impossible without fresh promotion evidence.

That qualification must stay separate from merge/deploy/install authority.
