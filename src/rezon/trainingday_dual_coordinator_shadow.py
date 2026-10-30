"""Fail-closed source-only rehearsal of two TrainingDay GPU coordinators.

All timeline rows, host states, lease identities, time readings and fencing
acknowledgements are caller-supplied TEST DECLARATIONS. This module issues no
OS-enforced lease, device token or permission to start an optimizer. A
content digest establishes only continuity of the supplied scenario.
"""

from __future__ import annotations

import hashlib
import json
import re


SCHEMA = "rezon.trainingday.two-coordinator-lease-shadow.v1"
MAX_EVENTS = 128
MAX_TTL_MS = 120_000
MAX_HEARTBEAT_GAP_MS = 30_000
MAX_HOST_WITNESS_AGE_MS = 30_000
MAX_CUMULATIVE_CLOCK_DIVERGENCE_MS = 5_000
_MAX_TIME = 2**63
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_LEASE_ID = re.compile(r"[A-Za-z0-9_-]{4,64}\Z")
_COORDINATORS = frozenset(("root-a", "root-b"))
_HOST_EVENT_KINDS = frozenset((
    "WAKE", "SUSPEND", "TUNNEL_RESTORED", "TUNNEL_LOST",
    "HOST_IDLE", "HOST_BUSY", "EXECUTOR_IDLE", "EXECUTOR_BUSY", "FENCE_ACK",
))
_COORDINATOR_EVENT_KINDS = frozenset(("REQUEST", "RENEW", "RELEASE"))
_EVENT_FIELDS = frozenset((
    "kind", "actor", "host", "lease", "epoch", "mono_ms", "wall_ms", "ttl_ms",
))


class ShadowLeaseError(ValueError):
    """Invalid synthetic evidence; not an exception granting host authority."""


def _bounded_int(value: object, upper: int, *, positive: bool = False) -> bool:
    return (type(value) is int and value <= upper
            and (value > 0 if positive else value >= 0))


def _validate_scenario(run_sha256: str, events: list[dict]) -> None:
    if (type(run_sha256) is not str or len(run_sha256) != 64
            or _SHA256.fullmatch(run_sha256) is None):
        raise ShadowLeaseError("invalid source-bound run SHA256")
    if type(events) is not list or not 1 <= len(events) <= MAX_EVENTS:
        raise ShadowLeaseError("synthetic timeline missing or exceeds 128 events")
    prior_mono = prior_wall = -1
    for event in events:
        if type(event) is not dict or set(event) != _EVENT_FIELDS:
            raise ShadowLeaseError("malformed exact-field synthetic event")
        kind = event["kind"]
        actor = event["actor"]
        if (type(kind) is not str or type(actor) is not str
                or type(event["host"]) is not str or event["host"] != "lappy"
                or not _bounded_int(event["mono_ms"], _MAX_TIME - 1)
                or not _bounded_int(event["wall_ms"], _MAX_TIME - 1)
                or event["mono_ms"] < prior_mono
                or event["wall_ms"] < prior_wall):
            raise ShadowLeaseError("noncanonical host/actor/clock declaration")
        prior_mono = event["mono_ms"]
        prior_wall = event["wall_ms"]
        if kind in _HOST_EVENT_KINDS:
            expected_epoch = kind == "FENCE_ACK"
            if (actor != "host-shadow" or type(event["lease"]) is not str
                    or event["lease"] != ""
                    or not _bounded_int(event["epoch"], 2**31 - 1,
                                        positive=expected_epoch)
                    or (not expected_epoch and event["epoch"] != 0)
                    or type(event["ttl_ms"]) is not int
                    or event["ttl_ms"] != 0):
                raise ShadowLeaseError("malformed fake host event")
        elif kind in _COORDINATOR_EVENT_KINDS:
            lease_id = event["lease"]
            needs_ttl = kind in ("REQUEST", "RENEW")
            if (actor not in _COORDINATORS or type(lease_id) is not str
                    or len(lease_id) > 64 or _LEASE_ID.fullmatch(lease_id) is None
                    or not _bounded_int(event["epoch"], 2**31 - 1, positive=True)
                    or not _bounded_int(event["ttl_ms"], MAX_TTL_MS,
                                        positive=needs_ttl)
                    or (not needs_ttl and event["ttl_ms"] != 0)):
                raise ShadowLeaseError("malformed coordinator lease declaration")
        else:
            raise ShadowLeaseError("unsupported event type")


