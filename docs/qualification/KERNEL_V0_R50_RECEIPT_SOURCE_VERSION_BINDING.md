# Rezon Kernel V0 R50 Receipt/Trace Source-Version Binding

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / R4_COMPOSITION_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R50 is the bounded hostile-review successor to failed R49 exact subject
`8ed6bfff2703f57b002daf30df2260f02c0c2183`.

## R49 hostile failure

Independent exact-head review found that R49 exported both:
- `ResultReceipt.source_versions`; and
- per-`TraceRecord.source_versions`

without requiring those representations to agree.

The canonical runner relationship is deterministic:
1. each execution view contributes its input source versions;
2. `EpisodeRunner` accumulates them in first-seen ordered-deduplicated order;
3. the same per-execution input versions are written to each `TraceRecord`;
4. the ordered aggregate becomes `ResultReceipt.source_versions`.

Therefore an otherwise exact `RunOutcome` with only receipt-level
`source_versions` replaced could emit mutually inconsistent provenance and
still receive a deterministic R49 evidence digest.

Disposition:
`R49_RECEIPT_TRACE_SOURCE_VERSION_BINDING = FAIL / CHANGES_REQUIRED`.

R49 remains preserved and unmerged.

## R50 repair

Active branch:
`work/rezon-kernel-v0-r50-receipt-source-version-binding`

Repair implementation is based on exact R49 and:
- recomputes expected receipt source versions from exact trace records;
- uses the runner's first-seen ordered-deduplication semantics;
- requires exact equality with `receipt.source_versions` before export;
- preserves every R49 output/producer/task-envelope consistency check;
- adds both positive and hostile source-version binding regressions.

Exact executable head before this qualification document:
`19e1a23cfaef6ab463a3c368e2b88ed59713341e`.

## Qualification

Independent local exact-head verification of `19e1a23...`:
- evidence-export suite: **8/8 PASS**;
- full suite: **273/273 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35474824502`;
- job `105982156946`;
- exact head `19e1a23cfaef6ab463a3c368e2b88ed59713341e`;
- conclusion: **SUCCESS**.

Accepted Benchmark R4 local-only no-commit composition:
- exact R50: `19e1a23cfaef6ab463a3c368e2b88ed59713341e`;
- Benchmark R4: `d7373867d3813d32032cb30463e54a6ddf573025`;
- common merge base: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`;
- zero conflicts;
- combined suite: **332/332 PASS**;
- compileall: PASS;
- reference benchmark replay: PASS;
- git diff --check: PASS;
- fixture aggregate digest:
  `374160c4b009ab39c57d134ed30feeb46be19851f3c169f46a055be2e14192f4`;
- strategy-input digest:
  `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`;
- guarded disposition remains 21/24;
- false accepts remain 2;
- deterministic operation count remains 174;
- required violation hits remain 9/15;
- zero unsupported acceptance;
- zero hidden-failure acceptance;
- zero provenance-currentness acceptance;
- zero authority/effect promotion errors;
- zero correlated-consensus laundering acceptance.

No remote integration commit was created.

## Claim ceiling

R50 establishes structural consistency between receipt-level aggregate source
versions and trace-level source-version evidence before run-evidence export.

R50 does not establish:
- cryptographic origin authentication;
- signature/attestation;
- independent reconstruction of source versions from external source material;
- outer subject currentness;
- Project Runner lease/fence validity;
- target authority;
- external effect/readback truth;
- completion truth;
- merge/deploy/install/provider/model/credential authority.

A caller capable of fabricating an entire internally consistent exact
`RunOutcome` can still fabricate structurally consistent evidence.

Issue #5 learned routing remains CLOSED.

## Remaining gate

Fresh independent hostile rereview must bind the exact final R50 head after this
qualification document. No merge or protected effect is authorized.
