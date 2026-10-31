"""Source-only host process-custody contracts; not platform qualification."""

from __future__ import annotations

import copy
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from threading import Event
import time
import unittest
from unittest.mock import patch

from rezon._linux_host_cgroup import (
    HostContainmentUnavailable, LinuxCgroupFence, _popen_bounded,
)
from rezon._windows_host_job import HostJobUnavailable, NativeWindowsKernel, WindowsJobFence
from rezon.providers import (
    AnthropicModel, OpenAICompatibleModel, ProviderOutcomeUnknown,
    _communicate_bounded, _request,
)
from rezon._process_supervision import terminate_local_tree


class FakeJobKernel:
    def __init__(self, failure=None):
        self.failure = failure
        self.events = []

    def record(self, name, *args):
        self.events.append((name, *args))
        if name == self.failure:
            raise OSError("injected kernel failure")

    def create_job(self):
        self.record("create_job")
        return "job"

    def apply_limits(self, job, *, process_count, memory_bytes):
        self.record("limit", process_count, memory_bytes)

    def create_suspended(self, executable, argv, env, cwd):
        self.record("suspend")
        return "process", "thread"

    def assign(self, job, process):
        self.record("assign")

    def resume(self, thread):
        self.record("resume")

    def terminate(self, process):
        self.record("terminate")

    def close(self, handle):
        self.record("close", handle)


class JobSourceContracts(unittest.TestCase):
    def setUp(self):
        self.fence = WindowsJobFence(max_processes=4, max_process_memory_bytes=64 << 20)
        self.kwargs = dict(executable=r"C:\Rezon\provider.exe", args=(),
                           cwd=r"C:\Rezon\work", safe_env={"SystemRoot": r"C:\Windows"})

    def test_job_is_assigned_before_process_resumes(self):
        kernel = FakeJobKernel()
        child = self.fence._launch_with_kernel(kernel, **self.kwargs)
        self.assertEqual([event[0] for event in kernel.events],
                         ["create_job", "limit", "suspend", "assign", "resume"])
        child.close()
        self.assertEqual(kernel.events[-3:],
                         [("close", "job"), ("close", "thread"), ("close", "process")])

    def test_failed_job_assignment_never_resumes_payload(self):
        kernel = FakeJobKernel("assign")
        with self.assertRaises(HostJobUnavailable):
            self.fence._launch_with_kernel(kernel, **self.kwargs)
        names = [event[0] for event in kernel.events]
        self.assertNotIn("resume", names)
        self.assertLess(names.index("terminate"), names.index("close"))

    def test_job_child_cannot_duplicate_native_handle_ownership(self):
        kernel = FakeJobKernel()
        child = self.fence._launch_with_kernel(kernel, **self.kwargs)
        try:
            with self.assertRaises(TypeError):
                copy.copy(child)
            with self.assertRaises(TypeError):
                copy.deepcopy(child)
        finally:
            child.close()
        child.close()
        self.assertEqual(len([event for event in kernel.events if event[0] == "close"]), 3)

    def test_real_win32_kernel_never_implicitly_runs_on_linux(self):
        if sys.platform == "win32":
            self.skipTest("native Windows host qualification intentionally excluded")
        with self.assertRaises(HostJobUnavailable):
            NativeWindowsKernel()


