from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from tempfile import TemporaryDirectory
from threading import Thread
import json

import pytest

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server


ADMIN = "super-secret-admin-token"
TOKENS = {"alice": "alice-secret-agent-token", "bob": "bob-secret-agent-token"}


class Integrator:
    agent_id = "integrator"

    def complete(self, messages):
        assert "Alice" in str(messages) and "Bob" in str(messages)
        return "Independent verification is still missing."


def _call(server, method, path, token=None, payload=None):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
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
