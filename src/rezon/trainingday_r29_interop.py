"""R29 source-only three-plane TrainingDay protocol interoperability probe.

R25 inference receipts, R26 fake coordinator leases and R28 fake recovery
timelines are interpreted together. This deliberately proves *nothing* about
real identities, gradients, GPUs, or protected host and model state.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Callable

from .trainingday_receipt_custody import assess_synthetic_three_node_chain
from .trainingday_dual_coordinator_shadow import assess_two_coordinator_shadow
from .trainingday_r28_recovery_sim import (
    MAX_HOST_WITNESS_AGE_MS, simulate_recovery,
)


SCHEMA = "rezon.trainingday.r29-protocol-interoperability.v1"
MAX_ACK_EVENTS = 128
MAX_INPUT_BYTES = 2_000_000
MAX_TREE_NODES = 20_000
MAX_TREE_DEPTH = 40
MAX_CONTAINER_ITEMS = 2_048
MAX_ACK_DELAY_MS = 30_000
_NODES = frozenset(("lappy", "vn1", "vn2"))
_KINDS = frozenset(("ACK", "PROGRESS", "OPTIMIZER_CLAIM"))
_ACK_FIELDS = frozenset(("kind", "node", "receipt_sha256", "generation",
                         "epoch", "step", "mono_ms", "sequence"))
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_MAX_INT = 2**63 - 1


class InteropScenarioError(ValueError):
    """The untrusted synthetic cross-plane envelope is malformed."""


def _valid_int(value: object, *, positive: bool = False) -> bool:
    return (type(value) is int and value <= _MAX_INT
            and (value > 0 if positive else value >= 0))


def _recovery_node_blocker_at(events: list[dict], node: str,
                              ack_at: int) -> str | None:
    """Reconstruct R28's declared node availability and age *at ACK time*.

    A later TUNNEL_DOWN or STANDBY invalidates previously asserted witnesses;
    neither a past COMMIT nor a later reconnection retroactively authenticates
    an ACK issued in the offline interval. Same-tick faults take precedence
    because inter-stream ordering within one timestamp is not attested.
    """
    awake = False
    wake_at = -1
    connected = {n: False for n in _NODES}
    tunnel_at = {n: -1 for n in _NODES}
    resumed = {"vn1": False, "vn2": False}
    worker_at = {"vn1": -1, "vn2": -1}
    for event in events:
        if event["mono_ms"] > ack_at:
            break
        kind = event["kind"]
        if (event["mono_ms"] == ack_at
                and kind in ("WAKE", "TUNNEL_UP", "WORKER_RESUME")):
            # Two unauthenticated streams have no intra-tick ordering proof.
            # Only strictly earlier readiness declarations can support ACK;
            # same-timestamp STANDBY/TUNNEL_DOWN faults still take priority.
            continue
        if kind == "WAKE":
            awake = True
            wake_at = event["mono_ms"]
        elif kind in ("STANDBY", "TUNNEL_DOWN"):
            awake = False
            wake_at = -1
            connected = {n: False for n in _NODES}
            tunnel_at = {n: -1 for n in _NODES}
            resumed = {"vn1": False, "vn2": False}
            worker_at = {"vn1": -1, "vn2": -1}
        elif kind == "TUNNEL_UP":
            connected[event["node"]] = True
            tunnel_at[event["node"]] = event["mono_ms"]
        elif kind == "WORKER_RESUME":
            worker_node = event["node"]
            if awake and connected[worker_node]:
                resumed[worker_node] = True
                worker_at[worker_node] = event["mono_ms"]
    if not (awake and connected[node]
            and (node == "lappy" or resumed[node])):
        return "ACK_WITHOUT_LIVE_RECOVERY_WITNESS"
    witness_times = (wake_at, tunnel_at[node])
    if node != "lappy":
        witness_times += (worker_at[node],)
    if any(not 0 <= ack_at - time <= MAX_HOST_WITNESS_AGE_MS
           for time in witness_times):
        return "ACK_WITHOUT_FRESH_RECOVERY_WITNESS"
    return None


def _clone_exact_json_tree(value: object) -> object:
    """Build one detached plain-data clone while rejecting custom hooks.

    An attacker-controlled dict/list subclass can override `.items()` or
    `__iter__` and conceal raw entries during encoding. Recursively traverse
    *only* exact builtin dict/list and bounded exact JSON scalar values,
    returning separately owned plain containers BEFORE any JSON encoder or
    external callback. Never re-read a caller-owned tree afterward.
    """
    visited = 0
    characters = 0
    active: set[int] = set()

    def walk(item: object, depth: int) -> object:
        nonlocal visited, characters
        visited += 1
        if depth > MAX_TREE_DEPTH or visited > MAX_TREE_NODES:
            raise InteropScenarioError("oversized or deeply nested fixture")
        kind = type(item)
        if kind is str:
            characters += len(item)
            if characters > MAX_INPUT_BYTES:
                raise InteropScenarioError("oversized synthetic string content")
            return item
        if kind is int:
            if item.bit_length() > 63:
                raise InteropScenarioError("oversized synthetic integer")
            return item
        if kind is float:
            if not math.isfinite(item):
                raise InteropScenarioError("nonfinite synthetic number")
            return item
        if kind in (bool, type(None)):
            return item
        if kind not in (dict, list):
            raise InteropScenarioError("non-exact JSON type in synthetic fixture")
        if len(item) > MAX_CONTAINER_ITEMS or id(item) in active:
            raise InteropScenarioError("cyclic or oversized synthetic container")
        active.add(id(item))
        if kind is dict:
            cloned: dict = {}
            for key, nested in item.items():
                if type(key) is not str:
                    raise InteropScenarioError("non-string synthetic dictionary key")
                cloned[walk(key, depth + 1)] = walk(nested, depth + 1)
        else:
            cloned = [walk(nested, depth + 1) for nested in item]
        active.remove(id(item))
        return cloned

    return walk(value, 0)


def _snapshot(*, job: dict, corpus_claim: dict, routes: dict,
              receipts: list, lease_events: list, recovery_events: list,
              ack_events: list) -> dict:
    """Canonical detached snapshot of ALL caller-owned input before callbacks.

    Count and byte caps are applied before any untrusted verifier can mutate
    source declarations. Each included leaf is a JSON primitive, not an alias.
    """
    if (type(job) is not dict or type(corpus_claim) is not dict
            or type(routes) is not dict or type(receipts) is not list
            or type(lease_events) is not list or type(recovery_events) is not list
            or type(ack_events) is not list
            or len(receipts) > 12
            or not 1 <= len(lease_events) <= 128
            or not 1 <= len(recovery_events) <= 128
            or not 1 <= len(ack_events) <= MAX_ACK_EVENTS):
        raise InteropScenarioError("invalid or unbounded cross-plane fixture")
    original = {"job": job, "corpus_claim": corpus_claim, "routes": routes,
                "receipts": receipts, "lease_events": lease_events,
                "recovery_events": recovery_events, "ack_events": ack_events}
    # The *same traversal* both validates and detaches private data. No
    # caller-owned object is touched after this point, including at json.dumps.
    try:
        frozen_source = _clone_exact_json_tree(original)
    except RuntimeError as exc:
        raise InteropScenarioError("synthetic fixture mutated during snapshot") from exc
    ack_events = frozen_source["ack_events"]
    # All ACKs are checked before expensive cross-module interpretation.
    for event in ack_events:
        if (type(event) is not dict or len(event) != len(_ACK_FIELDS)
                or set(event) != _ACK_FIELDS or type(event["kind"]) is not str
                or event["kind"] not in _KINDS
                or type(event["node"]) is not str
                or event["node"] not in _NODES
                or type(event["receipt_sha256"]) is not str
                or _SHA.fullmatch(event["receipt_sha256"]) is None
                or any(not _valid_int(event[k], positive=True)
                       for k in ("generation", "epoch", "step", "sequence"))
                or not _valid_int(event["mono_ms"])):
            raise InteropScenarioError("invalid exact-field ACK envelope")
    try:
        # Bound the *complete* serialized envelope, not merely the event count.
        raw = json.dumps(frozen_source, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode("ascii")
        if len(raw) > MAX_INPUT_BYTES:
            raise InteropScenarioError("oversized synthetic envelope")
        return json.loads(raw)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        if isinstance(exc, InteropScenarioError):
            raise
        raise InteropScenarioError("noncanonical synthetic envelope") from exc


def assess_interop(
    run_sha256: str, job: dict, corpus_claim: dict, routes: dict,
    receipts: list, *, now_unix: int, lease_events: list,
    recovery_events: list, ack_events: list,
    verify_claim: Callable[[bytes, str, str], bool] | None = None,
) -> dict:
    """Compose R25/R26/R28 over one immutable-input synthetic snapshot.

    ACK transport delivery order is intentionally irrelevant to the content
    digest, while the ordering of host and recovery state transitions matters.
    No ACK or forged optimizer claim authorizes any physical operation.
    """
    if (type(run_sha256) is not str or _SHA.fullmatch(run_sha256) is None
            or not _valid_int(now_unix)):
        raise InteropScenarioError("invalid run identity or fixture clock")
    snap = _snapshot(job=job, corpus_claim=corpus_claim, routes=routes,
                     receipts=receipts, lease_events=lease_events,
                     recovery_events=recovery_events, ack_events=ack_events)
    custody = assess_synthetic_three_node_chain(
        snap["job"], snap["corpus_claim"], snap["routes"], snap["receipts"],
        now_unix=now_unix, verify_claim=verify_claim)
    lease = assess_two_coordinator_shadow(run_sha256, snap["lease_events"])
    recovery = simulate_recovery(run_sha256, snap["recovery_events"])

    faults: set[str] = set()
    if custody["blockers"] or not custody["source_level_chain_complete"]:
        faults.add("CUSTODY_BLOCKER")
    if lease["denials"]:
        faults.add("LEASE_DENIAL")
    if recovery["denials"]:
        faults.add("RECOVERY_DENIAL")
    if not recovery["successful_generations"]:
        faults.add("NO_DURABLE_SUCCESS")
    lease_owners = {(r["actor"], r["epoch"])
                    for r in lease["accepted_requests"]}
    recovery_owners = {(r["actor"], r["epoch"])
                       for r in recovery["receipts"] if r["event"] == "ACQUIRE"}
    if (not recovery_owners or not lease_owners
            or recovery_owners != lease_owners
            or lease["final_owner"] != recovery["final_owner"]):
        faults.add("CROSS_PLANE_OWNER_MISMATCH")

    receipt_nodes = {r["device"]: r["receipt_sha256"]
                     for r in snap["receipts"]}
    successful = set(recovery["successful_generations"])
    # An accepted synthetic COMMIT is still explicitly NOT an optimizer receipt.
    committed_rows = {
        r["step"]: snap["recovery_events"][r["index"]]
        for r in recovery["receipts"] if r["event"] == "COMMIT"
    }
    success_rows = {
        r["step"]: snap["recovery_events"][r["index"]]
        for r in recovery["receipts"] if r["event"] == "CLAIM_SUCCESS"
    }
    lease_starts = {(r["actor"], r["epoch"]): r["mono_ms"]
                    for r in lease["accepted_requests"]}
    # Historical, half-open time intervals preserve ACKs issued before a
    # later clean RELEASE. Removing an owner on RELEASE would incorrectly
    # invalidate earlier ACKs during the lease's valid window.
    lease_intervals: dict[tuple[str, int], list[int]] = {}
    accepted_starts = {(r["actor"], r["epoch"], r["mono_ms"])
                       for r in lease["accepted_requests"]}
    for row in snap["lease_events"]:
        identity = (row["actor"], row["epoch"])
        if (row["kind"] == "REQUEST"
                and (*identity, row["mono_ms"]) in accepted_starts):
            lease_intervals[identity] = [
                row["mono_ms"], row["mono_ms"] + row["ttl_ms"]]
        elif row["kind"] == "RENEW" and identity in lease_intervals:
            # Renewal acceptance must be established by R26: any R26 denial
            # already globally blocks all synchronization in this fixture.
            lease_intervals[identity][1] = row["mono_ms"] + row["ttl_ms"]
        elif row["kind"] == "RELEASE" and identity in lease_intervals:
            lease_intervals[identity][1] = min(
                lease_intervals[identity][1], row["mono_ms"])
    accepted: dict[int, set[str]] = {}
    seen: dict[tuple[str, int], dict] = {}
    for row in snap["ack_events"]:
        kind, node, generation = row["kind"], row["node"], row["generation"]
        if kind == "PROGRESS":
            faults.add("UNVERIFIED_PROGRESS")
            continue
        if kind == "OPTIMIZER_CLAIM":
            faults.add("UNVERIFIED_OPTIMIZER_CLAIM")
            continue
        identity = (node, row["sequence"])
        previous = seen.setdefault(identity, row)
        if previous is not row:
            faults.add("REPLAYED_ACK" if previous == row else "CONFLICTING_ACK_SEQUENCE")
            continue
        if receipt_nodes.get(node) != row["receipt_sha256"]:
            faults.add("UNSOLICITED_ACK")
            continue
        if (generation not in successful or generation not in committed_rows
                or generation not in success_rows):
            faults.add("GENERATION_NOT_COMMITTED")
            continue
        if row["step"] != generation:
            faults.add("ACK_STEP_GENERATION_CONFLICT")
            continue
        committed = committed_rows[generation]
        if (row["epoch"] != committed["epoch"]
                or (committed["actor"], committed["epoch"]) not in lease_owners):
            faults.add("FENCED_GENERATION_MISMATCH")
            continue
        if committed["mono_ms"] < lease_starts.get(
                (committed["actor"], committed["epoch"]), _MAX_INT):
            faults.add("COMMIT_PRECEDES_LEASE_START")
            continue
        # R25 inference receipts have job/corpus identity but not optimizer
        # generation identity. Later generation claims are unbound; no fake
        # ACK can silently promote those into demonstrated continuity.
        if generation != 1:
            faults.add("GENERATION_RECEIPT_UNBOUND")
            continue
        if row["mono_ms"] < committed["mono_ms"]:
            faults.add("ACK_BEFORE_GENERATION_COMMIT")
            continue
        if row["mono_ms"] <= success_rows[generation]["mono_ms"]:
            # R28 accepting a CLAIM_SUCCESS at a later time does not grant
            # provenance to an already-delivered ACK. Cross-stream ties have
            # no authenticated intra-tick order, so equality also fails.
            faults.add("ACK_NOT_AFTER_SUCCESS_CLAIM")
            continue
        if row["mono_ms"] - committed["mono_ms"] > MAX_ACK_DELAY_MS:
            faults.add("DELAYED_NODE_ACK")
            continue
        recovery_blocker = _recovery_node_blocker_at(
            snap["recovery_events"], node, row["mono_ms"])
        if recovery_blocker is not None:
            faults.add(recovery_blocker)
            continue
        if any(e["kind"] in ("STANDBY", "TUNNEL_DOWN")
               and committed["mono_ms"] <= e["mono_ms"] <= row["mono_ms"]
               for e in snap["recovery_events"]):
            # A later declared reconnect restores simulated availability,
            # not the unavailable authenticated buffer/ACK provenance.
            faults.add("ACK_SPANS_UNATTESTED_RECOVERY_FAULT")
            continue
        claimed_window = lease_intervals.get((committed["actor"],
                                              committed["epoch"]))
        if (claimed_window is None
                or not (claimed_window[0] <= row["mono_ms"] < claimed_window[1])):
            faults.add("ACK_AFTER_LEASE_EXPIRY")
            continue
        if node in accepted.setdefault(generation, set()):
            faults.add("DUPLICATE_NODE_ACK")
        else:
            accepted[generation].add(node)

    for generation in successful:
        if accepted.get(generation, set()) != _NODES:
            faults.add("MISSING_NODE_ACK")

    # Digest preserves host/recovery order, normalizes transport ACK ordering.
    digest_input = {"schema": SCHEMA, "run_sha256": run_sha256,
                    "now_unix": now_unix, "custody": custody["assessment_sha256"],
                    "lease": lease["scenario_sha256"],
                    "recovery": recovery["scenario_sha256"],
                    "ack_events": sorted(snap["ack_events"],
                                         key=lambda r: json.dumps(r, sort_keys=True))}
    digest = hashlib.sha256(json.dumps(
        digest_input, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False).encode("ascii")).hexdigest()
    return {
        "schema": SCHEMA + ".assessment", "status": "SOURCE_ONLY_HOLD",
        "run_sha256": run_sha256, "interop_sha256": digest,
        "custody_assessment_sha256": custody["assessment_sha256"],
        "lease_scenario_sha256": lease["scenario_sha256"],
        "recovery_scenario_sha256": recovery["scenario_sha256"],
        "fault_reasons": sorted(faults),
        "accepted_synthetic_ack_nodes": sorted({
            node for values in accepted.values() for node in values}),
        "source_level_synchronized_generations": (
            sorted(g for g, nodes in accepted.items() if nodes == _NODES)
            if not faults else []),
        "custody_blockers": custody["blockers"],
        "lease_denials": lease["denials"],
        "recovery_denial_reasons": list(recovery["denial_reasons"]),
        "actual_host_witnesses_verified": False,
        "host_lease_authenticated": False,
        "checkpoint_bytes_verified": False,
        "physical_optimizer_steps_executed": 0,
        "authorizes_optimizer_start": False,
        "authorizes_model_release": False,
        "distributed_gradients_proven": False,
    }
