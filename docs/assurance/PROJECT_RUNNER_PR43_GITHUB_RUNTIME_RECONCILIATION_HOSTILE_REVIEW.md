# Rezon Hostile Exact-Head Review — Project Runner PR #43

Reviewed repository: `thebrazenbeard/project-runner`  
Reviewed pull request: #43  
Reviewed exact head: `848c2172e6fa98cdab722b43d1ff4817990c5968`  
Reviewed exact base: `bbf78f1b72931745367175896f585f4c15750c2c`  
Review class: hostile exact-head runtime qualification / unknown-outcome reconciliation review  
Review disposition: **SURVIVES_NARROWED_READ_ONLY_RUNTIME_AND_RECONCILIATION**

## Runtime backend note

WoWSQL is retired under current live project authority.

This review does not treat WoWSQL as temporarily unavailable and does not attempt
to consult it. No successor currentness backend is inferred or installed by this
review.

## Exact qualification state

At the reviewed Project Runner head:

- PR #43 is draft and mergeable;
- its base exactly equals reviewed PR #42 head
  `bbf78f1b72931745367175896f585f4c15750c2c`;
- push CI completed successfully;
- pull-request CI completed successfully;
- **305 tests passed**;
- registry validation passed;
- recursive restart proof passed;
- push CI exact-head GitHub read smoke passed;
- push CI live HC -> Transcendence proof passed;
- the configured push-run GitHub token performed the new read-only
  `github-source-write-runtime-qualify` command successfully;
- that live qualification returned:
  - `update_refs_available=true`;
  - `before_oid_available=true`;
  - `after_oid_available=true`;
  - `force_available=true`;
  - `stable_snapshot=true`;
  - `status=PASS`;
  - `write_exercised=false`;
  - exact ref `848c2172e6fa98cdab722b43d1ff4817990c5968`;
  - exact tree `03c5fef68d71def6fa7ad5ce250e4dec5ce571b3`.

No source mutation, Git object creation, ref movement, merge, deployment,
installation, credential/permission change, or other protected effect was
performed by the qualification path.

## External API contract

GitHub's current public GraphQL Git reference documents:

- mutation `updateRefs`;
- `UpdateRefsInput.repositoryId`;
- `UpdateRefsInput.refUpdates`;
- `RefUpdate.name`;
- `RefUpdate.beforeOid`;
- `RefUpdate.afterOid`;
- `RefUpdate.force`.

The same documentation states that `updateRefs` applies updates atomically and
that `beforeOid` requires the reference to point to the specified OID before
performing the updates.

Reference:
https://docs.github.com/en/graphql/reference/git

The runtime probe validates schema visibility on the configured endpoint/token,
not write permission.

## Claim that survives

PR #43 survives only for:

`READ-ONLY REAL GITHUB ROUTE QUALIFICATION`

and

`RECORDED SOURCE_WRITE OUTCOME_UNKNOWN -> READ-ONLY RECONCILIATION`

It does not survive as a live write qualification.

## Hostile findings closed at the reviewed head

### H1 — Source-write runtime qualification existed only as mocked source tests

**Closed.**

Push CI now runs the qualification command against the configured GitHub token
and actual repository branch.

The command performs exact ref read, exact commit/tree read, GraphQL schema
introspection, and a second exact ref read.

The live run returned PASS without exercising a write.

### H2 — Schema documentation could differ from the configured endpoint/token

**Closed to read-only introspection.**

The route probes the actual GraphQL endpoint for the exact mutation/input fields
required by the adapter.

Documentation and runtime introspection now independently agree on the required
schema surface.

### H3 — Runtime qualification could mix observations across a moving branch

**Closed.**

The runtime probe uses:

`B0 ref -> exact B0 commit/tree -> schema probe -> B1 ref`

and requires B0 == B1.

A moving ref makes the qualification fail rather than producing a mixed
currentness claim.

### H4 — OUTCOME_UNKNOWN lacked enough durable evidence for later reconciliation

**Closed for PR #43-produced unknown outcomes.**

`GitHubOutcomeUnknown` now carries the candidate commit SHA and candidate blob
SHA after those objects have been constructed.

The promoted adapter journals those candidate object IDs with the
`OUTCOME_UNKNOWN` result under the original work fingerprint/fence.

Older unknown results without both candidate IDs are not silently upgraded; the
reconciler rejects them.

### H5 — Reconciliation could blindly replay the source write

**Closed.**

The source-write reconciliation path exposes no write operation.

It reconstructs durable promotion/request state, validates the request digest,
and performs only ref/file reads before recording reconciliation evidence.

No call to `put_file_exact_head`, `updateRefs`, branch creation, or file
mutation occurs.

### H6 — Reconciliation could mix a branch head from one instant with file state from another

**Closed.**

The reconciler uses:

