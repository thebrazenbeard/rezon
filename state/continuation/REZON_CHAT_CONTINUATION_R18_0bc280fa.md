# REZON CHAT CONTINUATION — R18 / 0bc280fa

Restore token: `REZON::RESTORE::R18::0bc280fa`

Recovery evidence only. No merge, promotion, deployment, installation, activation, provider/model mutation, training, or learned-routing authority is implied.

## Current Kernel frontier

Draft PR #31:
- branch: `work/rezon-kernel-v0-r18-mandatory-state-binding`
- failed R17 base: `5369f7e14cc8d732f3dc61717ed196c4f1b9a6ca`
- R18 RED: `84b282344b4575f09a07df09d29b634684ce4b81`
- executable repair: `20483207680a7c80013712b4f652c8cd805906d6`
- executable tree: `e98e9662fb2524eef402947f3d7d1d8fcc8888b4`
- CI enablement: `80af2bf6715f3a80110a7cc0705d05ba831bcbe7`
- final review head: `0bc280fae627684e27543ec666a8360d86055347`
- final tree: `9b9fb6c5b889353f00f88106787aa7d190e4b5ca`
- draft / open / unmerged

## R17 failure preserved

Exact R17 allowed callers to omit `expected_episode_snapshot_digest` from public execution-result admission.

Fresh hostile probe:
- result computed from old Episode state;
- Episode changed before admission;
- caller omitted expected snapshot digest;
- stale result admitted successfully against new state.

Bus failure:
- `1a034af925872ff2b57611663cff10541efd92f0`
- `messages/rezon-r17-stale-state-omission-fail.md`

## R18 repair

`admit_execution_result()` now requires:
`expected_episode_snapshot_digest: str`

There is no default/fallback.

Admission recomputes current canonical state digest and requires exact equality before mutation.

Runner already supplies the exact digest captured from the snapshot used to build ExecutionView.

Historical direct-admission tests were updated to bind explicitly to their current Episode snapshot.

## Qualification

RED `84b28234…`:
- 1 failed / 2 passed as expected.

After repair:
- focused controls: **14/14 PASS**
- full local: **143/143 PASS**
- compileall PASS
- diff-check PASS

Fresh exact executable `20483207…`:
- **143/143 PASS**
- compileall PASS
- diff-check PASS

CI enablement `80af2bf6…`:
- hosted run `35410572521`: SUCCESS

Final exact `0bc280fa…`:
- fresh local **143/143 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35410626192`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R18_MANDATORY_ADMISSION_STATE_BINDING.md`

Review routing:
- PR #31
- Bus commit `a56b2c1a3f1cba7766e3eb458ecb8f880a7c5e71`
- `messages/rezon-kernel-r18-final-head-hostile-rereview-0bc280fa.md`
- fresh exact-head Mune/Masa/One review pending

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_143 / FINAL_R18_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Benchmark R4

Accepted exact:
- `d7373867d3813d32032cb30463e54a6ddf573025`
- frozen vector: 24 cases / digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a` / guarded 21/24 / false accepts 2 / ops 174.

R18 + R4 local-only probe:
- zero conflicts
- **202/202 PASS**
- compileall PASS
- benchmark PASS
- diff-check PASS
- benchmark vector unchanged
- Bus evidence `e6b3f857086f281738c209cb4c249c6af4c7819f`
- no remote integration subject

## Benchmark R5 design gate

PR #19 repaired design remains `05c668bf67349e87738990aa65f40ec07e9001e4`.
Fresh exact rereview still pending at last check.
Do not implement until that gate clears.

## Failed predecessor chain

R8 context leak -> R9 full-envelope leak -> R10 task-id leak -> R11 dynamic-history leak -> R12 attempt-ID collision -> R13 random attempt contaminated canonical state -> R14 same-version state collision -> R15 retry/no-output producer ambiguity -> R16 cross-task producer collision -> R17 optional stale-state binding bypass.

Preserve every failed exact subject as evidence.

## Immediate restore actions

1. Fresh-check PR #31 exact head remains `0bc280fa…`.
2. Fresh-check PR #31 reviews/comments and Bus lanes `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2`.
3. If R18 FAIL: preserve exact subject and create R19 RED-first.
4. If R18 independent PASS: record exact PASS and hold merge/integration gate; do not merge.
5. R5 implementation remains gated on fresh exact design rereview.
6. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
