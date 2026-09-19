# REZON CHAT CONTINUATION — R19 / c1804411

Restore token: `REZON::RESTORE::R19::c1804411`

Recovery evidence only. No merge, promotion, deployment, installation, activation, provider/model mutation, training, or learned-routing authority is implied.

## Current Kernel frontier

Draft PR #32:
- branch: `work/rezon-kernel-v0-r19-atomic-admission`
- failed R18 base: `0bc280fae627684e27543ec666a8360d86055347`
- R19 RED: `7f2493388f2d9b953379df498d81a5c5b8e1dd1a`
- executable repair: `d352758e99c7239f92c6046ff2bb1233672f0cbe`
- executable tree: `73b8091cde8eaf8afa4aeb66118bb46ccfe7f8fa`
- CI enablement: `a79c769c2cb62e1e9a6780a26027d6f23c9e28bf`
- final review head: `c180441157c7fb4a52c128455237485e96884be9`
- final tree: `ed825d0857fcc7c30e05c61dcb6395447f4838e3`
- draft / open / unmerged

## R18 failure preserved

Exact R18 had a real concurrent TOCTOU window:
- caller supplied the correct mandatory pre-execution snapshot digest;
- admission verified it;
- a second thread mutated the same Episode before canonical output mutation;
- stale output was still admitted.

Bus failure:
- `f9486139b495901159973aac7780d5b5ae4dbc02`
- `messages/rezon-r18-concurrent-admission-toctou-fail.md`

## R19 repair

Each Episode now has one `threading.RLock`.

Lock-protected operations:
- snapshot
- add proposition
- retract proposition
- add relation

Episode exposes `atomic_mutation()`.

`admit_execution_result()` holds that same reentrant guard across:
- state-digest check
- validation
- prevalidation
- canonical mutation
- AdmissionReceipt construction

The deterministic thread-race regression proves a concurrent mutator cannot complete inside admission.

## Qualification

RED `7f249338…`:
- 1/1 FAIL as expected;
- predecessor observed `interleaved == [True]`.

After repair:
- focused R16-R19 controls: **15/15 PASS**
- full local: **144/144 PASS**
- compileall PASS
- diff-check PASS

Fresh exact executable `d352758e…`:
- **144/144 PASS**
- compileall PASS
- diff-check PASS

Exact CI head `a79c769c…`:
- fresh local **144/144 PASS**
- hosted run `35411074313`: SUCCESS

Final exact `c1804411…`:
- fresh local **144/144 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35411144423`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R19_ATOMIC_ADMISSION.md`

Review routing:
- PR #32
- Bus commit `8c854e0733dc2301828ac14a051e8fad13d543be`
- `messages/rezon-kernel-r19-final-head-hostile-rereview-c1804411.md`
- fresh exact-head Mune/Masa/One review pending

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_144 / FINAL_R19_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Benchmark R4

Accepted exact:
- `d7373867d3813d32032cb30463e54a6ddf573025`
- frozen vector: 24 cases / digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a` / guarded 21/24 / false accepts 2 / ops 174.

R19 + R4 local-only probe:
- zero conflicts
- **203/203 PASS**
- compileall PASS
- benchmark PASS
- diff-check PASS
- benchmark vector unchanged
- Bus evidence `36d3391928cdc9fca0785537a8b8f118cc2bbbc7`
- no remote integration subject

## Benchmark R5 design gate

PR #19 repaired design remains `05c668bf67349e87738990aa65f40ec07e9001e4`.
Fresh exact rereview still pending at last check.
Do not implement until that gate clears.

## Failed predecessor chain

R8 context leak -> R9 full-envelope leak -> R10 task-id leak -> R11 dynamic-history leak -> R12 attempt-ID collision -> R13 random attempt contaminated canonical state -> R14 same-version state collision -> R15 retry/no-output producer ambiguity -> R16 cross-task producer collision -> R17 optional stale-state binding bypass -> R18 concurrent TOCTOU.

Preserve every failed exact subject as evidence.

## Immediate restore actions

1. Fresh-check PR #32 exact head remains `c1804411…`.
2. Fresh-check PR #32 reviews/comments and Bus lanes `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2`.
3. If R19 FAIL: preserve exact subject and create R20 RED-first.
4. If R19 independent PASS: record exact PASS and hold merge/integration gate; do not merge.
5. R5 implementation remains gated on fresh exact design rereview.
6. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
7. R19 atomicity scope is in-process / one Episode object only; no cross-process/distributed claim.
