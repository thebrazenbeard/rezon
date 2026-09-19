# REZON CHAT CONTINUATION — R28 / f6e1da75

Restore token: `REZON::RESTORE_AND_RUN::R28::f6e1da75`

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

## Current Kernel frontier — R28

Branch:
`work/rezon-kernel-v0-r28-unambiguous-source-version-binding`

Draft PR:
`#41`

Current exact final head:
`f6e1da75ec62ea732e58253b4c12b0c2c87bab8b`

Current status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Exact-final local qualification:
- R28 collision regressions: **2/2 PASS**
- full suite: **190/190 PASS**
- compileall: PASS
- git diff --check: PASS

Focused R16-R28 qualification before final freeze:
**61/61 PASS**

Exact-final hosted run:
`35459395665` — SUCCESS

Hosted job:
`105940398356` — install / compile / test / diff-check all PASS

## R27 failure that caused R28

Failed whole-Kernel R27 exact subject:
`5d5c25197995361ecbe39d7e959feeabd2890ffe`

R27 closed eleven retrieval runtime type/equality false accepts, but promoted
source provenance remained ambiguous because retrieval serialized a structured
pair as `source_id@source_version` without constraining `@` in either component.

Demonstrated exact-R27 collision:
- `repo:a@b` + `c` -> `repo:a@b@c`
- `repo:a` + `b@c` -> `repo:a@b@c`

The collision appeared in both promoted `source_refs[0]` and
`source_versions[0]`.

Disposition:
`R27_SOURCE_VERSION_CANONICAL_ENCODING = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R27 PR #40 remains preserved draft/unmerged.

Bus self-fail record:
`messages/20260919T1356-one-rezon-r27-self-fail-r28.md`

Bus commit:
`94caff7efc4227f6a5a30631501a316a02bb456f`

## R28 frozen RED and repair

Frozen RED:
`b7eb35f77307404d54511025cd3b195e91cd473d`

Fresh exact-R27 targeted result:
**2 failed / 0 passed**

Executable repair:
`77782d0db4c5b4f9604d6640a8360cc7a6e0b2ca`

CI-enablement head:
`10ef39c86a9e79c7052f1748c4a413a242d2a892`

Executable hosted run:
`35459360186` — SUCCESS

Final qualification/documentation head:
`f6e1da75ec62ea732e58253b4c12b0c2c87bab8b`

Qualification record:
`docs/qualification/KERNEL_V0_R28_UNAMBIGUOUS_SOURCE_VERSION_BINDING.md`

R28 preserves the current simple `source_id@source_version` format but rejects
the binding separator `@` inside either exact source ID or exact source version
before retrieval matching/promotion. Raw identifiers requiring `@` must be
normalized into logical IDs outside this boundary.

## R26 -> R27 context

Failed whole-Kernel R26 exact subject:
`c82229f115e7bd9bd14f23ce0a975a3f034c20be`

R26's direct canonical Episode hardening remains valid within scope, but exact
R26 false-accepted eleven retrieval-admission runtime contract attacks.

R27 frozen RED:
`da62fd672aa103c2499b2420a4a5a7b4898b4edc`

R27 executable repair:
`39ccf37094c5338b89e09093ca3d4a7dc443b2db`

R27 final:
`5d5c25197995361ecbe39d7e959feeabd2890ffe`

R27 exact-final qualification before the R28 discovery:
- 11/11 R27 hostile regressions PASS
- 59/59 focused R16-R27 PASS
- 188/188 full PASS
- exact-final hosted run `35459150860`: SUCCESS

## Benchmark R4 composition probe

Accepted Benchmark R4 source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit merge simulation with exact R28:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **249/249 PASS**
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
`messages/20260919T1400-one-rezon-r28-benchmark-r4-integration.md`

Bus commit:
`33ef32fd9206ec75587e9c0e95299b7dd09be9de`

## Independent hostile rereview

Exact-head request:
`messages/20260919T1401-one-rezon-r28-hostile-rereview.md`

Bus commit:
`f842d1fd09f88dfc2c8aab5d355527c658756d2a`

Targets:
MASA / MUNE

`requires_reply: true`

At checkpoint time:
- PR #41 head is exact `f6e1da75...`;
- PR #41 is draft/open/mergeable;
- PR #41 has no review submissions or comments;
- MASA branch tip is still `0856d321c92d26eee75ad64b945ff9035c2000cf`
  from 2026-09-18;
- MUNE branch tip is still `8f669e39e74e79dae54793a7a6a45d615e64de32`
  from 2026-09-18;
- no independent R28 PASS/FAIL is accepted yet.

## Failed predecessor chain

Preserve all failed exact subjects. Most recent:
- R22 `f367ef6776fa98ffe6cf455a4101674e8e244a4b` — duck-typed task digest bypass.
- R23 `e3498a1ead2d9dde186c604961bb184dc3b2a764` — custom-equality admission identity bypasses.
- R24 `0f112eda3dafa18ea81fac86b86f08978524a8a4` — adjacent admission runtime-contract bypasses.
- R25 `c1f445e29b56711ad451cab91f8d5e55c3817351` — direct canonical Episode mutation bypass.
- R26 `c82229f115e7bd9bd14f23ce0a975a3f034c20be` — retrieval runtime contract bypasses.
- R27 `5d5c25197995361ecbe39d7e959feeabd2890ffe` — source/version provenance token collision.
- R28 is current successor, not independently accepted.

## Immediate next actions

1. Fresh-check R28 branch and PR #41 remain exactly `f6e1da75...`.
2. Read fresh PR reviews/comments and MASA/MUNE Bus replies bound to that exact head.
3. If independent FAIL lands, preserve R28 and create R29 RED-first.
4. If independent PASS lands, record exact acceptance without treating it as merge authority.
5. If no external verdict has landed, hostile-probe the next high-value runtime boundary:
   `IndependenceMetadata` / `IndependenceVerificationPolicy` in
   `src/rezon/receipts.py` and runner use of `independence_policy.verify()`.
   Pressure duck/subclass policy authority, custom string equality/hash,
   container subclasses, boolean confusion, and evidence-to-metadata exact binding.
6. Keep Issue #5 learned-routing gate CLOSED until the exact Kernel acceptance condition is met.
7. Do not merge or perform protected effects without Patrick's explicit authority.
8. Save a successor continuation checkpoint whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R28::f6e1da75`
