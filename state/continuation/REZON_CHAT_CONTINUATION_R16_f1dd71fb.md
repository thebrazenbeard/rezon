# REZON CHAT CONTINUATION — R16 / f1dd71fb

Restore token:

`REZON::RESTORE::R16::f1dd71fb`

Recovery evidence only. No merge, canonical promotion, deployment, installation, activation, provider/model mutation, learned-routing activation, or qualification authority is implied.

## Current Kernel frontier — R16

Draft PR #29:
- branch: `work/rezon-kernel-v0-r16-canonical-production-event-identity`
- base: failed R15 branch `work/rezon-kernel-v0-r15-canonical-state-digest-binding`
- failed R15 exact: `b6256a487727caf8e1bc0425651d8699e86afb44`
- final R16 review head: `f1dd71fb32afd8dc0a3391caa3661dab39ae3131`
- final R16 tree: `fe73a6a4d73de2c00b74f86e8e5f9344604ebee4`
- draft / open / unmerged

R16 lineage:
- production-event RED: `403260481da77711f47d9a8a6329bba8a59c6e4f`
- initial executable repair: `2f0ad4de662c45943ca38951c1103a3fb0ff47f4`
- CI enablement: `1dea29d497db8eb4878f9eec4807bb639f8a42f8`
- corrected relation regression: `315cfc367e844a762a787940e1e70ab8166c1c9b`
- failed-output regression: `d69011204e42e7dcdd017f828e35f642f0edaf33`
- admission-control RED: `227302fab81c2b17e440cb1adf239d08618c993d`
- admission-owned repair: `65a431c0410592be602e5587434e8910b9adbfc4`
- repair tree: `89db5185e02b6aaf484ecce09284810450b3dec2`
- final docs/review head: `f1dd71fb32afd8dc0a3391caa3661dab39ae3131`
- final tree: `fe73a6a4d73de2c00b74f86e8e5f9344604ebee4`

## R15 failure preserved

Fresh exact-R15 retry/no-output hostile probe:
- first actual attempt: successful no-output;
- canonical state unchanged;
- second actual attempt: same state, durable proposition output;
- actual attempt IDs differed;
- canonical input-state digests matched;
- R15 canonical producer IDs matched;
- durable proposition therefore pointed to an identity shared with a prior non-producing attempt.

Bus failure record:
- commit `f16d53e2749b04139531a1b559a71d631b8d3800`
- file `messages/rezon-r15-retry-producer-provenance-fail.md`

Do not promote R15.

## R16 provenance model

R16 separates:
1. actual attempt identity — UUID-backed, executor-facing, exact pre-admission provenance;
2. canonical input-state digest — deterministic exact pre-execution EpisodeSnapshot fingerprint;
3. canonical attempted output digest — deterministic proposition/relation output fingerprint after stripping random attempt producer IDs;
4. canonical durable producer identity — only for successfully admitted durable output.

No-output, preflight, exception, and failed-result paths have no durable canonical producer ID.

Shared implementation:
- `src/rezon/provenance.py`
- canonical EpisodeSnapshot digest
- canonical output digest
- canonical producer ID

## Admission boundary hardening

Hostile direct-admission probe against predecessor `d690112…`:
- caller supplied `canonical_producer_execution_id="forged-canonical-producer"`;
- admission accepted it;
- durable proposition producer became that arbitrary string.

Frozen admission-control RED:
- exact `227302fab81c2b17e440cb1adf239d08618c993d`
- 2/2 FAIL as expected.

Repair `65a431c…`:
- removes caller-supplied canonical producer parameter;
- admission recomputes current canonical state digest;
- admission optionally verifies runner-supplied expected pre-execution digest;
- admission computes output digest and canonical producer identity internally;
- exact opaque attempt provenance is validated before rewrite;
- mutation occurs only after validation;
- admission returns immutable AdmissionReceipt with exact provenance readback;
- runner records that receipt rather than deriving parallel durable identity.

Stale-state/TOCTOU regression:
- if Episode changes after view capture, admission rejects stale result and does not mutate with it.

## R16 qualification

