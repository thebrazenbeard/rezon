# REZON CHAT CONTINUATION — 2026-09-18 10:50 ET

Restore token:

`REZON::RESTORE::REZON_CHAT_CONTINUATION_20260918T1050-0400`

This is a durable chat-continuation checkpoint for Rezon. It is **not** a merge, canonical promotion, deployment, installation, activation, or qualification artifact. The branch is intentionally separate from active reviewed branches.

## 1. Authority and operating rules

Repository: `thebrazenbeard/rezon`.

Canonical repo `main` remains `e3d7a41eccb49a9f403ef66f511faef677ceec1b` at this save. Do not describe unmerged PR source as merged `main`.

Current user/project rules still apply:

- live user instruction outranks this checkpoint;
- fresh exact Git/PR/Bus evidence outranks this continuation text;
- keep source/build/test/hosted-CI/independent-review/merge/runtime/effect states separate;
- do not merge, deploy, install, activate providers/models/training/learned routing, mutate credentials, or perform other protected effects without Patrick's exact authority;
- all non-PR inter-agent coordination goes through `thebrazenbeard/chat-communication-bus`;
- if a reviewed exact head moves, prior PASS/FAIL does not automatically carry forward;
- for failed reviewed subjects, preserve them as evidence and repair on a successor branch rather than rewriting the reviewed subject;
- green tests are evidence, not semantic truth or reasoning-superiority proof.

## 2. Rezon purpose and core invariants

Working definition:

> Rezon dynamically composes partially independent computational processes over a provenance-preserving temporal epistemic hypergraph, allocating additional reasoning according to uncertainty, contradiction, information value, cost, and verification need.

Core invariants to preserve:

- evidence != inference != hypothesis != assumption != observation != test result != decision;
- repetition/model consensus does not promote a hypothesis to evidence;
- nodes are constrained epistemic/computational operations, not personas;
- heterogeneous executors are expected;
- routing != authority/truth/confidence;
- a verified counterexample may outweigh unsupported consensus;
- private chain-of-thought is not durable project state; persist structured rationale/evidence/derivation/trace artifacts instead;
- same-model blind runs are not statistically independent; lineage matters;
- preserve ambiguity rather than forcing convergence;
- fast/slow loops, reasoning type, depth/effort, and architecture are distinct;
- extra reasoning is allocated by uncertainty, contradiction, expected information value, causal importance, and verification need;
- learned/latent structures remain advisory and cannot establish identity, provenance, authority, currentness, or truth on their own.

Issue #5 donor/learned-routing gate remains closed until Kernel V0 receives fresh exact-head independent acceptance.

## 3. IMPORTANT supersession note from this chat

This conversation locally began repairing R6 from test-only RED head `19c330786c88f01e9e6779784b18921842bb62be` and temporarily held an uncommitted partial repair in a local temp checkout.

That local WIP is **superseded and must be discarded**.

A newer completed R6 already exists in GitHub PR #20. Do not reconstruct or continue the stale local patch from this conversation. Continue from exact final PR #20 head below.

The user supplied a screenshot showing this later state; fresh GitHub readback confirmed it.

## 4. Kernel V0 R6 — primary current frontier

PR: #20 — `P0 R6: close Kernel V0 hostile whole-PR blockers`

Branch:
`work/rezon-kernel-v0-r6-hostile-hardening`

Failed R5 base:
`d60f99d1420b56b2923e6977a3d0c3a7f3412762`

Important R6 provenance:

- imported Masa hostile head: `ff22ca92eb5e588f3f50c2a5c0d61599655e9b5a`
- combined hostile RED head: `19c330786c88f01e9e6779784b18921842bb62be`
- initial executable GREEN: `5b05fba48c8a93bfb9f9cc41c049a866a1184f2a`
- late B4 self-hostile RED: `f87e887`
- current executable GREEN: `7492271c356f445561a4125a771942b2cf0c95eb`
- **final documentation/review head:** `f94f8f5aa3075179ab9b3eae7fdf8c81773f582a`
- **final tree:** `dcff3a2712be7a4606b973b843aa4f6e84fe6e92`

PR #20 is open, draft, mergeable, unmerged.

Final repaired semantics:

### B1 — duplicate node ID / descriptor substitution
- duplicate node IDs fail closed before scheduling;
- schedule decisions carry exact descriptor index;
- runner executes exact indexed descriptor and checks node ID match.

