"""Deterministic, nonauthorizing three-node TrainingDay fault rehearsal.

Events are *untrusted synthetic declarations*, not authenticated Executor, OS,
GPU, checkpoint or fencing receipts. No filesystem/network/host operation occurs.
The one-owner state machine intentionally refuses progress under ambiguity.
"""

from __future__ import annotations

import hashlib
import json
import re
from types import MappingProxyType


SCHEMA = "rezon.trainingday.r28-recovery-simulation.v1"
MAX_EVENTS = 128
LEASE_TTL_MS = 30_000
MAX_HOST_WITNESS_AGE_MS = 30_000
MAX_CUMULATIVE_CLOCK_DRIFT_MS = 5_000
_TIME_MAX = 2**63 - 1
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_NODES = frozenset(("lappy", "vn1", "vn2"))
_ROOTS = frozenset(("root-a", "root-b"))
_KINDS = frozenset((
    "WAKE", "STANDBY", "TUNNEL_UP", "TUNNEL_DOWN", "WORKER_RESUME",
    "ACQUIRE", "RELEASE", "FENCE_ACK", "BEGIN_STEP", "PARTIAL_WRITE",
    "SEAL", "COMMIT", "CLAIM_SUCCESS", "ROLLOVER",
))
_FIELDS = frozenset((
    "kind", "actor", "node", "epoch", "step", "mono_ms", "wall_ms", "digest",
))
_HASH_KINDS = frozenset((
    "PARTIAL_WRITE", "SEAL", "COMMIT", "CLAIM_SUCCESS", "ROLLOVER",
))
_STEP_KINDS = _HASH_KINDS | {"BEGIN_STEP"}
_ROOT_KINDS = _STEP_KINDS | {"ACQUIRE", "RELEASE"}


class RecoveryScenarioError(ValueError):
    """Reject malformed public synthetic timeline before event interpretation."""


def _int(value: object, *, positive: bool = False) -> bool:
    return (type(value) is int and value <= _TIME_MAX
            and (value > 0 if positive else value >= 0))


def _immutable_snapshot(events: list[dict]) -> tuple[MappingProxyType, ...]:
    """Copy bounded exact dict/scalar values once before any validation.

    The source protocol contains only exact ints and strs, so a private copy
    of each event is a *deep* ownership cut: there are no mutable nested
    objects to alias. A mapping proxy plus tuple prevents the validator (or a
    validation callback) from later changing the data that will be replayed.
    """
    if type(events) is not list or not 1 <= len(events) <= MAX_EVENTS:
        raise RecoveryScenarioError("invalid or oversized synthetic timeline")
    frozen = []
    for event in tuple(events):
        if type(event) is not dict or len(event) != len(_FIELDS):
            raise RecoveryScenarioError("noncanonical event shape")
        private = event.copy()
        if (len(private) != len(_FIELDS)
                or not all(type(key) is str for key in private)
                or set(private) != _FIELDS
                or not all(type(value) in (str, int) for value in private.values())):
            raise RecoveryScenarioError("noncanonical immutable event fields")
        frozen.append(MappingProxyType(private))
    return tuple(frozen)


def _validate(run_sha256: str, events: tuple[MappingProxyType, ...]) -> None:
    if (type(run_sha256) is not str or len(run_sha256) != 64
            or _SHA.fullmatch(run_sha256) is None):
        raise RecoveryScenarioError("invalid source-bound run digest")
    if type(events) is not tuple or not 1 <= len(events) <= MAX_EVENTS:
        raise RecoveryScenarioError("invalid immutable synthetic timeline")
    mono = wall = -1
    for event in events:
        if (type(event) is not MappingProxyType or len(event) != len(_FIELDS)
                or not all(type(key) is str for key in event)
                or set(event) != _FIELDS):
            raise RecoveryScenarioError("noncanonical event shape")
        kind, actor, node = event["kind"], event["actor"], event["node"]
        if (type(kind) is not str or len(kind) > 20 or kind not in _KINDS
                or type(actor) is not str or len(actor) > 20
                or type(node) is not str or len(node) > 5
                or node not in _NODES
                or not _int(event["mono_ms"])
                or not _int(event["wall_ms"])
                or event["mono_ms"] < mono or event["wall_ms"] < wall):
            raise RecoveryScenarioError("unsupported actor/node/clock")
        mono, wall = event["mono_ms"], event["wall_ms"]
        step, epoch, digest = event["step"], event["epoch"], event["digest"]
        if (not _int(step, positive=kind in _STEP_KINDS)
                or (kind not in _STEP_KINDS and step != 0)
                or not _int(epoch, positive=kind in (_ROOT_KINDS | {"FENCE_ACK"}))
                or (kind not in (_ROOT_KINDS | {"FENCE_ACK"}) and epoch != 0)
                or type(digest) is not str
                or (kind in _HASH_KINDS and (len(digest) != 64
                                            or _SHA.fullmatch(digest) is None))
                or (kind not in _HASH_KINDS and digest != "")):
            raise RecoveryScenarioError("malformed kind-specific step/epoch/digest")
        if kind in _ROOT_KINDS:
            if actor not in _ROOTS or node != "lappy":
                raise RecoveryScenarioError("invalid coordinator actor")
        elif kind == "WORKER_RESUME":
            if actor != "worker-shadow" or node not in ("vn1", "vn2"):
                raise RecoveryScenarioError("invalid synthetic worker")
        elif actor != "host-shadow" or (kind in ("WAKE", "STANDBY", "FENCE_ACK")
                                        and node != "lappy"):
            raise RecoveryScenarioError("invalid synthetic host witness")


