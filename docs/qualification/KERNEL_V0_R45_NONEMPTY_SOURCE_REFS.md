# Rezon Kernel V0 R45 Non-Empty Canonical Source References

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R45 is the bounded successor to failed whole-Kernel R44 exact subject
`1f7bb9838b0be49fff31ba4ddbd2357211b1856b`.

R44's non-empty direct execution-identity repair remains valid within that
narrower scope. Fresh hostile review found that canonical source-reference
identities could still be empty strings.

## R44 hostile failure

Exact R44 accepted:
- a canonical Proposition with `source_refs=("",)`;
- the same malformed provenance through direct admission;
- a canonical Hyperrelation with `source_refs=("",)`.

When paired with `source_versions=("source@v1",)`, the existing source/version
association helper produced `("", "source@v1")`.

That is a canonical provenance version associated with no source identity.

Disposition:
`R44_EMPTY_CANONICAL_SOURCE_REF = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R44 remains preserved, draft, and unmerged.

## Frozen R45 RED

Regression file:
`tests/test_r45_nonempty_source_refs.py`

Exact RED commit:
`c7d84f09acabde7e6af881fd26038f36b99d777b`

Fresh exact-R44 result:
**3 failed / 0 passed**.

Frozen variants:
1. direct Episode proposition addition with empty source ref;
2. direct admission with empty proposition source ref;
3. direct Episode relation addition with empty source ref.

## R45 repair

Episode repair:
`8ecafd93d47cb7f1a51f5697b7358199a7238541`

Admission repair:
`602d1baf33eec09201d86a3eae762abff3097e40`

ExecutionResult/nested output repair:
`51a03d581f97bfec221230273cd4ac9f1552ff59`

The exact-string tuple validators at canonical Episode, public admission, and
runner ExecutionResult boundaries now require every present string value to be
both:
- exact built-in `str`; and
- non-empty.

Empty tuples remain valid where provenance is absent.

This prevents empty source identities from entering canonical propositions,
canonical relations, direct admission, or governed runner output while
preserving optional empty provenance sets.

## Qualification

CI-enablement head:
`20abf4c5bbfaf2d6b65a4c2db7a28477cd2c6458`

Fresh detached-checkout qualification:
- R45 regressions: **3/3 PASS**;
- focused R16-R45 controls: **129/129 PASS**;
- recent controls: **47/47 PASS** before remote cut;
- full suite: **258/258 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35468896112`;
- exact head `20abf4c5bbfaf2d6b65a4c2db7a28477cd2c6458`;
- test job `105966136081`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R44 final: `1f7bb9838b0be49fff31ba4ddbd2357211b1856b`
- R45 branch: `work/rezon-kernel-v0-r45-nonempty-source-refs`
- frozen RED: `c7d84f09acabde7e6af881fd26038f36b99d777b`
- Episode repair: `8ecafd93d47cb7f1a51f5697b7358199a7238541`
- admission repair: `602d1baf33eec09201d86a3eae762abff3097e40`
- result repair: `51a03d581f97bfec221230273cd4ac9f1552ff59`
- CI-enablement head: `20abf4c5bbfaf2d6b65a4c2db7a28477cd2c6458`

## Explicit scope / non-claims

R45 establishes non-empty canonical source-reference identities at Episode,
direct admission, and governed result boundaries.

It does not establish:
- semantic truth or real-world source validity;
- source-currentness verification beyond existing contracts;
- a same-process sandbox;
- filesystem/network/process side-effect rollback;
- persistent/database or distributed durability;
- independent hostile PASS on R45;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve every failed exact subject.
5. Do not merge without Patrick's explicit authority.
