"""Synthetic slow-drip completion tests; no real provider or credentials."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
import time

import pytest

from rezon.providers import AnthropicModel, OpenAICompatibleModel, ProviderOutcomeUnknown


@contextmanager
def slow_origin(*, delay_seconds=0.03):
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            seen.append(self.path)
            if self.path.endswith("/messages"):
                value = {"content": [{"type": "text", "text": "test-answer"}]}
            else:
                value = {"choices": [{"message": {"content": "test-answer"}}]}
            data = json.dumps(value).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            for byte in data:
                try:
                    self.wfile.write(bytes((byte,)))
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    return
                time.sleep(delay_seconds)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1", seen
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.parametrize("cls", [OpenAICompatibleModel, AnthropicModel])
def test_completion_enforces_total_monotonic_deadline_over_slow_drip(cls):
    with slow_origin() as (url, seen):
        adapter = cls("worker", "synthetic", url, "SYNTHETIC-ONLY", timeout_seconds=0.20)
        start = time.monotonic()
        with pytest.raises(ProviderOutcomeUnknown, match="total deadline.*outcome unknown"):
            adapter.complete(({"role": "user", "content": "hello"},))
        elapsed = time.monotonic() - start
    assert seen
    assert elapsed < 0.80, f"slow response consumed {elapsed:.2f}s after 0.20s deadline"
