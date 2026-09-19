# REZON CHAT CONTINUATION — R35 / a364dbab

Restore token: `REZON::RESTORE_AND_RUN::R35::a364dbab`

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

## Current frontier — R35

Branch:
`work/rezon-kernel-v0-r35-exact-run-episode-contract`

Draft PR:
`#51`

Exact final head:
`a364dbab81f748a58d9254e78e71841b0675596b`

Status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Qualification:
- R35 hostile regressions: **3/3 PASS**
- focused R16-R35: **102/102 PASS**
- full suite: **231/231 PASS**
- compileall: PASS
- git diff --check: PASS
- exact-final hosted run: `35463279361` SUCCESS
- hosted job: `105950846866` SUCCESS

Qualification file:
`docs/qualification/KERNEL_V0_R35_EXACT_RUN_EPISODE_CONTRACT.md`

### R35 failure repaired

Failed whole-Kernel R34 exact subject:
`7e91323b09dda776a8b507262f1530ec786f3a5a`

R34 correctly hardened run task identity, but EpisodeRunner still accepted
non-exact Episode values until admission.

Frozen R35 RED:
`1c235ea0115d7e627901c79cc2eea390c499d638`

Exact-R34 RED result:
**3 failed / 0 passed**

Critical reproduction:
- base canonical Episode state already contained hypothesis `existing`;
- deceptive Episode subclass overrode snapshot() to expose no hypotheses;
- scheduler selected `echo_hypothesis`;
- executor ran once;
- admission only then rejected the non-exact Episode.

R35 repair:
`76448dbee029405ff69924b156a79160b4914f9a`

R35 requires exact base Episode at run entry before any episode method,
scheduler, visibility projection, executor invocation, or admission. Invalid
episodes fail closed with `runner:invalid_episode_contract`.

R34's invalid-task-ID rejection path was also made independent of
`episode.snapshot()`, using diagnostic episode version
`runner:unbound_episode`.

CI-enablement head:
`66a6f984252041fc94477400c95913db16501ed7`

Executable hosted run:
`35463246567` SUCCESS

## Accepted Benchmark R4 composition

Benchmark R4 accepted source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit R35 + R4 simulation:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **290/290 PASS**
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
`messages/20260919T1526-one-rezon-r35-benchmark-r4-integration.md`

Bus commit:
`e77ba2fe47b7b869b69c96a0b97c1ccfe7eb00d8`

## Independent review

Exact-head request:
`messages/20260919T1527-one-rezon-r35-hostile-rereview.md`

Bus commit:
`87c9b81cc72df50cffa1e418d7e89de7a82cafef`

Targets: MASA / MUNE / RADAR
`requires_reply: true`

At checkpoint time:
- PR #51 exact head is `a364dbab...`
- PR #51 is open, draft, mergeable
- no PR review/comment has landed
- MASA tip: `0856d321c92d26eee75ad64b945ff9035c2000cf` (2026-09-18)
- MUNE tip: `8f669e39e74e79dae54793a7a6a45d615e64de32` (2026-09-18)
- no exact R35 independent PASS/FAIL is accepted

## Parallel Radar convergence

Radar independently found the same Episode-preflight defect on a parallel R33
base and published:
- PR #50
- exact head `9b210ffee12916a628164b50d630036329a241cf`
- hosted PASS 225/225 on that narrower subject

Radar Bus message:
`messages/20260919T1504-radar-rezon-r34-exact-episode-preflight.md`
commit:
`f713cd83885116454c7daea2d32362e4fa752124`

This independently corroborates the defect/repair direction but is NOT an
exact-head review of R35 because Radar's subject branches from R33 and does not
carry R34 task-ID hardening.

Reconciliation message:
`messages/20260919T1529-one-rezon-r35-radar-convergence-reconcile.md`
Bus commit:
`bca024ca487b496c1106f0c65c792195f5374f04`

## Recent failed whole-Kernel chain

Preserve:
- R30 original `4f088c0f085df3f05bd3e59e284b4825e0e3e537`
- R30 moved repair `ac38eeed02c508fbdf10cfaf47a1e54aba326782`
- R31 `94c5547399891f46cefb85652c626ecca539ab99`
- R32 `5abcb6a3021cd61a387d322673cec0b5f8801e8e`
- R33 `c9f689cc648684a840a8ea1097db94b0c0d98d67`
- R34 `7e91323b09dda776a8b507262f1530ec786f3a5a`
- R35 `a364dbab81f748a58d9254e78e71841b0675596b` current successor,
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

1. Fresh-check PR #51 still exact `a364dbab...`.
2. Fresh-check PR reviews/comments and MASA/MUNE/RADAR Bus replies.
3. If independent FAIL: preserve R35 and create R36 RED-first.
4. If independent PASS: record exact acceptance; do not infer merge authority.
5. If no verdict: probe only concrete effect-bearing boundaries. Candidate areas:
   exact RunnerNode visibility/control subobjects or any remaining caller-owned
   value that can cause executor invocation before a contract check. Do not
   pursue cleanup-only typing.
6. Keep Issue #5 learned-routing CLOSED.
7. Do not merge or perform protected effects without Patrick's explicit authority.
8. Save a successor continuation whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R35::a364dbab`
