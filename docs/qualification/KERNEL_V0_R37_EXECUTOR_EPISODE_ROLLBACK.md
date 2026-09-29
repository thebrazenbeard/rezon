# Rezon Kernel V0 R37 Executor Episode Rollback

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R37 is the bounded successor to failed whole-Kernel R36 exact subject
`7c75d69682cfcb7c40c314d58b05ef26f52dd866`.

R36's frozen RunnerNode-set binding remains valid within that narrower scope.
Fresh hostile review found that canonical Episode mutation performed directly by
an executor was detected later by admission but not contained or rolled back.

## R36 hostile failure

Exact R36 failed all four frozen R37 cases.

An executor retained the exact canonical Episode through an ordinary Python
reference while receiving only its governed ExecutionView. During
`execute()`, it mutated the Episode directly through the public API.

Observed behavior on exact R36:
- direct proposition addition remained canonical after returned output was
  rejected for snapshot mismatch;
- direct proposition retraction remained canonical;
- direct relation addition remained canonical;
- mutation performed before an executor exception also remained canonical.

The runner detected returned-result/admission inconsistency, but detection did
not restore the pre-execution Episode state.

Disposition:
`R36_EXECUTOR_EPISODE_MUTATION_ROLLBACK = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R36 remains preserved, draft, and unmerged.

## Frozen R37 RED

Regression file:

`tests/test_r37_executor_episode_rollback.py`

Exact RED commit:

`edaaa4dcd4b02198939ca7b6589240ee9e6ca31b`

Fresh exact-R36 result:

**4 failed / 0 passed**.

Frozen attacks:
1. direct proposition add + ordinary return;
2. direct retraction + ordinary return;
3. direct relation add + ordinary return;
4. direct proposition add + executor exception.

## R37 repair

Runner repair:

`746406903d7903577e3cad74b8731f2105b44afd`

R37 executes each executor inside `Episode.atomic_mutation()`.

Immediately after a nominal executor return, while the Episode transaction is
still open, the runner recomputes the canonical Episode snapshot digest and
compares it with the exact digest captured before executor invocation.

If the canonical Episode changed:
- the runner raises an internal mutation sentinel inside the Episode
  transaction;
- `Episode.atomic_mutation()` restores the pre-execution canonical state;
- the run records `FailureState.CONTRACT_VIOLATION`;
- unresolved includes
  `executor_episode_mutation:<execution_id>`;
- returned output is never admitted.

If the executor raises after directly mutating the Episode:
- the executor exception escapes the Episode transaction first;
- `Episode.atomic_mutation()` restores the checkpoint;
- existing runner exception handling records
  `FailureState.ATTEMPTED_UNKNOWN`;
- no direct canonical mutation remains.

Because the Episode lock is held across the executor call, ordinary public
Episode mutations from other threads cannot interleave with the execution
window.

## Qualification

CI-enablement head:

`7c6593b680e683fa795cc0e5a375298d1f8ef98c`

Fresh detached-checkout qualification:

- R37 rollback regressions: **4/4 PASS**;
- focused R16-R37 controls: **109/109 PASS**;
- recent control/rollback focused set: **26/26 PASS** before remote cut;
- full suite: **238/238 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35464193588`;
- exact head `7c6593b680e683fa795cc0e5a375298d1f8ef98c`;
- test job `105953278640`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R36 final: `7c75d69682cfcb7c40c314d58b05ef26f52dd866`
- R37 branch: `work/rezon-kernel-v0-r37-executor-episode-rollback`
- frozen RED: `edaaa4dcd4b02198939ca7b6589240ee9e6ca31b`
- runner repair: `746406903d7903577e3cad74b8731f2105b44afd`
- CI-enablement head: `7c6593b680e683fa795cc0e5a375298d1f8ef98c`

## Explicit scope / non-claims

R37 establishes rollback containment for canonical Episode mutations made
through the ordinary Episode state/API during a governed executor call.

It does not establish:
- a sandbox against arbitrary same-process Python code or private-memory
  corruption;
- filesystem/network/process side-effect rollback;
- protection against source/class monkeypatching;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R37;
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
