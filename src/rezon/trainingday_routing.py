"""Offline, non-authorizing assessment of TrainingDay host-routing declarations.

These inputs are claims supplied by a coordinator, *not* observations directly
authenticated by Executor. A passing assessment can never issue a lease or
authorize execution. Transport, physical host identity, workload occupancy and
lease enforcement remain separate, independent obligations of the host layer.
"""
from __future__ import annotations

import re

from .trainingday_pool import PoolError, _digest, validate_job


_DEVICE = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")
_WORKER_NAME = re.compile(r"[a-z][a-z0-9_]{1,31}\Z")
_LEASE = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
_MAX_HOSTS = 8
_MAX_OBSERVATION_AGE_SECONDS = 30
_MAX_LEASE_HORIZON_SECONDS = 120


def _valid_device(value: object) -> bool:
    return type(value) is str and _DEVICE.fullmatch(value) is not None


def _valid_time(value: object) -> bool:
    return type(value) is int and 0 <= value < 2**63


def assess_routing_declarations(
    job: dict,
    routes: dict,
    observations: list,
    leases: list,
    *,
    now_unix: int,
    max_age_seconds: int = 30,
) -> dict:
    """Compare *untrusted* local declarations for conflicts; never dispatch.

    A retry must be independently reevaluated with a fresh observation and
    host-enforced lease. The result is informational, including when clean.
    """
    validate_job(job)
    if (not _valid_time(now_unix) or type(max_age_seconds) is not int
            or not 1 <= max_age_seconds <= _MAX_OBSERVATION_AGE_SECONDS):
        raise PoolError("routing assessment clock/age bound invalid")
    if (type(routes) is not dict or len(routes) > _MAX_HOSTS
            or any(type(worker) is not str or not _WORKER_NAME.fullmatch(worker)
                   or not _valid_device(device)
                   for worker, device in routes.items())):
        raise PoolError("routing declaration malformed or unbounded")
    if (type(observations) is not list or type(leases) is not list
            or len(observations) > _MAX_HOSTS or len(leases) > _MAX_HOSTS):
        raise PoolError("host declaration list malformed or unbounded")

    blockers: set[str] = set()
    workers = set(job["workers"])
    if (set(routes) != workers or any(type(worker) is not str or not _valid_device(device)
                                      for worker, device in routes.items())):
        blockers.add("WORKER_ROUTE_INCOMPLETE")
    valid_routes = {worker: device for worker, device in routes.items()
                    if worker in workers and _valid_device(device)}
    if len(set(valid_routes.values())) != len(valid_routes):
        blockers.add("DEVICE_ROUTE_COLLISION")

    by_device: dict[str, dict] = {}
    for row in observations:
        if (type(row) is not dict or set(row) != {
                "device", "connected", "execution_active", "observed_at_unix"}
                or not _valid_device(row["device"])
                or type(row["connected"]) is not bool
                or type(row["execution_active"]) is not int
                or not 0 <= row["execution_active"] <= 100_000
                or not _valid_time(row["observed_at_unix"])):
            raise PoolError("host observation declaration malformed")
        device = row["device"]
        if device in by_device:
            blockers.add("HOST_OBSERVATION_DUPLICATE")
        by_device[device] = row
    if set(by_device) != set(valid_routes.values()):
        blockers.add("HOST_OBSERVATION_INCOMPLETE")
    for device in valid_routes.values():
        row = by_device.get(device)
        if row is None:
            continue
        if not row["connected"]:
            blockers.add("HOST_DISCONNECTED")
        if row["execution_active"] != 0:
            blockers.add("HOST_WORKLOAD_OCCUPIED")
        if not 0 <= now_unix - row["observed_at_unix"] <= max_age_seconds:
            blockers.add("HOST_OBSERVATION_STALE")

    lease_ids: set[str] = set()
    lease_workers: set[str] = set()
    lease_devices: set[str] = set()
    for row in leases:
        if (type(row) is not dict or set(row) != {
                "device", "worker", "lease_id", "expires_at_unix"}
                or not _valid_device(row["device"])
                or type(row["worker"]) is not str
                or _WORKER_NAME.fullmatch(row["worker"]) is None
                or type(row["lease_id"]) is not str
                or _LEASE.fullmatch(row["lease_id"]) is None
                or not _valid_time(row["expires_at_unix"])):
            raise PoolError("logical lease declaration malformed")
        if row["lease_id"] in lease_ids:
            blockers.add("LEASE_ID_COLLISION")
        if row["worker"] in lease_workers or row["device"] in lease_devices:
            blockers.add("LEASE_ROUTE_COLLISION")
        lease_ids.add(row["lease_id"])
        lease_workers.add(row["worker"])
        lease_devices.add(row["device"])
        if routes.get(row["worker"]) != row["device"]:
            blockers.add("LEASE_ROUTE_MISMATCH")
        if row["expires_at_unix"] <= now_unix:
            blockers.add("LEASE_EXPIRED")
        if row["expires_at_unix"] - now_unix > _MAX_LEASE_HORIZON_SECONDS:
            blockers.add("LEASE_HORIZON_TOO_LONG")
    if lease_workers != workers or lease_devices != set(valid_routes.values()):
        blockers.add("LEASE_ROUTE_INCOMPLETE")

    result = {
        "schema": "rezon.trainingday.routing-assessment.v2",
        "job_sha256": job["job_sha256"],
        "assessed_at_unix": now_unix,
        "max_age_seconds": max_age_seconds,
        "status": "HOLD_HOST_DECLARATION_CONFLICT" if blockers else "DECLARATION_CONSISTENT_NOT_AUTHORIZED",
        "blockers": sorted(blockers),
        "dispatch_authorized": False,
        "host_lease_authenticated": False,
        "shared_gradient_computation_proven": False,
    }
    # Bind the *actual untrusted declarations*, not just job identity/status.
    # Sorting unordered rows makes a transport reorder hash-equivalent while
    # retaining duplicate rows and every asserted observation/lease field.
    evidence = {
        "result": result,
        "routes": dict(sorted(routes.items())),
        "observations": sorted(observations, key=lambda row: (
            row["device"], row["observed_at_unix"], row["connected"],
            row["execution_active"],
        )),
        "leases": sorted(leases, key=lambda row: (
            row["device"], row["worker"], row["lease_id"],
            row["expires_at_unix"],
        )),
    }
    result["assessment_sha256"] = _digest(evidence)
    return result
