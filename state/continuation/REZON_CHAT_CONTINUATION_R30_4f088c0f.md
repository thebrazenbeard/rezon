# REZON CHAT CONTINUATION — R30 / 4f088c0f

Restore token: `REZON::RESTORE_AND_RUN::R30::4f088c0f`

This is the durable recovery point for the current Rezon execution terminal.

Recovery evidence only. No merge, canonical promotion, deployment, installation,
activation, provider/model mutation, training, learned-routing activation,
credential/provider mutation, or other protected effect is authorized by this
file.

## Canonical operating rules

- Canonical repository: `thebrazenbeard/rezon`.
- Kernel work remains branch/PR based and exact-head bound.
- Preserve every failed exact subject as evidence; never rewrite a failed head into a passing one.
- Patrick is sole merge/protected-effect authority.
- All non-PR inter-agent communication goes through `thebrazenbeard/chat-communication-bus`.
- Source/build/test/hosted/review/merge/install/runtime/effect/behavior are separate states.
- Green local/hosted CI is not independent acceptance.
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing gate remains CLOSED until fresh exact-head Kernel acceptance.

## Current Kernel frontier — R30

Branch:
`work/rezon-kernel-v0-r30-exact-node-descriptor-preflight`

Draft PR:
`#43`

Current exact final head:
`4f088c0f085df3f05bd3e59e284b4825e0e3e537`

Current status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Exact-final local qualification:
- R30 hostile regressions: **8/8 PASS**
- full suite: **209/209 PASS**
- compileall: PASS
- git diff --check: PASS

Focused R16-R30 qualification before final freeze:
**80/80 PASS**

Scheduler/admission/independence focused set during repair:
**70/70 PASS**

Exact-final hosted run:
`35460329346` — SUCCESS

Hosted job:
`105942916433` — install / compile / test / diff-check all PASS

Executable hosted run before documentation freeze:
`35460288405` — SUCCESS

## R29 failure that caused R30

Failed whole-Kernel R29 exact subject:
`8026c7932ff95bab3029b71f12686717178b818c`

R29's independence metadata/policy hardening remains valid within its narrower
scope, but `NodeDescriptor` runtime fields could still affect scheduling and
execution before the descriptor contract was validated.

Critical exact-R29 reproduced bypass:

A stateful `independence_required` value returned true during scheduler reads
and false later in the runner. The scheduler chose independent generation, but
the runner then used the non-independent path. A prior peer-produced hypothesis
became visible, the worker copied it, and `copied-peer` was admitted with no
`CONTRACT_VIOLATION`.

A stateful `mandatory_verification` value also scheduled a node as mandatory
then switched false before verification enforcement.

Additional exact-R29 failures:
- NodeDescriptor subclass reached executor before late rejection;
- custom node-id string reached executor before late rejection;
- list-backed permitted output kinds reached executor before late rejection;
- list-backed accepted input kinds were accepted and executed;
- empty list required-authority data was normalized and executed;
- list-backed verification target IDs were accepted and executed.

