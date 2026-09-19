# REZON CHAT CONTINUATION — R23 / e3498a1e

Restore token: `REZON::RESTORE_AND_RUN::R23::e3498a1e`

This is the durable recovery point for the current Rezon execution terminal.

Recovery evidence only. No merge, canonical promotion, deployment, installation, activation, provider/model mutation, training, learned-routing activation, credential/provider mutation, or other protected effect is authorized by this file.

## Canonical operating rules

- Canonical repository: `thebrazenbeard/rezon`.
- Current Kernel work must remain branch/PR based and exact-head bound.
- Preserve every failed exact subject as evidence; never rewrite a failed head into a passing one.
- Patrick is sole merge/protected-effect authority.
- All non-PR inter-agent communication goes through `thebrazenbeard/chat-communication-bus`.
- External-repo PR coordination must be mirrored/referenced on the Bus.
- Source/build/test/hosted/review/merge/install/runtime/effect/behavior are separate states.
- Do not infer independent acceptance from green local or hosted CI.
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing gate remains CLOSED until Kernel V0 receives fresh exact-head independent acceptance.

## Current Kernel frontier — R23

Branch:
`work/rezon-kernel-v0-r23-exact-task-specification`

Current exact branch head:
`e3498a1ead2d9dde186c604961bb184dc3b2a764`

Current exact tree:
`95d392326d583d22cae2c7a70dd6eee79040d1d3`

Current head message:
`docs: freeze R23 exact TaskSpecification evidence`

Current R23 status:
`SOURCE_CREATED / EXECUTABLE_GREEN / HOSTED_CI_GREEN / FINAL_DOC_HEAD_HOSTED_GREEN / FINAL_DOC_HEAD_LOCAL_REQUALIFICATION_NOT_YET_REPEATED_IN_THIS_SAVE / PR_NOT_YET_OPEN / INDEPENDENT_REREVIEW_NOT_YET_ROUTED / UNMERGED`

### R23 lineage

- failed R22 exact subject:
  `f367ef6776fa98ffe6cf455a4101674e8e244a4b`
- failed R22 tree:
  `cf29ac76c34bd12ffcd457e5a383c8fb3bc0d5e0`
- R23 RED:
  `ae58f7b753979ff4d8c35881a4bcd1c667da9e55`
- R23 executable repair:
  `348200dbe6b9186df7c9a4f41c80044b01323062`
- executable tree:
  `bddbe7d8b2e8a2c5be527ef5a050358274d6bb9c`
- CI-enablement head:
  `fd753cf4b2e7e11249a3683225dfbbac65e5aa4d`
- CI-enablement tree:
  `60d4de292f43c02a8e29ea88f60c0e07bb138074`
- documentation/final current head:
  `e3498a1ead2d9dde186c604961bb184dc3b2a764`
- final current tree:
  `95d392326d583d22cae2c7a70dd6eee79040d1d3`

### R22 failure that caused R23

R22 hardened the state-binding value against caller-controlled equality, but `task_specification: TaskSpecification | None` was still only annotation-enforced.

Fresh hostile probe supplied a non-`TaskSpecification` object with a caller-controlled `.digest`.

Observed:
- fake digest `aaaaaaaa...` admitted;
- fake digest `bbbbbbbb...` admitted;
- AdmissionReceipt reflected each fake digest;
- otherwise identical state/output produced different canonical producer IDs solely because the fake object chose a different task digest.

Disposition:
`R22_TASK_SPEC_DUCK_TYPING = FAIL / CHANGES_REQUIRED`

Bus failure record:
`messages/rezon-r22-task-spec-duck-typing-fail.md`

Bus commit:
`b6021fae63bd2ca219e26482b0a096a619a514fd`

PR #35 contains a conversation note marking R22 failed/superseded. Keep PR #35 unmerged as evidence.

### R23 frozen RED

Test file:
`tests/test_r23_exact_task_specification.py`

Exact RED:
`ae58f7b753979ff4d8c35881a4bcd1c667da9e55`

Fresh predecessor result:
- arbitrary duck-typed task object: FAIL;
- `TaskSpecification` subclass overriding digest: FAIL;
- exact `TaskSpecification`: PASS;
- explicit `None` no-task path: PASS;
- exact targeted result: **2 failed / 2 passed**.

### R23 repair

Before reading `.digest`, execution-result admission now requires:

`task_specification is None OR type(task_specification) is TaskSpecification`

Otherwise it raises `AdmissionError`.

