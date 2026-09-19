# Rezon Kernel V0 R34 Exact Runner Episode Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PENDING / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R34 is the bounded successor to R33 exact subject
`c9f689cc648684a840a8ea1097db94b0c0d98d67`.

R33's exact runner-budget contract remains valid within that narrower scope.
Fresh hostile review found that `EpisodeRunner.run()` did not enforce the exact
`Episode` runtime boundary before scheduler/executor work.

## R33 hostile failure

Direct admission already rejects non-exact `Episode` objects, but the runner
invoked the executor before calling direct admission.

A plain `Episode` subclass therefore reached executor code and incremented the
executor side-effect counter before admission later returned
`CONTRACT_VIOLATION`.

That violates the governed-runner preflight expectation: malformed runtime
control subjects must fail before executor invocation.

## Frozen R34 RED

Regression:

`tests/test_r34_exact_runner_episode_contract.py`

Exact RED commit:

`b1b7fdab3663230ed045ae15e27cd68bd6e3a247`

Fresh exact-R33 result:

**1 failed / 0 passed**.

Observed critical value:

- executor calls: **1**

The eventual receipt contained an admission failure, proving the reject happened
too late.

## R34 repair

Exact repair commit:

`0d3e7b04c3a1c6f0673d749405d6c1f1cf69fdbc`

`EpisodeRunner.run()` now requires `type(episode) is Episode` before calling
any episode method, scheduler logic, visibility projection, or executor code.

A non-exact episode returns a non-promotional PLAN receipt with:

- `FailureState.CONTRACT_VIOLATION`;
- unresolved `runner:invalid_episode_contract`;
- sentinel version `invalid_episode@0`.

No method is called on the invalid episode to construct that failure receipt.

## Qualification

Fresh local exact-repair qualification:

- R34 regression: **1/1 PASS**;
- full repository suite: **225/225 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted exact-head CI and fresh independent hostile rereview remain pending until
the final documentation head is published.

## Exact ancestry

- R33 subject: `c9f689cc648684a840a8ea1097db94b0c0d98d67`
- R34 branch: `work/rezon-kernel-v0-r34-exact-runner-episode-contract`
- frozen RED: `b1b7fdab3663230ed045ae15e27cd68bd6e3a247`
- repair: `0d3e7b04c3a1c6f0673d749405d6c1f1cf69fdbc`

## Explicit scope / non-claims

R34 establishes ordinary in-process fail-closed validation of the runner's
Episode argument before governed scheduling/execution begins.

It does not establish:

- protection against source/class monkeypatching;
- arbitrary executor side-effect safety after valid preflight;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R34;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Publish the final documentation head without rewriting history.
2. Re-run exact-head local and hosted CI.
3. Obtain fresh independent hostile rereview.
4. Continue only on concrete effect-bearing control bypasses.
5. Preserve every failing exact subject.
6. Do not merge without Patrick's explicit authority.
