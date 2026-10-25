"""Reject ambiguous singleton HTTP headers at the authenticated gateway."""

from http.client import HTTPConnection
import json
from tempfile import TemporaryDirectory
from threading import Thread

import pytest

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server


ADMIN = "super-secret-admin-token"
TOKENS = {"alice": "alice-secret-agent-token"}


def _with_duplicate_header(server, name, first, second, *, method="GET"):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
    payload = (json.dumps({"prompt": "Original", "agents": ["alice"]}).encode()
               if method == "POST" else None)
    try:
        conn.putrequest(method, "/v1/episodes" if method == "POST" else "/v1/episodes/collective-absent")
        if name != "Authorization":
            conn.putheader("Authorization", f"Bearer {ADMIN}")
        if method == "POST":
            if name != "Content-Type":
                conn.putheader("Content-Type", "application/json")
            if name != "Content-Length":
                conn.putheader("Content-Length", str(len(payload)))
        conn.putheader(name, first)
        conn.putheader(name, second)
        conn.endheaders(payload)
        response = conn.getresponse()
        return response.status, json.loads(response.read())
    finally:
        conn.close()


@pytest.mark.parametrize("header,first,second,expected", [
    ("Authorization", f"Bearer {ADMIN}", "Bearer untrusted", 401),
    ("Content-Length", "44", "44", 400),
    ("Content-Type", "application/json", "application/json", 400),
])
def test_conflicting_singleton_headers_are_rejected(header, first, second, expected):
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        server = make_server(store, ADMIN, TOKENS)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, _ = _with_duplicate_header(server, header, first, second,
                                               method="GET" if header == "Authorization" else "POST")
            assert status == expected
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def test_transfer_encoding_with_content_length_is_rejected():
    with TemporaryDirectory() as tmp:
        store = CollectiveStore(f"{tmp}/episodes.sqlite3")
        server = make_server(store, ADMIN, TOKENS)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
        payload = json.dumps({"prompt": "Original", "agents": ["alice"]}).encode()
        try:
            conn.putrequest("POST", "/v1/episodes")
            conn.putheader("Authorization", f"Bearer {ADMIN}")
            conn.putheader("Content-Type", "application/json")
            conn.putheader("Content-Length", str(len(payload)))
            conn.putheader("Transfer-Encoding", "chunked")
            conn.endheaders(payload)
            response = conn.getresponse()
            assert response.status == 400
            response.read()
        finally:
            conn.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
