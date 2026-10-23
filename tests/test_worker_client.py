"""Adversarial one-shot worker tests; no real provider credentials or remote hosts."""
from contextlib import contextmanager
from http.server import HTTPServer
import io
import json
from pathlib import Path
import secrets
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import URLError

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server
from rezon.worker_client import (
    OutcomeUnknown, WorkerClientError, _gateway, _request, main, run,
)


@contextmanager
def gateway():
    with TemporaryDirectory() as root:
        store = CollectiveStore(Path(root) / "episode.sqlite3")
        agents = ("lappy", "vn1", "vn2", "malaphor")
        tokens = {x: secrets.token_urlsafe(32) for x in agents}
        admin = secrets.token_urlsafe(32)
        server = make_server(store, admin, tokens)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            episode = store.create("Does the intervention improve accuracy?", agents)
            yield store, tokens, server, episode
        finally:
            server.shutdown()
            server.server_close()
            thread.join(4)


class FakeModel:
    calls = []

    def __init__(self, *args, **kwargs):
        self.__class__.calls.append(("construct", args, kwargs))

    def complete(self, messages):
        self.__class__.calls.append(("complete", messages))
        return "The assertion needs preregistered held-out comparison."


class WorkerClientTests(unittest.TestCase):
    def setUp(self):
        FakeModel.calls = []

    def test_remote_plaintext_rejected(self):
        for value in ("http://vpn.example:8765", "https://name:secret@example.com",
                      "https://example.com/v1", "https://example.com?secret=1",
                      "https://example.com/#frag", "file:///tmp/secret"):
            with self.subTest(value=value):
                with self.assertRaises(WorkerClientError):
                    _gateway(value)
        self.assertEqual(_gateway("https://vn2.tail86ea75.ts.net/"),
                         "https://vn2.tail86ea75.ts.net")

    def test_status_proves_no_host_attestation(self):
        with gateway() as (_, tokens, server, episode):
            url = f"http://127.0.0.1:{server.server_port}"
            status = run("status", url, episode, tokens["vn2"])
            self.assertEqual(status["agent_id"], "vn2")
            self.assertFalse(status["host_independence_verified"])
            self.assertEqual(status["authority"], "NONE")
            self.assertNotIn("prompt", status)

    @patch("rezon.worker_client.OpenAICompatibleModel", FakeModel)
    def test_real_gateway_accepts_one_model_answer_without_echoing_text(self):
        with gateway() as (store, tokens, server, episode):
            url = f"http://127.0.0.1:{server.server_port}"
            result = run("answer", url, episode, tokens["vn1"], model_id="test-model",
                         model_api_key="local-placeholder")
            self.assertEqual(result["contribution_id"], "answer:vn1")
            self.assertFalse(result["host_independence_verified"])
            self.assertEqual(result["gateway_status"], "ACCEPTED_UNATTESTED")
            self.assertNotIn("The assertion", json.dumps(result))
            self.assertEqual(store.snapshot(episode).answers[0].agent_id, "vn1")
            with self.assertRaisesRegex(WorkerClientError, "already submitted"):
                run("answer", url, episode, tokens["vn1"], model_id="test-model",
                    model_api_key="local-placeholder")

    @patch("rezon.worker_client.OpenAICompatibleModel", FakeModel)
    def test_review_targets_all_other_answers(self):
        with gateway() as (store, tokens, server, episode):
            for name in ("lappy", "vn1", "vn2", "malaphor"):
                store.submit_answer(episode, name, "Claim from " + name)
            url = f"http://127.0.0.1:{server.server_port}"
            result = run("review", url, episode, tokens["vn2"],
                         model_id="test-model", model_api_key="local-placeholder")
            self.assertEqual(result["contribution_id"], "review:vn2")
            review = store.snapshot(episode).reviews[0]
            self.assertEqual(set(review.target_ids), {
                "answer:lappy", "answer:vn1", "answer:malaphor"
            })
            self.assertNotIn("answer:vn2", review.target_ids)

    @patch("rezon.worker_client.OpenAICompatibleModel", FakeModel)
    def test_missing_initial_answers_block_review(self):
        with gateway() as (_, tokens, server, episode):
            url = f"http://127.0.0.1:{server.server_port}"
            with self.assertRaisesRegex(WorkerClientError, "HTTP 409"):
                run("review", url, episode, tokens["vn1"],
                    model_id="test-model", model_api_key="local-placeholder")
            self.assertFalse(FakeModel.calls)

    def test_wrong_credential_is_not_worker(self):
        with gateway() as (_, tokens, server, episode):
            url = f"http://127.0.0.1:{server.server_port}"
            with self.assertRaisesRegex(WorkerClientError, "HTTP 401"):
                run("status", url, episode, "not-a-valid-worker-token-1234")

    def test_client_does_not_follow_redirect_with_bearer(self):
        from http.server import BaseHTTPRequestHandler
        class Redirect(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", "https://example.com/collect")
                self.end_headers()
        serv = HTTPServer(("127.0.0.1", 0), Redirect)
        thread = Thread(target=serv.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertRaisesRegex(WorkerClientError, "HTTP 302"):
                _request(f"http://127.0.0.1:{serv.server_port}",
                         "/v1/episodes/collective-" + "a"*32,
                         "safe-test-token-1234567890")
        finally:
            serv.shutdown()
            serv.server_close()
            thread.join(4)

    def test_network_failure_during_post_is_unknown_not_retry(self):
        with patch("rezon.worker_client.build_opener") as opener:
            opener.return_value.open.side_effect = URLError("credential-secret")
            with self.assertRaises(OutcomeUnknown) as found:
                _request("https://example.com", "/v1/episodes/collective-"+"a"*32+
                         "/answers", "safe-test-token-1234567890",
                         method="POST", body={"content": "test"})
            self.assertNotIn("credential-secret", str(found.exception))
            self.assertIn("OUTCOME_UNKNOWN", str(found.exception))
            self.assertEqual(opener.return_value.open.call_count, 1)

    def test_cli_errors_do_not_print_secret(self):
        old = "secret-token-for-test-only-abcdefgh"
        with patch("rezon.worker_client.os.environ", {"REZON_WORKER_TOKEN": old}), (
             patch("rezon.worker_client.sys.stderr", new_callable=io.StringIO) as stderr):
            code = main(["status", "--gateway", "http://some-public-host",
                         "--episode", "collective-"+"a"*32])
        self.assertEqual(code, 2)
        self.assertNotIn(old, stderr.getvalue())

    def test_no_model_without_opt_in(self):
        with gateway() as (_, tokens, server, episode):
            with self.assertRaises(WorkerClientError):
                run("answer", f"http://127.0.0.1:{server.server_port}",
                    episode, tokens["vn1"])


if __name__ == "__main__":
    unittest.main()
