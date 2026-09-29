# Rezon Kernel V0 R44 Non-Empty Direct Admission Execution Identity

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R44 is the bounded successor to failed whole-Kernel R43 exact subject
`b7282364fad6676cae35aae403688c4ebc93b2f1`.

R43's evidence source-version independence repair remains valid within that
narrower scope. Fresh hostile review found that the public direct-admission
boundary accepted an empty execution identity.

## R43 hostile failure

Exact R43 allowed `admit_execution_result()` to canonicalize output when:
- `result.execution_id == ""`;
- emitted proposition `producer_execution_id == ""`; and
- either `expected_execution_id == ""` or the expected ID was omitted.

Because admission checked only exact string type, the empty result identity
could satisfy equality binding. Admission then derived a non-empty canonical
producer identity and committed the proposition to canonical Episode state.

This creates canonical production provenance without a non-empty attempt
execution identity.

Disposition:
`R43_EMPTY_DIRECT_ADMISSION_EXECUTION_ID = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R43 remains preserved, draft, and unmerged.

## Frozen R44 RED

Regression file:
`tests/test_r44_nonempty_admission_execution_id.py`

Exact RED commit:
`be17911aa4c4e6c086934ae7b7b576687e1cf907`

Fresh exact-R43 result:
**2 failed / 0 passed**.

Frozen variants:
1. empty result identity plus explicitly empty expected identity;
2. empty result identity with expected identity omitted.

Both mutated canonical Episode state before R44.

## R44 repair

Admission repair:
`1219c49cb47f2c9542e15ee855cad7fedcd09ce4`

Direct admission now requires:
- `result.execution_id` to be a non-empty exact built-in string;
- any supplied `expected_execution_id` to be a non-empty exact built-in string;
- result and expected identities to match when an expected identity is supplied.

These checks run before canonical output admission or canonical producer identity
derivation.

## Qualification

CI-enablement head:
`3638456808e0baa8445dfb8a62fe2c2713745531`

Fresh detached-checkout qualification:
- R44 regressions: **2/2 PASS**;
- focused R16-R44 controls: **126/126 PASS**;
- recent controls: **45/45 PASS** before remote cut;
- full suite: **255/255 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35468584189`;
- exact head `3638456808e0baa8445dfb8a62fe2c2713745531`;
- test job `105965305439`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R43 final: `b7282364fad6676cae35aae403688c4ebc93b2f1`
- R44 branch: `work/rezon-kernel-v0-r44-nonempty-admission-execution-id`
- frozen RED: `be17911aa4c4e6c086934ae7b7b576687e1cf907`
- admission repair: `1219c49cb47f2c9542e15ee855cad7fedcd09ce4`
- CI-enablement head: `3638456808e0baa8445dfb8a62fe2c2713745531`

## Explicit scope / non-claims

R44 establishes non-empty exact attempt execution identity at the public direct
admission boundary.

It does not establish:
- semantic truth;
- a same-process sandbox;
- filesystem/network/process side-effect rollback;
- persistent/database or distributed durability;
- independent hostile PASS on R44;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve every failed exact subject.
5. Do not merge without Patrick's explicit authority.
