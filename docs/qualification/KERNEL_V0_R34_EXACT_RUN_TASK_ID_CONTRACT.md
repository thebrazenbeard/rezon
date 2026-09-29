# Rezon Kernel V0 R34 Exact Run Task-ID Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R34 is the bounded successor to failed whole-Kernel R33 exact subject
`c9f689cc648684a840a8ea1097db94b0c0d98d67`.

R33's exact runner-budget hardening remains valid within that narrower scope.
Fresh hostile review found that the run-level `task_id` itself remained an
unvalidated identity/provenance control input.

## R33 hostile failure

Exact R33 failed all four frozen R34 cases:

1. a duck task-ID object compared equal to exact envelope task ID
   `t-governed`, formatted itself as `t-governed`, executed, and admitted
   canonical output;
2. a `str` subclass with custom equality/formatting did the same;
3. a non-string task ID with no TaskEnvelope executed and was recorded through
   attacker-controlled formatting;
4. an empty exact task ID crossed executor/admission and only failed during
   final ResultReceipt construction.

Critical reproduced result for the duck object:

- executor calls: **1**
- receipt failures: **none**
- receipt task type: attacker-defined object
- execution ID: `t-governed:exec:1:echo_hypothesis`
- canonical output admitted: `ran`

Disposition:
`R33_RUN_TASK_ID_RUNTIME_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R33 remains preserved, draft, and unmerged.

## Frozen R34 RED

Regression file:

`tests/test_r34_exact_run_task_id_contract.py`

Exact RED commit:

`b51bd6565285d5f4f96491d0663ac7a083e0d8c6`

Fresh exact-R33 result:

**4 failed / 0 passed**.

## R34 repair

Runner repair:

`803297dbbf8dc64925b8530ce33f71ca73119181`

At the first executable line of `EpisodeRunner.run()`, R34 now requires the
run-level task ID to be:

- exact built-in `str`;
- non-empty.

Malformed values fail closed before:

- TaskEnvelope contract evaluation;
- task-envelope digesting;
- task-ID equality;
- node validation;
- budget handling;
- scheduler creation;
- executor invocation;
- canonical admission.

The rejection path emits a non-promotional contract-violation receipt under the
fixed diagnostic identity `runner:invalid_task_id`, with unresolved marker of
the same value. It never formats, compares, or records the hostile task object.

## Qualification

CI-enablement head:

`5f27ba8b52d17f08a5a0999db7d7f8dd9a5847a5`

Fresh detached-checkout qualification:

- R34 task-ID regressions: **4/4 PASS**;
- focused R16-R34 controls: **99/99 PASS**;
- focused task/scheduler/budget set: **24/24 PASS** before remote cut;
- full suite: **228/228 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35463035558`;
- exact head `5f27ba8b52d17f08a5a0999db7d7f8dd9a5847a5`;
- test job `105950197610`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R33 final: `c9f689cc648684a840a8ea1097db94b0c0d98d67`
- R34 branch: `work/rezon-kernel-v0-r34-exact-run-task-id-contract`
- frozen RED: `b51bd6565285d5f4f96491d0663ac7a083e0d8c6`
- runner repair: `803297dbbf8dc64925b8530ce33f71ca73119181`
- CI-enablement head: `5f27ba8b52d17f08a5a0999db7d7f8dd9a5847a5`

## Explicit scope / non-claims

R34 establishes ordinary in-process exact validation of the run-level task ID
before it can participate in TaskEnvelope identity binding, execution identity,
or canonical admission.

It does not establish:

- cryptographic caller or task identity;
- protection against source/class monkeypatching;
- arbitrary executor side-effect safety outside the governed runner;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R34;
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
