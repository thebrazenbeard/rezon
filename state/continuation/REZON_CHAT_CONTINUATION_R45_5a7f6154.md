# REZON CHAT CONTINUATION — R45 / 5a7f6154

Restore token: `REZON::RESTORE_AND_RUN::R45::5a7f6154`

Recovery evidence only. This file does not authorize merge, canonical promotion,
deployment, install, activation, provider/model/credential mutation, training,
learned-routing activation, or any other protected effect.

## Operating rules

- Repository: `thebrazenbeard/rezon`.
- Patrick retains sole merge/protected-effect authority.
- Preserve failed exact subjects; do not rewrite a failed head into a pass.
- Non-PR coordination goes through `thebrazenbeard/chat-communication-bus`.
- Source/local/hosted/review/merge/install/runtime/behavior remain separate states.
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing remains CLOSED pending
  fresh exact-head Kernel acceptance.

## Current frontier — R45

Branch:
`work/rezon-kernel-v0-r45-nonempty-source-refs`

Draft PR:
`#64`

Exact final head:
`5a7f6154f8b51212b70ea673fcfcbee9a6b017c7`

Status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Qualification:
- R45 hostile regressions: **3/3 PASS**
- focused R16-R45: **129/129 PASS**
- full suite: **258/258 PASS**
- compileall: PASS
- git diff --check: PASS
- exact-final hosted run: `35468936354` SUCCESS
- hosted job: `105966248222` SUCCESS

Qualification file:
`docs/qualification/KERNEL_V0_R45_NONEMPTY_SOURCE_REFS.md`

### R45 failure repaired

Failed whole-Kernel R44 exact subject:
`1f7bb9838b0be49fff31ba4ddbd2357211b1856b`

R44 closed empty direct-admission attempt identity, but exact empty source refs
could still enter canonical propositions/relations and direct admission.

Frozen R45 RED:
`c7d84f09acabde7e6af881fd26038f36b99d777b`

Exact-R44 RED:
**3 failed / 0 passed**

Frozen variants:
- direct Episode proposition with `source_refs=("",)`;
- direct admission proposition with `source_refs=("",)`;
- direct Episode relation with `source_refs=("",)`.

With `source_versions=("source@v1",)`, this permitted a provenance association
`("", "source@v1")`.

R45 repairs:
- Episode: `8ecafd93d47cb7f1a51f5697b7358199a7238541`
- admission: `602d1baf33eec09201d86a3eae762abff3097e40`
- governed result: `51a03d581f97bfec221230273cd4ac9f1552ff59`

Every present string in the relevant source-ref/source-version tuples must now
be an exact non-empty built-in string. Empty tuples remain valid when provenance
is absent.

CI-enablement head:
`20abf4c5bbfaf2d6b65a4c2db7a28477cd2c6458`

Executable hosted run:
`35468896112` SUCCESS

## Accepted Benchmark R4 composition

Benchmark R4 accepted source:
`d7373867d3813d32032cb30463e54a6ddf573025`

Local-only no-commit R45 + R4:
- merge base `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **317/317 PASS**
- compileall `src tests scripts`: PASS
- benchmark replay: PASS
- diff-check: PASS
- fixture digest:
  `374160c4b009ab39c57d134ed30feeb46be19851f3c169f46a055be2e14192f4`
- strategy-input digest:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded disposition: 21/24
- false accepts: 2
- deterministic operations: 174
- required violation hits: 9/15

No remote integration subject or merge was created.

Bus integration:
`messages/20260919T1731-one-rezon-r45-benchmark-r4-integration.md`

Bus commit:
`90a2a46e2a9deebb59ece82f8d0a8f7169bba47b`

## Independent review

Exact-head request:
`messages/20260919T1732-one-rezon-r45-hostile-rereview.md`

Bus commit:
`0de0315ec1b3870821a7df29773fe680b98773bc`

Targets: MASA / MUNE / RADAR
`requires_reply: true`

At checkpoint time:
- PR #64 exact head `5a7f6154...`
- PR #64 open, draft, mergeable, unmerged
- no PR review/comment landed
- MASA tip `0856d321c92d26eee75ad64b945ff9035c2000cf`
- MUNE tip `8f669e39e74e79dae54793a7a6a45d615e64de32`
- Radar tip `79e3c9686e9ed5646a613c29e64f1a20104dcba6`
- no exact R45 independent PASS/FAIL accepted

## This continuation's advancement

Starting restored subject:
R42 `0445e72d9d9952f8f05b8578479c5fc499166196`

### R43 — evidence source-version correlation

Failed whole-Kernel subject:
`b7282364fad6676cae35aae403688c4ebc93b2f1`

Frozen RED:
`7832b635c33ab20542c872965b5a9a03308a3e2b`

Finding:
differently named evidence objects backed by the same source version could both
be accepted as independent.

R43 repair:
`903dd4491de0fb49803c969f72594560e0556145`

Qualification before successor failure:
- 2/2 R43 PASS
- 124/124 focused PASS
- 253/253 full PASS
- hosted `35468364748` SUCCESS
- R43 + R4: 312/312 PASS

### R44 — direct admission attempt identity

Failed whole-Kernel subject:
`1f7bb9838b0be49fff31ba4ddbd2357211b1856b`

Frozen RED:
`be17911aa4c4e6c086934ae7b7b576687e1cf907`

Finding:
direct admission could canonicalize output with empty execution identity.

R44 repair:
`1219c49cb47f2c9542e15ee855cad7fedcd09ce4`

Qualification before successor failure:
- 2/2 R44 PASS
- 126/126 focused PASS
- 255/255 full PASS
- hosted `35468618743` SUCCESS
- R44 + R4: 314/314 PASS

### R45 — canonical source-reference identity

Current successor:
`5a7f6154f8b51212b70ea673fcfcbee9a6b017c7`

Finding repaired:
empty source-reference identity could enter canonical provenance.

## Recent whole-Kernel chain

Preserve every earlier failed exact subject R22 through R44.
Current successor:
R45 `5a7f6154f8b51212b70ea673fcfcbee9a6b017c7`,
green locally/hosted/composition, not independently accepted.

## Immediate next actions

1. Fresh-check PR #64 remains exact `5a7f6154...`.
2. Fresh-check MASA/MUNE/Radar exact-head replies.
3. If independent FAIL: preserve R45 and create R46 RED-first.
4. If independent PASS: record exact acceptance; do not infer merge authority.
5. If no verdict: probe only concrete canonical effect/provenance failures.
   Avoid ambiguous expansion of relation-vs-evidence independence semantics,
   cleanup-only typing, source/class monkeypatching, and private-memory attacks
   outside the current claim ceiling.
6. Keep Issue #5 learned-routing CLOSED.
7. No merge/protected effects without Patrick's explicit authority.

## Restore command

`REZON::RESTORE_AND_RUN::R45::5a7f6154`