`B0 branch head -> target file read at exact B0 commit -> B1 branch head`

If B0 != B1, the outcome is `INDETERMINATE`.

File inspection is therefore bound to the exact commit used for classification.

### H7 — Candidate publication could be falsely confirmed from path content alone

**Closed.**

`EFFECT_CONFIRMED` requires all of:

- stable B0/B1 ref snapshot;
- observed head == exact candidate commit SHA;
- target file exists at that exact candidate commit;
- target blob SHA == exact candidate blob SHA;
- exact content == the promotion-bound intended content.

A coincidentally matching path/content on a different head does not qualify.

### H8 — A reverted current branch could be misclassified as proof that no write occurred

The first reconciliation design treated an exact return to the pre-write
head/blob as `NO_EFFECT_CONFIRMED`.

That was too strong: the candidate may have been transiently published and
later reverted, with possible webhook/audit side effects.

**Closed by narrowing.**

Current pre-write-looking state now remains `INDETERMINATE`.

PR #43's GitHub source-write reconciler does not manufacture
`NO_EFFECT_CONFIRMED` from current repository state alone.

### H9 — Recorded-result reconciliation could become a generic escape hatch

**Closed.**

The durable reconciliation API still rejects recorded-result reconciliation by
default.

The explicit opt-in path is accepted only when the recorded result:

- exists;
- is failed;
- has classification exactly `OUTCOME_UNKNOWN`.

A recorded `PRECONDITION_FAILED`, success result, or any other classification
cannot use this path.

### H10 — Conclusive reconciliation could be rewritten later

**Closed by the existing journal contract.**

The reconciliation journal permits refinement only from
`INDETERMINATE`.

A conclusive reconciliation cannot be changed into another outcome by a later
call.

### H11 — An EFFECT_CONFIRMED unknown could become retryable

**Closed.**

`EFFECT_CONFIRMED` does not release the fence or move work to
`FAILED_RETRYABLE`.

The attempt remains non-retryable pending later verification/finalization.

### H12 — Current pre-write state could release the fence and permit a duplicate write

**Closed.**

Because that state remains `INDETERMINATE`, the fence/work are not released
for retry by the GitHub source-write reconciler.

## Remaining limits / unresolved frontiers

### R1 — Runtime qualification does not test write permission

The live token proved:

- repository/ref read access;
- exact commit/tree read access;
- GraphQL schema visibility.

It did **not** invoke `updateRefs`, create Git objects, or test repository write
authorization.

That is deliberate.

### R2 — Schema visibility does not establish provider authorization

Seeing `updateRefs` and `beforeOid` in introspection proves the configured
endpoint exposes those fields.

It does not prove the token can execute the mutation on a specific repository.

### R3 — No definitive no-effect proof exists for an ambiguous publication

Current repository state alone cannot prove that the candidate commit was never
temporarily published.

PR #43 correctly leaves such cases `INDETERMINATE`.

A future `NO_EFFECT_CONFIRMED` source would need stronger independent evidence,
such as provider-side mutation/audit evidence with adequate completeness.

### R4 — EFFECT_CONFIRMED is current-publication proof, not full downstream-effect proof

Exact candidate publication confirms the repository effect.

It does not prove every downstream webhook, CI, mirror, deployment, or consumer
effect.

### R5 — Reconciliation reads can still fail

Transport/API failure during B0/file/B1 read does not produce a conclusive
outcome. The command fails rather than inventing evidence.

### R6 — Runtime GitHub token authority remains an external boundary

The qualification command uses the configured token but does not inspect or
certify its complete permission set.

### R7 — SQLite fencing remains local to the shared state database

As in predecessor reviews, this does not establish distributed fencing across
independent state databases/hosts.

### R8 — WoWSQL retirement leaves no successor currentness backend established here

This review records the live retirement instruction and stops there.

No replacement is inferred from GitHub, prior Project instructions, or historical
Lantern material.

## Claim ceiling

`PR43_READ_ONLY_GITHUB_RUNTIME_ROUTE_AND_UNKNOWN_RECONCILIATION_SURVIVES__LIVE_SCHEMA_REF_TREE_PASS__NO_WRITE_PERMISSION_OR_LIVE_EFFECT_QUALIFICATION`

## Next frontier

The next bounded frontier is **effect-verification/finalization after
EFFECT_CONFIRMED**, still without performing a new write.

That layer should:

1. consume the exact conclusive reconciliation;
2. revalidate the current fence/work/promotion binding;
3. independently re-read the candidate commit/blob/content;
4. convert confirmed repository effect into the existing verification/final
   lifecycle without backend replay;
5. preserve `INDETERMINATE` as non-retryable;
6. avoid claiming downstream deployment/install effects.

A later live source-write qualification, if desired, should use a disposable,
explicitly authorized repository/ref rather than canonical project source.
