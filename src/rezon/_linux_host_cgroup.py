"""Linux cgroup-v2 atomic provider containment (host-provisioned, fail closed).

This module does not provision authority or create a cgroup. A protected host
service must supply an EXCLUSIVE delegated leaf, distinct payload identity,
and root-owned verified native clone3 helper. No `Popen` + `cgroup.procs` attach
fallback is ever attempted: such a sequence lets code run before containment.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import selectors
import stat
import subprocess
import sys
import threading
import time
from dataclasses import dataclass


class HostContainmentUnavailable(RuntimeError):
    """The host has not established an independently enforced process fence."""


class ProviderDispatchUnknown(RuntimeError):
    """Transport state may have changed; blindly reissuing a POST is unsafe."""


def _read_bounded(path: Path, limit: int = 128) -> str:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise HostContainmentUnavailable(f"oversized {path.name}")
    return raw.decode("ascii", errors="strict").strip()


def _finite_positive_limit(text: str, upper: int) -> int:
    if not text.isdecimal() or int(text) < 1 or int(text) > upper:
        raise HostContainmentUnavailable("required finite cgroup resource bound unavailable")
    return int(text)


def _cgroup2_mount(path: Path) -> Path | None:
    """Find the nearest cgroup2 mount, excluding unrelated bind-mount trees."""
    resolved = str(path.resolve(strict=True))
    best: Path | None = None
    with open("/proc/self/mountinfo", encoding="utf-8") as mounts:
        for line in mounts:
            lhs, separator, rhs = line.partition(" - ")
            if not separator or not rhs.startswith("cgroup2 "):
                continue
            fields = lhs.split()
            if len(fields) < 5:
                continue
            mount_point = fields[4].replace("\\040", " ")
            if resolved == mount_point or resolved.startswith(mount_point.rstrip("/") + "/"):
                if best is None or len(mount_point) > len(str(best)):
                    best = Path(mount_point)
    return best


_LAUNCH_CAPACITY = threading.BoundedSemaphore(8)


def _popen_bounded(command: list[str], *, deadline: float,
                   late_cleanup, owned_fds: tuple[int, ...] = (),
                   **kwargs) -> subprocess.Popen:
    """Bound Popen while its worker exclusively owns inherited descriptors.

    A timed-out caller must NEVER close an FD named by a still-blocked Popen
    worker's ``pass_fds``: the OS may reuse that number for an unrelated FD.
    Only the worker closes these descriptors once the constructor resolves.
    """
    def close_owned_fds() -> None:
        for fd in owned_fds:
            try:
                os.close(fd)
            except OSError:
                pass

    remaining = deadline - time.monotonic()
    if remaining <= 0 or not _LAUNCH_CAPACITY.acquire(timeout=remaining):
        close_owned_fds()
        raise HostContainmentUnavailable("bounded launch capacity unavailable")
    lock = threading.Lock()
    release_lock = threading.Lock()
    done = threading.Event()
    result: dict[str, object] = {"cancelled": False}
    released = False

    def release_permit_once() -> None:
        nonlocal released
        with release_lock:
            if not released:
                released = True
                _LAUNCH_CAPACITY.release()

    def worker() -> None:
        child = None
        try:
            child = subprocess.Popen(command, **kwargs)
            with lock:
                if not result["cancelled"]:
                    result["child"] = child
                    child = None
        except Exception:
            with lock:
                result["failed"] = True
        finally:
            try:
                if child is not None:
                    late_cleanup(child)
            finally:
                close_owned_fds()
                done.set()
                release_permit_once()

    thread = threading.Thread(target=worker, name="rezon-cgroup-launch", daemon=True)
    try:
        thread.start()
    except BaseException:
        # Thread creation can fail under resource exhaustion. The worker may
        # also have begun before a custom thread adapter reports failure;
        # cancel and clean any late child without double-releasing capacity.
        with lock:
            result["cancelled"] = True
            late = result.pop("child", None)
        try:
            if late is not None:
                late_cleanup(late)
        finally:
            # A thread can begin running and then its start() call can be
            # interrupted. In that case only the worker may release capacity:
            # releasing here while Popen remains active over-admits launches.
            if thread.ident is None:
                close_owned_fds()
                release_permit_once()
        raise
    try:
        completed = done.wait(max(0, deadline - time.monotonic()))
        if not completed:
            raise HostContainmentUnavailable("native launch exceeded deadline before request dispatch")
        child = result.get("child")
        if child is None:
            raise HostContainmentUnavailable("native launch failed before request dispatch")
        assert isinstance(child, subprocess.Popen)
        # The caller takes ownership only after every synchronous check has
        # completed. All failures/cancellations before this return are reaped.
        return child
    except BaseException:
        # The caller can be interrupted while the Popen worker is blocked or
        # after it has delivered a child but before ownership is returned.
        # Transfer every unreturned child to teardown, and mark late arrivals
        # cancelled so that ONLY the worker cleans those up on completion.
        with lock:
            result["cancelled"] = True
            late = result.pop("child", None)
        if late is not None:
            late_cleanup(late)
        raise


def _check_secure_ancestors(path: Path) -> None:
    """Prevent replacement through symlinked or group/world-writable parents."""
    current = path
    while current != current.parent:
        entry = current.lstat()
        if stat.S_ISLNK(entry.st_mode) or entry.st_mode & 0o022:
            raise HostContainmentUnavailable("path has an attacker-writable or symlink ancestor")
        current = current.parent


@dataclass(frozen=True)
class LinuxCgroupFence:
    leaf: Path
    helper: Path
    helper_sha256: str
    payload_uid: int
    payload_gid: int
    max_pids: int = 16
    max_memory_bytes: int = 1024 * 1024 * 1024

    def validate(self) -> None:
        if sys.platform != "linux":
            raise HostContainmentUnavailable("Linux cgroup-v2 containment unavailable")
        leaf = self.leaf
        mount = _cgroup2_mount(leaf) if leaf.is_absolute() else None
        if mount is None:
            raise HostContainmentUnavailable("untrusted cgroup leaf or mount")
        if leaf.resolve() == mount.resolve() or len(leaf.resolve().parts) < len(mount.resolve().parts) + 2:
            raise HostContainmentUnavailable("refusing broad cgroup target")
        if os.statvfs(leaf).f_flag & getattr(os, "ST_RDONLY", 1):
            raise HostContainmentUnavailable("cgroup mount is read-only")
        if self.payload_uid <= 0 or self.payload_gid <= 0 or self.payload_uid == os.geteuid():
            raise HostContainmentUnavailable("host and payload identities are not separated")
        leaf_stat = leaf.lstat()
        if not stat.S_ISDIR(leaf_stat.st_mode) or leaf_stat.st_uid == self.payload_uid:
            raise HostContainmentUnavailable("cgroup leaf writable by untrusted identities")
        _check_secure_ancestors(leaf)
        for item in ("cgroup.kill", "cgroup.procs", "cgroup.events", "pids.max", "memory.max"):
            if not (leaf / item).is_file():
                raise HostContainmentUnavailable(f"cgroup control missing: {item}")
        _finite_positive_limit(_read_bounded(leaf / "pids.max"), self.max_pids)
        _finite_positive_limit(_read_bounded(leaf / "memory.max"), self.max_memory_bytes)
        if _read_bounded(leaf / "cgroup.procs"):
            raise HostContainmentUnavailable("nonexclusive cgroup already has members")
        events = _read_bounded(leaf / "cgroup.events", 512).splitlines()
        if "populated 0" not in events:
            raise HostContainmentUnavailable("cgroup subtree is already populated")
        # An exclusive leaf must not contain child cgroups at reservation time.
        if any(entry.is_dir(follow_symlinks=False) for entry in os.scandir(leaf)):
            raise HostContainmentUnavailable("cgroup leaf contains nested unmanaged groups")

        helper_stat = self.helper.lstat()
        if not stat.S_ISREG(helper_stat.st_mode) or helper_stat.st_uid != 0:
            raise HostContainmentUnavailable("native launcher is not a root-owned file")
        if helper_stat.st_mode & 0o022 or not helper_stat.st_mode & 0o111:
            raise HostContainmentUnavailable("native launcher permissions are unsafe")
        if not self.helper.is_absolute() or len(self.helper_sha256) != 64:
            raise HostContainmentUnavailable("native launcher pin is invalid")
        _check_secure_ancestors(self.helper)
        digest = hashlib.sha256(self.helper.read_bytes()).hexdigest()
        if digest != self.helper_sha256:
            raise HostContainmentUnavailable("native launcher digest mismatch")

    def kill_leaf(self) -> None:
        """Kill ONLY the preprovisioned exclusive cgroup; no process-name kill."""
        with (self.leaf / "cgroup.kill").open("wb", buffering=0) as signal_file:
            signal_file.write(b"1\n")

    def _is_member(self, pid: int) -> bool:
        return str(pid) in _read_bounded(self.leaf / "cgroup.procs", 65536).splitlines()

    def launch(self, executable: Path, arguments: tuple[str, ...], *, deadline: float,
               cwd: Path) -> "ContainedChild":
        """Return only after kernel cgroup placement and local membership readback.

        No request bytes or credentials are supplied at launch. Other layers
        must bound the `Popen` constructor itself; this one rejects on deadline.
        """
        self.validate()
        if not executable.is_absolute() or not executable.is_file():
            raise HostContainmentUnavailable("no pinned absolute payload executable")
        if not cwd.is_absolute() or not cwd.is_dir() or cwd.is_symlink():
            raise HostContainmentUnavailable("isolated child working directory unavailable")
        if time.monotonic() >= deadline:
            raise HostContainmentUnavailable("deadline elapsed before launch")
        ready_r, ready_w = os.pipe()
        env = {"PATH": "/usr/bin:/bin", "LANG": "C", "REZON_READY_FD": str(ready_w)}
        command = [str(self.helper), str(self.leaf), str(self.payload_uid),
                   str(self.payload_gid), "--", str(executable), *arguments]
        def _late_cleanup(child: subprocess.Popen) -> None:
            try:
                self.kill_leaf()
            except OSError:
                pass  # Never pretend a failed kill was successful supervision.
            try:
                child.kill()
            except OSError:
                pass
            try:
                child.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
            for stream in (child.stdin, child.stdout, child.stderr):
                if stream is not None and not stream.closed:
                    stream.close()

        try:
            proc = _popen_bounded(command, deadline=deadline, late_cleanup=_late_cleanup,
                                  owned_fds=(ready_w,),
                                  env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, pass_fds=(ready_w,),
                                  close_fds=True, start_new_session=True, cwd=str(cwd))
        except BaseException as exc:
            # Cancellation/KeyboardInterrupt must not leak the parent's
            # readiness reader. The writer remains exclusively under bounded
            # worker custody; closing it here could recycle a live pass_fd.
            os.close(ready_r)
            if not isinstance(exc, Exception):
                raise
            raise HostContainmentUnavailable("native launcher did not start within deadline") from exc
        try:
            with os.fdopen(ready_r, "rb", buffering=0) as ready_stream:
                with selectors.DefaultSelector() as selector:
                    selector.register(ready_stream, selectors.EVENT_READ)
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not selector.select(remaining):
                        raise HostContainmentUnavailable("no timely kernel-placement witness")
                    ready_line = ready_stream.read(64)
                if not re.fullmatch(rb"[1-9][0-9]{0,18}\n", ready_line):
                    raise HostContainmentUnavailable("native launcher placement witness invalid")
                pid = int(ready_line)
            if not self._is_member(pid):
                raise HostContainmentUnavailable("payload not independently visible in cgroup")
            return ContainedChild(fence=self, proc=proc, pid=pid)
        except BaseException:
            # A cancellation during placement readback is just as dangerous
            # as an ordinary validation error: the child was already started
            # and must not survive a caller that never received custody.
            try:
                self.kill_leaf()
            finally:
                proc.kill()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    pass
            raise


@dataclass
class ContainedChild:
    fence: LinuxCgroupFence
    proc: subprocess.Popen
    pid: int

    def close(self) -> None:
        try:
            self.fence.kill_leaf()
        finally:
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=2)
            finally:
                for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
                    if stream is not None and not stream.closed:
                        stream.close()

    def request_once(self, request: bytes, *, deadline: float,
                     max_request: int = 1 << 20, max_output: int = 1 << 20) -> bytes:
        """One bounded request only; uncertain outcomes NEVER authorize replay."""
        if len(request) > max_request or time.monotonic() >= deadline:
            self.close()
            raise HostContainmentUnavailable("request exceeds admission bounds")
        if not self.fence._is_member(self.pid):
            self.close()
            raise ProviderDispatchUnknown("provider containment changed before dispatch")
        try:
            # Concurrent, strictly bounded nonblocking I/O prevents deadlock
            # when a worker writes stdout/stderr before reading its request.
            assert self.proc.stdin is not None and self.proc.stdout is not None
            assert self.proc.stderr is not None
            streams = {"stdin": self.proc.stdin, "stdout": self.proc.stdout,
                       "stderr": self.proc.stderr}
            for stream in streams.values():
                os.set_blocking(stream.fileno(), False)
            sent = 0
            chunks: list[bytes] = []
            retained = 0
            stderr_retained = 0
            with selectors.DefaultSelector() as selector:
                if request:
                    selector.register(streams["stdin"], selectors.EVENT_WRITE, "stdin")
                else:
                    streams["stdin"].close()
                selector.register(streams["stdout"], selectors.EVENT_READ, "stdout")
                selector.register(streams["stderr"], selectors.EVENT_READ, "stderr")
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise ProviderDispatchUnknown("provider request deadline elapsed")
                    selected = selector.select(remaining)
                    if not selected:
                        raise ProviderDispatchUnknown("provider channel stalled")
                    for key, _mask in selected:
                        mode = key.data
                        stream = key.fileobj
                        if mode == "stdin":
                            try:
                                written = os.write(stream.fileno(), request[sent:sent + 65536])
                            except BlockingIOError:
                                continue
                            sent += written
                            if sent == len(request):
                                selector.unregister(stream)
                                stream.close()
                        else:
                            try:
                                block = os.read(stream.fileno(), 65536)
                            except BlockingIOError:
                                continue
                            if not block:
                                selector.unregister(stream)
                                stream.close()
                            elif mode == "stdout":
                                retained += len(block)
                                if retained > max_output:
                                    raise ProviderDispatchUnknown("provider output exceeded admission cap")
                                chunks.append(block)
                            else:
                                stderr_retained += len(block)
                                if stderr_retained > 4096:
                                    raise ProviderDispatchUnknown("provider diagnostics exceeded admission cap")
            if self.proc.wait(timeout=max(0, deadline - time.monotonic())) != 0:
                raise ProviderDispatchUnknown("provider exit outcome uncertain")
            return b"".join(chunks)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProviderDispatchUnknown("provider may have received request; do not retry") from exc
        finally:
            self.close()