Production-event RED `40326048…`:
- 3/3 FAIL as expected.

Admission-control RED `227302fa…`:
- 2/2 FAIL as expected.

Final executable repair `65a431c0…`:
- focused controls: **12/12 PASS**
- full fresh local: **138/138 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35407770031`: SUCCESS

Final exact review head `f1dd71fb…`:
- fresh clean **138/138 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35407860832`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R16_CANONICAL_PRODUCTION_EVENT_IDENTITY.md`

Review routing:
- PR #29
- Bus commit `88792b202205aca44aee8af41b7472eaf06f134e`
- file `messages/rezon-kernel-r16-final-head-hostile-rereview-f1dd71fb.md`
- requires fresh exact-head Mune/Masa/One review

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_138 / FINAL_R16_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Intermediate relation-test harness failures

Preserve but classify correctly:
- `67c36913…`, hosted `35406948888`: relation-only node was unschedulable; no production execution.
- `8f37e930…`, hosted `35407017200`: node remained outside fixed V0 scheduler rule names; no production execution.
- corrected fixture at `315cfc36…`: 134/134 local, hosted `35407072061` SUCCESS.

These are test-harness failures, not production semantic failures.

## Failed predecessor chain — preserve

- R8 `c88ab7f…`: context_refs leak
- R9 `cd7ffed…`: full TaskEnvelope authority/privacy leak
- R10 `bfcd54e…`: task_id leak
- R11 `8d30b047…`: dynamic episode-version + execution ordinal leak
- R12 `663e3aa5…`: deterministic execution-attempt identity collision
- R13 `9ff7d5c0…`: random attempt UUID contaminated deterministic canonical state
- R14 `4361191a…`: same-version divergent canonical states collided on producer identity
- R15 `b6256a48…`: no-output retry shared durable producer identity with producing attempt

Each failed subject remains evidence. Do not rewrite/promote.

## Benchmark R4 accepted exact source

PR #18:
- exact `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`
- independent exact-head PASS
- hosted run `35342387478` SUCCESS
- frozen vector:
  - 24 cases
  - digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
  - guarded 21/24
  - false accepts 2
  - ops 174
- draft/open/unmerged

R16 + R4 local-only integration probe:
- exact R16 `f1dd71fb…`
- exact R4 `d7373867…`
- common merge base `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest **197/197 PASS**
- compileall PASS
- reference benchmark PASS
- diff-check PASS
- benchmark vector unchanged
- Bus evidence commit `99135796b88eecee9ffbe6ade4e4268aef02c488`
- no remote integration branch/commit

## Benchmark R5 design gate

PR #19:
- exact repaired design `05c668bf67349e87738990aa65f40ec07e9001e4`
- design-only / draft / unmerged
- predecessor `798b6318…` got Masa CHANGES_REQUESTED
- repaired B1-B4 and M1
- fresh exact-head rereview still pending at last check
- DO NOT IMPLEMENT until fresh exact repaired-design review clears

## Lantern

Lantern currentness remains UNKNOWN unless exact WoWSQL `bt2-479e4ad9` V3 preflight -> B0 -> payload -> B1 succeeds.
Do not use Supabase fallback.

## Immediate restore actions

1. Fresh-check PR #29 remains exact `f1dd71fb…`.
2. Fresh-check PR #29 reviews/comments and `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2`.
3. If R16 FAIL/CHANGES_REQUESTED: preserve `f1dd71fb…`, create R17 successor RED-first.
4. If R16 exact independent PASS: record exact PASS and hold integration/merge gate; do not merge.
5. Fresh-check PR #19 exact repaired R5 design; implementation remains gated on fresh exact review.
6. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
7. If reviews remain pending, continue self-hostile audit of frozen R16 without moving the exact head unless a reproducible defect is found.
8. High-value R16 self-hostile checks:
   - direct admission callers omitting expected snapshot digest;
   - duplicate semantic output with different IDs/order;
   - output-order canonicalization assumptions;
   - relation/proposition mixed output;
   - admission failure after producer derivation but before mutation;
   - state change between prevalidation and actual mutation in a concurrent/malicious trusted host boundary.
