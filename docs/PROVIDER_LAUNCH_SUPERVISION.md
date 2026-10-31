# Provider launch supervision (source-only)

Rezon starts model-provider adapter subprocesses under a monotonic request deadline.
The launch phase itself can block inside the OS process constructor. A bounded
daemon launch custodian now retains ownership until the caller accepts a child;
late children are killed without writing a model request or API key to stdin.
At most eight launch constructors can remain outstanding. Uncertain completion
outcomes retain their existing no-blind-retry exception classification.

This is **not** a host process-tree security boundary. POSIX process groups
clean up ordinary descendants but cannot stop a child that creates a new
session, and Windows child termination does not imply descendant termination.
A program may also run before parent-side resource-limit adjustments.

Before host release, the operator must separately qualify:

1. Linux: delegated cgroup v2 with a trusted blocked/atomic child launch,
   resource-limit readback, cgroup.kill on deadline/cancellation and evidence
   that setsid descendants remain in the cgroup.
2. Windows: a host-owned CREATE_SUSPENDED launch into a Job Object with
   KILL_ON_JOB_CLOSE and process/memory limits before resumption, plus
   physical cancellation and orphan tests.
3. Authenticated, exclusive TRAININGDAY/process owner handoff and bounded
   credentials; Rezon endpoint catalog claims are not host or model attestation.

The tests in this branch exercise local subprocess behavior and synthetic
failure paths. They must not be treated as authorization for installation,
protected host execution, real model training, or PR merge.