### B2 — source-version typing
- `Proposition` and `Hyperrelation` carry explicit `source_versions`;
- no semantic inference from `"@" in source_ref`;
- retrieval admission emits explicit version provenance;
- worker-emitted versions absent from governed view fail admission;
- version entries are non-empty and unique.

### B3/B4 — generic ResultReceipt is non-dispositional
The stronger final rule supersedes an earlier typed-disposition-evidence attempt:

- `claim_disposition_complete` defaults to `False`;
- generic `ResultReceipt` rejects any non-empty accepted/rejected claim IDs;
- generic `ResultReceipt` rejects `claim_disposition_complete=True`;
- runner never emits claim-disposition completeness;
- claim disposition is deferred to a future separately governed artifact.

### B5 — relation blindness
Kernel V0 has no typed safe-shared worker-relation class. An independence-required view fails closed if it contains any worker-produced relation.

### B6 — external independence attestation
`IndependenceVerificationEvidence` binds:
- `saw_other_answer`;
- common-evidence refs;
- consumed-evidence refs;
- executor/model/provider/prompt/context lineage.

Policy requires exact external attestation and `saw_other_answer=False`. Pairwise independence also rejects shared consumed-evidence intersection.

### M1 — hostile consensus oracle
Consensus counted as evidence fails closed when worker independence is missing, empty, false, or partially non-true.

Qualification:

- exact final head `f94f8f5…`
- fresh CPython 3.12.10 checkout: **104/104 tests PASS**
- compileall: PASS
- `git diff --check`: PASS
- tracked working tree: clean
- hosted GitHub Actions run `35351778076`: **SUCCESS**
- hosted install / compile / test / diff-check: all PASS
- qualification record: `docs/qualification/KERNEL_V0_R6_HOSTILE_HARDENING.md`

Current state:

`SOURCE_BUILD_TEST_HOSTED_GREEN_104 / FINAL_R6_EXACT_HEAD_FROZEN / INDEPENDENT_HOSTILE_REREVIEW_PENDING / DRAFT / UNMERGED`

### R6 Bus correction

Earlier Bus request commit `0c4fd088366e92a4821ea1c7c4a1d3b7e184afc3` was stale because it bound review to obsolete head `f3438cc…`.

This checkpoint corrected that before save.

Current exact-head rebind Bus commit:

`2d3057087f57a91b877573ba700245a94740d5bf`

That message explicitly supersedes `f3438cc…` and asks Mune/Masa/One to review exact final `f94f8f5…`.

## 5. Benchmark V1 R4 — frozen independent-review subject

PR #18.

Branch:
`rezon/benchmark-v1-r4-unknown-currentness`

Exact frozen review head:
`d7373867d3813d32032cb30463e54a6ddf573025`

Tree:
`efbfa03efa824b65379a6cb65cb7c6353733061c`

Status:
- draft/open/mergeable/unmerged;
- local exact tests: 105/105 PASS;
- public `StrategyInput` direct path now rejects duplicate source IDs, duplicate candidate IDs, and missing primary candidate;
- frozen 24-case benchmark remains unchanged:
  - strategy-input digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
  - 21/24 disposition-correct
  - 2 false accepts
  - 174 operations
  - 9/15 required violation hits.
- no exact-head hosted-GREEN claim was established at the last readback;
- independent qualification remains pending.

Relevant Bus repair commit:
`f6b0ce3e770d59a4e25b3da3bfdf6e09c0c719a7`

Keep PR #18 frozen while exact-head review is pending.

## 6. Benchmark V1 R5 typed support/verification design — frozen design-only subject

PR #19.

Branch:
`rezon/benchmark-v1-r5-typed-support-design-final`

Exact successor head:
`05c668bf67349e87738990aa65f40ec07e9001e4`

Tree:
`8f9e2e4d5c1178d5078fd880122dd314c197abdd`

Design-only. No R5 implementation or qualification is implied.

Masa predecessor verdict was:
`CHANGES_REQUESTED / DESIGN_HOSTILE_FAIL`

Successor design addresses:

- B1 verification-source admission/currentness governance;
- B2 explicit `DISTINCT_EXECUTION_REQUIRED` anti-circularity for every verification kind;
- B3 unique `(target_type,target_id,kind)` receipt tuple so VERIFIED/REFUTED collision is structural invalidity;
- B4 evaluator-independent false-`VERIFIED` oracle;
- M1 unsolicited/non-required REFUTED receipts are diagnostic only and cannot candidate-local DoS.

