"""Windows Job Object process tree containment with assignment before resume.

The host supplies an explicit executable, isolated environment and a separate
authenticated bounded IPC channel. No payload token or request content is
accepted via command-line arguments by this API. A source test is not a real
Windows service/Job Object attestation; physical host qualification is needed.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess
from pathlib import PureWindowsPath
from threading import Lock
from typing import Protocol


class HostJobUnavailable(RuntimeError):
    pass


class JobKernel(Protocol):
    def create_job(self) -> object: ...
    def apply_limits(self, job: object, *, process_count: int, memory_bytes: int) -> None: ...
    def create_suspended(self, executable: str, argv: tuple[str, ...],
                         env: dict[str, str], cwd: str) -> tuple[object, object]: ...
    def assign(self, job: object, process: object) -> None: ...
    def resume(self, thread: object) -> None: ...
    def terminate(self, process: object) -> None: ...
    def close(self, handle: object) -> None: ...


class JobChild:
    """Single close-capable owner for native Win32 handles.

    Native HANDLE values can be recycled after closing. Copying this wrapper
    would create a second owner of the *same* handle values, so all ordinary
    Python copying/serialization is rejected explicitly.
    """

    __slots__ = ("kernel", "job", "process", "thread", "closed", "_close_lock")

    def __init__(self, kernel: JobKernel, job: object, process: object, thread: object):
        self.kernel = kernel
        self.job = job
        self.process = process
        self.thread = thread
        self.closed = False
        self._close_lock = Lock()

    def __copy__(self):
        raise TypeError("native JobChild handles cannot be copied")

    def __deepcopy__(self, _memo):
        raise TypeError("native JobChild handles cannot be deep-copied")

    def __reduce_ex__(self, _protocol):
        raise TypeError("native JobChild handles cannot be serialized")

    def close(self) -> None:
        # A Win32 HANDLE can be reused immediately after CloseHandle. Hold the
        # per-child lock through every kernel close and state transition so two
        # callers cannot independently close an already-released handle value.
        with self._close_lock:
            if self.closed:
                return
            # KILL_ON_JOB_CLOSE: attempt the job handle first. Retain every
            # failed handle for retry; never claim teardown while one remains.
            failures: list[Exception] = []
            for name in ("job", "thread", "process"):
                handle = getattr(self, name)
                if handle is None:
                    continue
                try:
                    self.kernel.close(handle)
                except Exception as exc:
                    failures.append(exc)
                else:
                    setattr(self, name, None)
            self.closed = self.job is None and self.thread is None and self.process is None
            if failures:
                raise failures[0]

    def send_request(self, _request: bytes) -> None:
        """No unauthenticated or unbounded IPC is exposed by this launcher."""
        raise HostJobUnavailable("a separately qualified bounded host IPC channel is required")


@dataclass(frozen=True)
class WindowsJobFence:
    max_processes: int = 16
    max_process_memory_bytes: int = 1 << 30

    def launch(self, *, executable: str, args: tuple[str, ...],
               cwd: str, safe_env: dict[str, str]) -> JobChild:
        """Production entrypoint cannot receive a caller-controlled Win32 shim."""
        return self._launch_with_kernel(NativeWindowsKernel(), executable=executable,
                                        args=args, cwd=cwd, safe_env=safe_env)

    def _launch_with_kernel(self, kernel: JobKernel, *, executable: str, args: tuple[str, ...],
               cwd: str, safe_env: dict[str, str]) -> JobChild:
        # Strict admission: a host, not model arguments, chooses these bounds.
        if not 1 <= self.max_processes <= 64 or not 1 << 20 <= self.max_process_memory_bytes <= 1 << 32:
            raise HostJobUnavailable("invalid finite job limits")
        path = PureWindowsPath(executable)
        if not path.is_absolute() or path.suffix.lower() != ".exe":
            raise HostJobUnavailable("payload executable must be an absolute .exe")
        if not PureWindowsPath(cwd).is_absolute():
            raise HostJobUnavailable("working directory must be explicitly pinned")
        if any(not key or "\x00" in key or "=" in key or "\x00" in value
               for key, value in safe_env.items()):
            raise HostJobUnavailable("invalid, non-isolated environment")
        if any("\x00" in part for part in args):
            raise HostJobUnavailable("invalid command-line argument")
        job = process = thread = None
        try:
            job = kernel.create_job()
            kernel.apply_limits(job, process_count=self.max_processes,
                                memory_bytes=self.max_process_memory_bytes)
            process, thread = kernel.create_suspended(executable, args, safe_env, cwd)
            # Critical invariant: payload code has not executed before this.
            kernel.assign(job, process)
            kernel.resume(thread)
            return JobChild(kernel=kernel, job=job, process=process, thread=thread)
        except Exception as exc:
            if process is not None:
                try:
                    kernel.terminate(process)
                except Exception:
                    pass
            for handle in (job, thread, process):
                if handle is not None:
                    try:
                        kernel.close(handle)
                    except Exception:
                        pass
            raise HostJobUnavailable("Windows Job Object admission failed closed") from exc


class NativeWindowsKernel:
    """Direct Win32 API adapter; deliberately unavailable outside Windows."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise HostJobUnavailable("Windows kernel unavailable")
        # Import only on Windows. The structure declarations are ABI-sized with
        # wintypes.HANDLE and c_size_t for both 32-bit and 64-bit processes.
        import ctypes
        from ctypes import wintypes

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                        ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t),
                        ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in
                        ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                         "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                        ("IoInfo", IO_COUNTERS),
                        ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]

        class STARTUPINFOW(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR),
                        ("lpDesktop", wintypes.LPWSTR), ("lpTitle", wintypes.LPWSTR),
                        ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
                        ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
                        ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
                        ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                        ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
                        ("lpReserved2", ctypes.POINTER(ctypes.c_ubyte)),
                        ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE),
                        ("hStdError", wintypes.HANDLE)]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
                        ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

        self.ctypes = ctypes
        self.k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.Extended = JOBOBJECT_EXTENDED_LIMIT_INFORMATION
        self.Startup = STARTUPINFOW
        self.ProcessInfo = PROCESS_INFORMATION
        handle = wintypes.HANDLE
        self.k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.k32.CreateJobObjectW.restype = handle
        self.k32.SetInformationJobObject.argtypes = [handle, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.k32.SetInformationJobObject.restype = wintypes.BOOL
        self.k32.CreateProcessW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR,
                                            ctypes.c_void_p, ctypes.c_void_p, wintypes.BOOL,
                                            wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
                                            ctypes.POINTER(STARTUPINFOW),
                                            ctypes.POINTER(PROCESS_INFORMATION)]
        self.k32.CreateProcessW.restype = wintypes.BOOL
        self.k32.AssignProcessToJobObject.argtypes = [handle, handle]
        self.k32.AssignProcessToJobObject.restype = wintypes.BOOL
        self.k32.ResumeThread.argtypes = [handle]
        self.k32.ResumeThread.restype = wintypes.DWORD
        self.k32.TerminateProcess.argtypes = [handle, wintypes.UINT]
        self.k32.TerminateProcess.restype = wintypes.BOOL
        self.k32.CloseHandle.argtypes = [handle]
        self.k32.CloseHandle.restype = wintypes.BOOL

    def _check(self, ok: object, op: str) -> None:
        if not ok:
            raise HostJobUnavailable(f"{op} failed: Win32 {self.ctypes.get_last_error()}")

    def create_job(self) -> object:
        job = self.k32.CreateJobObjectW(None, None)
        self._check(job, "CreateJobObjectW")
        return job

    def apply_limits(self, job: object, *, process_count: int, memory_bytes: int) -> None:
        info = self.Extended()
        # kill-on-close, active process, per-process AND aggregate job memory
        info.BasicLimitInformation.LimitFlags = 0x2000 | 0x8 | 0x100 | 0x200
        info.BasicLimitInformation.ActiveProcessLimit = process_count
        info.ProcessMemoryLimit = memory_bytes
        info.JobMemoryLimit = memory_bytes * process_count
        self._check(self.k32.SetInformationJobObject(job, 9, self.ctypes.byref(info),
                                                    self.ctypes.sizeof(info)),
                    "SetInformationJobObject")

    def create_suspended(self, executable: str, argv: tuple[str, ...],
                         env: dict[str, str], cwd: str) -> tuple[object, object]:
        command = subprocess.list2cmdline([executable, *argv])
        mutable_cmd = self.ctypes.create_unicode_buffer(command)
        envblock = "\x00".join(f"{k}={v}" for k, v in sorted(env.items(), key=lambda item: item[0].upper())) + "\x00\x00"
        envptr = self.ctypes.create_unicode_buffer(envblock)
        startup = self.Startup()
        startup.cb = self.ctypes.sizeof(startup)
        info = self.ProcessInfo()
        flags = 0x4 | 0x400 | 0x08000000  # CREATE_SUSPENDED | UNICODE_ENV | NO_WINDOW
        self._check(self.k32.CreateProcessW(executable, mutable_cmd, None, None,
                                            False, flags, envptr, cwd,
                                            self.ctypes.byref(startup), self.ctypes.byref(info)),
                    "CreateProcessW suspended")
        return info.hProcess, info.hThread

    def assign(self, job: object, process: object) -> None:
        self._check(self.k32.AssignProcessToJobObject(job, process), "AssignProcessToJobObject")

    def resume(self, thread: object) -> None:
        if self.k32.ResumeThread(thread) == 0xFFFFFFFF:
            raise HostJobUnavailable("ResumeThread failed")

    def terminate(self, process: object) -> None:
        self._check(self.k32.TerminateProcess(process, 126), "TerminateProcess")

    def close(self, handle: object) -> None:
        self._check(self.k32.CloseHandle(handle), "CloseHandle")
