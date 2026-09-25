# Rezon Kernel V0 R35 Exact Run Episode Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R35 is the bounded successor to failed whole-Kernel R34 exact subject
`7e91323b09dda776a8b507262f1530ec786f3a5a`.

R34's exact run task-ID hardening remains valid within that narrower scope.
Fresh hostile review found that `EpisodeRunner.run()` still accepted non-exact
Episode values until canonical admission, after scheduling and executor
invocation.

## R34 hostile failure

Exact R34 failed all three frozen R35 cases:

1. a plain `Episode` subclass reached executor invocation before late admission
   rejected the non-exact episode;
2. a deceptive subclass overrode `snapshot()`, hid an existing hypothesis from
   scheduler-visible state, caused generator execution, and was only rejected
   later by admission;
3. a duck episode similarly reached executor invocation before the exact-Episode
   admission guard fired.

Critical deceptive-subclass result:

- canonical base Episode state already contained hypothesis `existing`;
- overridden snapshot exposed no hypotheses;
- scheduler selected `echo_hypothesis`;
- executor calls: **1**;
- admission eventually returned CONTRACT_VIOLATION;
- late rejection did not undo the fact that execution had already occurred.

Disposition:
`R34_RUN_EPISODE_RUNTIME_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R34 remains preserved, draft, and unmerged.

## Frozen R35 RED

Regression file:

`tests/test_r35_exact_run_episode_contract.py`

Exact RED commit:

`1c235ea0115d7e627901c79cc2eea390c499d638`

Fresh exact-R34 result:

**3 failed / 0 passed**.

## R35 repair

Runner repair:

`76448dbee029405ff69924b156a79160b4914f9a`

At run entry, after validating the run-level task ID but before any use of
episode-provided state, R35 now requires:

- `type(episode) is Episode`.

Non-exact values fail closed with:

- unresolved: `runner:invalid_episode_contract`;
- `FailureState.CONTRACT_VIOLATION`;
- no scheduler creation;
- no executor invocation;
- no canonical admission.

The invalid-task-ID path was also adjusted so it does not call
`episode.snapshot()` merely to construct its rejection receipt. Its diagnostic
episode version is fixed as `runner:unbound_episode`, preventing an invalid
task ID from becoming a route to invoke behavior on an untrusted episode object.

## Qualification

CI-enablement head:

`66a6f984252041fc94477400c95913db16501ed7`

Fresh detached-checkout qualification:

- R35 episode regressions: **3/3 PASS**;
- focused R16-R35 controls: **102/102 PASS**;
- focused recent run-entry controls: **20/20 PASS** before remote cut;
- full suite: **231/231 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35463246567`;
- exact head `66a6f984252041fc94477400c95913db16501ed7`;
- test job `105950754897`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R34 final: `7e91323b09dda776a8b507262f1530ec786f3a5a`
- R35 branch: `work/rezon-kernel-v0-r35-exact-run-episode-contract`
- frozen RED: `1c235ea0115d7e627901c79cc2eea390c499d638`
- runner repair: `76448dbee029405ff69924b156a79160b4914f9a`
- CI-enablement head: `66a6f984252041fc94477400c95913db16501ed7`

## Explicit scope / non-claims

R35 establishes ordinary in-process exact validation of the Episode object at
EpisodeRunner run entry before scheduling or executor invocation.

It does not establish:

- arbitrary executor side-effect safety outside the governed runner;
- protection against source/class monkeypatching of exact base classes;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R35;
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
