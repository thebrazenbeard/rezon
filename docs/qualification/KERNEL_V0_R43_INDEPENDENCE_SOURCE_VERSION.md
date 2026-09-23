# Rezon Kernel V0 R43 Independence Source-Version Binding

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R43 is the bounded successor to failed whole-Kernel R42 exact subject
`0445e72d9d9952f8f05b8578479c5fc499166196`.

R42's frozen TaskEnvelope repair remains valid within that narrower scope.
Fresh hostile review found a source-version correlation laundering gap in the
pairwise strong-independence check.

## R42 hostile failure

Exact R42 accepted two workers as independently verified even though the
evidence visible to each worker was backed by the same exact source version.

Frozen setup:
- verifier A sees evidence `ev-a`, source ref `src:a`, source version
  `source@v1`;
- verifier B sees evidence `ev-b`, source ref `src:b`, source version
  `source@v1`;
- metadata/policy attestations correctly name each worker's distinct visible
  evidence refs;
- all worker/model/provider/prompt/context lineage values are distinct.

Observed exact-R42 result:
- verifier A executes;
- verifier B executes;
- both traces report `independence_demonstrated=True`;
- both verification results are admitted;
- final receipt has no failures or unresolved items.

The pairwise check compared consumed evidence refs but did not compare consumed
source versions, allowing a shared underlying provenance version to masquerade
as independent through different evidence/ref names.

Disposition:
`R42_INDEPENDENCE_SOURCE_VERSION_CORRELATION = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R42 remains preserved, draft, and unmerged.

## Frozen R43 RED

Regression file:
`tests/test_r43_independence_source_version.py`

Exact RED commit:
`7832b635c33ab20542c872965b5a9a03308a3e2b`

Fresh exact-R42 result:
- shared-source-version hostile case: FAIL as intended;
- distinct-source-version control: PASS.

## R43 repair

Runner repair:
`903dd4491de0fb49803c969f72594560e0556145`

Final regression assertion normalization:
`37199f998384511155071cfc60872d0ad31e4e2f`

R43 derives the source versions actually visible through EVIDENCE propositions
for every independence-required worker.

For a candidate independent worker, pairwise independence now requires both:
- existing metadata/lineage/reference independence; and
- no overlap between its visible evidence source versions and the visible
  evidence source versions of previously admitted independent workers.

Only successfully admitted independent workers contribute to the prior
source-version set.

Therefore:
- differently named evidence/ref aliases cannot establish independence when
  they resolve to the same exact source-version token;
- distinct source versions remain independently admissible when all other
  strong-independence checks pass.

## Qualification

CI-enablement head:
`cb5f1b2b239e77de4bfec30e8a7b3f95c7b88efe`

Fresh detached-checkout qualification:
- R43 regressions: **2/2 PASS**;
- focused R16-R43 controls: **124/124 PASS**;
- recent controls: **43/43 PASS** before remote cut;
- full suite: **253/253 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35468322667`;
- exact head `cb5f1b2b239e77de4bfec30e8a7b3f95c7b88efe`;
- test job `105964624739`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R42 final: `0445e72d9d9952f8f05b8578479c5fc499166196`
- R43 branch: `work/rezon-kernel-v0-r43-independence-source-version`
- frozen RED: `7832b635c33ab20542c872965b5a9a03308a3e2b`
- runner repair: `903dd4491de0fb49803c969f72594560e0556145`
- regression normalization: `37199f998384511155071cfc60872d0ad31e4e2f`
- CI-enablement head: `cb5f1b2b239e77de4bfec30e8a7b3f95c7b88efe`

## Explicit scope / non-claims

R43 establishes pairwise source-version disjointness for evidence visible to
successfully admitted independence-required workers.

It does not prove:
- two different source-version identifiers represent genuinely independent
  real-world sources;
- semantic truth;
- a same-process sandbox;
- filesystem/network/process side-effect rollback;
- persistent/database or distributed durability;
- independent hostile PASS on R43;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve every failed exact subject.
5. Do not merge without Patrick's explicit authority.
