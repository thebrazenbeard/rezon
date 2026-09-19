# Rezon Kernel V0 R30 Exact NodeDescriptor Preflight Contract

Status: `SOURCE_REPAIRED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PENDING / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R30 is the bounded successor to failed whole-Kernel R29 exact subject
`8026c7932ff95bab3029b71f12686717178b818c`.

R29's independence metadata/policy hardening remains valid within that narrower
boundary. Fresh hostile review found that mutable or malformed
`NodeDescriptor` runtime semantics could still reach scheduling/execution
before the descriptor was fully validated.

## R29 hostile failure

Exact R29 failed all eight frozen R30 cases:

1. a stateful `independence_required` value returned true while scheduling,
   then false in the runner; peer output became visible, was copied, and the copy
   was admitted with no contract failure;
2. a stateful `mandatory_verification` value scheduled as mandatory, then
   turned false before verification enforcement;
3. a `NodeDescriptor` subclass reached the executor before admission rejected it;
4. a custom node-ID string reached the executor before late rejection;
5. non-tuple permitted output kinds reached the executor before late rejection;
6. non-tuple accepted input kinds were accepted and executed;
7. non-tuple empty required-authority data was normalized and executed;
8. non-tuple verification target IDs were accepted and executed.

Disposition:
`R29_NODE_DESCRIPTOR_PRE_SCHEDULER_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R29 remains preserved, draft, and unmerged.

## Frozen R30 RED

Regression file:

`tests/test_r30_exact_node_descriptor_preflight.py`

Exact RED commit:

`ffb938b071315fe72f8ee21e18d4591c5f722a31`

Fresh exact-R29 result:

**8 failed / 0 passed**.

## R30 repair

Exact descriptor contract:

`0032d1bd45ca1b995d54da28f4071efa63e4da3a`

Admission enforcement:

`3ffdb078c289153761998d630506df4952669a04`

Scheduler preflight enforcement:

`9faaa698c84445dc3d846629a443ead449b78411`

R30 defines one exact `NodeDescriptor` runtime contract and applies it before
the scheduler evaluates descriptor semantics.

The contract requires:

- exact base `NodeDescriptor`;
- non-empty exact built-in string node ID;
- exact tuples of exact `PropositionKind` for permitted output and accepted
  input kinds;
- exact built-in booleans for mandatory verification and independence-required;
- exact tuples containing non-empty exact strings for required authority,
  permitted relation types, verification target IDs, and independence blind IDs;
- an exact tuple of exact `PropositionKind` for independence blind kinds;
- explicit verification targets whenever mandatory verification is true.

The scheduler now terminates with `CONTRACT_VIOLATION` before node selection or
executor invocation if any descriptor violates the contract.

Direct admission uses the same contract so callers cannot bypass scheduler
preflight by invoking admission directly.

## Qualification

CI-enablement head:

`1d223c4dd42f2c5921944b9180fb15896a639d40`

Fresh detached-checkout qualification:

- R30 hostile regressions: **8/8 PASS**;
- focused R16-R30 controls: **80/80 PASS**;
- scheduler/admission/independence focused set: **70/70 PASS** before remote cut;
- full suite: **209/209 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35460288405`;
- exact head `1d223c4dd42f2c5921944b9180fb15896a639d40`;
- test job `105942803105`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R29 final: `8026c7932ff95bab3029b71f12686717178b818c`
- R30 branch: `work/rezon-kernel-v0-r30-exact-node-descriptor-preflight`
- frozen RED: `ffb938b071315fe72f8ee21e18d4591c5f722a31`
- descriptor contract: `0032d1bd45ca1b995d54da28f4071efa63e4da3a`
- admission enforcement: `3ffdb078c289153761998d630506df4952669a04`
- scheduler preflight: `9faaa698c84445dc3d846629a443ead449b78411`
- CI-enablement head: `1d223c4dd42f2c5921944b9180fb15896a639d40`

## Explicit scope / non-claims

R30 establishes ordinary in-process exact runtime validation of the current
NodeDescriptor contract before scheduler execution and at direct admission.

It does not establish:

- correctness or safety of arbitrary executor implementation side effects outside
  the governed runner;
- cryptographic caller identity;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R30;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Pressure the next adjacent runtime boundary only if no independent verdict
   arrives, preserving every failed exact subject.
5. Do not merge without Patrick's explicit authority.


## 2026-09-19 scheduler-to-execution descriptor binding repair

Fresh hostile review of exact predecessor `4f088c0f085df3f05bd3e59e284b4825e0e3e537` found that `EpisodeRunner` accepted an arbitrary sequence-like `nodes` object. A stateful sequence could yield one exact strict `RunnerNode`/`NodeDescriptor` during scheduler iteration and then return a different exact weak `RunnerNode` with the same `node_id` during indexed execution. The runner compared only the ID, so descriptor semantics used for scheduling were not bound to the descriptor later executed.

The frozen local RED demonstrates the ordinary-Python bypass with a strict scheduled descriptor requiring protected authority and a weak same-ID execution descriptor requiring none. Exact predecessor behavior executed the weak node and emitted output with no contract failure.

The repair requires the runner's node set to be an exact immutable tuple of exact `RunnerNode` values whose descriptors satisfy the same exact `NodeDescriptor` contract already used by scheduler/admission. Non-exact/stateful containers now fail before scheduling with `runner:invalid_node_contract`; executor invocation remains zero.

Fresh local successor evidence before publish:

- R30 exact-node regressions: **9/9 PASS**;
- full suite: **210/210 PASS**;
- changed-file `py_compile`: PASS;
- `git diff --check`: PASS.

This closes the reviewed scheduler-to-execution substitution path without widening authority. Hosted CI and fresh independent hostile rereview remain exact-successor gates.
