# REZON CHAT CONTINUATION — R14 / 4361191a

Restore token:

`REZON::RESTORE::R14::4361191a`

Continuation/recovery evidence only. No merge, canonical promotion, deployment, installation, activation, provider/model mutation, learned-routing activation, or qualification authority is implied.

## Current Kernel frontier — R14

Draft PR #27:
- branch: `work/rezon-kernel-v0-r14-attempt-vs-producer-identity`
- base: failed R13 branch `work/rezon-kernel-v0-r13-opaque-execution-identity`
- failed R13 exact: `9ff7d5c025fec8a69b22640394e03fbbe3304409`
- final R14 review head: `4361191a9abf5f86f070b0a1c2bea14972c8ec76`
- final R14 tree: `056b620e6b7b22f57c4012d38f3f0f91758cdb07`
- draft / open / unmerged

R14 lineage:
- RED: `48894d5be8d3694dc9817d5afcfa2f022ce9f106`
- executable GREEN: `c24fa63817be21cfd7ad0ce96658cca6253e0b15`
- GREEN tree: `52ef5683dce9bcc3432b9af100802b020bf6bdcc`
- CI enablement: `ee367bee10a52eb168860418fab622631424e4d4`
- final docs/review head: `4361191a9abf5f86f070b0a1c2bea14972c8ec76`

## R13 failure preserved

R13 used UUID-backed strong-independent attempt IDs directly as canonical proposition/relation `producer_execution_id`.

Fresh exact-head determinism probe:
- identical fresh episodes;
- same episode ID;
- same task;
- same deterministic strong-independent node;
- same semantic proposition output;
- only attempt UUID differed.

Observed:
- attempt IDs differed;
- episode events identical;
- semantic fields identical;
- canonical EpisodeSnapshot unequal solely because random UUID was persisted as producer provenance.

This conflicted with the Kernel design statement:
`The canonical episode state is explicit and deterministic.`

Bus R13 failure record:
- commit `687788f71290028a3fa5bcb0ea72c31f82d7a458`
- file `messages/rezon-r13-canonical-state-determinism-fail.md`

Do not promote R13.

## R14 identity split

R14 now separates:

### Attempt identity

Strong-independent executor sees:
`independent:exec:<node_id>:<uuid4-hex>`

This remains:
- unique per actual attempt;
- opaque;
- not task-ID-derived;
- not canonical-version-derived;
- not execution-ordinal-derived;
- mandatory for ExecutionResult identity and worker-emitted producer fields before admission.

### Canonical producer identity

Runner derives durable producer provenance from:
- node ID;
- exact pre-execution canonical episode version;
- exact executor-visible TaskSpecification digest, or explicit no-task-spec marker.

Format:
`canonical:exec:<node_id>:<sha256(...)>`

This ID is audit/canonical-side and is not sent to the strong-independent worker as its execution ID.

Admission:
1. validates result + proposition/relation producer IDs against exact opaque attempt ID;
2. validates all existing output/source/provenance constraints;
3. only then rewrites admitted proposition/relation producer provenance to deterministic canonical producer ID.

Trace binds both:
- `execution_id` = opaque actual attempt
- `canonical_producer_execution_id` = durable deterministic producer provenance

## R14 qualification

RED `48894d5b…`:
- targeted 2/2 FAIL as expected.

After repair:
- focused R12-R14 identity/isolation: **8/8 PASS**
- full local suite: **126/126 PASS**
- compileall PASS
- diff-check PASS
- inherited forged runner identity/provenance regression PASS
- inherited exact worker producer provenance regression PASS

Fresh clean executable head `c24fa638…`:
- 126/126 PASS
- compileall PASS
- diff-check PASS

Hosted CI:
- CI head `ee367bee…`
- run `35404488301`: SUCCESS

Final exact review head `4361191a…`:
- fresh clean 126/126 PASS
- compileall PASS
- diff-check PASS
- hosted exact-head run `35404598603`: SUCCESS

Qualification:
- `docs/qualification/KERNEL_V0_R14_ATTEMPT_VS_PRODUCER_IDENTITY.md`

Review routing:
- Bus commit `03570d8988a95c53b3893d2ac4b7eaea36841c41`
- file `messages/rezon-kernel-r14-final-head-hostile-rereview-4361191a.md`
- requires fresh exact-head Mune/Masa/One review

State:
`SOURCE_BUILD_TEST_HOSTED_GREEN_126 / FINAL_R14_EXACT_HEAD_FROZEN / INDEPENDENT_REREVIEW_PENDING / DRAFT / UNMERGED`

## Failed predecessor chain — preserve

- R8 `c88ab7f…`: context_refs leak
- R9 `cd7ffed…`: full TaskEnvelope authority/privacy leak
- R10 `bfcd54e…`: task_id leak
- R11 `8d30b047…`: dynamic episode-version + execution ordinal leak
- R12 `663e3aa5…`: deterministic execution-attempt identity collision
- R13 `9ff7d5c0…`: random attempt UUID contaminated deterministic canonical state

Each failed subject remains evidence. Do not rewrite/promote.

## Benchmark R4 accepted exact source

PR #18:
- exact `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`
- Mune exact-head PASS
- hosted run `35342387478` SUCCESS
- 105/105 local
- frozen vector:
  - 24 cases
  - digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
  - guarded 21/24
  - false accepts 2
  - ops 174
- draft/open/unmerged

R14 + R4 local-only integration probe:
- exact R14 `4361191a…`
- exact R4 `d7373867…`
- common merge base `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest **185/185 PASS**
- compileall PASS
- reference benchmark PASS
- diff-check PASS
- frozen benchmark vector unchanged
- Bus evidence commit `00c7daca04573ab41b1d475bc48db5927d542d92`
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
Any Lantern-dependent currentness claim requires the V3 WoWSQL preflight -> B0 -> payload -> B1 sequence.

## Immediate restore actions

1. Fresh-check PR #27 remains exact `4361191a…`.
2. Fresh-check `bus/mune-v2`, `bus/masa-v2`, `bus/one-v2` and PR #27 for exact R14 review.
3. If R14 FAIL/CHANGES_REQUESTED: preserve `4361191a…`, create R15 successor RED-first.
4. If R14 fresh independent PASS: report exact-subject PASS and hold integration/merge gate; do not merge.
5. Fresh-check PR #19 exact repaired R5 design. If exact PASS lands, implementation may start only on a new branch reconciled to accepted R4, RED-first.
6. Do not create canonical R14+R4 integration without relevant review gates and Patrick authority.
7. Issue #5 donor/learned-routing gate remains CLOSED until Kernel V0 independent acceptance.
8. If reviews remain pending, continue read-only/self-hostile audit of frozen R14. High-value attack: duplicate/no-output/retry semantics of deterministic canonical producer derivation.
