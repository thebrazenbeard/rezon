# REZON CHAT CONTINUATION — R25 / c1f445e2

Restore token: `REZON::RESTORE_AND_RUN::R25::c1f445e2`

This is the durable recovery point for the current Rezon execution terminal.

Recovery evidence only. No merge, canonical promotion, deployment, installation,
activation, provider/model mutation, training, learned-routing activation,
credential/provider mutation, or other protected effect is authorized by this
file.

## Canonical operating rules

- Canonical repository: `thebrazenbeard/rezon`.
- Current Kernel work remains branch/PR based and exact-head bound.
- Preserve every failed exact subject as evidence; never rewrite a failed head into a passing one.
- Patrick is sole merge/protected-effect authority.
- All non-PR inter-agent communication goes through `thebrazenbeard/chat-communication-bus`.
- Source/build/test/hosted/review/merge/install/runtime/effect/behavior are separate states.
- Green local/hosted CI is not independent acceptance.
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing gate remains CLOSED until fresh exact-head Kernel acceptance.

## Current Kernel frontier — R25

Branch:
`work/rezon-kernel-v0-r25-exact-admission-contract`

Draft PR:
`#38`

Current exact final head:
`c1f445e29b56711ad451cab91f8d5e55c3817351`

Current status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

GitHub exact-final hosted run:
`35457175282` — SUCCESS

Fresh exact-final local qualification:
- R25 hostile regressions: **9/9 PASS**
- full suite: **168/168 PASS**
- compileall: PASS
- git diff --check: PASS

Focused local R16-R25 qualification before final freeze:
**39/39 PASS**

## R24 failure that caused R25

Failed exact R24 subject:
`0f112eda3dafa18ea81fac86b86f08978524a8a4`

R24 had hardened initial identity comparisons, but adjacent runtime fields still
trusted Python annotations/equality/hash/lower behavior.

Frozen R25 RED against R24:
`9ab8cee33fc426c461d8df62a60502ae7f1ce5d7`

Nine hostile cases failed on R24:
- eight false-PASS governed checks/failure-hiding paths;
- one malformed proposition-kind path escaped governed rejection and raised an unhandled AttributeError.

False-PASS classes included:
- emitted source refs;
- emitted source versions;
- relation participant refs;
- relation type;
- trusted governed source refs;
- trusted governed source versions;
- trusted governed source bindings;
- a non-empty falsey failure tuple hiding a reported failure.

R24 PR #37 is preserved draft/unmerged and carries the failure disposition.

Bus R24 self-fail record:
`messages/20260919T1308-one-rezon-r24-self-fail-r25.md`
commit:
`4f9b01a0e959e5882450a111214af1423aa2d39d`

## R25 repair

Executable repair:
`4862a5f9be683242402092f7ed8f5a0c68bba0d9`

CI-enablement head:
`ab8898435c04c53ec695e9ab15d3d41cd879aaf9`

Final qualification/documentation head:
`c1f445e29b56711ad451cab91f8d5e55c3817351`

Qualification record:
`docs/qualification/KERNEL_V0_R25_EXACT_ADMISSION_CONTRACT.md`

R25 validates the runtime admission contract before canonical output hashing or
governed equality/membership checks. It requires exact runtime types for the
structured objects, enums, strings, tuples, provenance inputs, relation
participants, permitted kinds/types, and failure state used by admission.

R23 exact-TaskSpecification and R24 exact identity hardening remain preserved.

## Benchmark R4 composition probe

Accepted Benchmark R4 source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit merge simulation with exact R25 final:
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **227/227 PASS**
- compileall `src tests scripts`: PASS
- reference Benchmark V1 replay: PASS
- git diff --check: PASS
- strategy-input digest preserved:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded disposition preserved: 21/24
- false accepts preserved: 2
- deterministic operations preserved: 174

No remote integration subject or merge was created.

Bus integration record:
`messages/20260919T1311-one-rezon-r25-benchmark-r4-integration.md`
commit:
`4d1041da7c2d115512a9c5bbfa8c878aada540ad`

## Independent hostile rereview

Exact-head request:
`messages/20260919T1312-one-rezon-r25-hostile-rereview.md`

Bus commit:
`463e251657656f06df88b34aaf86e305ca82095a`

Targets:
MASA / MUNE

`requires_reply: true`

At checkpoint time:
- PR #38 had no submitted reviews;
- no independent PASS/FAIL is accepted for R25 yet.

Do not inherit any prior R23/R24/local/hosted verdict as R25 independent acceptance.

## Failed predecessor chain

Preserve all exact failed subjects, including R8-R24.
Most recent:
- R22 `f367ef6776fa98ffe6cf455a4101674e8e244a4b` — duck-typed task digest bypass.
- R23 `e3498a1ead2d9dde186c604961bb184dc3b2a764` — custom-equality identity binding bypasses.
- R24 `0f112eda3dafa18ea81fac86b86f08978524a8a4` — adjacent admission runtime-contract/equality bypasses.
- R25 is current successor, not independently accepted.

## Immediate next actions

1. Fresh-check R25 branch and PR #38 still point exactly to `c1f445e2...`.
2. Read fresh PR reviews/comments and MASA/MUNE Bus replies bound to the exact head.
3. If independent FAIL lands, preserve R25 exactly and create R26 RED-first.
4. If independent PASS lands, record exact acceptance without treating it as merge authority.
5. Keep Issue #5 learned-routing gate CLOSED until the exact Kernel acceptance condition is satisfied under current governance.
6. Do not merge or perform protected effects without Patrick's explicit authority.
7. Continue bounded hostile probing while waiting for external review if a fresh attack surface is available.
8. Preserve successor continuation state if the exact subject advances.

## Restore command

`REZON::RESTORE_AND_RUN::R25::c1f445e2`
