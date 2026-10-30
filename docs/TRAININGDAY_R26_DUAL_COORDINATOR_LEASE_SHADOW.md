# TrainingDay R26 — two-coordinator lease shadow (source-only)

This is a **deterministic public/CPU fixture**, not a daemon, lease broker,
GPU reservation, hardware observation, authorization token or authenticated
Blotter/Executor receipt. It never contacts Lappy, VN1 or VN2. Every event,
host/wake status, monotonic/wall clock and fake fence acknowledgment is
supplied by the caller and can be forged by that caller.

## Exact scope

`rezon.trainingday_dual_coordinator_shadow.assess_two_coordinator_shadow`
accepts one source-bound run SHA and up to 128 strictly shaped chronological
events for `root-a`, `root-b`, and `host-shadow`, all pinned to **`lappy`**.
The schema is `rezon.trainingday.two-coordinator-lease-shadow.v1`. Each event
must have exactly these fields:

| Field | Allowed |
| --- | --- |
| `kind` | `REQUEST`, `RENEW`, `RELEASE`, `WAKE`, `SUSPEND`, `TUNNEL_RESTORED`, `TUNNEL_LOST`, `HOST_IDLE`, `HOST_BUSY`, `EXECUTOR_IDLE`, `EXECUTOR_BUSY`, `FENCE_ACK` |
| `actor` | `root-a`/`root-b` for coordinator events, otherwise `host-shadow` |
| `host` | exactly `lappy` |
| `lease` | ASCII `[A-Za-z0-9_-]{4,64}` for coordinator events, empty otherwise |
| `epoch` | positive bounded integer for coordinator/fence events; zero for other host events |
| `mono_ms`, `wall_ms` | nonnegative, nondecreasing signed-63-bit integer timestamps |
| `ttl_ms` | 1..120000 for requests/renewals, zero otherwise |

The source simulation has one holder slot. A different root's request while
the old holder's claim remains unexpired is **denied**. An expired claim
remains blocked until a strictly later *synthetic* fence claim, with the
host again declared awake, connected, idle and Executor idle. Active claims
cannot be displaced by a fence. A fake release from a different root or
release of an already expired claim is rejected. Fencing epochs must be the
next consecutive generation, not a jump to an arbitrary high value. Any
standby, tunnel loss, host busy or Executor busy declaration quarantines
ownership until controlled synthetic recovery with fresh post-fault awake,
tunnel, host-idle and Executor-idle witnesses. A renewal after
30 seconds without its claimed coordinator heartbeat is rejected. An
unsolicited fence when there is no outstanding lease, expiry, or ambiguous
custody is also rejected; it cannot manufacture a fake generation.
Tunnel,
host-idle and Executor-idle declarations must each be no older than 30
seconds; their timestamps are **not authenticated**.

A 5-second cumulative monotonic-vs-wall discrepancy is rejected, including
the case where each adjacent observation individually differs by a smaller
amount. The digest binds the source-declared run and ordered scenario, but
is **not** a signature, kernel-observed heartbeat, or atomic compare-and-swap.

## Source gate and negative controls

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -p test_trainingday_dual_coordinator_shadow.py -q`

The fixture tests:

1. Two competing roots and normal owner-release handoff, max one holder.
2. Missing initial host proof, Executor queued/busy evidence, and standby.
3. Tunnel disconnect; unexpired owner cannot be fenced; expired owner
   cannot be stolen without synthetic fencing, fresh post-fault witnesses,
   and a consecutive fencing epoch.
4. Stale coordinator heartbeat, stale host witness, fake second-root release,
   expired release bypass attempt.
5. Cumulative clock divergence that evades per-sample drift checks.
6. Oversized lease/event list, invalid Unicode/booleans/NaN/object data,
   and source-bound scenario digest changes.

## Hard limits

The implementation intentionally **never** returns a physical start
capability: `host_lease_authenticated=false`,
`authorizes_optimizer_start=false`, `authorizes_gpu_reservation=false`,
`qualified_exclusive_gpu_lease=false`, and `supports_shared_gradients=false`
for *all* outcomes. The caller can forge fake host and fence events, so
success in this simulator does not prove an actual cross-chat/Executor
atomic lease or prevent a separate process from starting CUDA. A physical
lease requires a single host-enforced coordinator/OS primitive and trusted
observations, not a JSON ledger created by collaborating assistants.

No host/Windows power settings, running services, credentials, private
evaluation bank, training model, tensor adapter, deployed Vera or recurring
automation are accessed or changed by this source-only artifact.
