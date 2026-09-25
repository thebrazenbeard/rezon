# Rezon Kernel V0 R32 Internal Scheduler Binding

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R32 is the bounded successor to failed whole-Kernel R31 exact subject
`94c5547399891f46cefb85652c626ecca539ab99`.

R31's TaskEnvelope / TaskSpecification hardening remains valid within that
narrower scope. Fresh hostile review found that EpisodeRunner still dispatched
through its mutable public `scheduler` attribute, allowing caller-controlled
scheduling semantics to bypass mandatory verification.

## R31 hostile failure

Exact R31 failed all three frozen R32 cases:

1. replacing `runner.scheduler` with a duck scheduler;
2. replacing it with a `DeterministicScheduler` subclass;
3. using an exact `DeterministicScheduler` instance with an instance-shadowed
   `next` method.

In every case the hostile scheduler selected `echo_hypothesis` instead of the
exact mandatory verifier at index 0. The generator executed, canonical output
`generated` was admitted, the verifier never ran, and the final receipt
reported no failure.

Disposition:
`R31_MUTABLE_SCHEDULER_CONTROL = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R31 remains preserved, draft, and unmerged.

## Frozen R32 RED

Regression file:

`tests/test_r32_exact_scheduler_binding.py`

Exact RED commit:

`97ad4977f885fd93c061d3b6716f219f724b485a`

Fresh exact-R31 result:

**3 failed / 0 passed**.

## R32 repair

Runner repair:

`89187fc0314f902bfd4ff57a4858ec9ea66cc9e7`

R32 binds scheduling to a fresh internal `DeterministicScheduler` instance
created inside each `EpisodeRunner.run()`.

The mutable public `runner.scheduler` attribute is no longer an execution
authority. Replacing it, subclassing it, or shadowing an instance method cannot
influence governed scheduling.

This preserves ordinary API compatibility while ensuring the scheduler that
selects mandatory verification, contradiction handling, independent generation,
falsification, and budget termination is created by the governed runner at the
start of the run.

## Qualification

CI-enablement head:

`c4a9753d4d75f0cfc88c22d21352105a54f1502a`

Fresh detached-checkout qualification:

- R32 scheduler-binding regressions: **3/3 PASS**;
- focused R16-R32 controls: **92/92 PASS**;
- scheduler/hostile focused set: **38/38 PASS** before remote cut;
- full suite: **221/221 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35462338566`;
- exact head `c4a9753d4d75f0cfc88c22d21352105a54f1502a`;
- test job `105948314621`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R31 final: `94c5547399891f46cefb85652c626ecca539ab99`
- R32 branch: `work/rezon-kernel-v0-r32-exact-scheduler-binding`
- frozen RED: `97ad4977f885fd93c061d3b6716f219f724b485a`
- runner repair: `89187fc0314f902bfd4ff57a4858ec9ea66cc9e7`
- CI-enablement head: `c4a9753d4d75f0cfc88c22d21352105a54f1502a`

## Explicit scope / non-claims

R32 establishes ordinary in-process binding of EpisodeRunner scheduling to a
fresh internal DeterministicScheduler for each run.

It does not establish:

- protection against source/class monkeypatching of DeterministicScheduler
  itself;
- correctness or safety of arbitrary executor side effects outside the governed
  runner;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R32;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. If review remains pending, probe only adjacent effect-bearing control paths.
5. Preserve every failed exact subject.
6. Do not merge without Patrick's explicit authority.
