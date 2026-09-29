# Rezon Kernel V0 R40 Targeted Executor Transaction

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R40 is the bounded successor to failed whole-Kernel R39 exact subject
`d95aac23823e4351303e737d22aeaee218cdf899`.

R39's visibility/independence preflight remains valid within that narrower
scope. Fresh hostile review found target-specific executor adaptation still ran
outside the Episode rollback transaction.

## R39 hostile failure

Exact R39 failed both frozen R40 attacks.

For targeted scheduler decisions such as falsification, the runner performed:

- `hasattr(executor, "target_hypothesis_id")`;
- optional `type(executor)(decision.target_id)`;

before entering `Episode.atomic_mutation()`.

Frozen attacks:
1. hostile attribute access mutates the canonical Episode during `hasattr`;
2. hostile target-specific constructor mutates the canonical Episode during
   executor replacement.

In both cases:
- canonical snapshot/digest had already been captured;
- mutation occurred before the rollback checkpoint;
- later digest mismatch was detected as CONTRACT_VIOLATION;
- rollback restored only the already-mutated checkpoint;
- the side effect remained canonical.

Disposition:
`R39_TARGETED_EXECUTOR_PRETRANSACTION = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R39 remains preserved, draft, and unmerged.

## Frozen R40 RED

Regression file:

`tests/test_r40_targeted_executor_transaction.py`

Exact RED commit:

`62618d81e65f287cb048846231dfe01cb3d5672a`

Fresh exact-R39 result:

**2 failed / 0 passed**.

## R40 repair

Runner repair:

`20cc1a4f6005e75600c4d1172dbd408cba990427`

R40 leaves only the inert stored executor reference outside the transaction.
All behavior-bearing target adaptation now runs inside
`Episode.atomic_mutation()`:

- target attribute probing;
- target-specific executor construction;
- executor invocation;
- exact ExecutionResult validation;
- canonical Episode digest verification.

Any Episode mutation caused by target probing, constructor logic, or execution
is therefore covered by the same rollback checkpoint and fails closed before
canonical admission.

## Qualification

CI-enablement head:

`472de840c1a84b73b316c181f3191bacf91e894c`

Fresh detached-checkout qualification:

- R40 hostile regressions: **2/2 PASS**;
- focused R16-R40 controls: **117/117 PASS**;
- recent controls: **36/36 PASS** before remote cut;
- full suite: **246/246 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35465226677`;
- exact head `472de840c1a84b73b316c181f3191bacf91e894c`;
- test job `105956218681`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R39 final: `d95aac23823e4351303e737d22aeaee218cdf899`
- R40 branch: `work/rezon-kernel-v0-r40-targeted-executor-transaction`
- frozen RED: `62618d81e65f287cb048846231dfe01cb3d5672a`
- runner repair: `20cc1a4f6005e75600c4d1172dbd408cba990427`
- CI-enablement head: `472de840c1a84b73b316c181f3191bacf91e894c`

## Explicit scope / non-claims

R40 establishes rollback containment for target-specific executor probing and
construction during governed execution.

It does not establish:
- a sandbox against arbitrary same-process Python/private-memory corruption;
- filesystem/network/process side-effect rollback;
- protection against source/class monkeypatching;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R40;
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
