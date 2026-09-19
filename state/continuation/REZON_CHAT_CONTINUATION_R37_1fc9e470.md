# REZON CHAT CONTINUATION — R37 / 1fc9e470

Restore token: `REZON::RESTORE_AND_RUN::R37::1fc9e470`

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

## Current frontier — R37

Branch:
`work/rezon-kernel-v0-r37-executor-episode-rollback`

Draft PR:
`#55`

Exact final head:
`1fc9e4704e728aff8e7d8e4c44d4231202a1ddc3`

Status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Qualification:
- R37 hostile regressions: **4/4 PASS**
- focused R16-R37: **109/109 PASS**
- full suite: **238/238 PASS**
- compileall: PASS
- git diff --check: PASS
- exact-final hosted run: `35464230715` SUCCESS
- hosted job: `105953384914` SUCCESS

Qualification file:
`docs/qualification/KERNEL_V0_R37_EXECUTOR_EPISODE_ROLLBACK.md`

### R37 failure repaired

Failed whole-Kernel R36 exact subject:
`7c75d69682cfcb7c40c314d58b05ef26f52dd866`

R36 correctly froze the preflighted RunnerNode tuple for each run, but direct
canonical Episode mutation performed from inside an executor was only detected
later by admission and therefore remained in canonical state.

Frozen R37 RED:
`edaaa4dcd4b02198939ca7b6589240ee9e6ca31b`

Exact-R36 RED result:
**4 failed / 0 passed**

Frozen leaks:
- direct proposition addition persisted;
- direct proposition retraction persisted;
- direct relation addition persisted;
- direct mutation before executor exception persisted.

R37 repair:
`746406903d7903577e3cad74b8731f2105b44afd`

Each executor call now runs inside `Episode.atomic_mutation()`. Before nominal
transaction commit, the runner recomputes the canonical Episode digest and
requires it to equal the exact pre-execution digest.

Direct canonical mutation causes an internal mutation sentinel, transaction
rollback, CONTRACT_VIOLATION, and unresolved
`executor_episode_mutation:<execution_id>`.

Executor exceptions also unwind through the Episode transaction before ordinary
ATTEMPTED_UNKNOWN handling, so direct canonical changes are rolled back.

CI-enablement head:
`7c6593b680e683fa795cc0e5a375298d1f8ef98c`

Executable hosted run:
`35464193588` SUCCESS

## Accepted Benchmark R4 composition

Benchmark R4 accepted source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit R37 + R4 simulation:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **297/297 PASS**
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
`messages/20260919T1557-one-rezon-r37-benchmark-r4-integration.md`

Bus commit:
`4287cbfb3edeedad3bf7f1ba87aa47841ed03fb0`

## Independent review

Exact-head request:
`messages/20260919T1558-one-rezon-r37-hostile-rereview.md`

Bus commit:
`f57769dbb4f80c696e37dcf2a4209af67911529a`

Targets: MASA / MUNE / RADAR
`requires_reply: true`

At checkpoint time:
- PR #55 exact head is `1fc9e470...`
- PR #55 is open, draft, mergeable
- no PR review/comment has landed
- MASA tip: `0856d321c92d26eee75ad64b945ff9035c2000cf` (2026-09-18)
- MUNE tip: `8f669e39e74e79dae54793a7a6a45d615e64de32` (2026-09-18)
- Radar tip last read: `5d72f653091ef3b3dd1cccf4be8272afcd78694e`
- no exact R37 independent PASS/FAIL is accepted

## Parallel review / provenance notes

Radar independently reproduced the earlier run-level task-ID defect on PR #52,
head `857c2a95a349ef9a58fa2c2b97fb54d05e8f770a`.
That corroborates the R34 boundary but is not an exact-head review of R37.

R35 PR #51 later received a coordinator review calling it the preferred combined
runner-preflight subject, but that review explicitly left independent hostile
rereview pending. R35 was subsequently self-failed by R36 and remains preserved.

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
- R37 `1fc9e4704e728aff8e7d8e4c44d4231202a1ddc3` current successor,
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

1. Fresh-check PR #55 still exact `1fc9e470...`.
2. Fresh-check PR reviews/comments and MASA/MUNE/RADAR Bus replies.
3. If independent FAIL: preserve R37 and create R38 RED-first.
4. If independent PASS: record exact acceptance; do not infer merge authority.
5. If no verdict: probe only concrete effect-bearing boundaries. Highest-value
   remaining targets are RunnerNode visibility/control subobjects or ordinary
   same-process state that can still influence scheduler/executor/admission
   semantics before a fail-closed check. Avoid cleanup-only typing.
6. Keep Issue #5 learned-routing CLOSED.
7. Do not merge or perform protected effects without Patrick's explicit authority.
8. Save a successor continuation whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R37::1fc9e470`
