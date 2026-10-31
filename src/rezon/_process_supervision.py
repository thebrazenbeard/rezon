"""Conservative local subprocess launch custody, not host-level containment.

The launch custodian is deliberately separate from the request-writing thread:
an OS-blocked Popen must never overrun the caller's request deadline or obtain
serialized credentials after that deadline. POSIX process groups improve normal
cleanup but cannot contain descendants that create a new session; production
hosts must additionally enforce cgroup v2 or Windows Job Object containment.
"""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time

_LAUNCH_SLOTS = threading.BoundedSemaphore(8)


class LaunchOutcomeUnknown(RuntimeError):
    """A launch outcome is not proven before a deadline; fail closed."""


def terminate_local_tree(child: subprocess.Popen) -> None:
    """Best-effort local cleanup; never call this an OS custody boundary."""
    if os.name != "nt" and isinstance(getattr(child, "pid", None), int):
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            pass
    try:
        if child.poll() is None:
            child.kill()
    except OSError:
        pass
    try:
        child.wait(timeout=1)
    except (OSError, subprocess.TimeoutExpired):
        pass
    for stream in (getattr(child, "stdin", None), getattr(child, "stdout", None)):
        try:
            if stream is not None and not stream.closed:
                stream.close()
        except OSError:
            pass


def launch_bounded(args: list[str], *, deadline: float, **kwargs) -> subprocess.Popen:
    """Start a child without letting Popen hold the caller past the deadline.

    The custodian owns a child until it is synchronously handed to the caller.
    If the handoff is late, it kills/reaps the child and never exposes its pipes
    to request-writing code. At most eight launch threads may be blocked.
    """
    remaining = deadline - time.monotonic()
    if remaining <= 0 or not _LAUNCH_SLOTS.acquire(timeout=remaining):
        raise LaunchOutcomeUnknown("child launch deadline exceeded")

    if os.name != "nt":
        # A new group lets best-effort cleanup include ordinary descendants.
        kwargs = {**kwargs, "start_new_session": True}

    ready = threading.Event()
    accepted = threading.Event()
    mutex = threading.Lock()
    state: dict[str, object] = {"abandoned": False}

    def start() -> None:
        try:
            try:
                child = subprocess.Popen(args, **kwargs)
            except (OSError, RuntimeError, ValueError) as exc:
                with mutex:
                    state["error"] = exc
                    ready.set()
                return
            with mutex:
                if state["abandoned"] or time.monotonic() >= deadline:
                    # Keep ownership while marking handoff impossible.
                    late = True
                else:
                    state["child"] = child
                    late = False
                ready.set()
            if not late:
                # Parent confirms custody before the custodian relinquishes
                # it. A delayed parent can never resurrect an expired child.
                accepted.wait(max(0.0, deadline - time.monotonic()))
                with mutex:
                    late = not state.get("accepted", False)
            if late:
                terminate_local_tree(child)
        finally:
            _LAUNCH_SLOTS.release()

    worker = threading.Thread(target=start, daemon=True, name="rezon-spawn-custodian")
    try:
        worker.start()
    except BaseException:
        _LAUNCH_SLOTS.release()
        raise

    try:
        remaining = max(0.0, deadline - time.monotonic())
        arrived = ready.wait(remaining)
    except BaseException:
        with mutex:
            state["abandoned"] = True
            accepted.set()
        raise
    with mutex:
        if not arrived or time.monotonic() >= deadline:
            state["abandoned"] = True
            accepted.set()
            raise LaunchOutcomeUnknown("child launch deadline exceeded")
        if "error" in state:
            accepted.set()
            raise LaunchOutcomeUnknown("child launch unavailable") from None
        child = state.get("child")
        if child is None:
            accepted.set()
            raise LaunchOutcomeUnknown("child launch handoff unavailable")
        state["accepted"] = True
        accepted.set()
        return child