def assess_two_coordinator_shadow(run_sha256: str, events: list[dict]) -> dict:
    """Trace *synthetic* exclusive ownership without issuing an actual lease.

    Two roots can present conflicting requests. The first synthetic owner is
    retained until exact owner release, or lease expiry followed by a newer
    fake fencing acknowledgement while host state is again declared clean.
    An expired lease alone is never enough for a takeover. An unexpired lease
    is never fenced. Clock drift and standby/tunnel ambiguity quarantine the
    scenario, and host-enforced authorization is always false.
    """
    _validate_scenario(run_sha256, events)
    # All event fields and their sizes were bounded before canonical encoding.
    digest_input = {"schema": SCHEMA, "run_sha256": run_sha256, "events": events}
    digest = hashlib.sha256(json.dumps(
        digest_input, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("ascii")).hexdigest()

    awake = connected = host_idle = executor_idle = False
    tunnel_observed_at = host_observed_at = executor_observed_at = -1
    wake_observed_at = -1
    quarantine_since = -1
    fence_required = False
    pending_fence_epoch: int | None = None
    last_epoch = 0
    holder: dict | None = None
    accepted: list[dict] = []
    denials: list[str] = []
    first_mono = events[0]["mono_ms"]
    first_wall = events[0]["wall_ms"]

    def host_declared_ready(now: int) -> bool:
        # A long-running lease requires freshly repeated *claimed* observations.
        # No host timestamp is authenticated by this CPU-only fixture.
        return (awake and connected and host_idle and executor_idle
                and all(0 <= now - observed <= MAX_HOST_WITNESS_AGE_MS
                        for observed in (tunnel_observed_at, host_observed_at,
                                         executor_observed_at)))

    for event in events:
        kind = event["kind"]
        now = event["mono_ms"]
        if abs((now - first_mono) - (event["wall_ms"] - first_wall)) > MAX_CUMULATIVE_CLOCK_DIVERGENCE_MS:
            if "CUMULATIVE_CLOCK_DIVERGENCE" not in denials:
                denials.append("CUMULATIVE_CLOCK_DIVERGENCE")
            fence_required = True
        if kind == "WAKE":
            awake = True
            wake_observed_at = now
        elif kind == "SUSPEND":
            awake = False
            fence_required = True
            quarantine_since = now
        elif kind == "TUNNEL_RESTORED":
            connected = True
            tunnel_observed_at = now
        elif kind == "TUNNEL_LOST":
            connected = False
            fence_required = True
            quarantine_since = now
        elif kind == "HOST_IDLE":
            host_idle = True
            host_observed_at = now
        elif kind == "HOST_BUSY":
            host_idle = False
            fence_required = True
            quarantine_since = now
        elif kind == "EXECUTOR_IDLE":
            executor_idle = True
            executor_observed_at = now
        elif kind == "EXECUTOR_BUSY":
            executor_idle = False
            fence_required = True
            quarantine_since = now
        elif kind == "FENCE_ACK":
            if (holder is None and not fence_required
                    and quarantine_since < 0):
                # No fault, expiry, stale custody or outstanding owner:
                # a coordinator cannot mint a fake fencing generation solely
                # by inserting a purported host acknowledgement.
                denials.append("UNSOLICITED_FENCE_ACK")
            elif holder is not None and now < holder["expires_mono_ms"]:
                denials.append("FENCE_REJECTED_ACTIVE_LEASE")
            elif (quarantine_since >= 0 and any(
                    observed <= quarantine_since for observed in (
                        wake_observed_at, tunnel_observed_at,
                        host_observed_at, executor_observed_at))):
                denials.append("FENCE_REJECTED_FRESH_POST_FAULT_WITNESS_MISSING")
            elif not host_declared_ready(now):
                denials.append("FENCE_REJECTED_HOST_CUSTODY_UNKNOWN")
            elif event["epoch"] != last_epoch + 1:
                denials.append("NONSEQUENTIAL_FENCE_EPOCH")
            elif "CUMULATIVE_CLOCK_DIVERGENCE" in denials:
                denials.append("FENCE_REJECTED_CLOCK_DIVERGENCE")
            else:
                # A forged fake acknowledgement is NOT a real host fence.
                holder = None
                last_epoch = event["epoch"]
                pending_fence_epoch = event["epoch"]
                fence_required = False
                quarantine_since = -1
        elif kind == "REQUEST":
            if holder is not None and now < holder["expires_mono_ms"]:
                denials.append("UNEXPIRED_OWNER_COLLISION")
            elif holder is not None:
                denials.append("EXPIRED_OWNER_NOT_FENCED")
                fence_required = True
            elif fence_required or not host_declared_ready(now):
                denials.append("HOST_CUSTODY_UNKNOWN")
            elif (pending_fence_epoch is not None
                  and event["epoch"] != pending_fence_epoch):
                denials.append("FENCED_EPOCH_MISMATCH")
            elif (pending_fence_epoch is None
                  and event["epoch"] != last_epoch + 1):
                denials.append("NONSEQUENTIAL_LEASE_EPOCH")
            else:
                holder = {
                    "actor": event["actor"], "lease": event["lease"],
                    "epoch": event["epoch"],
                    "last_heartbeat_mono_ms": now,
                    "expires_mono_ms": now + event["ttl_ms"],
                }
                last_epoch = event["epoch"]
                pending_fence_epoch = None
                accepted.append({
                    "actor": event["actor"], "lease": event["lease"],
                    "epoch": event["epoch"], "mono_ms": now,
                })
        elif kind == "RENEW":
            if (holder is None or event["actor"] != holder["actor"]
                    or event["lease"] != holder["lease"]
                    or event["epoch"] != holder["epoch"]):
                denials.append("RENEW_NOT_CURRENT_OWNER")
            elif now >= holder["expires_mono_ms"]:
                denials.append("EXPIRED_RENEWAL_REJECTED")
                fence_required = True
            elif now - holder["last_heartbeat_mono_ms"] > MAX_HEARTBEAT_GAP_MS:
                denials.append("STALE_RENEWAL_HEARTBEAT")
                fence_required = True
                quarantine_since = now
            elif fence_required or not host_declared_ready(now):
                denials.append("RENEW_DURING_AMBIGUOUS_CUSTODY")
                fence_required = True
                quarantine_since = now
            else:
                holder["last_heartbeat_mono_ms"] = now
                holder["expires_mono_ms"] = now + event["ttl_ms"]
        elif kind == "RELEASE":
            if (holder is None or event["actor"] != holder["actor"]
                    or event["lease"] != holder["lease"]
                    or event["epoch"] != holder["epoch"]):
                denials.append("RELEASE_NOT_CURRENT_OWNER")
            elif now >= holder["expires_mono_ms"]:
                denials.append("EXPIRED_RELEASE_NEEDS_FENCE")
                fence_required = True
            else:
                holder = None
                pending_fence_epoch = None

    return {
        "schema": SCHEMA + ".assessment",
        "status": "SOURCE_ONLY_HOLD",
        "scenario_sha256": digest,
        "run_sha256": run_sha256,
        "accepted_requests": accepted,
        "denials": denials,
        "final_owner": holder["actor"] if holder is not None else None,
        # State machine has a single holder slot; conflicting roots only
        # produce denials, not second lease records.
        "max_concurrent_claims": 1 if accepted else 0,
        "synthetic_fencing_claimed": pending_fence_epoch is not None,
        "host_lease_authenticated": False,
        "authorizes_optimizer_start": False,
        "authorizes_gpu_reservation": False,
        "qualified_exclusive_gpu_lease": False,
        "supports_shared_gradients": False,
    }