Disposition:
`R29_NODE_DESCRIPTOR_PRE_SCHEDULER_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R29 PR #42 remains preserved draft/unmerged.

Bus self-fail record:
`messages/20260919T1418-one-rezon-r29-self-fail-r30.md`

Bus commit:
`03b61a7e365b9b0433fb24728cf623b1d6913ca0`

## R30 frozen RED and repair

Frozen RED:
`ffb938b071315fe72f8ee21e18d4591c5f722a31`

Fresh exact-R29 targeted result:
**8 failed / 0 passed**

Exact descriptor contract:
`0032d1bd45ca1b995d54da28f4071efa63e4da3a`

Admission enforcement:
`3ffdb078c289153761998d630506df4952669a04`

Scheduler preflight enforcement:
`9faaa698c84445dc3d846629a443ead449b78411`

CI-enablement head:
`1d223c4dd42f2c5921944b9180fb15896a639d40`

Final qualification/documentation head:
`4f088c0f085df3f05bd3e59e284b4825e0e3e537`

Qualification record:
`docs/qualification/KERNEL_V0_R30_EXACT_NODE_DESCRIPTOR_PREFLIGHT.md`

R30 defines one exact NodeDescriptor runtime contract:
- exact base NodeDescriptor;
- non-empty exact node ID;
- exact PropositionKind tuples for output/input/blind kinds;
- exact booleans for mandatory-verification and independence-required;
- exact non-empty string tuples for authority/relation/verification/blind-ID fields;
- mandatory verification implies explicit targets.

The scheduler evaluates this contract before any descriptor semantics, node
selection, or executor invocation. Direct admission applies the same contract.

## R29 independence context

Frozen R29 RED:
`92ea9b14d0770e69d61b1a96f5000afc4c08d34a`

R29 repairs:
- receipts: `e5bfe6da1ead22f0af6d515be0fb48e7499c965f`
- runner: `dfd794ef21fd13c6e6076bdd8f48b737d1c81b14`

R29 exact-final qualification before R30 discovery:
- 11/11 R29 hostile regressions PASS
- 72/72 focused R16-R29 PASS
- 201/201 full PASS
- exact-final hosted run `35459962934`: SUCCESS
- R29 + accepted Benchmark R4: 260/260 PASS, vector preserved

## R28 and predecessor context

Failed whole-Kernel R28:
`f6e1da75ec62ea732e58253b4c12b0c2c87bab8b`
— exact retrieval source/version binding hardened, then failed on independence
verification runtime authority.

Failed R27:
`5d5c25197995361ecbe39d7e959feeabd2890ffe`
— retrieval runtime type/equality hardening, then failed on source/version token collision.

Failed R26:
`c82229f115e7bd9bd14f23ce0a975a3f034c20be`
— canonical Episode boundary hardening, then failed on retrieval admission runtime contract.

Preserve earlier failed exact heads:
- R22 `f367ef6776fa98ffe6cf455a4101674e8e244a4b`
- R23 `e3498a1ead2d9dde186c604961bb184dc3b2a764`
- R24 `0f112eda3dafa18ea81fac86b86f08978524a8a4`
- R25 `c1f445e29b56711ad451cab91f8d5e55c3817351`

## Benchmark R4 composition probe

Accepted Benchmark R4 source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit merge simulation with exact R30:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **268/268 PASS**
- compileall `src tests scripts`: PASS
- reference Benchmark V1 replay: PASS
- git diff --check: PASS
- strategy-input digest preserved:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded disposition: 21/24
- false accepts: 2
- deterministic operations: 174

No remote integration subject or merge was created.

Bus integration record:
`messages/20260919T1421-one-rezon-r30-benchmark-r4-integration.md`

Bus commit:
`1121a16fe210e73194e91e9492c8eed9e3767295`

## Independent hostile rereview

Exact-head request:
`messages/20260919T1422-one-rezon-r30-hostile-rereview.md`

Bus commit:
`f9bb8d797398b60978709ccb9a6513592ff3190c`

Targets:
MASA / MUNE

`requires_reply: true`

At checkpoint time:
- PR #43 head is exact `4f088c0f...`;
- PR #43 is draft/open/mergeable;
- PR #43 has no submitted reviews or comments;
- MASA branch tip remains `0856d321c92d26eee75ad64b945ff9035c2000cf`
  from 2026-09-18;
- MUNE branch tip remains `8f669e39e74e79dae54793a7a6a45d615e64de32`
  from 2026-09-18;
- no independent R30 PASS/FAIL is accepted yet.

## Immediate next actions

1. Fresh-check R30 branch and PR #43 remain exactly `4f088c0f...`.
2. Read fresh PR reviews/comments and MASA/MUNE Bus replies bound to that exact head.
3. If independent FAIL lands, preserve R30 and create R31 RED-first.
4. If independent PASS lands, record exact acceptance without treating it as merge authority.
5. If no external verdict has landed, probe only high-value effect-bearing adjacent
   runtime boundaries, prioritizing:
   - exact `RunnerNode` structure and whether malformed node wrappers can alter
     descriptor/executor/visibility/policy relationships after scheduler preflight;
   - `VisibilityPolicy` / `build_execution_view` custom equality/container
     behavior where it can expose blinded peer output or hide governed evidence;
   - `ExecutionView` mutation/type confusion only where it crosses into executor
     or admission authority;
   - scheduler `Budget` / completed-node inputs only where malformed state can
     cause unauthorized executor invocation.
6. Do not create cleanup-only type work absent a concrete semantic/effect bypass.
7. Keep Issue #5 learned-routing gate CLOSED until the exact Kernel acceptance condition is met.
8. Do not merge or perform protected effects without Patrick's explicit authority.
9. Save a successor continuation checkpoint whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R30::4f088c0f`
