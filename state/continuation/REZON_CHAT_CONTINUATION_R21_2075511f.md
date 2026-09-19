# REZON CHAT CONTINUATION — R21 / 2075511f

Restore token: `REZON::RESTORE::R21::2075511f`

Recovery evidence only. No merge, promotion, deployment, installation, activation, provider/model mutation, training, or learned-routing authority is implied.

## Current Kernel frontier

Draft PR #34:
- branch: `work/rezon-kernel-v0-r21-nonnullable-state-binding`
- failed R20 base: `71ff317cb2e086088866c551854e8b9e3bca708b`
- R21 RED: `3e3c6fecc20cb9c7337b774aac178de2689b767d`
- executable repair: `3fc81ebd7338e2c84fcd86f317ff1172d975b5df`
- executable tree: `7f6acc07305339464cedcdd69cb68758113d1a5c`
- CI enablement: `7ccf6b3dd830938f95f5dd86a5b8253d2472b7fb`
- final review head: `2075511f48c88c8b113c5afe85a9204e30f41c45`
- final tree: `3df26c4a1f6ad519e756b11a0adbe04da0bc1216`
- draft / open / unmerged

## R20 failure preserved

Exact R20 allowed explicit `expected_episode_snapshot_digest=None` to skip state equality checking and admit stale output.

Bus failure:
- `33c6f9c4486e64b1ff04caead2482086e438aabf`
- `messages/rezon-r20-null-state-binding-fail.md`

## R21 repair

Admission now compares current canonical snapshot digest against the supplied binding unconditionally.

Therefore:
- omitted argument -> TypeError;
- explicit None -> AdmissionError;
- stale/wrong/arbitrary value -> AdmissionError;
- exact current digest -> normal admission path.

R20 rollback and R19 mutual exclusion remain unchanged.

## Qualification

RED `3e3c6fec…`:
- **1/1 FAIL as expected**.

After repair:
- focused R16-R21 controls: **18/18 PASS**
- full local: **147/147 PASS**
- compileall PASS
- diff-check PASS

Fresh exact executable `3fc81ebd…`:
- **147/147 PASS**
- compileall PASS
- diff-check PASS

Exact CI head `7ccf6b3d…`:
- fresh local **147/147 PASS**
- hosted run `35453058686`: SUCCESS

Final exact `2075511f…`:
- fresh local **147/147 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35453131243`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R21_NONNULLABLE_STATE_BINDING.md`

Review routing:
- PR #34
- Bus commit `321132896ac6c201439ef8329232c1e603c724c1`
- `messages/rezon-kernel-r21-final-head-hostile-rereview-2075511f.md`
- fresh exact-head Mune/Masa/One review pending

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_147 / FINAL_R21_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Benchmark R4

Accepted exact:
- `d7373867d3813d32032cb30463e54a6ddf573025`
- frozen vector: 24 cases / digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a` / guarded 21/24 / false accepts 2 / ops 174.

R21 + R4 local-only probe:
- zero conflicts
- **206/206 PASS**
- compileall PASS
- benchmark PASS
- diff-check PASS
- benchmark vector unchanged
- Bus evidence `4cda4b49fe2c8480ebe489550a29dac52ff79762`
- no remote integration subject

## Benchmark R5 design gate

PR #19 repaired design remains `05c668bf67349e87738990aa65f40ec07e9001e4`.
Fresh exact rereview still pending at last check.
Do not implement until that gate clears.

## Failed predecessor chain

R8 context leak -> R9 full-envelope leak -> R10 task-id leak -> R11 dynamic-history leak -> R12 attempt-ID collision -> R13 random attempt contaminated canonical state -> R14 same-version state collision -> R15 retry/no-output producer ambiguity -> R16 cross-task producer collision -> R17 optional stale-state binding bypass -> R18 concurrent TOCTOU -> R19 partial-commit failure -> R20 explicit-null state-binding bypass.

Preserve every failed exact subject as evidence.

## Immediate restore actions

1. Fresh-check PR #34 exact head remains `2075511f…`.
2. Fresh-check PR #34 reviews/comments and Bus lanes `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2`.
3. If R21 FAIL: preserve exact subject and create R22 RED-first.
4. If R21 independent PASS: record exact PASS and hold merge/integration gate; do not merge.
5. R5 implementation remains gated on fresh exact design rereview.
6. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
