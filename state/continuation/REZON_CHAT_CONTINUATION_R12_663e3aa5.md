# REZON CHAT CONTINUATION — R12 / 663e3aa5

Restore token:

`REZON::RESTORE::R12::663e3aa5`

This checkpoint is continuation/recovery state only. It is NOT merge authority, canonical promotion, deployment, installation, activation, provider/model mutation, learned-routing activation, or qualification.

## Operating rules

- repo: `thebrazenbeard/rezon`
- live user instruction > this checkpoint
- fresh exact Git/PR/Bus state > this checkpoint
- non-PR coordination uses `thebrazenbeard/chat-communication-bus`
- preserve failed exact subjects as evidence; repair on successors
- source/build/test/hosted/review/merge/install/runtime/effect/behavior remain separate
- green tests/CI never substitute for semantic review
- no merge/deploy/install/provider/model/credential/learned-routing/protected effect without Patrick's exact authority
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing gate remains CLOSED until Kernel V0 receives fresh exact-head independent acceptance

## Current Kernel frontier — R12

Draft PR #25:
- title: `P0 R12: isolate strong-independent dynamic history metadata`
- branch: `work/rezon-kernel-v0-r12-episode-version-isolation`
- base: failed R11 branch `work/rezon-kernel-v0-r11-task-spec-boundary`
- failed R11 exact: `8d30b04728488d0d1fcc3bb9d176e77c49923478`
- failed R11 tree: `58cfd2b0f0254c16d1b1605263016b2cd667e189`
- R12 final review head: `663e3aa5fbb4f8ca2751a2c792a100303070ec35`
- R12 final tree: `d0364b00cd3728717788b2159ab4e64ec4724db1`
- draft / open / mergeable / unmerged at last fresh read

Exact R12 lineage:
- RED1 episode-version family: `21585dfdf7ec2f8f85f45a98e4c809ee78cbc145`
- RED2 execution-ordinal leak: `96c437e03cd82a55bd3ba8db116188641c8bacb0`
- executable GREEN: `dd8af9b4fd5414f3a2ea6b3af2d8e6e21b3992ba`
- executable GREEN tree: `060fb41c333a9176a2f0174b1e7fd131d81e9fd2`
- CI-enablement head: `9b52b40c9bc78664802b0771ac879f8e3b5eef9e`
- final docs/review head: `663e3aa5fbb4f8ca2751a2c792a100303070ec35`

R12 failures reproduced before repair:

1. Dynamic episode-version leak on exact R11:
   - one hidden peer-produced hypothesis created event count 1;
   - independent worker saw zero proposition IDs;
   - `view.episode_version` exposed `trusted-opaque-episode@1`;
   - runner still reported `independence_demonstrated=True`.
   - RED1 froze the version/trace family; final controls strengthen it to same episode ID with only event count varying.

2. Execution ordinal leak:
   - same allowed task specification + same independent generator;
   - no prior node => `independent:exec:1:echo_hypothesis`;
   - prior blinded mandatory verifier => `independent:exec:2:echo_hypothesis`;
   - exact RED2 `96c437e0…` failed as expected.

R12 repair:
- strong-independent executor-visible `episode_version` is constant `independent@0`;
- canonical audit version remains exact in `TraceRecord.episode_version`;
- new `TraceRecord.executor_episode_version` binds what the executor actually saw;
- normal, exception, and preflight trace paths bind executor-visible version;
- strong-independent execution ID no longer depends on task ID, event count, trace count, or prior execution ordinal;
- strong-independent execution ID derives only from static node identity + allowed `TaskSpecification.digest` (or `no-task-spec`);
- non-independent workers retain the real episode version and existing task-derived execution-ID behavior.

Preserved predecessor controls:
- non-empty `context_refs` fail closed before strong-independent execution;
- full `TaskEnvelope` is absent from strong-independent executor;
- allowed TaskSpecification contains only literal request / subject refs / constraints;
- task ID / authority / privacy / budget / context refs remain structurally absent from task specification;
- executor-facing independence metadata is empty;
- complete attestation remains runner/audit-side and gates preflight;
- output admission binds exact runner-issued execution ID;
- non-independent workers retain full TaskEnvelope;
- task envelope digest and executor-visible task-spec digest remain separately traced.

R12 qualification:
- focused final R12 controls: 4/4 PASS
- executable `dd8af9b4…` fresh clean clone: 122/122 PASS, compileall PASS, diff-check PASS
- hosted run on `9b52b40c…`: `35399955230` SUCCESS
- final exact `663e3aa5…` fresh clean clone: 122/122 PASS, compileall PASS, diff-check PASS
- final exact-head hosted run: `35400035412` SUCCESS
- qualification doc: `docs/qualification/KERNEL_V0_R12_DYNAMIC_HISTORY_ISOLATION.md`

