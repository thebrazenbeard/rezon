from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from http.client import HTTPConnection
from hashlib import sha256
import hmac
from tempfile import TemporaryDirectory
from threading import Event, Thread
from time import monotonic
from unittest.mock import patch
import json
import os
import secrets
import sqlite3

import pytest

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server


ADMIN = "super-secret-admin-token"
READ_ONLY = secrets.token_hex(32)
TOKENS = {"alice": "alice-secret-agent-token", "bob": "bob-secret-agent-token"}


class Integrator:
    agent_id = "integrator"

    def complete(self, messages):
        assert "Alice" in str(messages) and "Bob" in str(messages)
        return "Independent verification is still missing."


def _call(server, method, path, token=None, payload=None, extra_headers=None):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)
    if payload is not None:
        headers["Content-Type"] = "application/json"
        payload = json.dumps(payload).encode()
    try:
        conn.request(method, path, body=payload, headers=headers)
        response = conn.getresponse()
        body = response.read()
        return response.status, json.loads(body)
    finally:
        conn.close()


def _raw_call(server, method, path, authorization):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
    try:
        conn.request(method, path, headers={"Authorization": authorization})
        response = conn.getresponse()
        raw = response.read()
        return response.status, json.loads(raw), raw, response.getheader("X-Rezon-State-Proof")
    finally:
        conn.close()


def _state_credential(path, challenge, client_nonce):
    server_nonce = challenge["server_nonce"]
    issued_ms, epoch = challenge["issued_ms"], challenge["epoch"]
    context = (b"GET\0" + path.encode() + b"\0" + challenge["audience"].encode()
               + b"\0" + bytes.fromhex(server_nonce) + bytes.fromhex(client_nonce)
               + issued_ms.to_bytes(8, "big") + bytes.fromhex(epoch))
    preflight = hmac.new(bytes.fromhex(READ_ONLY),
        b"rezon-state-read/preflight/v2\0" + context, sha256).hexdigest()
    assert hmac.compare_digest(challenge["proof"], preflight)
    mac = hmac.new(bytes.fromhex(READ_ONLY),
        b"rezon-state-read/request/v2\0" + context, sha256).hexdigest()
    credential = f"Rezon-Read-HMAC {server_nonce}.{client_nonce}.{issued_ms}.{epoch}.{mac}"
    return credential, context


def _mac_read(server, path):
    client_nonce = secrets.token_hex(32)
    status, challenge = _call(server, "GET", "/v1/read-challenge", extra_headers={
        "X-Rezon-State-Path": path, "X-Rezon-Client-Nonce": client_nonce})
    assert status == 200 and challenge["expires_in_ms"] == 10000
    assert challenge["audience"] == f"127.0.0.1:{server.server_port}"
    credential, context = _state_credential(path, challenge, client_nonce)
    status, payload, raw, proof = _raw_call(server, "GET", path, credential)
    if status == 200:
        expected = hmac.new(bytes.fromhex(READ_ONLY),
            b"rezon-state-read/response/v2\0" + context + sha256(raw).digest(),
            sha256).hexdigest()
        assert proof is not None and hmac.compare_digest(expected, proof)
    return status, payload, credential


