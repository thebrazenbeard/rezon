# Rezon Kernel V0 R38 Exact ExecutionResult Boundary

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R38 is the bounded successor to failed whole-Kernel R37 exact subject
`1fc9e4704e728aff8e7d8e4c44d4231202a1ddc3`.

R37's executor Episode rollback remains valid within that narrower scope. Fresh
hostile review found that the executor transaction ended before the runner
structurally validated the returned ExecutionResult.

## R37 hostile failure

Exact R37 failed both hostile R38 attacks while the exact control passed.

Critical path:
1. executor returns a non-exact result while the Episode transaction is clean;
2. R37 exits the transaction;
3. runner calls `canonical_output_digest(result)` and later reads source fields;
4. hostile result attribute access mutates the exact canonical Episode;
5. admission eventually rejects the non-exact result;
6. the post-transaction Episode mutation remains canonical.

Frozen attacks:
- duck result mutates Episode from `emitted_propositions` access;
- ExecutionResult subclass mutates Episode from `source_refs` access.

The exact ExecutionResult control continued to execute and admit normally.

Disposition:
`R37_POST_TRANSACTION_EXECUTION_RESULT_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R37 remains preserved, draft, and unmerged.

## Frozen R38 RED

Regression file:

`tests/test_r38_exact_execution_result_boundary.py`

Exact RED commit:

`9afb95e85f7aa9abe9002e859342ba7b72874086`

Fresh exact-R37 result:

- hostile cases: **2 failed / 0 passed**;
- exact control: **1 passed**.

## R38 repair

ExecutionResult exact contract:

`5152491a3d8b412808310182d2a94222ed2db2cb`

Runner transaction-bound validation:

`bd53506e18277a6668f069349560aed8e909c6e3`

R38 defines `execution_result_contract_is_exact()`, covering:
- exact base ExecutionResult;
- exact non-empty execution/node identity strings;
- exact tuple containers;
- exact Proposition values and their identity/kind/content/provenance/confidence fields;
- exact Hyperrelation and Participant values;
- exact FailureState values;
- exact source-ref/source-version tuples;
- exact VerificationStatus or None;
- exact non-empty verification-target strings.

The runner invokes that complete validator while `Episode.atomic_mutation()`
is still active and before any returned-result field is read outside the
transaction.

If the result contract is invalid:
- an internal invalid-result sentinel is raised inside the Episode transaction;
- any Episode mutation performed during executor execution or contract
  validation is rolled back;
- the runner records CONTRACT_VIOLATION;
- unresolved contains
  `execution_result:invalid_contract:<execution_id>`;
- no post-transaction result digest/source/admission read occurs.

This closes the late exact-type check that previously lived only in admission.

## Qualification

CI-enablement head:

`d9d395b2093d064a4baa92a9c2903d1b29e1641f`

Fresh detached-checkout qualification:

- R38 regression file: **3/3 PASS**;
- focused R16-R38 controls: **112/112 PASS**;
- recent control set: **30/30 PASS** before remote cut;
- full suite: **241/241 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35464802080`;
- exact head `d9d395b2093d064a4baa92a9c2903d1b29e1641f`;
- test job `105955075536`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R37 final: `1fc9e4704e728aff8e7d8e4c44d4231202a1ddc3`
- R38 branch: `work/rezon-kernel-v0-r38-exact-execution-result-boundary`
- frozen RED: `9afb95e85f7aa9abe9002e859342ba7b72874086`
- result-contract repair: `5152491a3d8b412808310182d2a94222ed2db2cb`
- runner repair: `bd53506e18277a6668f069349560aed8e909c6e3`
- CI-enablement head: `d9d395b2093d064a4baa92a9c2903d1b29e1641f`

## Explicit scope / non-claims

R38 establishes exact structural validation of returned ExecutionResult material
before the Episode transaction can commit and before post-execution runner field
reads.

It does not establish:
- a sandbox against arbitrary same-process Python/private-memory corruption;
- filesystem/network/process side-effect rollback;
- protection against source/class monkeypatching;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R38;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Probe further only when a concrete effect-bearing control bypass is found.
5. Preserve every failed exact subject.
6. Do not merge without Patrick's explicit authority.
