# Rezon Kernel V0 R36 Frozen Runner Node Set

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R36 is the bounded successor to failed whole-Kernel R35 exact subject
`a364dbab81f748a58d9254e78e71841b0675596b`.

R35's exact run task-ID and Episode preflight remains valid within that narrower
scope. Fresh hostile review found a time-of-check/time-of-use gap in the
preflighted RunnerNode tuple.

## R35 hostile failure

Exact R35 failed all three frozen R36 variants.

Initial state:
- exact tuple of two exact RunnerNode values;
- both descriptors are mandatory verifiers;
- one-time runner node preflight passes.

Attack:
1. mandatory verifier A executes;
2. A satisfies its own exact verification contract;
3. inside A's executor call, caller-controlled code rewrites `runner.nodes`;
4. the next scheduler iteration reads the rewritten tuple;
5. mandatory verifier B is absent and never runs;
6. A's canonical test result remains admitted;
7. the final receipt reports no failures or unresolved items.

Frozen variants:
- remove verifier B;
- replace the node tuple with empty;
- replace verifier B with a non-mandatory node.

Disposition:
`R35_MUTABLE_RUNNER_NODE_SET = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R35 remains preserved, draft, and unmerged.

## Frozen R36 RED

Regression file:

`tests/test_r36_frozen_runner_node_set.py`

Exact RED commit:

`1fd0340ecd14dc2c569418109dd626dc8f10717e`

Fresh exact-R35 result:

**3 failed / 0 passed**.

## R36 repair

Runner repair:

`786e83c8b616fb9a28a19d993a7b49d3744c631a`

R36 snapshots `self.nodes` exactly once into a run-local candidate, validates
that exact tuple and every exact RunnerNode/NodeDescriptor, then binds the
validated tuple as `governed_nodes`.

Every subsequent scheduling/index/dispatch read in the run uses
`governed_nodes`, not the mutable public `runner.nodes` attribute.

Therefore executor-side reassignment of `runner.nodes`, concurrent ordinary
attribute reassignment, or post-preflight replacement cannot add, remove, or
substitute nodes for the current run.

The public attribute may still change as ordinary Python state, but such changes
can only affect a future run that independently re-enters preflight.

## Qualification

CI-enablement head:

`cc7eafadea523392ed4a55b26fb2c251baec0685`

Fresh detached-checkout qualification:

- R36 node-set regressions: **3/3 PASS**;
- focused R16-R36 controls: **105/105 PASS**;
- recent run-entry/control focused set: **23/23 PASS** before remote cut;
- full suite: **234/234 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35463917160`;
- exact head `cc7eafadea523392ed4a55b26fb2c251baec0685`;
- test job `105952553624`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R35 final: `a364dbab81f748a58d9254e78e71841b0675596b`
- R36 branch: `work/rezon-kernel-v0-r36-frozen-runner-node-set`
- frozen RED: `1fd0340ecd14dc2c569418109dd626dc8f10717e`
- runner repair: `786e83c8b616fb9a28a19d993a7b49d3744c631a`
- CI-enablement head: `cc7eafadea523392ed4a55b26fb2c251baec0685`

## Explicit scope / non-claims

R36 establishes ordinary in-process binding of each run to the exact RunnerNode
tuple that passed run-entry preflight.

It does not establish:
- arbitrary executor side-effect safety outside the governed runner;
- protection against source/class monkeypatching of exact base classes;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R36;
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
