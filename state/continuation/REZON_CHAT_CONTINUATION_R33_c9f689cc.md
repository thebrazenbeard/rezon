# REZON CHAT CONTINUATION — R33 / c9f689cc

Restore token: `REZON::RESTORE_AND_RUN::R33::c9f689cc`

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

## Current frontier — R33

Branch:
`work/rezon-kernel-v0-r33-exact-runner-budget-contract`

Draft PR:
`#47`

Exact final head:
`c9f689cc648684a840a8ea1097db94b0c0d98d67`

Status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Qualification:
- R33 hostile regressions: **3/3 PASS**
- focused R16-R33: **95/95 PASS**
- full suite: **224/224 PASS**
- compileall: PASS
- git diff --check: PASS
- exact-final hosted run: `35462633622` SUCCESS
- hosted job: `105949112090` SUCCESS

Qualification file:
`docs/qualification/KERNEL_V0_R33_EXACT_RUNNER_BUDGET_CONTRACT.md`

### R33 failure repaired

Failed whole-Kernel R32 exact subject:
`5abcb6a3021cd61a387d322673cec0b5f8801e8e`

R32 correctly bound scheduling to a fresh internal DeterministicScheduler, but
`EpisodeRunner.budget_limit` remained unvalidated.

Frozen R33 RED:
`fbf1b330a5ad24efee6674392057b923ce50b548`

Exact-R32 RED result:
**3 failed / 0 passed**

Critical reproduction:
- exact TaskEnvelope `resource_budget=0`
- hostile duck runner budget with caller-controlled comparisons
- executor still invoked
- canonical proposition `ran` admitted
- no failure reported

Also reproduced by post-construction mutation and by an int subclass.

R33 repair:
`7675b0311c63ba23d17cc682f1658ab0328a5124`

R33 requires runner budget to be exact built-in non-negative int before
effective-budget calculation, scheduler creation, or executor invocation.
Invalid values fail closed with:
`runner:invalid_budget_contract`.

CI-enablement head:
`eddf5473177800edfae675fb0c64048a22c28cd8`

Executable hosted run:
`35462602973` SUCCESS

## Accepted Benchmark R4 composition

Benchmark R4 accepted source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit R33 + R4 simulation:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **283/283 PASS**
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
`messages/20260919T1505-one-rezon-r33-benchmark-r4-integration.md`

Bus commit:
`b3f1383fc136a4a18a19ec1dec33d13336dcae8e`

## Independent review

Exact-head request:
`messages/20260919T1506-one-rezon-r33-hostile-rereview.md`

Bus commit:
`5eaeb9f676fe2f0912851f88f352480d3819d192`

Targets: MASA / MUNE / RADAR
`requires_reply: true`

At checkpoint time:
- PR #47 exact head is `c9f689cc...`
- PR #47 is open, draft, mergeable
- no PR review/comment has landed
- MASA tip: `0856d321c92d26eee75ad64b945ff9035c2000cf` (2026-09-18)
- MUNE tip: `8f669e39e74e79dae54793a7a6a45d615e64de32` (2026-09-18)
- no exact R33 independent PASS/FAIL is accepted

## Recent failed whole-Kernel chain

Preserve these exact subjects:
- R30 original `4f088c0f085df3f05bd3e59e284b4825e0e3e537`
  — scheduler-to-execution RunnerNode substitution.
- R30 moved repair `ac38eeed02c508fbdf10cfaf47a1e54aba326782`
  — TaskEnvelope subclass/task-spec context smuggling.
- R31 `94c5547399891f46cefb85652c626ecca539ab99`
  — mutable public scheduler bypass of mandatory verifier.
- R32 `5abcb6a3021cd61a387d322673cec0b5f8801e8e`
  — runner budget override of exact zero envelope budget.
- R33 `c9f689cc648684a840a8ea1097db94b0c0d98d67`
  — current successor, green locally/hosted/composition, not independently accepted.

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

1. Fresh-check PR #47 still exact `c9f689cc...`.
2. Fresh-check PR reviews/comments and MASA/MUNE/RADAR Bus replies.
3. If independent FAIL: preserve R33 and create R34 RED-first.
4. If independent PASS: record exact acceptance; do not infer merge authority.
5. If no verdict: probe only concrete effect-bearing boundaries. Highest-value
   candidate is the runner call's `task_id` exact identity contract if custom
   equality/type semantics can cause unauthorized execution or misbinding.
6. Avoid cleanup-only typing.
7. Keep Issue #5 learned-routing CLOSED.
8. Do not merge or perform protected effects without Patrick's explicit authority.
9. Save a successor continuation whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R33::c9f689cc`
