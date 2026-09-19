# REZON CHAT CONTINUATION — R20 / 71ff317c

Restore token: `REZON::RESTORE::R20::71ff317c`

Recovery evidence only. No merge, promotion, deployment, installation, activation, provider/model mutation, training, or learned-routing authority is implied.

## Current Kernel frontier

Draft PR #33:
- branch: `work/rezon-kernel-v0-r20-transaction-rollback`
- failed R19 base: `c180441157c7fb4a52c128455237485e96884be9`
- R20 RED: `6fe033f9231fffce44c45fe39e8e91e1bdd2931f`
- executable repair: `b699b684b78b7fcdf37e6a827bde46c299a4e824`
- executable tree: `a1846d91b1955aa42fb2671aa40990cd0ede68ce`
- CI enablement: `b7370c7c3f1334960d5dc13617f4992ff10b5e4d`
- final review head: `71ff317cb2e086088866c551854e8b9e3bca708b`
- final tree: `b1daee6b5db3e3887835cd89f1072dfaeca477ae`
- draft / open / unmerged

## R19 failure preserved

Exact R19 provided mutual exclusion but failed all-or-nothing semantics.
A deterministic relation insertion failure after proposition insertion left:
- proposition current;
- relation absent;
- proposition-added event durable;
- failed admission partially committed.

Bus failure:
- `58ec4237d9aa73db52f03eb6c7366a247be4cb7c`
- `messages/rezon-r19-partial-commit-atomicity-fail.md`

## R20 repair

`Episode.atomic_mutation()` now checkpoints:
- propositions
- relations
- active proposition set
- active relation set
- events

On any BaseException it restores all five containers and re-raises.
The R19 per-Episode RLock remains in place, so successful admission is mutually exclusive and failed admission rolls back before lock release.

## Qualification

RED `6fe033f9…`:
- **2/2 FAIL as expected**.

After repair:
- focused R16-R20 controls: **17/17 PASS**
- full local: **146/146 PASS**
- compileall PASS
- diff-check PASS

Fresh exact executable `b699b684…`:
- **146/146 PASS**
- compileall PASS
- diff-check PASS

Exact CI head `b7370c7c…`:
- fresh local **146/146 PASS**
- hosted run `35452535604`: SUCCESS

Final exact `71ff317c…`:
- fresh local **146/146 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35452605864`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R20_ADMISSION_TRANSACTION_ROLLBACK.md`

Review routing:
- PR #33
- Bus commit `93fc024ebd3abc354d285a6e5cefd7d5d9d3bdd8`
- `messages/rezon-kernel-r20-final-head-hostile-rereview-71ff317c.md`
- fresh exact-head Mune/Masa/One review pending

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_146 / FINAL_R20_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Benchmark R4

Accepted exact:
- `d7373867d3813d32032cb30463e54a6ddf573025`
- frozen vector: 24 cases / digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a` / guarded 21/24 / false accepts 2 / ops 174.

R20 + R4 local-only probe:
- zero conflicts
- **205/205 PASS**
- compileall PASS
- benchmark PASS
- diff-check PASS
- benchmark vector unchanged
- Bus evidence `db7ba942c6c1f56964a43d16d333e7775b6c56b7`
- no remote integration subject

## Benchmark R5 design gate

PR #19 repaired design remains `05c668bf67349e87738990aa65f40ec07e9001e4`.
Fresh exact rereview still pending at last check.
Do not implement until that gate clears.

## Failed predecessor chain

R8 context leak -> R9 full-envelope leak -> R10 task-id leak -> R11 dynamic-history leak -> R12 attempt-ID collision -> R13 random attempt contaminated canonical state -> R14 same-version state collision -> R15 retry/no-output producer ambiguity -> R16 cross-task producer collision -> R17 optional stale-state binding bypass -> R18 concurrent TOCTOU -> R19 partial-commit failure.

Preserve every failed exact subject as evidence.

## Immediate restore actions

1. Fresh-check PR #33 exact head remains `71ff317c…`.
2. Fresh-check PR #33 reviews/comments and Bus lanes `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2`.
3. If R20 FAIL: preserve exact subject and create R21 RED-first.
4. If R20 independent PASS: record exact PASS and hold merge/integration gate; do not merge.
5. R5 implementation remains gated on fresh exact design rereview.
6. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
7. R20 rollback scope is current in-memory Episode state only; no persistence/distributed claim.