class CgroupSourceContracts(unittest.TestCase):
    def make_unprovisioned(self):
        return LinuxCgroupFence(Path("/sys/fs/cgroup"), Path("/usr/bin/false"),
                                "0" * 64, 12345, 12345)

    def test_global_or_unprovisioned_cgroup_is_denied(self):
        with self.assertRaises(HostContainmentUnavailable):
            self.make_unprovisioned().validate()

    def test_native_helper_requires_atomic_cgroup_clone(self):
        helper = Path(__file__).resolve().parents[1] / "src/rezon/native/cgroup_clone3_helper.c"
        source = helper.read_text()
        self.assertIn("CLONE_INTO_CGROUP", source)
        self.assertIn("SYS_clone3", source)
        self.assertNotIn("cgroup.procs", source)
        if sys.platform != "linux" or not shutil.which("cc"):
            self.skipTest("native helper syntax check requires a Linux compiler")
        proc = subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                               "-fsyntax-only", str(helper)],
                              capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_timed_out_constructor_keeps_pass_fd_alive_until_worker_finishes(self):
        """Late Popen must never inherit a recycled unrelated descriptor."""
        started, unblock, checked = Event(), Event(), Event()
        ready_r, ready_w = os.pipe()
        observed: list[bool] = []

        def blocked_constructor(_command, **kwargs):
            self.assertEqual(kwargs["pass_fds"], (ready_w,))
            started.set()
            unblock.wait(1)
            try:
                os.fstat(ready_w)
                observed.append(True)
            except OSError:
                observed.append(False)
            finally:
                checked.set()
            raise OSError("simulated late constructor failure")

        try:
            with patch("rezon._linux_host_cgroup.subprocess.Popen",
                       side_effect=blocked_constructor):
                with self.assertRaises(HostContainmentUnavailable):
                    _popen_bounded(["/not/executed"], deadline=time.monotonic() + 0.05,
                                   late_cleanup=lambda _child: None,
                                   owned_fds=(ready_w,), pass_fds=(ready_w,))
                self.assertTrue(started.is_set())
                # The calling thread timed out, but the constructor still owns
                # the descriptor and may safely duplicate it once it resumes.
                os.fstat(ready_w)
                unblock.set()
                self.assertTrue(checked.wait(1))
                self.assertEqual(observed, [True])
        finally:
            unblock.set()
            os.close(ready_r)

    def test_launch_cancellation_closes_readiness_reader(self):
        """BaseException cancellation must not leak a readiness read end."""
        created: dict[str, int] = {}
        actual_pipe = os.pipe

        def record_pipe():
            read_fd, write_fd = actual_pipe()
            created.update(read=read_fd, write=write_fd)
            return read_fd, write_fd

        def interrupted_constructor(_command, **kwargs):
            # Simulate the launch worker releasing its exclusively owned FD
            # before cancellation escapes through the calling thread.
            os.close(kwargs["owned_fds"][0])
            raise KeyboardInterrupt("synthetic cancellation")

        with tempfile.TemporaryDirectory() as dirname:
            with patch.object(LinuxCgroupFence, "validate", return_value=None), \
                 patch("rezon._linux_host_cgroup.os.pipe", side_effect=record_pipe), \
                 patch("rezon._linux_host_cgroup._popen_bounded",
                       side_effect=interrupted_constructor):
                with self.assertRaises(KeyboardInterrupt):
                    self.make_unprovisioned().launch(
                        Path(sys.executable), (), deadline=time.monotonic() + 1,
                        cwd=Path(dirname))
        with self.assertRaises(OSError):
            os.fstat(created["read"])

    def test_cancellation_after_native_start_kills_unreturned_child(self):
        """A cancelled membership check must not strand a launched payload."""
        class FakeProc:
            stdin = stdout = stderr = None
            killed = False
            waited = False

            def kill(self):
                self.killed = True

            def wait(self, *, timeout):
                self.waited = True
                return 0

        child = FakeProc()
        killed: list[bool] = []

        def fake_constructor(_command, **kwargs):
            os.write(kwargs["owned_fds"][0], b"123\n")
            os.close(kwargs["owned_fds"][0])
            return child

        with tempfile.TemporaryDirectory() as dirname:
            with patch.object(LinuxCgroupFence, "validate", return_value=None), \
                 patch.object(LinuxCgroupFence, "_is_member",
                              side_effect=KeyboardInterrupt), \
                 patch.object(LinuxCgroupFence, "kill_leaf",
                              side_effect=lambda: killed.append(True)), \
                 patch("rezon._linux_host_cgroup._popen_bounded",
                       side_effect=fake_constructor):
                with self.assertRaises(KeyboardInterrupt):
                    self.make_unprovisioned().launch(
                        Path(sys.executable), (), deadline=time.monotonic() + 1,
                        cwd=Path(dirname))
        self.assertTrue(killed)
        self.assertTrue(child.killed)
        self.assertTrue(child.waited)

    def test_trusted_fence_optin_denies_before_network_dispatch(self):
        with self.assertRaises(ProviderOutcomeUnknown):
            _request("https://example.invalid/v1/chat/completions",
                     {"Authorization": "Bearer sample-not-a-real-secret"},
                     {"model": "test"}, 1,
                     host_process_fence=self.make_unprovisioned())

    def test_windows_job_without_qualified_ipc_cannot_dispatch(self):
        with self.assertRaises(ProviderOutcomeUnknown):
            _request("https://example.invalid/v1/chat/completions",
                     {"Authorization": "Bearer sample-not-a-real-secret"},
                     {"model": "test"}, 1,
                     host_process_fence=WindowsJobFence())

    def test_models_reject_forged_custody_shim(self):
        common = dict(agent_id="A", model="example", base_url="https://example.invalid",
                      api_key="redacted")
        with self.assertRaises(ValueError):
            OpenAICompatibleModel(**common, host_process_fence=object())
        with self.assertRaises(ValueError):
            AnthropicModel(**common, host_process_fence=object())

    def test_host_helper_stderr_flood_is_bounded_not_left_blocked(self):
        script = ("import os,sys; sys.stdin.buffer.read();"
                  "os.write(2,b'X'*65536);os.write(1,b'OK')")
        child = subprocess.Popen([sys.executable, "-u", "-c", script],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, start_new_session=True)
        try:
            with self.assertRaises(ProviderOutcomeUnknown):
                _communicate_bounded(child, b"request", time.monotonic() + 2)
        finally:
            terminate_local_tree(child)


if __name__ == "__main__":
    unittest.main()
