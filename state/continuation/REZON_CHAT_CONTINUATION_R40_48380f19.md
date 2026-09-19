# REZON CHAT CONTINUATION — R40 / 48380f19

Restore token: `REZON::RESTORE_AND_RUN::R40::48380f19`

Recovery evidence only. This file does not authorize merge, canonical promotion,
deployment, install, activation, provider/model/credential mutation, training,
learned-routing activation, or any other protected effect.

## Operating rules

- Repository: `thebrazenbeard/rezon`.
- Patrick retains sole merge/protected-effect authority.
- Preserve failed exact subjects; do not rewrite a failed head into a pass.
- Non-PR coordination goes through `thebrazenbeard/chat-communication-bus`.
- Source/local/hosted/review/merge/install/runtime/behavior remain separate states.
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing remains CLOSED pending
  fresh exact-head Kernel acceptance.

## Current frontier — R40

Branch:
`work/rezon-kernel-v0-r40-targeted-executor-transaction`

Draft PR:
`#58`

Exact final head:
`48380f19c7e16a558d268b15a7f7f32d5473250d`

Status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Qualification:
- R40 hostile regressions: **2/2 PASS**
- focused R16-R40: **117/117 PASS**
- full suite: **246/246 PASS**
- compileall: PASS
- git diff --check: PASS
- exact-final hosted run: `35465267586` SUCCESS
- hosted job: `105956333901` SUCCESS

Qualification file:
`docs/qualification/KERNEL_V0_R40_TARGETED_EXECUTOR_TRANSACTION.md`

### R40 failure repaired

Failed whole-Kernel R39 exact subject:
`d95aac23823e4351303e737d22aeaee218cdf899`

R39 correctly preflighted visibility and independence control objects, but
target-specific executor adaptation still ran before the Episode transaction.

Frozen R40 RED:
`62618d81e65f287cb048846231dfe01cb3d5672a`

Exact-R39 RED result:
**2 failed / 0 passed**

Frozen leaks:
- attacker-controlled target attribute access during
  `hasattr(executor, "target_hypothesis_id")`;
- attacker-controlled target-specific constructor execution.

Both could mutate canonical Episode state before rollback checkpoint creation.

R40 repair:
`20cc1a4f6005e75600c4d1172dbd408cba990427`

Target probing, target-specific executor construction, executor invocation,
exact ExecutionResult validation, and canonical Episode digest verification now
all run inside `Episode.atomic_mutation()`.

CI-enablement head:
`472de840c1a84b73b316c181f3191bacf91e894c`

Executable hosted run:
`35465226677` SUCCESS

## Accepted Benchmark R4 composition

Benchmark R4 accepted source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit R40 + R4 simulation:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **305/305 PASS**
- compileall `src tests scripts`: PASS
- benchmark replay: PASS
- diff-check: PASS
- strategy-input digest:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded disposition: 21/24
- false accepts: 2
- deterministic operations: 174
- required violation hits: 9/15

No remote integration subject or merge was created.

Bus integration:
`messages/20260919T1708-one-rezon-r40-benchmark-r4-integration.md`

Bus commit:
`11b871a0aee3a18dbcf1a345b240cfce46ad29ed`

## Independent review

Exact-head request:
`messages/20260919T1709-one-rezon-r40-hostile-rereview.md`

Bus commit:
`c274d6c9517c538fd85a9ffa97754b03a0a17ac8`

Targets: MASA / MUNE / RADAR
`requires_reply: true`

At checkpoint time:
- PR #58 exact head is `48380f19...`
- PR #58 is open, draft, mergeable
- no PR review/comment has landed
- MASA tip: `0856d321c92d26eee75ad64b945ff9035c2000cf` (2026-09-18)
- MUNE tip: `8f669e39e74e79dae54793a7a6a45d615e64de32` (2026-09-18)
- Radar tip last read: `cb1ae1f83622637568d360044fcd4e59d61856ed`
- no exact R40 independent PASS/FAIL is accepted

## This restore-run advancement

Starting restored subject:
R37 `1fc9e4704e728aff8e7d8e4c44d4231202a1ddc3`

Successor failures found and preserved:

### R38 — post-transaction ExecutionResult field behavior

Failed subject:
`f2954e63d4e4a1eca90fef8275df0aebdb7600a7`

Frozen RED:
`9afb95e85f7aa9abe9002e859342ba7b72874086`

Finding:
returned result material could execute attacker behavior after the Episode
transaction had closed but before admission exact validation.

### R39 — pre-view control subobjects

Failed subject:
`d95aac23823e4351303e737d22aeaee218cdf899`

Frozen RED:
`5ca446970981ceb022cae5f90e4a81883c056393`

Finding:
VisibilityPolicy and IndependenceMetadata behavior could mutate canonical state
between digest capture and rollback checkpoint.

### R40 — targeted executor adaptation

Current successor:
`48380f19c7e16a558d268b15a7f7f32d5473250d`

Frozen predecessor RED:
`62618d81e65f287cb048846231dfe01cb3d5672a`

Finding repaired:
target-specific executor attribute access/construction occurred before rollback
checkpoint creation.

## Recent failed whole-Kernel chain

Preserve:
- R30 original `4f088c0f085df3f05bd3e59e284b4825e0e3e537`
- R30 moved repair `ac38eeed02c508fbdf10cfaf47a1e54aba326782`
- R31 `94c5547399891f46cefb85652c626ecca539ab99`
- R32 `5abcb6a3021cd61a387d322673cec0b5f8801e8e`
- R33 `c9f689cc648684a840a8ea1097db94b0c0d98d67`
- R34 `7e91323b09dda776a8b507262f1530ec786f3a5a`
- R35 `a364dbab81f748a58d9254e78e71841b0675596b`
- R36 `7c75d69682cfcb7c40c314d58b05ef26f52dd866`
- R37 `1fc9e4704e728aff8e7d8e4c44d4231202a1ddc3`
- R38 `f2954e63d4e4a1eca90fef8275df0aebdb7600a7`
- R39 `d95aac23823e4351303e737d22aeaee218cdf899`
- R40 `48380f19c7e16a558d268b15a7f7f32d5473250d` current successor,
  green locally/hosted/composition, not independently accepted.

Earlier failed chain remains preserved:
R22 `f367ef6776fa98ffe6cf455a4101674e8e244a4b`;
R23 `e3498a1ead2d9dde186c604961bb184dc3b2a764`;
R24 `0f112eda3dafa18ea81fac86b86f08978524a8a4`;
R25 `c1f445e29b56711ad451cab91f8d5e55c3817351`;
R26 `c82229f115e7bd9bd14f23ce0a975a3f034c20be`;
R27 `5d5c25197995361ecbe39d7e959feeabd2890ffe`;
R28 `f6e1da75ec62ea732e58253b4c12b0c2c87bab8b`;
R29 `8026c7932ff95bab3029b71f12686717178b818c`.

## Immediate next actions

1. Fresh-check PR #58 still exact `48380f19...`.
2. Fresh-check PR reviews/comments and MASA/MUNE/RADAR Bus replies.
3. If independent FAIL: preserve R40 and create R41 RED-first.
4. If independent PASS: record exact acceptance; do not infer merge authority.
5. If no verdict: probe only concrete effect-bearing boundaries. Candidate areas
   include any remaining behavior-bearing caller object access outside Episode
   transaction/preflight and concurrent/deferred canonical Episode mutation.
   Avoid cleanup-only typing.
6. Keep Issue #5 learned-routing CLOSED.
7. Do not merge or perform protected effects without Patrick's explicit authority.
8. Save a successor continuation whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R40::48380f19`