def test_read_mac_nonce_expires_and_is_single_use_under_concurrency():
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        server = make_server(store, ADMIN, TOKENS, read_token=READ_ONLY)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, created = _call(server, "POST", "/v1/episodes", ADMIN,
                                    {"prompt": "Nonce race", "agents": ["alice", "bob"]})
            assert status == 201
            path = f"/v1/episodes/{created['episode_id']}/state"
            for _ in range(300):
                status, _ = _call(server, "GET", "/v1/read-challenge",
                    extra_headers={"X-Rezon-State-Path": path,
                                   "X-Rezon-Client-Nonce": secrets.token_hex(32)})
                assert status == 200
            assert server.read_consumed == {}  # unauthenticated flood reserved no slots
            client_nonce = secrets.token_hex(32)
            status, challenge = _call(server, "GET", "/v1/read-challenge",
                                      extra_headers={"X-Rezon-State-Path": path,
                                                     "X-Rezon-Client-Nonce": client_nonce})
            assert status == 200
            stale, _ = _state_credential(path, challenge, client_nonce)
            with patch("rezon.collective_http.monotonic", return_value=monotonic() + 11):
                assert _raw_call(server, "GET", path, stale)[0] == 401

            client_nonce = secrets.token_hex(32)
            status, challenge = _call(server, "GET", "/v1/read-challenge",
                                      extra_headers={"X-Rezon-State-Path": path,
                                                     "X-Rezon-Client-Nonce": client_nonce})
            assert status == 200
            credential, _ = _state_credential(path, challenge, client_nonce)
            with ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(pool.map(lambda _: _raw_call(server, "GET", path, credential)[0],
                                          range(2)))
            assert sorted(responses) == [200, 401]
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_multiple_authenticated_remote_agents_share_state_then_synthesize():
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        server = make_server(store, ADMIN, TOKENS, Integrator())
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, created = _call(server, "POST", "/v1/episodes", ADMIN,
                                    {"prompt": "Determine the cause", "agents": ["alice", "bob"]})
            assert status == 201
            ep = created["episode_id"]
            assert _call(server, "GET", f"/v1/episodes/{ep}", TOKENS["alice"])[1]["prompt"] == "Determine the cause"
            assert _call(server, "GET", f"/v1/episodes/{ep}/state", TOKENS["alice"])[0] == 409

            def submit(agent):
                return _call(server, "POST", f"/v1/episodes/{ep}/answers", TOKENS[agent],
                             {"content": agent.title() + " finds an unresolved issue"})

            with ThreadPoolExecutor(max_workers=2) as pool:
                replies = list(pool.map(submit, ("alice", "bob")))
            assert all(status == 201 for status, _ in replies)
            assert _call(server, "POST", f"/v1/episodes/{ep}/answers", ADMIN,
                         {"content": "impostor"})[0] == 403
            assert _call(server, "POST", f"/v1/episodes/{ep}/answers", "incorrect-token",
                         {"content": "impostor"})[0] == 401
            status, state = _call(server, "GET", f"/v1/episodes/{ep}/state", TOKENS["alice"])
            assert status == 200 and state["complete"]
            assert {a["agent_id"] for a in state["answers"]} == {"alice", "bob"}
            assert _call(server, "POST", f"/v1/episodes/{ep}/reviews", TOKENS["alice"],
                         {"content": "Need measurement", "target_ids": ["answer:bob"]})[0] == 201
            status, synthesis = _call(server, "POST", f"/v1/episodes/{ep}/synthesize", ADMIN, {})
            assert status == 201
            assert synthesis["status"] == "unverified_model_synthesis"
            assert store.snapshot(ep).syntheses[-1].content == synthesis["content"]
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_server_rejects_insecure_credentials_and_non_loopback_binding():
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        with pytest.raises(ValueError):
            make_server(store, "short", TOKENS)
        with pytest.raises(ValueError):
            make_server(store, ADMIN, {"alice": ADMIN})
        with pytest.raises(ValueError):
            make_server(store, ADMIN, TOKENS, host="0.0.0.0")
        with pytest.raises(ValueError):
            make_server(store, ADMIN, {"alice": "pass with spaces 12345"})
        for invalid in (ADMIN, TOKENS["alice"], "short", "bad with spaces 123456", 12):
            with pytest.raises(ValueError):
                make_server(store, ADMIN, TOKENS, read_token=invalid)


