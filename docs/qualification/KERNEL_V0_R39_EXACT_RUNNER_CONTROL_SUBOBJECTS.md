# Rezon Kernel V0 R39 Exact Runner Control Subobjects

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R39 is the bounded successor to failed whole-Kernel R38 exact subject
`f2954e63d4e4a1eca90fef8275df0aebdb7600a7`.

R38's exact ExecutionResult boundary remains valid within that narrower scope.
Fresh hostile review found pre-execution RunnerNode control subobjects that could
mutate canonical Episode state after the pre-execution digest was captured but
before the executor transaction checkpoint was established.

## R38 hostile failure

Exact R38 failed all three frozen R39 cases.

Frozen attacks:
1. VisibilityPolicy subclass mutates the exact Episode from `allow_ids`
   attribute access inside `build_execution_view()`;
2. exact VisibilityPolicy carrying a hostile tuple subclass mutates the Episode
   when `set(policy.allow_ids)` iterates it;
3. IndependenceMetadata subclass mutates the Episode from truthiness evaluation
   in `independence or IndependenceMetadata()`.

In all three cases:
- the canonical pre-execution digest was captured first;
- attacker-controlled pre-view behavior mutated Episode state;
- the executor transaction began only afterward, checkpointing the already
  mutated Episode;
- later digest mismatch was detected and reported as CONTRACT_VIOLATION;
- rollback could only restore the contaminated checkpoint;
- the mutation remained canonical.

Disposition:
`R38_RUNNER_CONTROL_SUBOBJECT_PREFLIGHT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R38 remains preserved, draft, and unmerged.

## Frozen R39 RED

Regression file:

`tests/test_r39_exact_runner_control_subobjects.py`

Exact RED commit:

`5ca446970981ceb022cae5f90e4a81883c056393`

Fresh exact-R38 result:

**3 failed / 0 passed**.

## R39 repair

Visibility contract:

`ba22bb94de011b0db74c76000fe018c7d2d67067`

Runner preflight:

`c403c22d05934e8f72e5b615f8262f9b714cb94b`

R39 adds `visibility_policy_contract_is_exact()`, requiring:
- exact base VisibilityPolicy;
- exact tuple containers for allow/blind kind sets;
- exact PropositionKind values;
- exact tuple containers for allow/blind ID sets;
- exact built-in str ID values.

RunnerNode preflight now rejects a node before any view construction unless:
- RunnerNode is exact;
- NodeDescriptor satisfies its exact contract;
- VisibilityPolicy satisfies its exact contract;
- IndependenceMetadata is the exact base type.

This moves the relevant validation before:
- canonical execution snapshot/digest capture;
- `build_execution_view()`;
- visibility container iteration;
- independence truthiness;
- executor invocation.

Malformed visibility/independence controls therefore cannot execute caller code
between canonical digest capture and executor rollback checkpoint.

## Qualification

CI-enablement head:

`b412db92e2ca0007e92fd9d6a81f48626694c1c5`

Fresh detached-checkout qualification:

- R39 hostile regressions: **3/3 PASS**;
- focused R16-R39 controls: **115/115 PASS**;
- recent controls: **33/33 PASS** before remote cut;
- full suite: **244/244 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35465036987`;
- exact head `b412db92e2ca0007e92fd9d6a81f48626694c1c5`;
- test job `105955700104`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R38 final: `f2954e63d4e4a1eca90fef8275df0aebdb7600a7`
- R39 branch: `work/rezon-kernel-v0-r39-exact-runner-control-subobjects`
- frozen RED: `5ca446970981ceb022cae5f90e4a81883c056393`
- visibility repair: `ba22bb94de011b0db74c76000fe018c7d2d67067`
- runner repair: `c403c22d05934e8f72e5b615f8262f9b714cb94b`
- CI-enablement head: `b412db92e2ca0007e92fd9d6a81f48626694c1c5`

## Explicit scope / non-claims

R39 establishes exact preflight for the RunnerNode visibility object and
IndependenceMetadata base type before execution-view construction.

It does not establish:
- a sandbox against arbitrary same-process Python/private-memory corruption;
- filesystem/network/process side-effect rollback;
- protection against source/class monkeypatching;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R39;
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