def simulate_recovery(run_sha256: str, events: list[dict]) -> dict:
    """Replay one strictly bounded scenario and return nonauthorizing receipts.

    Simulated `COMMIT` only occurs after a matching PARTIAL_WRITE -> SEAL for
    the active step. A fault discards inflight work without incrementing the
    committed counter. After fault, host-post-fault witness claims, expiry and
    a declared fence are all required for a second synthetic owner.
    """
    # Validate, hash and replay ONE detached immutable snapshot. Referencing
    # the caller's mutable list again after validation was a source TOCTOU.
    events = _immutable_snapshot(events)
    _validate(run_sha256, events)
    scenario_digest = hashlib.sha256(json.dumps({
        "schema": SCHEMA, "run_sha256": run_sha256,
        "events": [dict(event) for event in events],
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
       allow_nan=False).encode("ascii")).hexdigest()

    connected = {node: False for node in _NODES}
    tunnel_witness = {node: -1 for node in _NODES}
    workers = {"vn1": False, "vn2": False}
    worker_witness = {node: -1 for node in workers}
    awake = False
    wake_witness = -1
    owner: str | None = None
    owner_epoch = 0
    last_epoch = 0
    expires_at = -1
    fault_at = -1
    needs_fence = False
    fence_epoch: int | None = None
    clock_quarantined = False
    inflight: tuple[int, str] | None = None
    pending_digest: str | None = None
    sealed_digest: str | None = None
    committed: dict[int, str] = {}
    success_claims: set[int] = set()
    retired_steps: set[int] = set()
    receipts: list[dict] = []
    denials: list[dict] = []
    first_mono = events[0]["mono_ms"]
    first_wall = events[0]["wall_ms"]

    def deny(index: int, reason: str) -> None:
        denials.append({"index": index, "reason": reason})

    def ready(now: int) -> bool:
        return (awake and all(connected.values()) and all(workers.values())
                and all(0 <= now - stamp <= MAX_HOST_WITNESS_AGE_MS
                        for stamp in (
                            wake_witness, *tunnel_witness.values(),
                            *worker_witness.values())))

    def after_fault() -> bool:
        return (wake_witness > fault_at
                and all(t > fault_at for t in tunnel_witness.values())
                and all(t > fault_at for t in worker_witness.values()))

    def fault(now: int) -> None:
        nonlocal awake, needs_fence, fault_at, inflight, pending_digest, sealed_digest
        if owner is not None:
            needs_fence = True
        fault_at = now
        # Conservative: no old tunnel/worker witness survives a fault.
        awake = False
        for node in _NODES:
            connected[node] = False
        for node in workers:
            workers[node] = False
        inflight = None
        pending_digest = sealed_digest = None

    for index, event in enumerate(events):
        kind, now = event["kind"], event["mono_ms"]
        actor, node = event["actor"], event["node"]
        epoch, step, digest = event["epoch"], event["step"], event["digest"]
        if abs((now - first_mono) - (event["wall_ms"] - first_wall)) > MAX_CUMULATIVE_CLOCK_DRIFT_MS:
            clock_quarantined = True
            if not any(d["reason"] == "CUMULATIVE_CLOCK_DRIFT" for d in denials):
                deny(index, "CUMULATIVE_CLOCK_DRIFT")
        if kind == "WAKE":
            awake = True
            wake_witness = now
        elif kind == "STANDBY":
            fault(now)
            receipts.append({"event": kind, "index": index, "inflight_aborted": True})
        elif kind == "TUNNEL_UP":
            connected[node] = True
            tunnel_witness[node] = now
        elif kind == "TUNNEL_DOWN":
            fault(now)
            receipts.append({"event": kind, "index": index, "inflight_aborted": True})
        elif kind == "WORKER_RESUME":
            if connected[node] and awake:
                workers[node] = True
                worker_witness[node] = now
                receipts.append({"event": kind, "node": node, "index": index})
            else:
                deny(index, "WORKER_WITHOUT_HOST_TUNNEL")
        elif kind == "FENCE_ACK":
            if not needs_fence:
                deny(index, "UNSOLICITED_FAKE_FENCE")
            elif owner is not None and now < expires_at:
                deny(index, "UNEXPIRED_OWNER_NOT_FENCED")
            elif not ready(now) or not after_fault() or clock_quarantined:
                deny(index, "FENCE_HOST_WITNESS_UNKNOWN")
            elif epoch != last_epoch + 1:
                deny(index, "FENCE_EPOCH_MISMATCH")
            else:
                # Synthetic host claim only. Never a real OS-fenced epoch.
                owner = None
                owner_epoch = 0
                fence_epoch = epoch
                needs_fence = False
                receipts.append({"event": kind, "epoch": epoch, "index": index,
                                 "host_fence_authenticated": False})
        elif kind == "ACQUIRE":
            expected_epoch = fence_epoch if fence_epoch is not None else last_epoch + 1
            if owner is not None:
                deny(index, "OWNER_COLLISION")
            elif needs_fence or clock_quarantined or not ready(now):
                deny(index, "HOST_CUSTODY_UNKNOWN")
            elif epoch != expected_epoch:
                deny(index, "NONSEQUENTIAL_EPOCH")
            else:
                owner, owner_epoch, last_epoch = actor, epoch, epoch
                expires_at = now + LEASE_TTL_MS
                fence_epoch = None
                receipts.append({"event": kind, "actor": actor, "epoch": epoch,
                                 "index": index, "synthetic_only": True})
        elif kind == "RELEASE":
            if owner != actor or owner_epoch != epoch:
                deny(index, "RELEASE_NOT_OWNER")
            elif needs_fence or now >= expires_at or inflight is not None:
                deny(index, "RELEASE_DURING_AMBIGUOUS_OR_INFLIGHT")
            else:
                owner, owner_epoch = None, 0
        elif kind in _STEP_KINDS:
            if (owner != actor or epoch != owner_epoch
                    or needs_fence or clock_quarantined or now >= expires_at
                    or not ready(now)):
                deny(index, "STEP_WITHOUT_ACTIVE_SYNTHETIC_OWNER")
                continue
            if kind == "BEGIN_STEP":
                if inflight is not None or step != (max(committed, default=0) + 1):
                    deny(index, "STEP_SEQUENCE_OR_INFLIGHT_CONFLICT")
                else:
                    inflight = (step, actor)
                    pending_digest = sealed_digest = None
            elif kind == "PARTIAL_WRITE":
                if inflight != (step, actor) or pending_digest is not None:
                    deny(index, "PARTIAL_OUTSIDE_INFLIGHT")
                else:
                    pending_digest = digest
            elif kind == "SEAL":
                if inflight != (step, actor) or pending_digest != digest:
                    deny(index, "SEAL_WITHOUT_MATCHING_PARTIAL")
                else:
                    sealed_digest = digest
            elif kind == "COMMIT":
                if inflight != (step, actor) or sealed_digest != digest:
                    deny(index, "COMMIT_WITHOUT_MATCHING_SEAL")
                elif step in committed or step in retired_steps:
                    deny(index, "DUPLICATE_OPTIMIZER_COMMIT")
                else:
                    committed[step] = digest
                    inflight = None
                    pending_digest = sealed_digest = None
                    receipts.append({"event": kind, "step": step, "digest": digest,
                                     "index": index, "optimizer_executed": False})
            elif kind == "CLAIM_SUCCESS":
                if step not in committed or committed[step] != digest:
                    deny(index, "SUCCESS_WITHOUT_DURABLE_COMMIT")
                elif step in success_claims:
                    deny(index, "DUPLICATE_GENERATION_SUCCESS")
                else:
                    success_claims.add(step)
                    receipts.append({"event": kind, "step": step, "digest": digest,
                                     "index": index, "generation_authenticated": False})
            elif kind == "ROLLOVER":
                latest = max(committed, default=0)
                if (step not in committed or committed[step] != digest
                        or step >= latest or latest not in success_claims):
                    deny(index, "UNSAFE_CHECKPOINT_ROLLOVER")
                else:
                    retired_steps.add(step)
                    del committed[step]
                    receipts.append({"event": kind, "step": step,
                                     "index": index, "deletion_executed": False})

    reasons = tuple(sorted({row["reason"] for row in denials}))
    return {
        "schema": SCHEMA + ".receipt", "status": "SOURCE_ONLY_HOLD",
        "scenario_sha256": scenario_digest, "run_sha256": run_sha256,
        "receipts": receipts, "denials": denials, "denial_reasons": reasons,
        "committed_step": max((*committed, *retired_steps), default=0),
        "successful_generations": sorted(success_claims),
        "retired_steps": sorted(retired_steps),
        "final_owner": owner, "clock_quarantined": clock_quarantined,
        "max_simultaneous_shadow_owners": (
            1 if any(r["event"] == "ACQUIRE" for r in receipts) else 0),
        "physical_optimizer_steps_executed": 0,
        "authorizes_optimizer_start": False,
        "host_lease_authenticated": False,
        "fencing_host_authenticated": False,
        "checkpoint_bytes_verified": False,
        "authorizes_model_release": False,
        "distributed_gradient_compute_proven": False,
    }
