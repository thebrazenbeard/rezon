# Kernel V0 R50 — Receipt/Trace Source-Version Binding

Status: `SOURCE_REPAIRED / LOCAL_FULL_PASS / BENCHMARK_R4_COMPOSITION_PASS / HOSTED_CI_PENDING / INDEPENDENT_REREVIEW_PENDING`

Exact failed predecessor:
`8ed6bfff2703f57b002daf30df2260f02c0c2183` (R49 / PR #71)

Frozen hostile RED:
`8b52d24a863f708e667fef99c35e19c82896904f`

Source repair:
`d9a2a35f2408a4fac7214d5cb8d300beb3762f65`

## Defect

R49 exported both:
- receipt-level `source_versions`; and
- per-`TraceRecord` `source_versions`.

The exporter validated execution IDs, output bindings, producer bindings and
task-envelope identity, but did not verify that receipt-level source versions
were the runner's ordered dedupe of trace-record source versions.

A caller could therefore use `dataclasses.replace()` to forge non-empty
receipt source versions while leaving the trace unchanged. The evidence export
would contain contradictory provenance and still receive an evidence digest.

## Frozen RED

The hostile regression replaces only:

`receipt.source_versions = ("forged-source-version",)`

while preserving the exact trace.

Exact R49 result:
**1/1 FAIL** because `export_run_evidence()` did not raise.

## Repair

`_validate_receipt_trace_binding()` now recomputes expected receipt source
versions from trace records using the same ordered first-seen dedupe semantics
as `EpisodeRunner` and requires exact tuple equality before export.

This keeps the existing structural claim ceiling. It is not object-origin
authentication, a signature, or independent proof of external source
currentness/authority.

## Qualification

Fresh repaired source:
- R49 evidence-export tests: **7/7 PASS**;
- full repository: **272/272 PASS**;
- compileall: PASS;
- `git diff --check`: PASS.

Accepted Benchmark R4 no-commit composition:
- exact R4: `d7373867d3813d32032cb30463e54a6ddf573025`;
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`;
- zero conflicts;
- composed full suite: **331/331 PASS**;
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

The local no-commit Benchmark R4 merge was aborted after verification. No
benchmark integration commit or branch was created.

## Claim ceiling

R50 establishes structural internal consistency between:
- receipt execution coverage;
- receipt output bindings;
- receipt producer bindings;
- receipt source-version aggregate;
- per-trace source-version evidence;
- task-envelope binding;
- canonical producer recomputation.

It does not establish:
- cryptographic object-origin authenticity;
- outer source currentness or provider authority;
- distributed fencing/completion truth;
- merge/deploy/install/provider/model/credential mutation authority;
- learned-routing qualification.

Issue #5 remains CLOSED.

No protected effect was performed.
