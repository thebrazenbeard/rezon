# Rezon Kernel V0 R47 Top-Level Canonical Producer Binding

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R47 is the bounded successor to failed whole-Kernel R46 exact subject
`854606a730a7ef5d628d51c5167a3f2e11ff1512`.

R46's top-level canonical output binding and the reviewed Rezon / Project Runner
outer-orchestration boundary remain valid within their narrower scopes.

The integration comparison continues to use the exact Project Runner M5 source:

`thebrazenbeard/project-runner@bc05812b560b4fcde3a362e72fba04c626cafac8`

Project Runner remains design evidence only. It does not grant authority over
Rezon.

## R46 hostile failure

R46 distinguished different canonical outputs at the top-level receipt, but
still allowed two materially different canonical input states to collapse to
the same receipt when the emitted canonical output happened to be identical.

Frozen reproduction:
- same task ID;
- same deterministic execution ID;
- same final Episode version;
- same canonical output digest;
- no failures/unresolved conditions;
- input snapshot A contains observation content `input-alpha`;
- input snapshot B contains observation content `input-beta`;
- canonical input snapshot digests differ;
- canonical producer execution IDs differ;
- **top-level R46 receipts compare equal**.

Observed exact-R46 trace subjects:

Snapshot A:
`76647456ef6e764ab8ed91ad8746d6555a6dbd41f147768672e4d10f049f57ca`

Snapshot B:
`ffc46e968d3d420b37f41a03ad4fcdab3c970fda6fa76dfd67a6abe2ec8d5015`

The canonical producer execution ID already commits to:
- node ID;
- canonical Episode snapshot digest;
- task-specification digest or explicit no-task-spec marker;
- canonical output digest.

Therefore the trace already possessed the exact provenance identity needed by
an outer exact-evidence orchestrator; the top-level receipt did not.

Disposition:
`R46_RECEIPT_INPUT_PROVENANCE_IDENTITY = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R46 remains preserved, draft, and unmerged.

## Frozen R47 RED

Regression file:
`tests/test_r47_receipt_producer_binding.py`

Exact RED commit:
`ce6f115d540719a4200a1cc1e0d87a8dee15f27f`

Fresh exact-R46 result:
**2 failed / 0 passed**.

Frozen tests:
1. same canonical output from different canonical input snapshots must produce
   different top-level receipts and explicit execution/producer bindings;
2. the same input/output reasoning event under the same deterministic run
   identity must produce the same receipt binding.

## R47 repair

Receipt repair:
`57d8fab238c6aa3dc0186d42aea980faee2433a7`

Runner repair:
`d5fc1919dc4f903180a626eba87d8cf2716ad483`

R47 adds:

`ResultReceipt.execution_producer_ids: tuple[tuple[str, str], ...]`

Each binding is:
`(execution_id, canonical_producer_execution_id)`

Receipt validation requires:
- the outer container is an exact tuple;
- every binding is an exact two-element tuple;
- execution ID and canonical producer ID are non-empty exact built-in strings;
- every bound execution ID exists in the receipt's `execution_ids`;
- no execution ID is producer-bound twice.

The runner emits producer bindings only for trace records whose
`canonical_producer_execution_id` is non-null.

R46's `execution_output_digests` is retained. Therefore the top-level receipt
now exposes both:
- exact canonical output identity; and
- exact canonical production-event identity.

## Project Runner relevance

Project Runner M5's outer completion contract distinguishes:
- semantic outer work identity;
- exact current input subject;
- backend result/evidence;
- durable lease/fence;
- target authority;
- independently verified completion.

R47 makes Rezon's natural top-level result evidence substantially more suitable
for that model because an adapter no longer needs trace internals merely to
distinguish identical output produced from different Rezon reasoning states.

This does **not** collapse the systems:
- Project Runner still owns durable outer work identity/currentness/fencing;
- Rezon still owns in-process reasoning/provenance;
- Rezon receipt remains evidence, not Project Runner COMPLETE;
- Project Runner target grants remain external evidence/governance and do not
  automatically satisfy Rezon `required_authority`.

The durable boundary remains:

`docs/architecture/PROJECT_RUNNER_OUTER_ORCHESTRATION_BOUNDARY.md`

## Effect ceiling preserved

`ResultReceipt.effect_state` remains constrained to `PLAN`.

Neither `execution_output_digests` nor `execution_producer_ids` proves:
- an external effect occurred;
- an external subject remained current;
- a durable lease/fence was valid;
- target authority existed;
- a deployment/install/runtime promotion occurred.

## Qualification

CI-enablement head:
`f7059ca38960302e861ba4b3ff59ff6c732d0221`

Fresh detached-checkout qualification:
- R47 regressions: **2/2 PASS**;
- focused R16-R47 controls: **133/133 PASS**;
- recent controls: **52/52 PASS** before remote cut;
- full suite: **262/262 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35471119146`;
- exact executable head `f7059ca38960302e861ba4b3ff59ff6c732d0221`;
- test job `105972145152`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R46 final: `854606a730a7ef5d628d51c5167a3f2e11ff1512`
- R47 branch: `work/rezon-kernel-v0-r47-receipt-producer-binding`
- frozen RED: `ce6f115d540719a4200a1cc1e0d87a8dee15f27f`
- receipt repair: `57d8fab238c6aa3dc0186d42aea980faee2433a7`
- runner repair: `d5fc1919dc4f903180a626eba87d8cf2716ad483`
- CI-enablement head: `f7059ca38960302e861ba4b3ff59ff6c732d0221`

## Explicit scope / non-claims

R47 establishes top-level binding from runner execution identity to canonical
producer execution identity.

It does not establish:
- Project Runner runtime installation or Rezon registration;
- distributed/process-restart durability inside Rezon;
- lease/fencing semantics inside Rezon;
- authority translation between Project Runner and Rezon;
- external mutation success/currentness/readback;
- semantic truth;
- independent hostile PASS on R47;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve every failed exact subject.
5. Do not merge without Patrick's explicit authority.
