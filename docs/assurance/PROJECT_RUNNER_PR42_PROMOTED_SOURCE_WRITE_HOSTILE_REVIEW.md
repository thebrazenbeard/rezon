# Rezon Hostile Exact-Head Review — Project Runner PR #42

Reviewed repository: `thebrazenbeard/project-runner`  
Reviewed pull request: #42  
Reviewed exact head: `bbf78f1b72931745367175896f585f4c15750c2c`  
Reviewed exact base: `11bdeae62d645c6bd0ad6e2be96b03efa149e452`  
Review class: hostile exact-head promoted-source-write / request-binding / CAS / outcome review  
Review disposition: **SURVIVES_NARROWED_SOURCE_WRITE_ADAPTER**

Lantern note: the required WoWSQL project `bt2-479e4ad9` remains unavailable through the mandated read path because the connector fails internally before preflight completion. Lantern currentness is therefore **UNKNOWN** and is not substituted by Git, Project prose, or model memory. This review is source/CI/API-contract evidence only.

## Exact qualification state

At the reviewed Project Runner head:

- PR #42 is draft and mergeable;
- its base exactly equals PR #41 head `11bdeae62d645c6bd0ad6e2be96b03efa149e452`;
- exact branch readback returned `bbf78f1b72931745367175896f585f4c15750c2c`;
- CI completed successfully on this exact head;
- **297 tests passed**;
- registry validation passed;
- recursive restart proof passed;
- the workflow live-read and HC live-proof steps were skipped on this exact run and are not claimed as passing;
- no live GitHub source mutation or other protected effect was performed.

GitHub's current public GraphQL contract documents `updateRefs` as atomic and `RefUpdate.beforeOid` as requiring the reference to point to the specified OID before update. That external contract is the publication-time CAS assumption used by this adapter.

## Claim that survives

PR #42 survives only for this source-controlled adapter contract:

`PROMOTED SOURCE_WRITE + DURABLE EXACT REQUEST + ACTIVE PROMOTION/FENCE -> EXACT REGULAR-FILE GIT OBJECT CONSTRUCTION -> beforeOid REF CAS -> READBACK -> JOURNALED RESULT`

This is not live write qualification and does not establish possession of a real write-capable GitHub token, real execution/effect authority keys, or permission to mutate any live repository.

## Hostile findings closed at the reviewed head

### H1 — Mutation parameters could be substituted after promotion

A generic `SOURCE_WRITE` promotion is insufficient if the caller can choose path/content later.

**Closed.**

For `SOURCE_WRITE`, the execution-authority document now contains the complete exact mutation request. Its canonical SHA-256 must also be carried by:

- review evidence;
- protected-effect authority;
- the durable promotion receipt.

The full canonical request is persisted in `execution_promotion_requests` in the same SQLite transaction as the RUNNING promotion.

Execution recovers that durable request internally. It does not accept replacement path/content/message/head/blob parameters from the caller.

### H2 — Durable request tampering could change execution intent

**Closed against accidental/tamper-without-digest-rewrite corruption.**

The recovered request is canonically rehashed before use. A modified request JSON with the old digest fails before backend invocation.

The request digest is also part of the promotion digest.

This is integrity evidence, not protection against an actor already authorized to rewrite the database and all cross-bound digests.

### H3 — Review/effect authority could approve a generic source-write class rather than the exact write

**Closed.**

A `SOURCE_WRITE` promotion requires:

- exact execution request inside execution authority;
- exact request digest in review evidence;
- the same exact request digest in protected-effect authority.

Mismatch at any layer fails promotion.

### H4 — Contents API pre-read was not an atomic branch-head CAS

The initial adapter design reused the GitHub Contents API after a branch-head pre-read. The branch could move after that read and before commit publication.

**Closed in the reviewed head.**

The adapter now constructs Git objects from the exact expected commit/tree and publishes the commit using GraphQL `updateRefs` with:

- `name = refs/heads/<branch>`;
- `beforeOid = expected_head`;
- `afterOid = new_commit`;
- `force = false`.

The source tests assert that exact mutation shape.

GitHub's documented `updateRefs` contract states that ref updates are atomic and that `beforeOid` is a required old-ref value. The adapter therefore uses `beforeOid` as the publication-time head compare-and-swap.

### H5 — Blob-level stale write could overwrite a different file version

**Closed for the supported regular-file subset.**

The transport traverses the tree at the exact expected commit.

For an existing target:

- type must be `blob`;
- mode must be exactly `100644`;
- `expected_blob_sha` is mandatory;
- the tree's exact blob SHA must equal that value.

For a missing target:

- `expected_blob_sha` must be absent;
- the new file is created as mode `100644`.

Executable files, symlinks, submodules, trees, and other modes are rejected rather than normalized.

### H6 — Path normalization after signature verification could change the signed target

**Closed.**

The signed path must already be canonical and repo-relative.

The adapter rejects leading/trailing slash, empty segments, `.`, and `..` rather than silently normalizing them after review/authorization.

### H7 — Branch movement after the promotion gate's final live read

**Closed to the GitHub publication contract.**

The promoted execution gate still performs its live exact-head read. The adapter then independently enforces the same exact head at publication through `beforeOid`.

The hostile suite moves the branch after the gate read and before adapter publication and proves no source mutation is published.

### H8 — Failed publication could be misclassified as safely retryable

A transport failure around ref publication cannot be assumed to mean no effect.

**Closed.**

