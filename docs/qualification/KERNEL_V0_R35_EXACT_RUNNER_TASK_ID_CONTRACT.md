# Rezon Kernel V0 R35 Exact Runner Task-ID Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PENDING / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R35 is the bounded successor to R34 exact subject
`9b210ffee12916a628164b50d630036329a241cf`.

R34's exact Episode preflight remains valid within that narrower scope.
Fresh hostile review found that the separate `task_id` argument to
`EpisodeRunner.run()` was not held to the same exact-string runtime discipline
as the TaskEnvelope.

## R34 hostile failure

An exact `TaskEnvelope(task_id="t-real")` was paired with a `str` subclass
whose underlying text was `"forged"` but whose custom equality claimed to equal
`"t-real"` and whose custom formatter emitted `"formatted-attacker-task"`.

Exact R34 behavior:

- task-envelope mismatch check passed;
- executor calls: **1**;
- receipt task_id: `"forged"` as the attacker subclass;
- execution ID: `formatted-attacker-task:exec:1:echo_hypothesis`;
- receipt failures: **none**.

The caller could therefore split the governed task identity across comparison,
receipt, and execution-id surfaces.

## Frozen R35 RED

Regression:

`tests/test_r35_exact_runner_task_id_contract.py`

Exact RED commit:

`11b63004212519d37831df92e42ea6102f5e05c0`

Fresh exact-R34 result:

**1 failed / 0 passed**.

## R35 repair

Exact repair commit:

`173566b948fb38a37e75e6e157dc150f746f2308`

`EpisodeRunner.run()` now requires its runner `task_id` to be:

- exact built-in `str`;
- non-empty.

The check occurs at the first preflight boundary, before any episode method,
TaskEnvelope comparison, formatting, scheduler logic, visibility projection, or
executor call.

Invalid task IDs return a non-promotional PLAN receipt with:

- task_id sentinel `invalid_task`;
- episode_version sentinel `preflight@0`;
- `FailureState.CONTRACT_VIOLATION`;
- unresolved `runner:invalid_task_id_contract`.

No attacker-controlled equality or formatting method is needed to create that
failure receipt.

## Qualification

Fresh local exact-repair qualification:

- R34 + R35 focused regressions: **2/2 PASS**;
- full repository suite: **226/226 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted exact-head CI and fresh independent hostile rereview remain pending until
the final documentation head is published.

## Exact ancestry

- R34 subject: `9b210ffee12916a628164b50d630036329a241cf`
- R35 branch: `work/rezon-kernel-v0-r35-exact-runner-task-id-contract`
- frozen RED: `11b63004212519d37831df92e42ea6102f5e05c0`
- repair: `173566b948fb38a37e75e6e157dc150f746f2308`

## Explicit scope / non-claims

R35 establishes ordinary in-process exact validation of the runner's task ID
before governed execution begins.

It does not establish:

- protection against source/class monkeypatching;
- arbitrary executor side-effect safety after valid preflight;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R35;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Publish the final documentation head without rewriting history.
2. Re-run exact-head local and hosted CI.
3. Obtain fresh independent hostile rereview.
4. Continue only on concrete effect-bearing control/identity bypasses.
5. Preserve every failing exact subject.
6. Do not merge without Patrick's explicit authority.
