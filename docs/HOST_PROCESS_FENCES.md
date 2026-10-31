# Rezon opt-in OS process fences — source integration, NOT host qualification

The ordinary Rezon provider subprocess is still a bounded *best-effort* local
child, not a security boundary against hostile descendants. Source tests do
not grant a protected device lease, authenticate a host, or install this code.

## Linux (atomic cgroup v2)

`rezon._linux_host_cgroup.LinuxCgroupFence` is an explicit opt-in
`host_process_fence` for both `OpenAICompatibleModel` and `AnthropicModel`.
When supplied, requests and catalog probes use the native
`src/rezon/native/cgroup_clone3_helper.c` launcher:

1. A **separate trusted host service** provisions a dedicated exclusive cgroup
   v2 leaf with finite memory and PID bounds, a distinct unprivileged payload
   UID/GID, a protected native launcher binary, and a known SHA-256 digest.
2. The Python adapter validates the protected leaf, pinned root-owned helper,
   resource limits, absence of existing members, and executable path.
3. The helper uses `clone3(CLONE_INTO_CGROUP)` to place the payload **at
   creation**; it never starts a payload and then writes its PID to
   `cgroup.procs`.
4. The parent withholds request bytes until a placement witness and
   independently checked cgroup membership are returned.
5. Completion and catalog code keep the existing single deadline, bounded
   stdin/stdout/stderr handling and nonreplay semantics. Teardown uses the
   *exclusive leaf's* `cgroup.kill`, including descendants that call
   `setsid`, plus helper reap.

There is deliberately **no fallback** to ordinary `Popen` when an explicit
host fence fails validation. The host supplies and protects the object; client
or model-produced arguments must never be treated as a lease or key custody.

## Windows (suspended Job Object)

`rezon._windows_host_job.WindowsJobFence` contains a source-level Win32
kernel adapter that creates a suspended process, applies finite Job Object
limits, assigns the process to the Job, and **only then** resumes it. The
`JobChild` wrapper has unique, noncopyable handle ownership and locked,
retryable close behavior. This source is *not* a production credential channel.

The Rezon provider request path explicitly **rejects a WindowsJobFence**:
there is not yet an independently qualified, bounded stdin/stdout transport
for the native process handle. No request credentials are passed to an
unqualified Windows child. Host physical verification and IPC work remain
mandatory before activating Windows Job custody.

## Verification and release gates

Source tests cover Linux non-provisioned/unsafe denial, helper compile under
`-Werror`, Windows assign-before-resume and failed-assignment cleanup,
noncopyable Win32 handles, Linux/Windows opt-in denial before network
dispatch, and bounded diagnostic-pipe flood behavior. These are not
performance or adversarial host isolation tests.

Release remains **HOLD** until separately evidenced:

- Signed/host-verifiable TRAININGDAY owner acknowledgment and exclusive lease.
- Root-owned pinned binary, cgroup v2 delegation and protected configuration,
  or Windows service with qualified Job and bounded IPC.
- Real process-tree tests: `setsid` escape attempt, nested descendants,
  memory/process ceilings, timeout, crash, repeated close, and no credential
  replay after unknown completion.
- Exact-head CI, independent hostile review, service restart/recovery and
  platform-specific host validation.

No host, tunnel, cgroup, service, token, or default provider configuration is
mutated by importing these modules or running the source-only suite.
