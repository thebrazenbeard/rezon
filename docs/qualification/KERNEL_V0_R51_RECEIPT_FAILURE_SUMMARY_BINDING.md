# Kernel V0 R51 — Receipt/Trace Failure Summary Binding

Status: `SOURCE_REPAIRED / LOCAL_FULL_PASS / BENCHMARK_R4_COMPOSITION_PASS / HOSTED_CI_PENDING / INDEPENDENT_REREVIEW_PENDING`

Exact failed predecessor:
`91253aaad94cc3a656321186935a89791f8a08ce` (R50 / PR #74)

Frozen hostile RED:
`8ea0b9ee8523a44604397eeb21bec13ef569db45`

Source repair:
`525711a5a34672272e17438602e24145f5754c33`

## Defect

R50 structurally bound receipt/trace execution IDs, source versions, output
digests, producer identities and task-envelope identity, but did not require
the top-level `ResultReceipt.failures` summary to cover failures recorded by
exact trace records.

A real runner-generated failed outcome can therefore be wrapped with only:

`dataclasses.replace(outcome.receipt, failures=())`

while preserving the failed trace. The exporter previously accepted and
digested evidence whose receipt concealed a trace-level
`CONTRACT_VIOLATION`.

## Frozen RED

The hostile regression uses a real runner path. An executor returning a
non-`ExecutionResult` produces:

- receipt failure: `CONTRACT_VIOLATION`;
- exact trace-record failure: `CONTRACT_VIOLATION`.

The test then clears only the receipt failure tuple.

Exact R50 result:
**1/1 FAIL** because `export_run_evidence()` did not reject the contradictory
summary.

## Repair

The exporter now ordered-dedupes failures present in exact trace records and
requires every such failure to appear in `receipt.failures`.

The relation is intentionally one-way rather than exact equality. Receipt-level
scheduler/authority/unavailable failures may legitimately exist without a
corresponding execution trace record.

A positive regression verifies that a receipt-only `UNAVAILABLE` failure is
still exportable when the trace contains no failure.

## Qualification

Fresh repaired source:
- evidence-export tests: **10/10 PASS**;
- full repository: **275/275 PASS**;
- compileall: PASS;
- `git diff --check`: PASS.

Accepted Benchmark R4 no-commit composition:
- exact R4: `d7373867d3813d32032cb30463e54a6ddf573025`;
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`;
- zero conflicts;
- composed full suite: **334/334 PASS**;
- compileall: PASS;
- diff-check: PASS;
- Benchmark V1 replay: PASS;
- fixture aggregate digest:
  `374160c4b009ab39c57d134ed30feeb46be19851f3c169f46a055be2e14192f4`;
- strategy-input digest:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`;
- guarded disposition: 21/24;
- false accepts: 2;
- deterministic operations: 174;
- required violation hits: 9/15.

The local Benchmark R4 merge was aborted after verification. No integration
commit or branch was created.

## Claim ceiling

R51 establishes structural containment from exact trace-record failures into
the receipt-level failure summary.

It does not establish:
- cryptographic object-origin authenticity;
- outer currentness or authority truth;
- distributed fencing/completion truth;
- semantic truth;
- merge/deploy/install/provider/model/credential authority;
- learned-routing qualification.

Issue #5 remains CLOSED.

No protected effect was performed.
