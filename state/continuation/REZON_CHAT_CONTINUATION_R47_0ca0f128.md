# REZON CHAT CONTINUATION — R47 / 0ca0f128

Restore token: `REZON::RESTORE_AND_RUN::R47::0ca0f128`

Recovery evidence only. This file does not authorize merge, canonical promotion,
deployment, install, activation, provider/model/credential mutation, training,
learned-routing activation, Project Runner registration/authority, or any other
protected effect.

## Operating rules

- Repository: `thebrazenbeard/rezon`.
- Patrick retains sole merge/protected-effect authority.
- Preserve failed exact subjects; never rewrite a failed head into a pass.
- Non-PR coordination uses `thebrazenbeard/chat-communication-bus`.
- Source/local/hosted/review/merge/install/runtime/behavior remain separate.
- Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing remains CLOSED pending
  fresh exact-head Kernel acceptance.

## External design source used this turn

Project Runner:
- repository: `thebrazenbeard/project-runner`
- exact reviewed main subject:
  `bc05812b560b4fcde3a362e72fba04c626cafac8`
- reviewed artifacts: `README.md`, `PROJECT_RUNNER.md`,
  `runner/leases.py`, `runner/persistent_state.py`,
  `runner/github_backend.py`, `runner/verify.py`,
  `runner/work_units.py`, M5 GitHub-backend plan.

Relevant Project Runner mechanisms:
- semantic work fingerprints;
- persistent lineage budgets with generation CAS;
- durable leases with monotonic fencing;
- stale-fence completion rejection;
- exact-subject currentness after execution;
- technical route capability separated from target authority;
- expected-head/blob mutation preconditions;
- post-write readback;
- backend success != completion until independent verification.

Project Runner is design evidence only. It does not grant Rezon authority and
was not installed/registered by this work.

Durable Rezon boundary doc:
`docs/architecture/PROJECT_RUNNER_OUTER_ORCHESTRATION_BOUNDARY.md`

Boundary doc commit:
`27a6b764ffc82a52ab01188996bb95dfb8b9148d`

## Current frontier — R47

Branch:
`work/rezon-kernel-v0-r47-receipt-producer-binding`

Draft PR:
`#67`

Exact final head:
`0ca0f1283775b2cf4220c830f42cc767e85a5116`

Status:
`SOURCE_CREATED / EXACT_FINAL_LOCAL_GREEN / EXACT_FINAL_HOSTED_GREEN / R4_COMPOSITION_GREEN / INDEPENDENT_REREVIEW_PENDING / DRAFT_PR / UNMERGED`

Qualification:
- R47 hostile regressions: **2/2 PASS**
- focused R16-R47: **133/133 PASS**
- full suite: **262/262 PASS**
- compileall: PASS
- git diff --check: PASS
- exact-final hosted run: `35471168474` SUCCESS
- hosted job: `105972276028` SUCCESS

Qualification file:
`docs/qualification/KERNEL_V0_R47_RECEIPT_PRODUCER_BINDING.md`

## R46 -> R47 failure repaired

Failed whole-Kernel R46:
`854606a730a7ef5d628d51c5167a3f2e11ff1512`

R46 added:
`ResultReceipt.execution_output_digests`
so different canonical outputs no longer collapse to equal top-level receipts.

Fresh R47 hostile probe found:
- two runs had different canonical Episode snapshot digests;
- same canonical output digest;
- different canonical producer execution IDs;
- equal R46 top-level receipts.

Frozen R47 RED:
`ce6f115d540719a4200a1cc1e0d87a8dee15f27f`

Exact-R46 RED result:
**2 failed / 0 passed**

R47 repairs:
- receipt: `57d8fab238c6aa3dc0186d42aea980faee2433a7`
- runner: `d5fc1919dc4f903180a626eba87d8cf2716ad483`

R47 adds:
`ResultReceipt.execution_producer_ids`

Each pair binds:
`(execution_id, canonical_producer_execution_id)`

Canonical producer execution ID commits to:
- node identity;
- canonical input snapshot digest;
- task-specification digest / no-task-spec marker;
- canonical output digest.

CI-enablement head:
`f7059ca38960302e861ba4b3ff59ff6c732d0221`

Executable hosted run:
`35471119146` SUCCESS

