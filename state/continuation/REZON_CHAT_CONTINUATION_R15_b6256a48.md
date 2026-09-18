# REZON CHAT CONTINUATION — R15 / b6256a48

Restore token:

`REZON::RESTORE::R15::b6256a48`

Continuation/recovery evidence only. No merge, canonical promotion, deployment, installation, activation, provider/model mutation, learned-routing activation, or qualification authority is implied.

## Current Kernel frontier — R15

Draft PR #28:
- branch: `work/rezon-kernel-v0-r15-canonical-state-digest-binding`
- base: failed R14 branch `work/rezon-kernel-v0-r14-attempt-vs-producer-identity`
- failed R14 exact: `4361191a9abf5f86f070b0a1c2bea14972c8ec76`
- final R15 review head: `b6256a487727caf8e1bc0425651d8699e86afb44`
- final R15 tree: `49338a95c0d6ea954ec8162b8484209c7ee3b6d3`
- draft / open / unmerged

R15 lineage:
- state-collision RED: `84bec288db402854db715196b1dcc0d7020c9a5c`
- executable GREEN: `00f3c0fe3427be250df8d32b280488187a15943c`
- executable tree: `64bbcd8c0b8f6fe8ad3ce22b05f9718bac699f53`
- CI enablement: `8f2b5e28cafa220f6448955c07df230c0a118e17`
- permanent multistep replay regression: `408f8145c812d0840a5d584ac89f1ad0a6730be0`
- multistep tree: `b6f58bb9afe8d23b9af608202ddc4f5986a4ace1`
- final docs/review head: `b6256a487727caf8e1bc0425651d8699e86afb44`

## R14 failure preserved

R14 separated opaque attempt identity from deterministic durable producer provenance but derived canonical producer identity from `episode_id@event_count`.

Exact-hostile probe:
- same episode ID;
- same version ref `same-episode-id@1`;
- different canonical observation contents;
- same node/task/policy;
- both executions succeeded;
- canonical producer IDs collided.

Conclusion:
`episode_id@event_count` is a counter, not a state fingerprint.

Bus R14 failure record:
- commit `a3747aa9d3f6919a8bad1cf3617b776ea90f61b1`
- file `messages/rezon-r14-canonical-producer-state-collision-fail.md`

Do not promote R14.

## R15 repair

R15 captures the exact pre-execution `EpisodeSnapshot` once and uses that exact object both to:
- compute `canonical_episode_snapshot_digest`;
- construct the execution/audit view.

Snapshot digest:
1. `dataclasses.asdict(snapshot)`
2. canonical JSON with sorted keys, compact separators, UTF-8
3. SHA-256

Canonical producer ID now derives from:
- node ID;
- exact snapshot digest;
- exact executor-visible TaskSpecification digest, or explicit no-task-spec marker.

Opaque attempt ID remains:
`independent:exec:<node_id>:<uuid4-hex>`

Strong-independent executor does NOT receive the canonical snapshot digest.

Trace binds:
- opaque attempt `execution_id`;
- deterministic `canonical_producer_execution_id`;
- exact `canonical_episode_snapshot_digest`.

Admission still validates worker result/proposition/relation producer IDs against the issued attempt ID BEFORE runner-side canonical provenance rewrite.

## R15 qualification

RED `84bec288…`:
- targeted 2/2 FAIL as expected.

Executable `00f3c0fe…`:
- focused R12-R15: **10/10 PASS**
- full local: **128/128 PASS**
- compileall PASS
- diff-check PASS
- fresh clean exact executable checkout: 128/128 PASS
- hosted CI enablement `8f2b5e28…`, run `35405320414`: SUCCESS

Multistep replay regression `408f8145…`:
- fresh clean **129/129 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35405464016`: SUCCESS

Final exact review head `b6256a48…`:
- fresh clean **129/129 PASS**
- compileall PASS
- diff-check PASS
- exact-head hosted run `35405566889`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R15_CANONICAL_STATE_DIGEST_BINDING.md`

Review routing:
- PR #28
- Bus commit `4618fa7684e8b504e8233a8bfd814e449f9af0fb`
- file `messages/rezon-kernel-r15-final-head-hostile-rereview-b6256a48.md`
- requires fresh exact-head Mune/Masa/One review

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_129 / FINAL_R15_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Failed predecessor chain — preserve

- R8 `c88ab7f…`: context_refs leak
- R9 `cd7ffed…`: full TaskEnvelope authority/privacy leak
- R10 `bfcd54e…`: task_id leak
- R11 `8d30b047…`: dynamic episode-version + execution ordinal leak
- R12 `663e3aa5…`: deterministic execution-attempt identity collision
- R13 `9ff7d5c0…`: random attempt UUID contaminated deterministic canonical state
- R14 `4361191a…`: same-version divergent canonical states collided on producer identity

Each failed subject remains evidence. Do not rewrite/promote.

## Benchmark R4 accepted exact source

PR #18:
- exact `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`
- independent exact-head PASS
- hosted run `35342387478` SUCCESS
- 105/105 local
- frozen vector:
  - 24 cases
  - digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
  - guarded 21/24
  - false accepts 2
  - ops 174
- draft/open/unmerged

R15 + R4 local-only integration probe:
- exact R15 `b6256a48…`
- exact R4 `d7373867…`
- common merge base `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest **188/188 PASS**
- compileall PASS
- reference benchmark PASS
- diff-check PASS
- frozen benchmark vector unchanged
- Bus evidence commit `123b93504df4482662043d8a76fd39577b369f3f`
- no remote integration branch/commit

## Benchmark R5 typed-support design

PR #19:
- exact repaired design head `05c668bf67349e87738990aa65f40ec07e9001e4`
- tree `8f9e2e4d5c1178d5078fd880122dd314c197abdd`
- design-only / draft / unmerged
- predecessor `798b6318…` got Masa CHANGES_REQUESTED
- repaired design addresses B1-B4 and M1
- fresh exact-head rereview still pending at last check
- DO NOT IMPLEMENT until exact repaired-design rereview clears
- R4->R5 source reconciliation Bus commit `db9ad271799de90205864a9119ce338e37e87181`

## Intranel

PR #5 exact `0338f053fa90cca66981c066180bdf706f0e8ca2`
- local 117/117
- independent source/semantic PASS
- hosted run `35379568632` zero-step/no-run
- ceiling: SOURCE/SEMANTIC PASS + LOCAL GREEN / HOSTED UNKNOWN-NO-RUN

## Lantern

Lantern currentness remains UNKNOWN.
WoWSQL exact connector previously failed internally.
Do not use Supabase fallback.
Any Lantern-dependent currentness claim requires V3 WoWSQL preflight -> B0 -> payload -> B1.

## Immediate restore actions

1. Fresh-check PR #28 remains exact `b6256a48…`.
2. Fresh-check `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2` and PR #28 for exact R15 review.
3. If R15 FAIL/CHANGES_REQUESTED: preserve `b6256a48…`, create R16 successor RED-first.
4. If R15 fresh independent PASS: report exact-subject PASS and hold integration/merge gate; do not merge.
5. Fresh-check PR #19 exact repaired R5 design. If exact PASS lands, implementation may start only on a new branch reconciled to accepted R4, RED-first.
6. Do not create canonical R15+R4 integration without relevant review gates and Patrick authority.
7. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
8. If reviews remain pending, continue self-hostile audit of frozen R15. High-value attack: multiple distinct actual attempts from identical canonical state, no-output/retry semantics, and ordering/canonicalization assumptions in snapshot serialization.
