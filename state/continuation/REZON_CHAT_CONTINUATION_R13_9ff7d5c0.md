# REZON CHAT CONTINUATION — R13 / 9ff7d5c0

Restore token:

`REZON::RESTORE::R13::9ff7d5c0`

Continuation/recovery evidence only. No merge, canonical promotion, deployment, installation, activation, provider/model mutation, learned-routing activation, or qualification authority is implied.

## Operating rules

- repo: `thebrazenbeard/rezon`
- live user instruction > checkpoint
- fresh exact Git/PR/Bus state > checkpoint
- non-PR coordination: `thebrazenbeard/chat-communication-bus`
- preserve failed exact subjects; repair successors RED-first
- source/build/test/hosted/review/merge/install/runtime/effect/behavior are separate
- no merge/deploy/install/provider/model/credential/learned-routing/protected effect without Patrick's exact authority
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing gate remains CLOSED until Kernel V0 has fresh exact-head independent acceptance

## Current Kernel frontier — R13

Draft PR #26:
- title: `P0 R13: issue opaque unique strong-independent execution identities`
- branch: `work/rezon-kernel-v0-r13-opaque-execution-identity`
- base: failed R12 `work/rezon-kernel-v0-r12-episode-version-isolation`
- failed R12 exact: `663e3aa5fbb4f8ca2751a2c792a100303070ec35`
- failed R12 tree: `d0364b00cd3728717788b2159ab4e64ec4724db1`
- final R13 review head: `9ff7d5c025fec8a69b22640394e03fbbe3304409`
- final R13 tree: `3218bbe5a58424c495f65f100a856744897f15f4`
- draft / open / unmerged

R13 lineage:
- RED execution-identity collision: `02bacee12a8e2c04519beb1be8ffe275234c1581`
- executable GREEN: `46e1999448a9431cc13634b360acdbaec6dfb4b4`
- GREEN tree: `43905771818e37a56a819b30d1ab74ad11a9fa87`
- CI enablement: `5337ea39cae6610e1bcf60413e706301f31cbbb1`
- final docs/review head: `9ff7d5c025fec8a69b22640394e03fbbe3304409`

R12 failure reproduced:
- same EpisodeRunner / same strong-independent node / same task specification / same episode;
- run twice as two distinct actual executions;
- both runs succeeded;
- both got identical deterministic execution ID:
  `independent:exec:echo_hypothesis:79a0066b1b79ca99f42ad7273d22b4d244c1b89ca4bb167959398dc4bfbf47a0`;
- audit episode versions differed;
- distinct propositions shared the same `producer_execution_id`.
- Bus failure record: commit `883f8cbad6e20c70f46d2d84ffc73ac54dd4c09d`

R13 RED:
- test `tests/test_r13_execution_identity_uniqueness.py`
- exact test-only head `02bacee1…`
- clean targeted result: **2 failed / 0 passed**

R13 repair:
- strong-independent execution ID:
  `independent:exec:<node_id>:<uuid4-hex>`
- fresh UUID4 per actual execution
- task ID / canonical episode version / event count / trace count / execution ordinal / task-spec digest are not used as provenance identity
- executor, trace, ExecutionResult, admission, and emitted producer provenance bind the same exact runner-issued ID
- R12 history-leak regression fixes UUID source under test; with randomness controlled, clean vs prior-blinded-verifier cases receive the same ID, proving history/count does not influence construction
- separate R13 real-UUID test proves distinct actual runs receive distinct IDs
- scheduler/routing determinism remains separate from execution-instance identity

Preserved R9-R12 controls:
- context_refs fail closed
- strong-independent executor receives TaskSpecification only
- TaskEnvelope absent
- task ID / authority / privacy / budget / context structurally absent from allowed task spec
- executor-facing independence metadata empty
- runner-side complete attestation governs preflight
- strong-independent executor-visible episode version remains `independent@0`
- trace preserves canonical audit version and executor-visible version separately
- non-independent workers keep full TaskEnvelope and real episode version
- admission binds exact runner-issued execution ID

R13 qualification:
- focused R12/R13 controls: 6/6 PASS
- executable `46e19994…` clean clone: **124/124 PASS**, compileall PASS, diff-check PASS
- hosted run on `5337ea39…`: `35400691144` SUCCESS
- final exact `9ff7d5c0…` clean clone: **124/124 PASS**, compileall PASS, diff-check PASS
- final exact-head hosted run: `35400759023` SUCCESS
- qualification doc: `docs/qualification/KERNEL_V0_R13_OPAQUE_EXECUTION_IDENTITY.md`