The adapter distinguishes:

- explicit `beforeOid` conflict / recognized HTTP conflict -> `PRECONDITION_FAILED`;
- unclassified GraphQL mutation error -> `OUTCOME_UNKNOWN`;
- transport uncertainty around the ref update -> `OUTCOME_UNKNOWN`;
- post-publication readback transport/mismatch -> `OUTCOME_UNKNOWN`.

An `OUTCOME_UNKNOWN` result is journaled under the original work fingerprint and fencing token. A second `execute_promoted()` call for the same attempt is refused because that attempt already has a backend result.

Blind mutation replay is therefore blocked.

### H9 — Generic GraphQL errors were initially treated as clean CAS failures

**Closed.**

Only errors explicitly identifiable as `beforeOid` mismatch are classified as clean GraphQL precondition failures.

Unclassified GraphQL errors are conservatively `OUTCOME_UNKNOWN`.

### H10 — Ref CAS rejection can still leave Git objects

**Narrowed, not eliminated.**

Blob/tree/commit objects are created before ref publication.

If `beforeOid` rejects the ref move, those objects may remain unreachable.

This does not publish the branch/source change, but it is still a storage-side artifact and therefore the claim is "no ref/source publication," not "absolutely no server-side object creation."

### H11 — Successful publication required independent readback

**Closed.**

After ref publication the transport reads back:

- branch head;
- target file;
- blob SHA;
- exact UTF-8 content.

Success requires all of them to match the newly created commit/blob/content.

Failure or uncertainty after publication becomes `OUTCOME_UNKNOWN`, not success.

### H12 — Internal transient GitHub work identity could detach the result from the original fence

**Closed.**

The promoted adapter returns its observed outcome under the original promoted work fingerprint.

`execute_promoted()` therefore journals the result under the original lineage, work fingerprint, and fencing token rather than an implementation-only transient mutation identity.

### H13 — Legacy no-request promotions could become unreadable

**Closed for no-request predecessor promotions.**

When no execution-request row exists, the reader can verify the predecessor promotion digest schema without the new nullable request field.

Request-bound `SOURCE_WRITE` promotions do not get this downgrade path.

## Remaining limits / unresolved frontiers

### R1 — No live GitHub write qualification

No real repository mutation was performed.

The reviewed tests use deterministic transports and source-level GitHub API construction. The current GitHub documentation supports the `updateRefs/beforeOid` assumptions, but this review does not prove that the actual future token/environment has:

- GraphQL mutation access;
- Git-data object creation access;
- source-write permission on the selected repository;
- the expected branch-protection interaction.

Those are installation/runtime/effect qualifications, not source qualification.

### R2 — Authority-key custody remains outside this PR

The adapter inherits PR #41's review/execution/protected-effect HMAC model.

This PR does not establish real key custody, rotation, revocation, identity governance, or possession by any live actor.

### R3 — GitHub token scope is not promoted authority

The actual GitHub token may technically be broader than one path.

The software adapter derives its target solely from the exact signed/promotion-bound request, but token/provider permissions remain a separate runtime security boundary.

### R4 — GraphQL error taxonomy is conservative but not exhaustive

Explicit `beforeOid` errors are treated as clean precondition rejection.

Everything unclassified is `OUTCOME_UNKNOWN`.

This intentionally sacrifices retry convenience rather than asserting no effect from an unfamiliar error shape.

### R5 — No durable grant revocation registry

Review/execution/effect authority remain freshness-window/key-based as in PR #41.

There is no per-grant revocation lookup immediately before publication.

### R6 — SQLite fence scope remains one state database

The source-write result is cross-bound to the local durable fence.

This does not establish distributed fencing across independent SQLite databases/hosts.

### R7 — Request-size/cost ceiling is not explicit

The adapter binds content exactly but does not introduce a separate maximum file-size or commit-message-size budget.

Provider limits and transport failure still bound actual execution, but an explicit source-write payload budget is a future hardening opportunity.

### R8 — UTF-8 regular files only

The transport constructs UTF-8 blob content and deliberately rejects existing non-`100644` modes.

Binary files, executable-bit preservation, symlinks, submodules, deletes, renames, and multi-file commits are outside V1.

### R9 — Source write is not terminal qualification

A successful adapter result is an observed backend result under the fence.

It is not by itself:

- terminal verification;
- merge;
- deployment;
- installation;
- runtime/effect qualification for downstream systems.

Existing verification/reconciliation machinery still governs later lifecycle states.

## Claim ceiling

`PR42_PROMOTED_GITHUB_SOURCE_WRITE_SURVIVES__EXACT_REQUEST_BEFOREOID_HEAD_CAS_BLOB_CAS_READBACK_AND_UNKNOWN_OUTCOME_FENCING__NO_LIVE_WRITE_AUTHORITY_OR_EFFECT_QUALIFICATION`

## Next frontier

The next bounded frontier should be **non-mutating runtime qualification of the real GitHub execution route and reconciliation contract**, without performing a source write.

That qualification should establish, using the actual configured runtime where permitted:

1. GraphQL endpoint/schema exposes `updateRefs` and `beforeOid`;
2. the runtime token can perform required read-only repository/ref/tree inspection;
3. write capability remains unexercised until separately authorized;
4. `OUTCOME_UNKNOWN` reconciliation can determine whether the promoted exact commit was published without blindly replaying the write;
5. any future live source-write qualification uses a disposable, explicitly authorized target rather than canonical source.