The design explicitly distinguishes its historical R4 source base from current R4 review subject `d7373867…` and requires reconciliation before implementation.

Design audit:
- one design document changed from reviewed predecessor;
- `git diff --check`: PASS;
- blocker/stale-rule audit: PASS;
- 665-line design.

Relevant Bus repair commit:
`a17d7f2129a08757de3e2a664c0e606a99533a4b`

Keep PR #19 frozen for exact-head hostile rereview. Do not implement R5 from this design until that gate clears and current R4 reconciliation is performed.

## 7. Intranel side project current subject

Repo:
`thebrazenbeard/intranel`

PR #3.

Branch:
`rezon/intranel-v1-r3-main-reconcile`

Exact head:
`27c4676d79621de6d17dd14ed4064ea5e742c107`

Tree:
`b94a4ab2cc73a4a34dd98306f3347deff95d495a`

Status:
- draft/open/mergeable/unmerged;
- CPython 3.12.10;
- 115/115 tests PASS;
- compile PASS;
- parser/schema hostile probe: 38 cases with one intentionally documented full-Gregorian parser boundary;
- admission/state probe: 29 cases / 0 violations;
- Python↔Node canonical probe: 26 cases / 0 mismatches;
- independent Node vector digest verification: 3/3 exact;
- hosted Actions remains NO-RUN due zero-runner/zero-step infrastructure on the exact head.

Latest repair was One's fractional-time blocker:
- 1–6 fractional digits only;
- six-digit ordering exact;
- 7+ digits rejected by parser and schema;
- RFC 3339-derived, offset-aware ISO 8601 profile;
- leap seconds not accepted.

Relevant Bus repair commit:
`68e4e8f88dab06b0b87dbd9ce5bd058743beb950`

Keep Intranel PR #3 frozen pending exact-head review.

## 8. What to do immediately after restore

1. Fresh-check Rezon PR #20 exact head. Expected current subject is `f94f8f5aa3075179ab9b3eae7fdf8c81773f582a`.
2. Fresh-check `bus/mune-v2`, `bus/masa-v2`, and `bus/one-v2` for replies to Bus commit `2d3057087f57a91b877573ba700245a94740d5bf`.
3. If a review names any other R6 head, treat it as stale for final R6 unless it explicitly binds to `f94f8f5…`.
4. If exact final R6 receives CHANGES_REQUESTED, preserve `f94f8f5…` and repair on a successor branch with RED-first executable evidence.
5. If exact final R6 receives independent PASS, report that exact-subject result separately from merge state. Do **not** merge without Patrick's explicit merge authority.
6. Continue checking frozen R4 PR #18 and R5 design PR #19 review lanes. Do not move either review subject just to create activity.
7. Continue Intranel only from exact PR #3 head if still current; otherwise rebind before work.
8. Never resurrect the stale local R6 partial patch that existed earlier in this chat.
9. After Kernel V0 independent acceptance and explicit integration authority, the next major frontier is the gated donor/learned-routing work (HCAE/HyPER/hyperbolic) plus stronger benchmark/live matched-budget work; do not cross that gate early.

## 9. Relevant historical review evidence retained for context

Kernel R5 PR #15 exact failed subject:
`d60f99d1420b56b2923e6977a3d0c3a7f3412762`

Mune:
`R5_DELTA_SOURCE = PASS / WHOLE_PR_SOURCE = CHANGES_REQUESTED`

Masa:
`HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED`

Those verdicts belong to R5 and are provenance for R6; they are not R6 verdicts.

Combined R6 RED at `19c3307…`:
**7 failed / 1 passed** before production repair.

The sole initially passing imported relation-blindness test was identified as a false negative because its generic node was never scheduled; R6 added a scheduler-selected case.

## 10. Restore behavior

On receiving the restore token in a new chat:

- read this checkpoint from exact branch/commit first;
- fresh-check current GitHub and Bus state before making any currentness claim;
- treat this file as recovery context, not higher authority than newer exact source/review evidence;
- continue as the Rezon project execution/review lane, not as a separate persona;
- use Bus for all non-PR coordination;
- preserve reviewed subjects and exact-head evidence;
- finish bounded work before expanding scope.

Do not infer that any pending independent review passed merely because source/build/test/CI are green.
