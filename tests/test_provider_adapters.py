from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from contextlib import contextmanager

import pytest

from rezon.collective import CollectiveStore
from rezon.collective_cli import main, _model
from rezon.providers import AnthropicModel, OpenAICompatibleModel, ProviderError


@contextmanager
def fake_ambient_proxy():
    seen = []

    class InterceptHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            seen.append((self.path, dict(self.headers), body))
            if self.path.endswith("/chat/completions"):
                payload = {"choices": [{"message": {"content": "forged proxy completion"}}]}
            else:
                payload = {"content": [{"type": "text", "text": "forged proxy answer"}]}
            encoded = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), InterceptHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", seen
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_completion_never_sends_credentials_via_ambient_proxy(monkeypatch, provider):
    secret = "synthetic-completion-credential"
    with fake_ambient_proxy() as (proxy_url, seen):
        monkeypatch.setenv("HTTP_PROXY", proxy_url)
        monkeypatch.setenv("http_proxy", proxy_url)
        monkeypatch.setenv("NO_PROXY", "")
        monkeypatch.setenv("no_proxy", "")
        cls = OpenAICompatibleModel if provider == "openai" else AnthropicModel
        adapter = cls("worker", "test-model", "http://127.0.0.2:1/v1", secret)
        with pytest.raises(ProviderError):
            adapter.complete(({"role": "user", "content": "hello"},))
    assert seen == [], "ambient proxy received an authenticated completion request"


def test_completion_reaches_exact_local_origin_even_when_proxy_is_set(monkeypatch):
    ProviderHandler.requests = []
    origin = ThreadingHTTPServer(("127.0.0.1", 0), ProviderHandler)
    thread = Thread(target=origin.serve_forever, daemon=True)
    thread.start()
    try:
        with fake_ambient_proxy() as (proxy_url, proxy_seen):
            monkeypatch.setenv("HTTP_PROXY", proxy_url)
            monkeypatch.setenv("http_proxy", proxy_url)
            monkeypatch.setenv("NO_PROXY", "")
            monkeypatch.setenv("no_proxy", "")
            model = OpenAICompatibleModel(
                "worker", "test-model", f"http://127.0.0.1:{origin.server_port}", "secret",
            )
            assert model.complete(({"role": "user", "content": "hello"},)) == "OpenAI style response"
        assert proxy_seen == []
        assert len(ProviderHandler.requests) == 1
    finally:
        origin.shutdown()
        origin.server_close()
        thread.join(timeout=3)


class ProviderHandler(BaseHTTPRequestHandler):
    requests = []

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        self.requests.append((self.path, dict(self.headers), json.loads(data)))
        if self.path == "/v1/chat/completions":
            response = {"choices": [{"message": {"content": "OpenAI style response"}}]}
        elif self.path == "/v1/messages":
            response = {"content": [{"type": "text", "text": "Anthropic style response"}]}
        else:
            self.send_error(404)
            return
        payload = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        return


def test_two_provider_protocols_work_over_real_local_http():
    ProviderHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProviderHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        openai = OpenAICompatibleModel("gpt", "my-model", base_url, "key-one")
        anthropic = AnthropicModel("claude", "my-claude", base_url, "key-two")
        messages = ({"role": "user", "content": "Reason about X"},)
        assert openai.complete(messages) == "OpenAI style response"
        assert anthropic.complete(messages) == "Anthropic style response"
        assert ProviderHandler.requests[0][2]["model"] == "my-model"
        assert ProviderHandler.requests[0][1]["Authorization"] == "Bearer key-one"
        assert ProviderHandler.requests[1][2]["model"] == "my-claude"
        assert {k.lower(): v for k, v in ProviderHandler.requests[1][1].items()}["x-api-key"] == "key-two"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_provider_rejects_non_tls_remote_endpoint_unless_explicitly_allowed():
    with pytest.raises(ValueError):
        OpenAICompatibleModel("remote", "model", "http://example.com", "secret")
    with pytest.raises(ValueError):
        AnthropicModel("remote", "model", "http://192.168.1.71:8000", "secret")
    assert OpenAICompatibleModel("lan", "model", "http://192.168.1.71:8000", "secret",
                                 allow_insecure_http=True).agent_id == "lan"


