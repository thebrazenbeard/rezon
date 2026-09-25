# Rezon Kernel V0 R42 Frozen TaskEnvelope

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R42 is the bounded successor to failed whole-Kernel R41 exact subject
`48bb0b19bb947771bb31108dd9d69f4622412408`.

R41's RunnerNode-control snapshot remains valid within that narrower scope.
Fresh hostile review found that the exact TaskEnvelope remained shared with
executors and reused across later iterations.

## R41 hostile failure

Exact R41 failed both frozen R42 attacks.

1. Executor-view mutation:
   - verifier A receives the exact TaskEnvelope in its ExecutionView;
   - A rewrites `literal_request` from `original-request` to
     `tampered-request`;
   - verifier B later receives `tampered-request` in both its TaskSpecification
     and TaskEnvelope;
   - the final receipt still carries the digest computed from the original
     envelope and reports no failure.

2. External-reference mutation:
   - verifier A mutates the caller's original exact TaskEnvelope through a
     separately retained reference;
   - verifier B again executes against the changed task;
   - the receipt remains bound to the original digest.

Disposition:
`R41_MUTABLE_TASK_ENVELOPE = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R41 remains preserved, draft, and unmerged.

## Frozen R42 RED

Regression file:
`tests/test_r42_frozen_task_envelope.py`

Exact RED commit:
`61a2f0a9dc9953f414176b224f717dc15e4e5de2`

Fresh exact-R41 result:
**2 failed / 0 passed**.

## R42 repair

Runner repair:
`8080cc87ed1092a70b720036f2334e250f849308`

After exact TaskEnvelope validation, R42 creates one run-local
`governed_task_envelope` snapshot.

Current-run semantics use only that snapshot for:
- task-envelope digest;
- task-ID binding;
- resource-budget bounding;
- execution-view TaskSpecification construction;
- independence context checks.

For each non-independent executor, R42 creates a separate TaskEnvelope copy in
the executor-facing ExecutionView. Executor mutation therefore cannot alter the
governed run snapshot.

Mutation of the caller's original TaskEnvelope after run entry likewise cannot
change current-run task semantics.

## Qualification

CI-enablement head:
`93a59e55bae8932e67d0e9339f3671e3d61e8123`

Fresh detached-checkout qualification:
- R42 regressions: **2/2 PASS**;
- focused R16-R42 controls: **122/122 PASS**;
- recent controls: **41/41 PASS** before remote cut;
- full suite: **251/251 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35467695515`;
- exact head `93a59e55bae8932e67d0e9339f3671e3d61e8123`;
- test job `105962941947`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R41 final: `48bb0b19bb947771bb31108dd9d69f4622412408`
- R42 branch: `work/rezon-kernel-v0-r42-frozen-task-envelope`
- frozen RED: `61a2f0a9dc9953f414176b224f717dc15e4e5de2`
- runner repair: `8080cc87ed1092a70b720036f2334e250f849308`
- CI-enablement head: `93a59e55bae8932e67d0e9339f3671e3d61e8123`

## Explicit scope / non-claims

R42 establishes run-local TaskEnvelope snapshotting and isolated executor
projections.

It does not establish:
- a sandbox against arbitrary same-process Python/private-memory corruption;
- filesystem/network/process side-effect rollback;
- source/class monkeypatch resistance;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R42;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve every failed exact subject.
5. Do not merge without Patrick's explicit authority.
