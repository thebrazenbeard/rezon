"""Subprocess launch-budget checks; no model endpoint or credentials."""

import io
import threading
import time

import pytest

from rezon import providers
from rezon._process_supervision import LaunchOutcomeUnknown, launch_bounded


def test_completion_blocked_popen_does_not_block_caller(monkeypatch):
    def delayed_failure(*args, **kwargs):
        time.sleep(0.28)
        raise OSError("fixture child did not start")

    monkeypatch.setattr(providers.subprocess, "Popen", delayed_failure)
    started = time.monotonic()
    with pytest.raises(providers.ProviderOutcomeUnknown):
        providers._request(
            "http://localhost:18000/v1/chat/completions",
            {"Authorization": "Bearer synthetic"},
            {"model": "fixture", "messages": []},
            0.05,
        )
    assert time.monotonic() - started < 0.20


def test_catalog_blocked_popen_does_not_block_caller(monkeypatch):
    def delayed_failure(*args, **kwargs):
        time.sleep(0.28)
        raise OSError("fixture child did not start")

    monkeypatch.setattr(providers.subprocess, "Popen", delayed_failure)
    model = providers.OpenAICompatibleModel("agent-fixture", "fixture", "http://localhost:18000", "synthetic")
    started = time.monotonic()
    with pytest.raises(providers.ProviderError):
        model.probe_availability(timeout_seconds=0.05)
    assert time.monotonic() - started < 0.20


def test_late_spawn_never_receives_request_bytes(monkeypatch):
    late = []

    class CaptureInput(io.BytesIO):
        def __init__(self):
            super().__init__()
            self.observed_writes = []

        def write(self, chunk):
            self.observed_writes.append(bytes(chunk))
            return super().write(chunk)

    class FakeProcess:
        def __init__(self):
            self.stdin = CaptureInput()
            self.stdout = io.BytesIO()
            self.pid = None
            self.returncode = None
            self.killed = False

        def kill(self):
            self.killed = True
            self.returncode = -9

        def poll(self):
            return self.returncode

        def wait(self, timeout=1):
            return self.returncode

    def late_spawn(*args, **kwargs):
        time.sleep(0.11)
        obj = FakeProcess()
        late.append(obj)
        return obj

    monkeypatch.setattr(providers.subprocess, "Popen", late_spawn)
    with pytest.raises(providers.ProviderOutcomeUnknown):
        providers._request(
            "http://localhost:18000/v1/chat/completions",
            {"Authorization": "Bearer synthetic"},
            {"model": "fixture", "messages": []},
            0.05,
        )
    time.sleep(0.14)
    assert len(late) == 1 and late[0].killed
    assert late[0].stdin.observed_writes == []


def test_at_most_eight_outstanding_blocked_launches(monkeypatch):
    release = threading.Event()
    launched = []

    def blocked_failure(*args, **kwargs):
        launched.append(1)
        release.wait(1)
        raise OSError("synthetic blocked launcher")

    monkeypatch.setattr(providers.subprocess, "Popen", blocked_failure)
    try:
        for _ in range(9):
            with pytest.raises(LaunchOutcomeUnknown):
                launch_bounded(["synthetic"], deadline=time.monotonic() + 0.01)
        assert len(launched) == 8
    finally:
        release.set()
