# REZON CHAT CONTINUATION — R26 / c82229f1

Restore token: `REZON::RESTORE_AND_RUN::R26::c82229f1`

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

## Current Kernel frontier — R26

Branch:
`work/rezon-kernel-v0-r26-exact-episode-boundary`

Draft PR:
`#39`

Current exact final head:
`c82229f115e7bd9bd14f23ce0a975a3f034c20be`

Current status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Exact-final local qualification:
- R26 hostile regressions: **9/9 PASS**
- full suite: **177/177 PASS**
- compileall: PASS
- git diff --check: PASS

Focused R16-R26 qualification before final freeze:
**48/48 PASS**

Exact-final hosted run:
`35457725684` — SUCCESS

Hosted job:
`105935879372` — install / compile / test / diff-check all PASS

## R25 failure that caused R26

Failed whole-Kernel R25 exact subject:
`c1f445e29b56711ad451cab91f8d5e55c3817351`

R25's execution-result admission validator remained green in its narrower scope,
but direct public `Episode` mutation remained a distinct canonical-state bypass.

Exact R25 reproduced:
- non-exact Episode identity accepted;
- public episode identity mutable after construction;
- foreign custom-equality proposition episode identity accepted;
- custom-equality proposition ID accepted;
- direct Proposition subclass accepted;
- forged retract ID removed a real canonical proposition;
- forged relation participant ref resolved to an active canonical object;
- custom-string relation type accepted;
- direct Hyperrelation subclass accepted.

Disposition:
`R25_DIRECT_EPISODE_CANONICAL_BOUNDARY = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R25 PR #38 remains preserved draft/unmerged.

Bus self-fail record:
`messages/20260919T1320-one-rezon-r25-self-fail-r26.md`

Bus commit:
`8ca2a9b4661b435d562ab8c621600630be57a65c`

## R26 frozen RED and repair

Frozen RED:
`e295ae28f916d7040d11facdcfbe9bf074884484`

Fresh exact-R25 targeted result:
**9 failed / 0 passed**

Executable repair:
`63cea8582e10fb495e4cd42ef29730d4905fcb33`

CI-enablement head:
`a729632f8ca34b7c3e94b61bbf43c56b32cf108d`

Executable hosted run:
`35457686513` — SUCCESS

Final qualification/documentation head:
`c82229f115e7bd9bd14f23ce0a975a3f034c20be`

Qualification record:
`docs/qualification/KERNEL_V0_R26_EXACT_EPISODE_BOUNDARY.md`

R26:
- requires exact non-empty Episode identity;
- makes episode identity immutable through the public property;
- validates exact canonical Proposition / Hyperrelation objects and relevant nested runtime types before mutation;
- validates exact retract ID/reason strings;
- preserves R25 admission hardening.

## Benchmark R4 composition probe

Accepted Benchmark R4 source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit merge simulation:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **236/236 PASS**
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
`messages/20260919T1324-one-rezon-r26-benchmark-r4-integration.md`

Bus commit:
`5c07e5493fa2ba3971593f405e1f915421aeca55`

## Independent hostile rereview

Exact-head request:
`messages/20260919T1325-one-rezon-r26-hostile-rereview.md`

Bus commit:
`075f4a014af162e76ddc23c61a328231bab18a47`

Targets:
MASA / MUNE

`requires_reply: true`

At checkpoint time:
- PR #39 head is still exact `c82229f1...`;
- PR #39 is draft/open/mergeable;
- PR #39 has no review submissions or comments;
- MASA branch tip remained `0856d321...` from 2026-09-18;
- MUNE branch tip remained `8f669e39...` from 2026-09-18;
- no independent R26 PASS/FAIL is accepted yet.

## Failed predecessor chain

Preserve all failed exact subjects. Most recent:
- R22 `f367ef6776fa98ffe6cf455a4101674e8e244a4b` — duck-typed task digest bypass.
- R23 `e3498a1ead2d9dde186c604961bb184dc3b2a764` — custom-equality admission identity bypasses.
- R24 `0f112eda3dafa18ea81fac86b86f08978524a8a4` — adjacent admission runtime-contract bypasses.
- R25 `c1f445e29b56711ad451cab91f8d5e55c3817351` — direct canonical Episode mutation bypass.
- R26 is current successor, not independently accepted.

## Immediate next actions

1. Fresh-check R26 branch and PR #39 remain exactly `c82229f1...`.
2. Read fresh PR reviews/comments and MASA/MUNE Bus replies bound to that exact head.
3. If independent FAIL lands, preserve R26 and create R27 RED-first.
4. If independent PASS lands, record exact acceptance without treating it as merge authority.
5. If no external verdict has landed, hostile-probe the retrieval-to-Episode governance boundary next:
   `RetrievalAdmissionPolicy.verify()`, receipt/evidence runtime types, equality/hash behavior, and exact admitted source/version/scope binding.
6. Keep Issue #5 learned-routing gate CLOSED until the exact Kernel acceptance condition is met.
7. Do not merge or perform protected effects without Patrick's explicit authority.
8. Save a successor continuation checkpoint whenever the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R26::c82229f1`