R13 review routing:
- Bus commit `12223b79d22bc2bc2c678c46f5ce7258ee96d8f4`
- file `messages/rezon-kernel-r13-final-head-hostile-rereview-9ff7d5c0.md`
- requires_reply true
- state:
  `SOURCE_BUILD_TEST_HOSTED_GREEN_124 / FINAL_R13_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

R13 trust/non-claim boundary:
- UUID4 is provenance identity only, not evidence/truth/authority/security credential
- no cryptographic executor/model/provider identity claim
- no absolute mathematical UUID-collision impossibility claim
- malicious trusted host controlling UUID source remains outside current honest-host boundary
- literal task-spec content can itself be answer-bearing because it is the requested task
- static episode_id/node_id remain trusted orchestration identifiers

## Failed predecessor chain — preserve

- R8 `c88ab7f…`: context_refs leak
- R9 `cd7ffed…`: full TaskEnvelope authority/privacy leak
- R10 `bfcd54e…`: task_id leak
- R11 `8d30b047…`: dynamic episode-version + execution-ordinal leak
- R12 `663e3aa5…`: deterministic execution-identity collision

All had green source/test evidence at some stage but failed semantic hostile checks. Do not promote them.

## Benchmark R4 — accepted exact source

PR #18:
- exact `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`
- Mune exact-head PASS
- hosted run `35342387478` SUCCESS
- 105/105 local
- 24 cases
- digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded 21/24
- false accepts 2
- ops 174
- unmerged

R13 + R4 local-only integration probe:
- exact R13 `9ff7d5c0…`
- exact R4 `d7373867…`
- common merge base `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest **183/183 PASS**
- compileall PASS
- benchmark PASS
- diff-check PASS
- frozen benchmark vector unchanged
- Bus evidence commit `3079054193aeb5ca51e1760a32dda0d9f9ec8ef5`
- no remote integration branch/commit; future integration is a NEW subject

## Benchmark R5 typed-support design — review gated

PR #19:
- exact repaired design head `05c668bf67349e87738990aa65f40ec07e9001e4`
- tree `8f9e2e4d5c1178d5078fd880122dd314c197abdd`
- design-only / draft / unmerged
- predecessor `798b6318…` got Masa CHANGES_REQUESTED
- repaired design addresses verification-source governance, distinct-execution verifier requirement, unique target/type/kind receipt tuple, false-VERIFIED evaluator oracle, and diagnostic-only unsolicited non-required refutation
- fresh exact-head rereview still pending at last check
- DO NOT IMPLEMENT until exact repaired-design review clears
- R4->R5 source reconciliation Bus commit `db9ad271799de90205864a9119ce338e37e87181`

## Intranel

PR #5 exact `0338f053fa90cca66981c066180bdf706f0e8ca2`
- local 117/117
- independent source/semantic PASS
- hosted run `35379568632` zero-step/no-run
- ceiling: SOURCE/SEMANTIC PASS + LOCAL GREEN / HOSTED UNKNOWN-NO-RUN

## Lantern

Lantern currentness remains UNKNOWN in this execution chain.
WoWSQL exact connector previously failed internally.
Do not fall back to Supabase.
Any Lantern currentness claim requires V3 exact WoWSQL preflight -> B0 -> payload -> B1.

## Immediate restore actions

1. Fresh-check PR #26 exact head remains `9ff7d5c0…`.
2. Fresh-check `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2` and PR #26 for exact R13 replies.
3. If exact R13 returns CHANGES_REQUESTED, preserve `9ff7d5c0…` and create R14 RED-first.
4. If exact R13 gets fresh independent PASS, report exact-subject PASS and hold merge/integration gate; do not merge.
5. Fresh-check PR #19 exact repaired R5 design. If PASS lands, implementation may start only on a new branch reconciled to accepted R4, RED-first.
6. Do not create canonical R13+R4 integration without relevant review gates and Patrick's authority.
7. Do not open donor/learned-routing gate before Kernel V0 independent acceptance.
8. If reviews remain pending, prefer read-only hostile analysis of frozen subjects over moving R13 without a reproducible defect.


## Additional R13 self-hostile full-view differential

After freezing R13, a read-only exact-head differential probe compared the complete strong-independent executor-visible `ExecutionView` across:
- same trusted static episode ID;
- same task/spec/node/policy;
- fixed identical UUID source;
- clean episode vs one prior hidden peer-produced proposition.

All executor-visible dataclass fields were compared:
`blinded_proposition_ids`, `blinded_relation_ids`, `episode_version`, `execution_id`, `independence`, `propositions`, `relations`, `task_envelope`, `task_specification`.

Observed:
- executor-visible `DIFFS = {}`;
- both runs succeeded;
- audit-side trace correctly differed in canonical episode version and blinded peer proposition ID;
- executor-facing history remained unchanged.

Bus evidence:
- commit `6420609dd65f1ee529c9b06410f6f1a91ca561be`
- file `messages/rezon-r13-full-executor-view-differential-self-hostile.md`

Meaning ceiling:
- self-hostile evidence only;
- not independent PASS and not proof against all side channels.
