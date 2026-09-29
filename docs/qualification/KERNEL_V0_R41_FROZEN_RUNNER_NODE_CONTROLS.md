# Rezon Kernel V0 R41 Frozen RunnerNode Controls

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R41 is the bounded successor to failed whole-Kernel R40 exact subject
`48380f19c7e16a558d268b15a7f7f32d5473250d`.

R40's targeted-executor transaction repair remains valid within that narrower
scope. Fresh hostile review found that the run-local governed node tuple still
contained the original mutable RunnerNode objects.

## R40 hostile failure

Exact R40 failed all three frozen R41 cases.

1. Descriptor permission escalation:
   - preflighted descriptor permits only HYPOTHESIS;
   - executor rewrites its RunnerNode descriptor during execution to permit CLAIM;
   - returned canonical CLAIM `c1` is admitted;
   - final receipt has no failure.

2. Mandatory-verifier removal:
   - two exact mandatory verifiers pass initial preflight;
   - verifier A rewrites verifier B's descriptor to remove mandatory verification;
   - the next scheduling cycle reads the mutated descriptor;
   - verifier B never runs.

3. Executor substitution:
   - verifier A replaces verifier B's executor pointer after preflight;
   - the next cycle invokes the replacement instead of the originally governed
     verifier.

Disposition:
`R40_MUTABLE_RUNNER_NODE_CONTROLS = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R40 remains preserved, draft, and unmerged.

## Frozen R41 RED

Regression file:

`tests/test_r41_frozen_runner_node_controls.py`

Exact RED commit:

`a14c06e16e3e74d85cce1ecf2d55ed0f82ea501d`

Fresh exact-R40 result:

**3 failed / 0 passed**.

## R41 repair

Runner repair:

`614cb8eb8130c2975123aff0da57e2846dee2726`

R41 converts every preflighted RunnerNode into a run-local governed copy before
scheduling begins.

The governed copy freezes:
- a newly reconstructed NodeDescriptor;
- the preflighted executor pointer;
- a newly reconstructed VisibilityPolicy;
- a newly reconstructed IndependenceMetadata;
- a newly reconstructed exact IndependenceVerificationPolicy and its exact
  evidence records when present;
- a newly reconstructed exact AuthorityVerificationPolicy and its exact
  evidence records when present.

All scheduler, visibility, verification, executor-selection, admission, trace,
and completion logic operates on these governed copies.

Mutating the original public RunnerNode objects after preflight therefore cannot:
- broaden current-run output permissions;
- remove or rewrite a mandatory verifier;
- replace a preflighted executor pointer;
- alter current-run visibility/independence policy values through top-level
  RunnerNode replacement.

This is a value/pointer snapshot boundary, not a process sandbox.

## Qualification

CI-enablement head:

`6464e71c759e66f235a3d64db11918b49020a159`

Fresh detached-checkout qualification:

- R41 hostile regressions: **3/3 PASS**;
- focused R16-R41 controls: **120/120 PASS**;
- recent controls: **38/38 PASS** before remote cut;
- full suite: **249/249 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35467353084`;
- exact head `6464e71c759e66f235a3d64db11918b49020a159`;
- test job `105962028402`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R40 final: `48380f19c7e16a558d268b15a7f7f32d5473250d`
- R41 branch: `work/rezon-kernel-v0-r41-frozen-runner-node-controls`
- frozen RED: `a14c06e16e3e74d85cce1ecf2d55ed0f82ea501d`
- runner repair: `614cb8eb8130c2975123aff0da57e2846dee2726`
- CI-enablement head: `6464e71c759e66f235a3d64db11918b49020a159`

## Explicit scope / non-claims

R41 establishes run-local snapshotting of preflighted RunnerNode control values
and executor pointers.

It does not establish:
- a sandbox against arbitrary same-process Python/private-memory corruption;
- immutability of an executor object's own internal state;
- filesystem/network/process side-effect rollback;
- protection against source/class monkeypatching;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R41;
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
