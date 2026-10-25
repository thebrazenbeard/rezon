"""Source-pinned, credential-free VN2 gateway preflight tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
from threading import Thread

import pytest

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "collective_state_read_preflight.py"
SPEC = importlib.util.spec_from_file_location("collective_state_read_preflight", SOURCE)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


def _head() -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True,
    ).strip()


def _server(tmp_path, read_token):
    store = CollectiveStore(tmp_path / "episodes.sqlite3")
    episode_id = store.create("Disposable preflight", ("alice", "bob"))
    server = make_server(
        store, "synthetic-admin-secret-at-least-16",
        {"alice": "synthetic-alice-secret-at-least-16",
         "bob": "synthetic-bob-secret-at-least-16"},
        read_token=read_token,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, episode_id


def test_real_v2_gateway_preflight_is_source_only(tmp_path):
    server, thread, episode_id = _server(tmp_path, "0123456789abcdef" * 4)
    try:
        result = preflight.qualify(ROOT, _head(), server.server_port, episode_id)
        assert result["status"] == "CHALLENGE_ONLY"
        assert result["source_revision_verified"] is True
        assert result["challenge_shape_valid"] is True
        assert result["authenticated_state_verified"] is False
        assert result["activation_authorized"] is False
        assert "proof" not in result
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_real_gateway_without_observer_credential_holds(tmp_path):
    server, thread, episode_id = _server(tmp_path, None)
    try:
        result = preflight.qualify(ROOT, _head(), server.server_port, episode_id)
        assert result["status"] == "HOLD"
        assert result["challenge_shape_valid"] is False
        assert result["http_status"] == 404
        assert result["activation_authorized"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_wrong_revision_never_contacts_gateway(monkeypatch):
    def would_contact(*_args, **_kwargs):
        raise AssertionError("source mismatch must stop before any network probe")

    monkeypatch.setattr(preflight, "probe_challenge", would_contact)
    result = preflight.qualify(ROOT, "f" * 40, 18765, "collective-" + "a" * 32)
    assert result["status"] == "HOLD"
    assert result["source_revision_verified"] is False
    assert result["http_status"] is None


def test_checkout_path_must_be_exact_git_root():
    assert preflight.source_revision_verified(ROOT, _head()) is True
    assert preflight.source_revision_verified(ROOT / "src", _head()) is False
    assert preflight.source_revision_verified(ROOT / "tests", _head()) is False


@pytest.mark.parametrize("episode,port", [
    ("collective-" + "a" * 31, 18765),
    ("collective-" + "A" * 32, 18765),
    ("collective-" + "a" * 32, 0),
    ("collective-" + "a" * 32, 65536),
])
def test_invalid_inputs_rejected_without_probe(episode, port):
    with pytest.raises(ValueError):
        preflight.qualify(ROOT, _head(), port, episode)


def test_malformed_or_redirected_challenge_rejected():
    episode = "collective-" + "a" * 32
    nonce = "f" * 64
    for wire in (
        b"HTTP/1.1 302 Found\r\nLocation: http://example.com\r\nContent-Length: 0\r\n\r\n",
        b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nContent-Length: 0\r\n\r\n",
        b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\n",
    ):
        assert preflight.validate_response(wire, 18765, episode, nonce)[0] is False


def test_ambiguous_duplicate_challenge_fields_rejected():
    episode = "collective-" + "a" * 32
    nonce = "f" * 64
    body = json.dumps({
        "server_nonce": "1" * 64, "epoch": "2" * 32,
        "proof": "3" * 64, "issued_ms": 12345, "expires_in_ms": 10000,
        "state_path": f"/v1/episodes/{episode}/state",
        "client_nonce": nonce, "audience": "127.0.0.1:18765",
    }, separators=(",", ":")).replace(
        '"epoch":"' + "2" * 32 + '"',
        '"epoch":"' + "2" * 32 + '","epoch":"' + "2" * 32 + '"',
    ).encode("utf-8")
    wire = (b"HTTP/1.0 200 OK\r\nContent-Length: " + str(len(body)).encode()
            + b"\r\nContent-Type: application/json\r\n\r\n" + body)
    assert preflight.validate_response(wire, 18765, episode, nonce)[0] is False
