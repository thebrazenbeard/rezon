# REZON CHAT CONTINUATION — R22 / f367ef67

Restore token: `REZON::RESTORE::R22::f367ef67`

Recovery evidence only. No merge, canonical promotion, deployment, installation, activation, provider/model mutation, training, or learned-routing authority is implied.

## Current Kernel frontier

Draft PR #35:
- branch: `work/rezon-kernel-v0-r22-exact-string-state-binding`
- failed R21 semantic base: `2075511f48c88c8b113c5afe85a9204e30f41c45`
- failed R21 tree: `3df26c4a1f6ad519e756b11a0adbe04da0bc1216`
- R22 RED: `5a7465bc97b387b9324ec4f7dfca120b4f20f001`
- executable repair: `44c86f9273da1d424207f221900de8d9f6958914`
- executable tree: `cfcc39a61a53ac06162ffdd3804bd28a32689efc`
- CI enablement: `9b18817773780acce555b8d9376a33ee118604b2`
- final review head: `f367ef6776fa98ffe6cf455a4101674e8e244a4b`
- final tree: `cf29ac76c34bd12ffcd457e5a383c8fb3bc0d5e0`
- draft / open / unmerged

R21's later branch head `73795ebef8bca7a8a1612b1ff53bcc603965bb64` is a zero-tree-delta child of `2075511f…`; R22 correctly preserves the exact failed semantic tree.

## R21 failure preserved

Exact R21 hostile probe supplied:
- an arbitrary non-string object with custom equality;
- a `str` subclass with custom equality.

Both could impersonate the canonical snapshot digest under Python equality semantics and admit stale output.

Bus failure:
- `messages/rezon-r21-custom-equality-state-binding-fail.md`

PR #34 has a conversation comment marking R21 failed and superseded by R22.

## R22 repair

Admission now requires:
`type(expected_episode_snapshot_digest) is str`

before comparing the binding to the live canonical EpisodeSnapshot digest.

This prevents caller-defined equality on arbitrary objects or `str` subclasses from participating.

## Qualification

Fresh exact RED `5a7465bc…`:
- **2/2 FAIL as expected**.

Exact executable `44c86f92…`:
- focused R16-R22 controls: **20/20 PASS**
- full suite: **149/149 PASS**
- compileall PASS
- diff-check PASS

Exact CI head `9b188177…`:
- fresh local **149/149 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35454665734`: SUCCESS

Final exact `f367ef67…`:
- fresh local **149/149 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35454763272`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R22_EXACT_STRING_STATE_BINDING.md`

Review routing:
- PR #35
- Bus commit `97d5c3a36846ff223e399f9785c2cdd918c19ffc`
- `messages/rezon-kernel-r22-final-head-hostile-rereview-f367ef67.md`
- fresh exact-head Mune/Masa/One review pending

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_149 / FINAL_R22_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Accepted Benchmark R4

Exact:
- `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`
- frozen vector: 24 cases
- digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded 21/24
- false accepts 2
- ops 174

R22 + R4 local-only integration probe:
- zero conflicts
- combined **208/208 PASS**
- compileall PASS
- benchmark PASS
- diff-check PASS
- benchmark vector unchanged
- Bus evidence commit `46a16048cce6424bd3dc4e093bfd73c38b40052f`
- no remote integration subject

## Benchmark R5 design gate

PR #19 repaired design:
- exact `05c668bf67349e87738990aa65f40ec07e9001e4`
- design only / draft / unmerged
- predecessor Masa review was on `798b6318…`
- repaired B1-B4 and M1
- fresh exact-head rereview still pending at last check
- DO NOT IMPLEMENT until exact repaired-design review clears

## Failed predecessor chain

R8 context leak -> R9 full-envelope leak -> R10 task-id leak -> R11 dynamic-history leak -> R12 attempt-ID collision -> R13 random attempt contaminated canonical state -> R14 same-version state collision -> R15 retry/no-output producer ambiguity -> R16 cross-task producer collision -> R17 optional stale-state binding bypass -> R18 concurrent TOCTOU -> R19 partial-commit failure -> R20 explicit-null state-binding bypass -> R21 caller-controlled equality bypass.

Preserve every failed exact subject as evidence.

## Immediate restore actions

1. Fresh-check PR #35 exact head remains `f367ef67…`.
2. Fresh-check PR #35 reviews/comments and Bus lanes `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2`.
3. If R22 FAIL: preserve exact subject and create R23 RED-first.
4. If R22 independent PASS: record exact PASS and hold merge/integration gate; do not merge.
5. R5 implementation remains gated on fresh exact design rereview.
6. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
7. If review remains pending, self-hostile frozen R22 without moving it unless a reproducible defect is found.
8. High-value probes:
   - duplicate identical emitted proposition/relation entries and canonical producer malleability;
   - output ordering and whether canonical production identity is intentionally order-sensitive;
   - nested atomic_mutation rollback semantics;
   - exceptions after successful writes but before AdmissionReceipt return.