def test_opt_in_state_reader_must_not_create_review_or_synthesize():
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        server = make_server(store, ADMIN, TOKENS, Integrator(), read_token=READ_ONLY)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, created = _call(server, "POST", "/v1/episodes", ADMIN,
                                    {"prompt": "Bound the view", "agents": ["alice", "bob"]})
            assert status == 201
            episode = created["episode_id"]
            state_url = f"/v1/episodes/{episode}/state"
            status, state, credential = _mac_read(server, state_url)
            assert status == 200 and state["episode_id"] == episode
            assert READ_ONLY not in credential
            assert _raw_call(server, "GET", state_url, credential)[0] == 401  # consumed challenge
            assert _raw_call(server, "GET", f"/v1/episodes/{episode}", credential)[0] == 401
            assert _raw_call(server, "GET", f"/v1/episodes/{episode}/tkal", credential)[0] == 401
            for path, payload in (
                ("/v1/episodes", {"prompt": "evil", "agents": ["alice", "bob"]}),
                (f"/v1/episodes/{episode}/answers", {"content": "forged"}),
                (f"/v1/episodes/{episode}/reviews", {"content": "forged", "target_ids": ["answer:bob"]}),
                (f"/v1/episodes/{episode}/synthesize", {}),
            ):
                # A stolen state-MAC header cannot be upgraded to a write.
                assert _raw_call(server, "POST", path, credential)[0] == 401
            assert store.snapshot(episode).answers == ()
            assert store.snapshot(episode).reviews == ()
            assert store.snapshot(episode).syntheses == ()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_no_reader_role_when_opt_in_token_absent():
    with TemporaryDirectory() as tmp:
        server = make_server(CollectiveStore(f"{tmp}/episodes.sqlite3"), ADMIN, TOKENS)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, created = _call(server, "POST", "/v1/episodes", ADMIN,
                                    {"prompt": "Default roles", "agents": ["alice", "bob"]})
            assert status == 201
            assert _call(server, "GET", "/v1/read-challenge")[0] == 404
            assert _call(server, "GET", f"/v1/episodes/{created['episode_id']}/state", READ_ONLY)[0] == 401
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_bad_roster_returns_client_error_and_server_remains_healthy():
    with TemporaryDirectory() as tmp:
        server = make_server(CollectiveStore(f"{tmp}/episodes.sqlite3"), ADMIN, TOKENS)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            assert _call(server, "POST", "/v1/episodes", ADMIN,
                         {"prompt": "Task", "agents": [{"alice": True}]})[0] == 400
            assert _call(server, "POST", "/v1/episodes", ADMIN,
                         {"prompt": "Task", "agents": ["alice", "alice"]})[0] == 400
            assert _call(server, "GET", "/healthz")[0] == 200
            assert _call(server, "POST", "/v1/episodes", ADMIN,
                         {"prompt": "Task", "agents": ["alice", "bob"]})[0] == 201
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_process_liveness_does_not_hide_unavailable_persistent_store():
    with TemporaryDirectory() as tmp:
        db = f"{tmp}/episodes.sqlite3"
        store = CollectiveStore(db)
        server = make_server(store, ADMIN, TOKENS, read_token=READ_ONLY)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, health = _call(server, "GET", "/healthz")
            assert status == 200 and health["status"] == "alive"
            assert _call(server, "GET", "/readyz")[0] == 401
            status, ready = _call(server, "GET", "/readyz", TOKENS["alice"])
            assert status == 200 and ready == {
                "service": "rezon-collective", "status": "ready"
            }

            # A gone SQLite file is not recreated by readiness. The server
            # remains alive, but must not claim its state store is ready.
            os.replace(db, f"{tmp}/moved.sqlite3")
            status, health = _call(server, "GET", "/healthz")
            assert status == 200 and health["status"] == "alive"
            status, unavailable = _call(server, "GET", "/readyz", TOKENS["alice"])
            assert status == 503 and unavailable == {
                "service": "rezon-collective", "status": "unavailable"
            }
            assert not os.path.exists(db)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_readiness_is_authenticated_and_fails_closed_on_wrong_schema():
    with TemporaryDirectory() as tmp:
        db = f"{tmp}/episodes.sqlite3"
        store = CollectiveStore(db)
        server = make_server(store, ADMIN, TOKENS, read_token=READ_ONLY)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(store, "readable", side_effect=AssertionError("unauthorized DB probe")):
                assert _call(server, "GET", "/readyz")[0] == 401
                assert _call(server, "GET", "/readyz", "wrong-token")[0] == 401
                assert _call(server, "GET", "/readyz", READ_ONLY)[0] == 401
            assert _call(server, "GET", "/readyz", ADMIN)[0] == 200
            with patch.object(store, "readable", side_effect=OSError("private database path")):
                status, result = _call(server, "GET", "/readyz", TOKENS["alice"])
                assert status == 503 and result["status"] == "unavailable"
                assert "private" not in str(result)
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.execute("DROP TABLE syntheses")
            status, result = _call(server, "GET", "/readyz", TOKENS["bob"])
            assert status == 503 and result["status"] == "unavailable"
            assert not any(key in result for key in ("database", "path", "error"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_readiness_checks_enabled_tkal_tables():
    from rezon.tkal_network import TkalVirtualNetwork

    with TemporaryDirectory() as tmp:
        db = f"{tmp}/episodes.sqlite3"
        store = CollectiveStore(db)
        network = TkalVirtualNetwork(store)
        server = make_server(store, ADMIN, TOKENS, tkal_network=network)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            assert _call(server, "GET", "/readyz", TOKENS["alice"])[0] == 200
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.execute("DROP TABLE tkal_challenges")
            assert _call(server, "GET", "/readyz", TOKENS["alice"])[0] == 503
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_concurrent_readiness_only_starts_one_storage_probe():
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        server = make_server(store, ADMIN, TOKENS)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        started, release = Event(), Event()

        def held_probe(*, include_tkal):
            started.set()
            assert release.wait(3)
            return True

        try:
            with patch.object(store, "readable", side_effect=held_probe) as reader:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    first = pool.submit(_call, server, "GET", "/readyz", TOKENS["alice"])
                    try:
                        assert started.wait(3)
                        second_status, second_payload = _call(
                            server, "GET", "/readyz", TOKENS["bob"]
                        )
                        assert second_status == 503
                        assert second_payload["status"] == "unavailable"
                        assert reader.call_count == 1
                    finally:
                        release.set()
                    assert first.result(timeout=3)[0] == 200
        finally:
            release.set()
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_http_peer_review_rejects_self_and_mixed_targets_without_side_effects():
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        server = make_server(store, ADMIN, TOKENS)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, created = _call(server, "POST", "/v1/episodes", ADMIN,
                                    {"prompt": "Assess independent challenges",
                                     "agents": ["alice", "bob"]})
            assert status == 201
            ep = created["episode_id"]
            for agent in ("alice", "bob"):
                assert _call(server, "POST", f"/v1/episodes/{ep}/answers",
                             TOKENS[agent], {"content": f"Initial {agent} claim"})[0] == 201

            for targets in (["answer:alice"], ["answer:bob", "answer:alice"]):
                assert _call(server, "POST", f"/v1/episodes/{ep}/reviews",
                             TOKENS["alice"], {"content": "Not independent",
                                              "target_ids": targets})[0] == 400
            assert store.snapshot(ep).reviews == ()

            assert _call(server, "POST", f"/v1/episodes/{ep}/reviews",
                         TOKENS["alice"], {"content": "Specific challenge to Bob",
                                          "target_ids": ["answer:bob"]})[0] == 201
            assert store.snapshot(ep).reviews[0].target_ids == ("answer:bob",)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