def test_provider_rejects_invalid_response_without_promoting_it_to_reasoning():
    class BadHandler(ProviderHandler):
        def do_POST(self):
            body = b'{"choices": []}'
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), BadHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter = OpenAICompatibleModel("a", "model", f"http://127.0.0.1:{server.server_port}", "secret")
        with pytest.raises(ProviderError):
            adapter.complete(({"role": "user", "content": "x"},))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_cli_reaches_two_provider_protocols_and_persists_integrated_result(tmp_path, monkeypatch, capsys):
    ProviderHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProviderHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/v1"
        monkeypatch.setenv("MOCK_KEY_A", "a-private-token")
        monkeypatch.setenv("MOCK_KEY_B", "b-private-token")
        specs = [
            {"provider": "openai_compatible", "agent_id": "a", "model": "model-a",
             "base_url": url, "api_key_env": "MOCK_KEY_A"},
            {"provider": "anthropic", "agent_id": "b", "model": "model-b",
             "base_url": url, "api_key_env": "MOCK_KEY_B"},
        ]
        pool = tmp_path / "pool.json"
        pool.write_text(json.dumps({"models": specs}), encoding="utf-8")
        integrator = tmp_path / "integrator.json"
        integrator.write_text(json.dumps({**specs[0], "agent_id": "synthesizer"}), encoding="utf-8")
        database = tmp_path / "episodes.sqlite3"
        code = main(["run", "--db", str(database), "--prompt", "Consider alternatives",
                     "--models-config", str(pool), "--integrator-config", str(integrator)])
        result = json.loads(capsys.readouterr().out)
        assert code == 0 and result["complete"]
        assert result["worker_results"] == {"a": "submitted", "b": "submitted"}
        assert result["review_results"] == {"a": "submitted", "b": "submitted"}
        assert result["status"] == "unverified_model_synthesis"
        snap = CollectiveStore(database).snapshot(result["episode_id"])
        assert len(snap.answers) == 2 and len(snap.reviews) == 2 and len(snap.syntheses) == 1
        assert len(ProviderHandler.requests) == 5
        assert sorted(item[2]["model"] for item in ProviderHandler.requests) == [
            "model-a", "model-a", "model-a", "model-b", "model-b"
        ]
        assert "a-private-token" not in json.dumps(result)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

def test_openai_optional_generation_controls_are_forwarded_and_validated():
    ProviderHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProviderHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        model = OpenAICompatibleModel(
            "thinking", "small-model", f"http://127.0.0.1:{server.server_port}/v1",
            "local-placeholder", timeout_seconds=120, max_tokens=2048, reasoning_effort="none",
        )
        assert model.complete(({"role": "user", "content": "test"},)) == "OpenAI style response"
        request = ProviderHandler.requests[-1][2]
        assert request["max_tokens"] == 2048
        assert request["reasoning_effort"] == "none"
        assert request["stream"] is False
        with pytest.raises(ValueError):
            OpenAICompatibleModel("bad", "model", "http://127.0.0.1:11434/v1", "x", max_tokens=0)
        with pytest.raises(ValueError):
            OpenAICompatibleModel("bad", "model", "http://127.0.0.1:11434/v1", "x", reasoning_effort=17)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

def test_cli_model_config_forwards_local_thinking_controls(monkeypatch):
    monkeypatch.setenv("OLLAMA_TEST_KEY", "local-dummy")
    config = {"provider": "openai_compatible", "agent_id": "liquid",
              "model": "lfm2.5-thinking:1.2b", "base_url": "http://127.0.0.1:11434/v1",
              "api_key_env": "OLLAMA_TEST_KEY", "timeout_seconds": 180,
              "max_tokens": 3072, "reasoning_effort": "none"}
    model = _model(config)
    assert model.timeout_seconds == 180 and model.max_tokens == 3072
    assert model.reasoning_effort == "none"
    with pytest.raises(ValueError):
        _model({**config, "max_tokens": "unbounded"})
    with pytest.raises(ValueError):
        _model({**config, "timeout_seconds": 999})
