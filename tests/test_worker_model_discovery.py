"""Read-only endpoint availability is not a distributed-host attestation."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
import time

import pytest

from rezon.providers import OpenAICompatibleModel, ProviderError


@contextmanager
def catalog_server(models, *, status=200, redirect=None, raw=None, drip=0):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.path, dict(self.headers)))
            if redirect is not None:
                self.send_response(302)
                self.send_header("Location", redirect)
                self.end_headers()
                return
            body = (json.dumps({"data": [{"id": model} for model in models]}).encode()
                    if raw is None else raw)
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if drip:
                for byte in body:
                    try:
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    time.sleep(drip)
            else:
                self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_catalog_probe_is_read_only_and_explicitly_unattested():
    with catalog_server(["model-a", "model-b"]) as (url, requests):
        candidate = OpenAICompatibleModel("vn1", "model-b", url, "private-test-key")
        receipt = candidate.probe_availability()
    assert receipt.agent_id == "vn1"
    assert receipt.model_id == "model-b"
    assert receipt.advertised is True
    assert receipt.evidence_class == "ENDPOINT_CATALOG_UNATTESTED"
    assert receipt.host_identity_verified is False
    assert receipt.inference_verified is False
    assert receipt.authority == "NONE"
    assert len(requests) == 1 and requests[0][0] == "/v1/models"
    assert requests[0][1]["Authorization"] == "Bearer private-test-key"
    assert "private-test-key" not in repr(receipt)


def test_catalog_probe_reports_absent_model_without_claiming_it_cannot_run():
    with catalog_server(["model-a"]) as (url, _requests):
        receipt = OpenAICompatibleModel("vn2", "model-b", url, "secret").probe_availability()
    assert receipt.advertised is False
    assert receipt.inference_verified is False


def test_catalog_probe_does_not_follow_bearer_redirect():
    with catalog_server(["model-a"]) as (destination_url, destination_requests):
        with catalog_server([], redirect=destination_url + "/models") as (url, _requests):
            with pytest.raises(ProviderError, match="catalog request failed"):
                OpenAICompatibleModel("lappy", "model-a", url, "secret").probe_availability()
    assert destination_requests == []


@pytest.mark.parametrize("raw", [
    b'{"data": [{"id":"a"}], "data": [{"id":"b"}]}',
    b'{"data": [{"id": 4}]}',
    b'{"data": [{"id": "a"}, {"id": "a"}]}',
    b'{"data": [{"id":"a"}]}garbage',
])
def test_catalog_probe_rejects_ambiguous_or_malformed_claims(raw):
    with catalog_server([], raw=raw) as (url, _requests):
        with pytest.raises(ProviderError):
            OpenAICompatibleModel("node", "model-a", url, "secret").probe_availability()


def test_catalog_probe_rejects_oversize_response_and_unbounded_timeout():
    with catalog_server([], raw=b"x" * 131073) as (url, _requests):
        worker = OpenAICompatibleModel("node", "model-a", url, "secret")
        with pytest.raises(ProviderError):
            worker.probe_availability()
        with pytest.raises(ValueError):
            worker.probe_availability(timeout_seconds=300)


def test_catalog_probe_refuses_ambient_proxy_and_never_sends_bearer(monkeypatch):
    token = "synthetic-secret-for-local-test"
    with catalog_server(["model-a"]) as (proxy_url, requests):
        monkeypatch.setenv("HTTP_PROXY", proxy_url.removesuffix("/v1"))
        monkeypatch.setenv("http_proxy", proxy_url.removesuffix("/v1"))
        monkeypatch.setenv("NO_PROXY", "")
        monkeypatch.setenv("no_proxy", "")
        unreachable = OpenAICompatibleModel(
            "worker", "model-a", "http://127.0.0.2:1/v1", token,
        )
        with pytest.raises(ProviderError):
            unreachable.probe_availability(timeout_seconds=0.5)
    assert requests == []


def test_catalog_probe_total_deadline_stops_slow_drip():
    with catalog_server([], drip=0.12) as (url, _requests):
        start = time.monotonic()
        with pytest.raises(ProviderError):
            OpenAICompatibleModel("worker", "model-a", url, "secret").probe_availability(
                timeout_seconds=0.3,
            )
        elapsed = time.monotonic() - start
    assert elapsed < 0.8, f"catalog consumed {elapsed:.2f}s beyond total deadline"


def test_catalog_probe_child_rejects_ambient_pythonpath_import_hijack(tmp_path, monkeypatch):
    fake_package = tmp_path / "rezon"
    fake_package.mkdir()
    (fake_package / "__init__.py").write_text("", encoding="utf-8")
    marker = tmp_path / "hijacked-child-ran"
    (fake_package / "_catalog_probe_child.py").write_text(
        "from pathlib import Path\n"
        + f"Path({str(marker)!r}).write_text('unsafe')\n"
        + "print('{\"advertised\":true}')\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    with catalog_server(["model-a"]) as (url, requests):
        receipt = OpenAICompatibleModel("worker", "model-a", url, "synthetic-key").probe_availability()
    assert receipt.advertised is True
    assert len(requests) == 1
    assert not marker.exists(), "child imported untrusted ambient PYTHONPATH package"