## R45 -> R46 context

Failed whole-Kernel R45:
`5a7f6154f8b51212b70ea673fcfcbee9a6b017c7`

Frozen R46 RED:
`a75ae464378c6953cd13ec44af4e1174a59347f4`

R45 allowed different admitted canonical outputs to return equal ResultReceipt
values.

R46 added execution/output-digest bindings, qualified at:
`854606a730a7ef5d628d51c5167a3f2e11ff1512`

R46 + R4:
**319/319 PASS**

R46 then failed R47.

## Accepted Benchmark R4 composition

Benchmark R4 accepted source:
`d7373867d3813d32032cb30463e54a6ddf573025`

R47 + R4 local-only no-commit simulation:
- merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- zero conflicts
- combined pytest: **321/321 PASS**
- compileall `src tests scripts`: PASS
- benchmark replay: PASS
- diff-check: PASS
- fixture aggregate digest:
  `374160c4b009ab39c57d134ed30feeb46be19851f3c169f46a055be2e14192f4`
- strategy-input digest:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- guarded disposition: 21/24
- false accepts: 2
- operation count: 174
- required violation hits: 9/15
- unsupported acceptance: 0
- hidden failure acceptance: 0
- provenance-currentness accepted: 0
- authority-effect promotion errors: 0
- correlated consensus laundering accepted: 0

Bus integration record:
`messages/20260919T1750-one-rezon-r47-benchmark-r4-integration.md`

Bus commit:
`cf9c9266ce2c79d039911489f5a883356a81b461`

## Independent review

Exact R47 request:
`messages/20260919T1751-one-rezon-r47-hostile-rereview.md`

Bus commit:
`6b179b9964c5e04a936b51200a8cc7eea633e70a`

Targets: MASA / MUNE / RADAR
`requires_reply: true`

At checkpoint time:
- PR #67 exact head: `0ca0f1283775b2cf4220c830f42cc767e85a5116`
- PR #67 open, draft, mergeable, unmerged
- no PR reviews/comments
- MASA latest known tip:
  `0856d321c92d26eee75ad64b945ff9035c2000cf`
- MUNE latest known tip:
  `8f669e39e74e79dae54793a7a6a45d615e64de32`
- Radar latest known tip:
  `91d18f98652e8fb45f00b7345e9e91e7b661b98e`
- no exact R47 independent PASS/FAIL accepted.

## Project Runner composition ceiling

Preferred composition:
1. Project Runner owns durable outer work identity, budget, lease/fence, exact
   external currentness, target authority, mutation preconditions/readback.
2. Rezon performs bounded reasoning/provenance and returns non-promotional exact
   evidence.
3. Project Runner treats Rezon result as backend evidence, not completion.
4. Project Runner separately verifies exact currentness/evidence/fence before its
   own COMPLETE state.
5. Rezon `required_authority` remains fail-closed; a Project Runner target
   grant does not automatically satisfy it.
6. Rezon `ResultReceipt.effect_state` remains PLAN.

No runtime adapter exists yet.

## Next bounded integration candidate

The highest-value Project Runner integration frontier after R47 checkpoint is a
versioned JSON-safe Rezon run-evidence export that:
- carries task/episode/execution/output/producer/source/failure identity;
- is deterministic and digestible;
- preserves `effect_state=PLAN`;
- performs no I/O and no authority translation;
- can later be wrapped by a Project Runner backend adapter without Project
  Runner needing Rezon trace internals.

Implement RED-first on a new successor only if exact R47 remains current.

## Immediate next actions

1. Fresh-check PR #67 exact head and reviewer state.
2. Fresh-check MASA/MUNE/Radar Bus replies.
3. If independent R47 FAIL: preserve R47 and create successor RED-first.
4. If independent R47 PASS: record exact acceptance; do not infer merge authority.
5. If no verdict and continuing:
   - implement the side-effect-free versioned JSON evidence export as a bounded
     integration feature;
   - do not add persistent databases/leases to Rezon;
   - do not translate Project Runner grants into Rezon authority.
6. Keep Issue #5 learned-routing CLOSED.
7. No merge/protected effect without Patrick's exact authority.

## Restore command

`REZON::RESTORE_AND_RUN::R47::0ca0f128`
