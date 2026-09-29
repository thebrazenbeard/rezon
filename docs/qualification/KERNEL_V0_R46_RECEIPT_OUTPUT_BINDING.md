# Rezon Kernel V0 R46 Top-Level Canonical Output Binding

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R46 is the bounded successor to failed whole-Kernel R45 exact subject
`5a7f6154f8b51212b70ea673fcfcbee9a6b017c7`.

R45's non-empty canonical source-reference repair remains valid within that
narrower scope.

R46 was prompted by comparison with the exact Project Runner M5 source
`thebrazenbeard/project-runner@bc05812b560b4fcde3a362e72fba04c626cafac8`,
whose completion model requires exact work/result evidence rather than a
convenience success pointer.

Project Runner is design evidence only. It does not grant authority over Rezon.

## R45 hostile failure

Exact R45 could execute and canonically admit two materially different outputs
while returning equal top-level `ResultReceipt` values.

Frozen reproduction:
- same task ID;
- same deterministic execution ID;
- same Episode ID/version shape;
- no failures/unresolved conditions;
- admitted output A content: `alpha`;
- admitted output B content: `beta`;
- trace A canonical output digest:
  `33035ee59277fef88243b876f7ddc49cb6f1967e02a5ab5403266d0fad702e99`;
- trace B canonical output digest:
  `48266b8a805d4e425dc17ac54427693915cc87e47fbacc48272f983e51d52e1c`;
- **top-level receipts compared equal**.

The exact output identity existed only in `TraceRecord`, while the natural
outer-orchestrator surface, `ResultReceipt`, did not bind it.

Therefore an outer exact-evidence orchestrator could not distinguish materially
different Rezon results by receipt identity alone.

Disposition:
`R45_RECEIPT_OUTPUT_IDENTITY = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R45 remains preserved, draft, and unmerged.

## Frozen R46 RED

Regression file:
`tests/test_r46_receipt_output_binding.py`

Exact RED commit:
`a75ae464378c6953cd13ec44af4e1174a59347f4`

Fresh exact-R45 result:
**2 failed / 0 passed**.

Frozen tests:
1. different canonical output digests must produce different receipts and
   expose explicit execution/output bindings;
2. the same canonical output under the same deterministic run identity must
   produce the same receipt binding.

## R46 repair

Receipt repair:
`3e9dc13d3cab13929a0dc458c27f4cf38a6c8c7d`

Runner repair:
`c78e129e88f7f3077c507bbcfa1ff73fa24809bd`

R46 adds:

`ResultReceipt.execution_output_digests: tuple[tuple[str, str], ...]`

Each binding is:
`(execution_id, canonical_output_digest)`

Receipt validation requires:
- the outer container is an exact tuple;
- every binding is an exact two-element tuple;
- execution ID and digest are non-empty exact built-in strings;
- every bound execution ID exists in the receipt's `execution_ids`;
- no execution ID is bound twice.

The runner emits bindings only for trace records with a non-null canonical
output digest.

Executions that produce no canonical output remain represented by
`execution_ids` without a fabricated output digest.

## Effect ceiling preserved

R46 does not turn `ResultReceipt` into a completion/authorization artifact.

`ResultReceipt.effect_state` remains constrained to `PLAN`.

The new binding proves only which canonical output digest was associated with a
recorded execution in this Rezon run. It does not prove:
- external effect completion;
- external subject currentness;
- durable lease ownership;
- target authority;
- deployment/installation;
- semantic truth.

## Project Runner composition rule

The reviewed outer-orchestration boundary is frozen in:

`docs/architecture/PROJECT_RUNNER_OUTER_ORCHESTRATION_BOUNDARY.md`

Architecture commit:
`27a6b764ffc82a52ab01188996bb95dfb8b9148d`

Normative split:
- Rezon owns in-process reasoning/provenance and exact non-promotional result
  evidence.
- Project Runner owns durable work fingerprinting, persistent budgets,
  claim/reclaim leases and fencing, external-subject currentness, target
  authority, mutation preconditions/readback, and independent completion
  verification.

Project Runner grants do not automatically satisfy Rezon
`required_authority`, and Rezon receipts do not automatically complete Project
Runner work.

## Qualification

CI-enablement head:
`363bf139c9184a906fd762c20d7ee1debebe617a`

Fresh detached-checkout qualification:
- R46 regressions: **2/2 PASS**;
- focused R16-R46 controls: **131/131 PASS**;
- recent controls: **50/50 PASS** before remote cut;
- full suite: **260/260 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35470748660`;
- exact executable head `363bf139c9184a906fd762c20d7ee1debebe617a`;
- test job `105971139471`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R45 final: `5a7f6154f8b51212b70ea673fcfcbee9a6b017c7`
- R46 branch: `work/rezon-kernel-v0-r46-receipt-output-binding`
- frozen RED: `a75ae464378c6953cd13ec44af4e1174a59347f4`
- receipt repair: `3e9dc13d3cab13929a0dc458c27f4cf38a6c8c7d`
- runner repair: `c78e129e88f7f3077c507bbcfa1ff73fa24809bd`
- CI-enablement head: `363bf139c9184a906fd762c20d7ee1debebe617a`
- Project Runner boundary doc:
  `27a6b764ffc82a52ab01188996bb95dfb8b9148d`

## Explicit scope / non-claims

R46 establishes top-level binding from Rezon execution identity to canonical
output digest.

It does not establish:
- distributed/process-restart durability;
- lease/fencing semantics inside Rezon;
- Project Runner runtime installation or Rezon registration;
- authority translation between Project Runner and Rezon;
- external mutation success/currentness/readback;
- semantic truth;
- independent hostile PASS on R46;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve every failed exact subject.
5. Do not merge without Patrick's explicit authority.
