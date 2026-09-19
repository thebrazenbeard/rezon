# REZON CHAT CONTINUATION — R17 / 5369f7e1

Restore token: `REZON::RESTORE::R17::5369f7e1`

Recovery evidence only. No merge, promotion, deployment, installation, activation, provider/model mutation, training, or learned-routing authority is implied.

## Kernel frontier

Draft PR #30:
- branch: `work/rezon-kernel-v0-r17-task-bound-production-identity`
- failed R16 base: `f1dd71fb32afd8dc0a3391caa3661dab39ae3131`
- R17 RED: `da69c0386855653ffa704cd2d87b18699adf79a7`
- executable repair: `b82503294341738b4b0dc7df352f31bd482c3bbc`
- executable tree: `e6673bac9f38612a279ceb6efccd03f06fe3656c`
- CI enablement: `359da34aa588726c6e237187b54571bd9c8ec4bd`
- final review head: `5369f7e14cc8d732f3dc61717ed196c4f1b9a6ca`
- final tree: `8bd573933e0fac4278662d288d8b6051d475c452`
- draft / open / unmerged

## R16 failure preserved

Exact R16 `f1dd71fb…` allowed:
- same canonical state;
- same node/executor;
- identical durable output;
- different executor-visible TaskSpecifications;
to share one durable canonical producer ID.

Task digests differed:
- A `aef4481f9b9d85ac26bad6e2d5717bc6db62653517bf8ee4d7e14c8d0d92378e`
- B `33fbe4cec1e548f34ae297ab2267107098f2fc25ebc269b270b49ee7f630f505`

Bus failure record:
- `f0f3df58afdd56970bc8837b1f208f994d90d8f1`
- `messages/rezon-r16-cross-task-producer-provenance-fail.md`

## R17 repair

Admission still owns durable producer provenance.

Runner passes the structured executor-visible TaskSpecification into admission.

Admission computes TaskSpecification.digest internally and derives canonical producer identity from:
- validated node ID;
- canonical pre-admission EpisodeSnapshot digest;
- task-spec digest or explicit no-task-spec;
- canonical output digest.

No raw canonical producer ID or raw task digest is accepted.

AdmissionReceipt now returns task_specification_digest.

## R17 qualification

RED `da69c038…`:
- 1 failed / 1 passed as expected.
- failing case: different tasks incorrectly collided under R16.
- passing control: same task/state/output stayed deterministic.

Executable `b8250329…`:
- focused R15-R17/admission controls: **14/14 PASS**
- fresh full local: **140/140 PASS**
- compileall PASS
- diff-check PASS

CI enablement `359da34a…`:
- hosted run `35408994021`: SUCCESS

Final exact `5369f7e1…`:
- fresh local **140/140 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35409054099`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R17_TASK_BOUND_PRODUCTION_IDENTITY.md`

Review routing:
- PR #30
- Bus commit `48f70079d1179fd0d200f254cc611ff0e405cc9a`
- `messages/rezon-kernel-r17-final-head-hostile-rereview-5369f7e1.md`
- fresh exact-head Mune/Masa/One review pending

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_140 / FINAL_R17_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Benchmark R4

Accepted exact source:
- `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`
- frozen vector: 24 cases / digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a` / guarded 21/24 / false accepts 2 / ops 174.

R17 + R4 local-only integration probe:
- zero conflicts
- combined **199/199 PASS**
- compileall PASS
- benchmark PASS
- diff-check PASS
- frozen benchmark vector unchanged
- Bus evidence `fe9565bbb9b83427bb642fc91d40b28afd9365d5`
- no remote integration subject

## Benchmark R5 design gate

PR #19 exact repaired design remains:
`05c668bf67349e87738990aa65f40ec07e9001e4`

Fresh exact rereview still pending at last check. Do not implement until that gate clears.

## Failed predecessor chain

R8 context leak -> R9 full-envelope leak -> R10 task-id leak -> R11 dynamic-history leak -> R12 attempt-ID collision -> R13 random attempt contaminated canonical state -> R14 same-version state collision -> R15 no-output retry producer ambiguity -> R16 cross-task producer collision.

Preserve every failed exact subject as evidence.

## Immediate restore actions

1. Fresh-check PR #30 exact head remains `5369f7e1…`.
2. Fresh-check PR #30 reviews/comments and Bus lanes `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2`.
3. If R17 FAIL: preserve exact subject and create R18 RED-first.
4. If R17 independent PASS: record exact PASS and hold merge/integration gate; do not merge.
5. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
6. R5 implementation remains gated on fresh exact design rereview.