R12 review routing:
- Bus commit `1552e69cb4557c0dca3fde8ea0d094ebc4c6686d`
- file `messages/20260918T1840-rezon-kernel-r12-final-head-hostile-rereview.md`
- requires_reply true
- fresh Mune/Masa/One exact-head hostile review required
- last fresh check: PR #25 had no reviews/comments and no new Mune/Masa/One exact R12 Bus reply
- state:
  `SOURCE_BUILD_TEST_HOSTED_GREEN_122 / FINAL_R12_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Failed predecessor chain — preserve, do not promote

R8:
- exact `c88ab7f480a1b6658951e3d6290a422d8b0e737c`
- source/test/hosted green
- semantic FAIL: TaskEnvelope context_refs leaked auxiliary peer-answer context

R9:
- exact `cd7ffed38d6970213829ae96dbf1afc995391ba8`
- source/test/hosted green
- semantic FAIL: full TaskEnvelope still exposed authority/privacy metadata

R10:
- exact `bfcd54e197b06104481df576afb11f3559b6e55b`
- local 115/115 + hosted green
- semantic FAIL: projected TaskEnvelope retained original task_id

R11:
- exact `8d30b04728488d0d1fcc3bb9d176e77c49923478`
- local 118/118 + hosted run `35393392204` SUCCESS
- semantic FAIL: dynamic episode-version event-count leak + execution ordinal leak

## Trust boundary after R12

Current V0 contracts intentionally expose static `episode_id` and `node_id` as orchestration identifiers.

R12 removes dynamic hidden-history metadata from the strong-independent executor-facing surface. It does NOT claim:
- a malicious trusted orchestrator cannot encode answers into trusted static IDs;
- literal request / subject refs / constraints are non-adversarial;
- cryptographic executor/model/provider identity;
- a qualified shared-context/shared-read independence class.

The independence identity/policy boundary remains a trusted-host boundary, not cryptographic issuer proof.

## Benchmark R4 — accepted exact source

PR #18:
- branch `rezon/benchmark-v1-r4-unknown-currentness`
- exact head `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`
- draft/open/unmerged
- Mune exact-head PASS
- hosted run `35342387478` SUCCESS

Fresh reproduced vector:
- pytest 105/105 PASS
- compile PASS
- reference benchmark PASS
- diff-check PASS
- 24 cases
- strategy-input digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded 21/24
- false accepts 2
- operations 174
- required violation hits 9/15

## R12 + Benchmark R4 integration-readiness

No remote integration branch or commit exists.

Local-only no-commit merge:
- exact R12 `663e3aa5…`
- exact R4 `d7373867…`
- common merge base `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: 181/181 PASS
- compileall `src tests scripts`: PASS
- reference benchmark PASS
- diff-check PASS
- benchmark vector unchanged: 24 cases / same digest / 21/24 / 2 false accepts / 174 ops

Bus integration evidence:
- commit `ea0668add5e28787e994f80b348fb9241b5ef245`
- file `messages/rezon-r12-benchmark-r4-integration-probe-663e3aa5.md`

Meaning ceiling:
- source-level compatibility only
- no canonical integration
- no combined hosted qualification
- no inherited review state
- future integration candidate is a NEW exact subject

## Benchmark R5 typed-support design — still gated

PR #19:
- branch `rezon/benchmark-v1-r5-typed-support-design-final`
- exact current head `05c668bf67349e87738990aa65f40ec07e9001e4`
- tree `8f9e2e4d5c1178d5078fd880122dd314c197abdd`
- design-only / draft / unmerged
- predecessor `798b6318…` got Masa CHANGES_REQUESTED / DESIGN_HOSTILE_FAIL
- current repaired design addresses:
  - verification-source admission/currentness
  - DISTINCT_EXECUTION_REQUIRED anti-circular verifier
  - unique target/type/kind receipt tuple
  - false-VERIFIED independent evaluator oracle
  - unsolicited/non-required REFUTED diagnostic-only
- fresh exact-head rereview still pending at last check
- DO NOT IMPLEMENT R5 until fresh exact design rereview clears

R4->R5 reconciliation:
- Bus commit `db9ad271799de90205864a9119ce338e37e87181`
- binds accepted R4 parser/schema, strategy, evaluator, digest/experiments, runner, fixtures, and vocabulary-only Kernel touch to gated R5 design

## Intranel side lane

PR #5:
- exact head `0338f053fa90cca66981c066180bdf706f0e8ca2`
- real repair: direct IntranelMessage construction rejects null governance-array members
- local 117/117 PASS / compile/diff PASS
- independent source/semantic PASS
- hosted run `35379568632` failed with zero-step jobs
- ceiling: SOURCE/SEMANTIC PASS + LOCAL GREEN / HOSTED UNKNOWN-NO-RUN
- do not invent a code failure or runner cause

## Lantern

Lantern currentness was not re-established in this execution chain.
Exact WoWSQL connector previously failed internally even on `SELECT 1`.
Do not fall back to Supabase or another backend.
Any Lantern-dependent currentness claim remains UNKNOWN until the V3 exact WoWSQL preflight -> B0 -> payload -> B1 sequence succeeds.

## Immediate restore actions

1. Fresh-check PR #25 head remains exact `663e3aa5…`; head movement invalidates inherited review state.
2. Fresh-check `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2` and PR #25 for exact R12 replies.
3. If exact R12 returns CHANGES_REQUESTED, preserve `663e3aa5…` and create R13 successor RED-first.
4. If exact R12 gets fresh independent PASS, report exact-subject PASS and hold merge/integration gate; do NOT merge.
5. Fresh-check PR #19. If exact `05c668…` receives PASS, implementation may begin only on a new branch reconciled to accepted R4, RED-first per the existing map.
6. Do not create canonical R12+R4 integration until relevant review gates clear and Patrick grants integration/merge authority.
7. Do not open learned-routing/donor gate before Kernel V0 independent acceptance.
8. If reviews remain pending, continue read-only/self-hostile audit of frozen R12 without moving its head unless a reproducible defect is found.
