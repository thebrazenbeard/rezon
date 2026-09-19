# REZON CHAT CONTINUATION — R42 / 0445e72d

Restore token: `REZON::RESTORE_AND_RUN::R42::0445e72d`

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

## Current frontier — R42

Branch:
`work/rezon-kernel-v0-r42-frozen-task-envelope`

Draft PR:
`#60`

Exact final head:
`0445e72d9d9952f8f05b8578479c5fc499166196`

Status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Qualification:
- R42 hostile regressions: **2/2 PASS**
- focused R16-R42: **122/122 PASS**
- full suite: **251/251 PASS**
- compileall: PASS
- git diff --check: PASS
- exact-final hosted run: `35467740226` SUCCESS
- hosted job: `105963058077` SUCCESS

Qualification file:
`docs/qualification/KERNEL_V0_R42_FROZEN_TASK_ENVELOPE.md`

### R42 failure repaired

Failed whole-Kernel R41 exact subject:
`48bb0b19bb947771bb31108dd9d69f4622412408`

R41 froze RunnerNode controls but reused the exact TaskEnvelope object across
executors and later iterations.

Frozen R42 RED:
`61a2f0a9dc9953f414176b224f717dc15e4e5de2`

Exact-R41 RED result:
**2 failed / 0 passed**

Frozen leaks:
- executor mutates its projected TaskEnvelope and later nodes receive changed
  TaskSpecification semantics;
- executor mutates the caller's original TaskEnvelope through an external
  reference and later nodes again receive changed task semantics;
- final receipt in both cases remains bound to the original envelope digest.

R42 repair:
`8080cc87ed1092a70b720036f2334e250f849308`

After exact validation, R42 creates a run-local governed TaskEnvelope snapshot.
Digest, task-ID, resource budget, task specification, and independence context
semantics use only that snapshot. Each non-independent executor receives a
separate envelope copy.

CI-enablement head:
`93a59e55bae8932e67d0e9339f3671e3d61e8123`

Executable hosted run:
`35467695515` SUCCESS

## Accepted Benchmark R4 composition

Benchmark R4 accepted source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit R42 + R4 simulation:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **310/310 PASS**
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
`messages/20260919T1640-one-rezon-r42-benchmark-r4-integration.md`

Bus commit:
`5c2142aa6f87b781a83e1dd25b4101ddcd4a1c3b`

## Independent review

Exact-head request:
`messages/20260919T1641-one-rezon-r42-hostile-rereview.md`

Bus commit:
`f06c554ce85e844a113681fa807ff167c6780cec`

Targets: MASA / MUNE / RADAR
`requires_reply: true`

At checkpoint time:
- PR #60 exact head is `0445e72d...`
- PR #60 is open, draft, mergeable
- no PR review/comment has landed
- MASA tip: `0856d321c92d26eee75ad64b945ff9035c2000cf` (2026-09-18)
- MUNE tip: `8f669e39e74e79dae54793a7a6a45d615e64de32` (2026-09-18)
- Radar tip: `cb1ae1f83622637568d360044fcd4e59d61856ed`
- no exact R42 independent PASS/FAIL is accepted

## This restore-run advancement

Starting restored subject:
R40 `48380f19c7e16a558d268b15a7f7f32d5473250d`

### R41 — mutable RunnerNode controls

Failed whole-Kernel subject:
`48bb0b19bb947771bb31108dd9d69f4622412408`

Frozen RED:
`a14c06e16e3e74d85cce1ecf2d55ed0f82ea501d`

Finding:
the run-local node tuple still contained original mutable RunnerNode objects.
Executor code could escalate descriptor permissions, remove a later mandatory
verifier, or replace a later executor pointer.

R41 repair:
`614cb8eb8130c2975123aff0da57e2846dee2726`

R41 qualification before successor failure:
- 3/3 R41 PASS
- 120/120 focused R16-R41 PASS
- 249/249 full suite PASS
- exact-final hosted run `35467400649` SUCCESS
- R41 + R4: 308/308 PASS

R41 was then self-failed by R42 and remains preserved draft/unmerged.

### R42 — TaskEnvelope TOCTOU

Current successor:
`0445e72d9d9952f8f05b8578479c5fc499166196`

Frozen RED:
`61a2f0a9dc9953f414176b224f717dc15e4e5de2`

Finding repaired:
the current run and executors shared the same mutable TaskEnvelope object,
allowing task semantics to change while the receipt remained bound to the
original digest.

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
- R40 `48380f19c7e16a558d268b15a7f7f32d5473250d`
- R41 `48bb0b19bb947771bb31108dd9d69f4622412408`
- R42 `0445e72d9d9952f8f05b8578479c5fc499166196` current successor,
  green locally/hosted/composition, not independently accepted.

Earlier failed chain remains preserved:
R22 `f367ef6776fa98ffe6cf455a4101674e8e244a4b`;
R23 `e3498a1ead2d9dde186c604961bb184dc3b2a764`;
R24 `0f112eda3dafa18ea81fac86b86f08978524a8a4b`;
R25 `c1f445e29b56711ad451cab91f8d5e55c3817351`;
R26 `c82229f115e7bd9bd14f23ce0a975a3f034c20be`;
R27 `5d5c25197995361ecbe39d7e959feeabd2890ffe`;
R28 `f6e1da75ec62ea732e58253b4c12b0c2c87bab8b`;
R29 `8026c7932ff95bab3029b71f12686717178b818c`.

## Immediate next actions

1. Fresh-check PR #60 still exact `0445e72d...`.
2. Fresh-check PR reviews/comments and MASA/MUNE/RADAR Bus replies.
3. If independent FAIL: preserve R42 and create R43 RED-first.
4. If independent PASS: record exact acceptance; do not infer merge authority.
5. If no verdict: probe only concrete effect-bearing boundaries. Candidate
   surfaces include any remaining run-level mutable object shared across
   iterations or executor-visible state whose mutation can change later control
   decisions without changing the bound receipt/provenance.
6. Keep Issue #5 learned-routing CLOSED.
7. Do not merge or perform protected effects without Patrick's explicit authority.
8. Save a successor continuation whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R42::0445e72d`