This preserves:
- explicit `None` as the no-task-spec path;
- exact `TaskSpecification`;
- admission-derived `TaskSpecification.digest`.

It rejects:
- arbitrary duck-typed digest providers;
- `TaskSpecification` subclasses capable of overriding digest semantics.

No producer formula, canonical output digest algorithm, state-binding algorithm, concurrency control, or rollback semantics changed.

### R23 qualification already obtained

After repair on local worktree:
- focused R16-R23 controls: **24/24 PASS**
- full suite: **153/153 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact executable repair:
`348200dbe6b9186df7c9a4f41c80044b01323062`

Result:
- **153/153 PASS**
- compileall PASS
- diff-check PASS

CI-enablement head:
`fd753cf4b2e7e11249a3683225dfbbac65e5aa4d`

Qualification doc records:
- fresh clean local **153/153 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35455579743`: SUCCESS

Current final documentation head:
`e3498a1ead2d9dde186c604961bb184dc3b2a764`

Hosted exact-final run:
- run `35455659250`
- conclusion: **SUCCESS**

Qualification doc:
`docs/qualification/KERNEL_V0_R23_EXACT_TASK_SPECIFICATION.md`

Important save-time caveat:
- exact final documentation head `e3498a1e…` has hosted PASS;
- this save did not complete a new clean-local rerun specifically at `e3498a1e…`;
- executable and CI heads were already clean-local green;
- next chat should run a clean exact-local final-head qualification before calling the final subject fully local+hosted frozen.

## Immediate R23 next actions

1. Fresh-check branch head is still exactly `e3498a1ead2d9dde186c604961bb184dc3b2a764`.
2. Clean-clone exact `e3498a1e…`; run full pytest, compileall, and `git diff --check`.
3. If green, open a Draft R23 PR against failed R22 branch:
   - head: `work/rezon-kernel-v0-r23-exact-task-specification`
   - base: `work/rezon-kernel-v0-r22-exact-string-state-binding`
   - preserve R22 as failed exact evidence.
4. Route exact final R23 head to Mune/Masa/One through the Bus with `requires_reply: true`.
5. Fresh-check PR review/comments and reviewer Bus lanes.
6. Run local-only no-commit R23 + accepted Benchmark R4 composition probe.
7. Persist integration evidence on the Bus.
8. Save a successor continuation checkpoint if exact R23 identity advances.
9. Do NOT merge.
10. If independent R23 FAIL lands, preserve exact R23 and create R24 RED-first.

## Kernel failed predecessor chain

Preserve all exact failed subjects.

- R8 — TaskEnvelope context leak.
- R9 — full-envelope leak.
- R10 — task-id leak.
- R11 — dynamic-history leak through executor episode metadata / ordinal identity.
- R12 — deterministic attempt-ID collision across distinct actual executions.
- R13 — random attempt identity contaminated canonical durable state.
- R14 — canonical producer bound only to episode version counter, allowing divergent-state collision.
- R15 — retry/no-output producer/provenance ambiguity.
- R16 — cross-task producer collision / admission producer-control hardening frontier.
- R17 — optional pre-execution state binding could be omitted.
- R18 — concurrent mutation after digest check but before admission mutation.
- R19 — admission mutual exclusion without rollback left partial canonical state.
- R20 — explicit `None` state-binding bypass.
- R21 — caller-controlled equality object / `str` subclass could impersonate digest.
- R22 — duck-typed task object could inject caller-chosen task digest.
- R23 — current successor; not yet independently accepted.

## R22 exact evidence

Draft PR #35:
- exact failed head `f367ef6776fa98ffe6cf455a4101674e8e244a4b`
- tree `cf29ac76c34bd12ffcd457e5a383c8fb3bc0d5e0`
- hosted/local qualification existed before hostile failure
- Bus exact-head review request:
  `messages/rezon-kernel-r22-final-head-hostile-rereview-f367ef67.md`
- review-route Bus commit:
  `97d5c3a36846ff223e399f9785c2cdd918c19ffc`
- R22 + Benchmark R4 integration evidence:
  `messages/rezon-r22-benchmark-r4-integration-probe-f367ef67.md`
- integration Bus commit:
  `46a16048cce6424bd3dc4e093bfd73c38b40052f`
- R22 old continuation:
  branch `state/rezon-chat-continuation-r22-f367ef67`
  commit `45aab864dc8174464316098cf57eb8d09495ce45`
  Bus receipt `c746b311dc97de00f936d8ff89b0255403b7c557`

Do not promote R22.

## Benchmark R4 — accepted exact source

PR #18 / branch:
`rezon/benchmark-v1-r4-unknown-currentness`

Exact:
`d7373867d3813d32032cb30463e54a6ddf573025`

Tree:
`efbfa03efa824b65379a6cb65cb7c6353733061c`

Accepted evidence:
- Mune exact-head PASS
- hosted run `35342387478`: SUCCESS
- fresh reproduced earlier: 105/105 PASS
- compile/replay/diff PASS

Frozen vector:
- 24 cases
- strategy-input digest:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded disposition: 21/24
- false accepts: 2
- deterministic ops: 174
- required violation hits: 9/15

Known limitations remain accepted as scope:
- contradiction omission / malformed receipt false accepts;
- mandatory verifier unavailable may ABSTAIN versus gold FAIL_CLOSED;
- typed support absent;
- candidate-order permutation not corpus-wide;
- failure visibility optional peer versus mandatory verifier not fully modeled.

## Benchmark R5 design gate

Draft PR #19:
- branch `rezon/benchmark-v1-r5-typed-support-design-final`
- exact repaired design `05c668bf67349e87738990aa65f40ec07e9001e4`
- tree `8f9e2e4d5c1178d5078fd880122dd314c197abdd`
- design only
- unmerged

Old Masa hostile design review on predecessor `798b6318…` found:
- B1 verification receipt sources bypass governance;
- B2 self-verification;
- B3 conflicting receipts;
- B4 no structurally valid but semantically false VERIFIED hostile case;
- M1 unsolicited REFUTED ambiguity.

Repaired `05c668…` normatively addresses:
- governed/current verification-source refs;
- `DISTINCT_EXECUTION_REQUIRED`;
- unique `(target_type,target_id,kind)` receipt tuple;
- false-VERIFIED evaluator oracle;
- diagnostic-only unsolicited/non-required REFUTED.

Fresh exact repaired-design rereview is still pending at save time.

DO NOT IMPLEMENT R5 until the fresh exact repaired-design review clears.

## Reviewer / Bus state

Last fresh sweep before this save:
- R22 PR #35 had no review yet when it was current;
- R5 PR #19 still only carried the old Masa predecessor review plus repair comments;
- no fresh exact R5 repaired-design verdict had landed;
- Mune/Masa/One Bus branches contained historical Rezon reviews but no fresh R22 acceptance before R22 was self-failed.

R23 has not yet been routed for independent review at this save.

## Hostile probing results immediately before save

### Duplicate identical emission probe

One proposition emitted once versus the same identical proposition emitted twice:
- canonical output digest differed;
- canonical producer ID differed;
- durable Episode state/events were identical;
- trace field is explicitly `emitted_proposition_ids`, so duplicate trace entries describe exact worker emission sequence, not count of distinct durable admissions.

Disposition at save:
- NOT promoted to a defect.
- Multiplicity may legitimately be part of exact attempted-output provenance.

### Retrieval mutation boundary

`admit_retrieval_as_evidence()` performs one proposition mutation through the lock-protected Episode API.
The R19/R20 multi-object partial-transaction failure did not directly reproduce on this boundary.

### R23 task-specification bypass

This was a real defect and is the current repaired frontier.

## Current scratch/runtime

Relevant Lappy device:
`937d921e-ecc8-4dc7-bc71-dee5f06ab653`

Temporary working directories may exist:
- `%TEMP%\bt2_rezon_r22_duplicate_probe`
- `%TEMP%\bt2_rezon_r23_red`
- `%TEMP%\bt2_rezon_r23_green`

They are disposable scratch only. Durable truth is Git/Bus.

Do not treat scratch as authority after restore.

## Restore-and-run procedure

On a new chat:

1. Read this exact checkpoint first.
2. Fresh-check all named exact Git heads and PRs before carrying PASS/FAIL forward.
3. Treat the checkpoint as a starting snapshot, not current truth.
4. Continue from current R23 exact branch if unchanged.
5. Preserve all failed exact predecessor subjects.
6. Finish exact R23 final-head local qualification.
7. Open/rout the R23 Draft PR and independent hostile review if still absent.
8. Continue the RED-first hostile loop without merging.
9. Keep Benchmark R5 implementation gated on exact repaired-design rereview.
10. Keep Issue #5 learned-routing gate CLOSED until fresh exact-head Kernel acceptance.

## Restore command

`REZON::RESTORE_AND_RUN::R23::e3498a1e`

