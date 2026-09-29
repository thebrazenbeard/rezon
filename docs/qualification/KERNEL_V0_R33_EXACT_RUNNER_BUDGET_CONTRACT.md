# Rezon Kernel V0 R33 Exact Runner Budget Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R33 is the bounded successor to failed whole-Kernel R32 exact subject
`5abcb6a3021cd61a387d322673cec0b5f8801e8e`.

R32's internal scheduler binding remains valid within that narrower scope. Fresh
hostile review found that runner-owned `budget_limit` remained an unvalidated
execution-control input and could override the exact TaskEnvelope resource
budget.

## R32 hostile failure

Exact R32 failed all three frozen R33 cases:

1. a duck runner budget defeated an exact TaskEnvelope `resource_budget=0`;
2. mutating an initially exact zero runner budget to that duck object reproduced
   the same effect;
3. an `int` subclass was accepted as runner budget despite not satisfying an
   exact runtime contract.

The duck object supplied caller-controlled comparison methods. It defeated both
the `min(runner_budget, envelope_budget)` bound and later scheduler exhaustion
comparison.

Critical exact-R32 result with an exact envelope resource budget of zero:

- executor calls: **1**
- receipt failures: **none**
- canonical output admitted: `ran`

Disposition:
`R32_RUNNER_BUDGET_RUNTIME_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R32 remains preserved, draft, and unmerged.

## Frozen R33 RED

Regression file:

`tests/test_r33_exact_runner_budget_contract.py`

Exact RED commit:

`fbf1b330a5ad24efee6674392057b923ce50b548`

Fresh exact-R32 result:

**3 failed / 0 passed**.

## R33 repair

Runner repair:

`7675b0311c63ba23d17cc682f1658ab0328a5124`

Before a runner budget participates in envelope bounding or scheduler state,
`EpisodeRunner.run()` now requires:

- exact built-in `int`;
- non-negative value.

Therefore bool, integer subclasses, duck comparison objects, and post-construction
mutation to those objects fail closed with:

`runner:invalid_budget_contract`

and `FailureState.CONTRACT_VIOLATION`.

The validation occurs before effective-budget computation, scheduler creation,
or executor invocation.

## Qualification

CI-enablement head:

`eddf5473177800edfae675fb0c64048a22c28cd8`

Fresh detached-checkout qualification:

- R33 budget regressions: **3/3 PASS**;
- focused R16-R33 controls: **95/95 PASS**;
- focused scheduler/task/budget controls: **21/21 PASS** before remote cut;
- full suite: **224/224 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35462602973`;
- exact head `eddf5473177800edfae675fb0c64048a22c28cd8`;
- test job `105949031366`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R32 final: `5abcb6a3021cd61a387d322673cec0b5f8801e8e`
- R33 branch: `work/rezon-kernel-v0-r33-exact-runner-budget-contract`
- frozen RED: `fbf1b330a5ad24efee6674392057b923ce50b548`
- runner repair: `7675b0311c63ba23d17cc682f1658ab0328a5124`
- CI-enablement head: `eddf5473177800edfae675fb0c64048a22c28cd8`

## Explicit scope / non-claims

R33 establishes ordinary in-process exact validation of EpisodeRunner's
runner-owned budget before it can influence TaskEnvelope resource bounding or
scheduler execution.

It does not establish:

- protection against source/class monkeypatching;
- arbitrary executor side-effect safety outside the governed runner;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R33;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Probe further only when a concrete effect-bearing control bypass is found.
5. Preserve every failing exact subject.
6. Do not merge without Patrick's explicit authority.
