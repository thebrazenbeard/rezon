"""Adversarial one-shot worker tests; no real provider credentials or remote hosts."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import secrets
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import URLError

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server
from rezon.providers import (
    AnthropicModel, OpenAICompatibleModel, ProviderOutcomeUnknown,
)
from rezon.worker_client import (
    OutcomeUnknown, WorkerClientError, _gateway, _request, _local_model_endpoint, main, run,
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
            calls = list(FakeModel.calls)
            with self.assertRaisesRegex(WorkerClientError, "review already submitted"):
                run("review", url, episode, tokens["vn2"],
                    model_id="test-model", model_api_key="local-placeholder")
            self.assertEqual(FakeModel.calls, calls)

    @patch("rezon.worker_client.OpenAICompatibleModel", FakeModel)
    def test_repeated_review_does_not_invoke_model_or_post_again(self):
        episode = "collective-" + "a" * 32
        record = {"episode_id": episode, "agent_id": "vn2", "prompt": "Task"}
        state = {
            "episode_id": episode, "complete": True,
            "agents": ["vn1", "vn2"], "prompt": "Task",
            "answers": [
                {"agent_id": "vn1", "id": "answer:vn1", "content": "A"},
                {"agent_id": "vn2", "id": "answer:vn2", "content": "B"},
            ],
            "reviews": [{"agent_id": "vn2", "id": "review:vn2"}],
        }
        with patch("rezon.worker_client._request", side_effect=[record, state]) as request:
            with self.assertRaisesRegex(WorkerClientError, "review already submitted"):
                run("review", "https://vn2.tail86ea75.ts.net", episode,
                    "safe-test-token-1234567890", model_id="test-model",
                    model_api_key="local-placeholder")
        self.assertEqual(request.call_count, 2)
        self.assertFalse(FakeModel.calls)

    @patch("rezon.worker_client.OpenAICompatibleModel", FakeModel)
    def test_malformed_or_duplicate_review_claims_are_rejected_before_inference(self):
        episode = "collective-" + "a" * 32
        record = {"episode_id": episode, "agent_id": "vn2", "prompt": "Task"}
        state = {
            "episode_id": episode, "complete": True,
            "agents": ["vn1", "vn2"], "prompt": "Task",
            "answers": [
                {"agent_id": "vn1", "id": "answer:vn1", "content": "A"},
                {"agent_id": "vn2", "id": "answer:vn2", "content": "B"},
            ],
        }
        for reviews in (None, {}, [{"agent_id": "vn1", "id": "review:vn2"}],
                        [{"agent_id": "vn1", "id": "review:vn1"}] * 2,
                        [{"agent_id": "unknown", "id": "review:unknown"}]):
            with self.subTest(reviews=reviews):
                with patch("rezon.worker_client._request", side_effect=[
                    record, {**state, "reviews": reviews}
                ]) as request:
                    with self.assertRaisesRegex(WorkerClientError, "invalid review state"):
                        run("review", "https://vn2.tail86ea75.ts.net", episode,
                            "safe-test-token-1234567890", model_id="test-model",
                            model_api_key="local-placeholder")
                self.assertEqual(request.call_count, 2)
        self.assertFalse(FakeModel.calls)

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

    def test_post_201_with_malformed_body_is_outcome_unknown(self):
        with patch("rezon.worker_client.build_opener") as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.status = 201
            response.read.return_value = b"{malformed"
            with self.assertRaises(OutcomeUnknown):
                _request("https://example.com",
                         "/v1/episodes/collective-" + "a"*32 + "/answers",
                         "safe-test-token-1234567890", method="POST",
                         body={"content": "hypothesis"})
            self.assertEqual(opener.return_value.open.call_count, 1)

    def test_post_502_is_unknown_not_safe_to_retry(self):
        from urllib.error import HTTPError
        with patch("rezon.worker_client.build_opener") as opener:
            opener.return_value.open.side_effect = HTTPError(
                "https://example.com", 502, "provider-error-secret", {}, None)
            with self.assertRaises(OutcomeUnknown):
                _request("https://example.com",
                         "/v1/episodes/collective-" + "a"*32 + "/answers",
                         "safe-test-token-1234567890", method="POST",
                         body={"content": "hypothesis"})

    @patch("rezon.worker_client.OpenAICompatibleModel", FakeModel)
    def test_mismatched_post_receipt_is_outcome_unknown(self):
        episode = "collective-" + "a"*32
        with patch("rezon.worker_client._request", side_effect=[
            {"episode_id": episode, "agent_id": "vn1", "prompt": "Test claim",
             "answer_submitted": False},
            {"contribution_id": "answer:someone-else"},
        ]):
            with self.assertRaises(OutcomeUnknown):
                run("answer", "https://vn2.tail86ea75.ts.net", episode,
                    "safe-test-token-1234567890", model_id="test-model",
                    model_api_key="local-placeholder")

    def test_cli_errors_do_not_print_secret(self):
        old = "secret-token-for-test-only-abcdefgh"
        with patch("rezon.worker_client.os.environ", {"REZON_WORKER_TOKEN": old}), \
             patch("rezon.worker_client.sys.stderr", new_callable=io.StringIO) as stderr:
            code = main(["status", "--gateway", "http://some-public-host",
                         "--episode", "collective-"+"a"*32])
        self.assertEqual(code, 2)
        self.assertNotIn(old, stderr.getvalue())

    @patch("rezon.worker_client.OpenAICompatibleModel", FakeModel)
    def test_bounded_max_tokens_reaches_real_model_adapter(self):
        with gateway() as (_, tokens, server, episode):
            url = f"http://127.0.0.1:{server.server_port}"
            reply = run("answer", url, episode, tokens["vn1"], model_id="test-model",
                        model_api_key="local-placeholder", max_tokens=240)
            self.assertEqual(reply["contribution_id"], "answer:vn1")
            self.assertEqual(FakeModel.calls[0][0], "construct")
            self.assertEqual(FakeModel.calls[0][2]["max_tokens"], 240)

    def test_max_tokens_rejects_out_of_bounds_before_network_or_inference(self):
        episode = "collective-" + "a"*32
        for bad in (0, -1, 1025, True, "256"):
            with self.subTest(bad=bad):
                with patch("rezon.worker_client._request") as request:
                    with self.assertRaises(WorkerClientError):
                        run("answer", "https://vn2.tail86ea75.ts.net", episode,
                            "safe-test-token-1234567890", model_id="test-model",
                            model_api_key="local-placeholder", max_tokens=bad)
                    request.assert_not_called()

    def test_cli_forwards_max_tokens_without_printing_credentials(self):
        token = "secret-token-for-test-only-abcdefgh"
        episode = "collective-" + "a"*32
        with patch("rezon.worker_client.os.environ", {"REZON_WORKER_TOKEN": token}), \
             patch("rezon.worker_client.run", return_value={"episode_id": episode}) as run_mock, \
             patch("rezon.worker_client.sys.stdout", new_callable=io.StringIO) as output:
            code = main(["status", "--gateway", "https://vn2.tail86ea75.ts.net",
                         "--episode", episode, "--max-tokens", "240"])
        self.assertEqual(code, 0)
        self.assertEqual(run_mock.call_args.kwargs["max_tokens"], 240)
        self.assertNotIn(token, output.getvalue())

    def test_no_model_without_opt_in(self):
        with gateway() as (_, tokens, server, episode):
            with self.assertRaises(WorkerClientError):
                run("answer", f"http://127.0.0.1:{server.server_port}",
                    episode, tokens["vn1"])

    def test_worker_model_protocols_reach_real_loopback_http_and_persist_claims(self):
        class ModelEndpoint(BaseHTTPRequestHandler):
            requests = []

            def do_POST(self):
                raw = self.rfile.read(int(self.headers["Content-Length"]))
                body = json.loads(raw)
                self.requests.append((self.path, dict(self.headers), body))
                if self.path == "/v1/chat/completions":
                    payload = {"choices": [{"message": {"content": "OpenAI-form claim"}}]}
                elif self.path == "/v1/messages":
                    payload = {"content": [{"type": "text", "text": "Anthropic-form claim"}]}
                else:
                    self.send_error(404)
                    return
                encoded = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, *_args):
                pass

        model_server = ThreadingHTTPServer(("127.0.0.1", 0), ModelEndpoint)
        model_thread = Thread(target=model_server.serve_forever, daemon=True)
        model_thread.start()
        try:
            with gateway() as (store, tokens, server, episode):
                endpoint = f"http://127.0.0.1:{model_server.server_port}/v1"
                gate = f"http://127.0.0.1:{server.server_port}"
                openai = run("answer", gate, episode, tokens["vn1"],
                             model_id="local-a", model_url=endpoint,
                             model_api_key="dummy-a", model_provider="openai_compatible")
                anthropic = run("answer", gate, episode, tokens["vn2"],
                                model_id="local-b", model_url=endpoint,
                                model_api_key="dummy-b", model_provider="anthropic")
                self.assertEqual(openai["model_protocol"], "openai_compatible")
                self.assertEqual(anthropic["model_protocol"], "anthropic")
                self.assertEqual(anthropic["gateway_status"], "ACCEPTED_UNATTESTED")
                self.assertEqual(anthropic["authority"], "NONE")
                self.assertFalse(anthropic["host_independence_verified"])
                self.assertEqual({c.content for c in store.snapshot(episode).answers},
                                 {"OpenAI-form claim", "Anthropic-form claim"})
                store.submit_answer(episode, "lappy", "Other test claim")
                store.submit_answer(episode, "malaphor", "Fourth test claim")
                review = run("review", gate, episode, tokens["vn2"],
                             model_id="local-b", model_url=endpoint,
                             model_api_key="dummy-b", model_provider="anthropic")
                self.assertEqual(review["contribution_id"], "review:vn2")
                self.assertEqual(review["model_protocol"], "anthropic")
                self.assertEqual(set(store.snapshot(episode).reviews[0].target_ids),
                                 {"answer:lappy", "answer:vn1", "answer:malaphor"})
                self.assertEqual([p for p, _, _ in ModelEndpoint.requests],
                                 ["/v1/chat/completions", "/v1/messages", "/v1/messages"])
                self.assertEqual(ModelEndpoint.requests[0][1]["Authorization"], "Bearer dummy-a")
                self.assertEqual({k.lower(): v for k, v in ModelEndpoint.requests[1][1].items()}["x-api-key"],
                                 "dummy-b")
                self.assertNotIn("dummy-b", json.dumps(anthropic))
        finally:
            model_server.shutdown()
            model_server.server_close()
            model_thread.join(4)

    def test_unrecognized_or_spoofed_provider_rejected_before_gateway_or_model(self):
        episode = "collective-" + "a" * 32
        class SpoofedProvider(str):
            def __eq__(self, other):
                return True

            def __hash__(self):
                return str.__hash__(self)

        for bad in ("unknown", "OPENAI_COMPATIBLE", SpoofedProvider("unknown"), None):
            with self.subTest(provider=str(bad)):
                with patch("rezon.worker_client._request") as request:
                    with self.assertRaisesRegex(WorkerClientError, "invalid model provider"):
                        run("answer", "https://gateway.example", episode,
                            "safe-test-token-1234567890", model_id="model",
                            model_api_key="dummy", model_provider=bad)
                    request.assert_not_called()

    def test_model_egress_denied_before_gateway_or_provider_calls(self):
        episode = "collective-" + "a" * 32
        unsafe_endpoints = (
            "https://api.vendor.example/v1", "http://192.168.1.71:11434/v1",
            "https://localhost.evil.example/v1", "http://127.0.0.2:11434/v1",
            "http://127.1:11434/v1", "http://2130706433:11434/v1",
            "http://localhost:11434/v1", "http://127.0.0.1./v1",
            "http://name:password@127.0.0.1:11434/v1",
            "http://127.0.0.1:11434/v1?remote=true",
            "http://127.0.0.1:11434/v1#fragment",
            "http://127.0.0.1:0/v1", "http://127.0.0.1/v1",
            "http://127.0.0.1:11434\\@remote.example/v1",
        )
        for protocol in ("openai_compatible", "anthropic"):
            for endpoint in unsafe_endpoints:
                for action in ("answer", "review"):
                    with self.subTest(protocol=protocol, endpoint=endpoint, action=action), \
                         patch("rezon.worker_client._request") as gateway_call, \
                         patch("rezon.worker_client.OpenAICompatibleModel") as openai_model, \
                         patch("rezon.worker_client.AnthropicModel") as anthropic_model:
                        with self.assertRaisesRegex(WorkerClientError, "local model endpoint"):
                            run(action, "https://gateway.example", episode,
                                "safe-test-token-1234567890", model_id="local-model",
                                model_url=endpoint, model_api_key="dummy",
                                model_provider=protocol)
                        gateway_call.assert_not_called()
                        openai_model.assert_not_called()
                        anthropic_model.assert_not_called()

    def test_numeric_ipv4_ipv6_endpoints_ignore_ambient_proxy(self):
        # PR147's isolated provider child uses ProxyHandler({}) at dispatch.
        # Ambient proxy values cannot turn an otherwise local model URL into
        # an off-host route, even if NO_PROXY is cleared after preflight.
        with patch.dict(os.environ, {
            "http_proxy": "http://127.0.0.1:9", "HTTP_PROXY": "http://127.0.0.1:9",
            "https_proxy": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
            "no_proxy": "", "NO_PROXY": "",
        }, clear=False):
            for url in ("http://127.0.0.1:11434/v1", "http://[::1]:11434/v1"):
                with self.subTest(url=url):
                    self.assertEqual(_local_model_endpoint(url), url)

    def test_gateway_bearer_cannot_reach_ambient_http_proxy(self):
        class DirectGateway(BaseHTTPRequestHandler):
            seen = []

            def do_GET(self):
                self.seen.append((self.path, self.headers.get("Authorization")))
                data = b'{"episode_id":"synthetic"}'
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_args):
                pass

        class InterceptingProxy(BaseHTTPRequestHandler):
            seen = []

            def do_GET(self):
                self.seen.append((self.path, self.headers.get("Authorization")))
                data = b'{"episode_id":"intercepted"}'
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_args):
                pass

        direct = HTTPServer(("127.0.0.1", 0), DirectGateway)
        proxy = HTTPServer(("127.0.0.1", 0), InterceptingProxy)
        threads = [Thread(target=server.serve_forever, daemon=True) for server in (direct, proxy)]
        for thread in threads:
            thread.start()
        token = "synthetic-worker-token-123456"
        try:
            proxy_url = f"http://127.0.0.1:{proxy.server_port}"
            with patch.dict(os.environ, {
                "http_proxy": proxy_url, "HTTP_PROXY": proxy_url,
                "no_proxy": "", "NO_PROXY": "",
            }, clear=False):
                result = _request(f"http://127.0.0.1:{direct.server_port}",
                                  "/v1/episodes/collective-" + "a" * 32, token)
            self.assertEqual(result["episode_id"], "synthetic")
            self.assertEqual(DirectGateway.seen, [
                ("/v1/episodes/collective-" + "a" * 32, "Bearer " + token),
            ])
            self.assertEqual(InterceptingProxy.seen, [])
        finally:
            for server in (direct, proxy):
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(4)

    def test_local_model_redirect_cannot_relay_prompt_or_credential(self):
        class RedirectModel(BaseHTTPRequestHandler):
            requests = 0
            location = ""

            def do_POST(self):
                self.__class__.requests += 1
                self.send_response(307)
                self.send_header("Location", self.location)
                self.end_headers()

            def log_message(self, *_args):
                pass

        class RedirectTrap(BaseHTTPRequestHandler):
            requests = 0

            def do_POST(self):
                self.__class__.requests += 1
                self.send_response(200)
                self.end_headers()

            def log_message(self, *_args):
                pass

        trap_server = HTTPServer(("127.0.0.1", 0), RedirectTrap)
        RedirectModel.location = f"http://127.0.0.1:{trap_server.server_port}/collect"
        model_server = HTTPServer(("127.0.0.1", 0), RedirectModel)
        threads = [Thread(target=server.serve_forever, daemon=True)
                   for server in (model_server, trap_server)]
        for thread in threads:
            thread.start()

        try:
            with gateway() as (store, tokens, server, episode):
                gate = f"http://127.0.0.1:{server.server_port}"
                endpoint = f"http://127.0.0.1:{model_server.server_port}/v1"
                # PR147's disposable subprocess deliberately collapses
                # provider HTTP failures to an ambiguous completion outcome.
                with self.assertRaisesRegex(ProviderOutcomeUnknown, "outcome unknown"):
                    run("answer", gate, episode, tokens["vn1"],
                        model_id="local-model", model_url=endpoint,
                        model_api_key="no-real-key", model_provider="anthropic")
                self.assertEqual(RedirectModel.requests, 1)
                self.assertEqual(RedirectTrap.requests, 0)
                self.assertFalse(store.snapshot(episode).answers)
        finally:
            for server in (model_server, trap_server):
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(4)

    def test_gateway_proxy_mutation_cannot_relay_local_model_prompt(self):
        """Regression: proxy environment changes after model URL preflight."""
        class DirectModel(BaseHTTPRequestHandler):
            seen = []

            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                self.seen.append((self.path, body))
                if self.path.endswith("/messages"):
                    reply = {"content": [{"type": "text", "text": "Direct claim"}]}
                else:
                    reply = {"choices": [{"message": {"content": "Direct claim"}}]}
                raw = json.dumps(reply).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, *_args):
                pass

        class InterceptingProxy(BaseHTTPRequestHandler):
            seen = []

            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                self.seen.append((self.path, body))
                if self.path.endswith("/messages"):
                    reply = {"content": [{"type": "text", "text": "Proxied claim"}]}
                else:
                    reply = {"choices": [{"message": {"content": "Proxied claim"}}]}
                raw = json.dumps(reply).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, *_args):
                pass

        direct = HTTPServer(("127.0.0.1", 0), DirectModel)
        proxy = HTTPServer(("127.0.0.1", 0), InterceptingProxy)
        threads = [Thread(target=server.serve_forever, daemon=True) for server in (direct, proxy)]
        for thread in threads:
            thread.start()
        try:
            episode = "collective-" + "a" * 32
            endpoint = f"http://127.0.0.1:{direct.server_port}/v1"
            proxy_url = f"http://127.0.0.1:{proxy.server_port}"
            env = {"http_proxy": "", "HTTP_PROXY": "", "no_proxy": "127.0.0.1",
                   "NO_PROXY": "127.0.0.1"}
            for protocol in ("openai_compatible", "anthropic"):
                DirectModel.seen = []
                InterceptingProxy.seen = []

                def gateway_then_mutate(_gateway, route, _token, method="GET", **_kwargs):
                    if method == "GET":
                        # Valid initial URL preflight has already happened.
                        os.environ.update({"http_proxy": proxy_url, "HTTP_PROXY": proxy_url,
                                           "no_proxy": "", "NO_PROXY": ""})
                        return {"episode_id": episode, "agent_id": "vn1",
                                "prompt": "SYNTHETIC_TOCTOU_PROMPT", "answer_submitted": False}
                    return {"contribution_id": "answer:vn1"}

                with self.subTest(protocol=protocol), patch.dict(os.environ, env, clear=False), \
                     patch("rezon.worker_client._request", side_effect=gateway_then_mutate):
                    result = run("answer", "https://gateway.example", episode,
                                 "safe-test-token-1234567890", model_id="local-model",
                                 model_url=endpoint, model_api_key="dummy-key",
                                 model_provider=protocol)
                    self.assertEqual(result["gateway_status"], "ACCEPTED_UNATTESTED")
                    self.assertEqual(len(DirectModel.seen), 1)
                    self.assertIn(b"SYNTHETIC_TOCTOU_PROMPT", DirectModel.seen[0][1])
                    self.assertEqual(InterceptingProxy.seen, [])

            # PR147's standalone providers ALSO use a direct isolated
            # subprocess, regardless of a caller's ambient proxy settings.
            DirectModel.seen = []
            InterceptingProxy.seen = []
            proxy_env = {"http_proxy": proxy_url, "HTTP_PROXY": proxy_url,
                         "no_proxy": "", "NO_PROXY": ""}
            with patch.dict(os.environ, proxy_env, clear=False):
                for model_type in (OpenAICompatibleModel, AnthropicModel):
                    regular = model_type("unrestricted", "model", endpoint, "dummy")
                    self.assertEqual(regular.complete(({"role": "user", "content": "proxy test"},)),
                                     "Direct claim")
            self.assertEqual(len(DirectModel.seen), 2)
            self.assertEqual(InterceptingProxy.seen, [])
        finally:
            for server in (direct, proxy):
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(4)

    def test_cli_forwards_selected_provider_without_disclosing_key(self):
        token = "secret-token-for-test-only-abcdefgh"
        episode = "collective-" + "a" * 32
        with patch("rezon.worker_client.os.environ", {"REZON_WORKER_TOKEN": token}), \
             patch("rezon.worker_client.run", return_value={"episode_id": episode}) as run_mock, \
             patch("rezon.worker_client.sys.stdout", new_callable=io.StringIO) as output:
            code = main(["status", "--gateway", "https://gateway.example",
                         "--episode", episode, "--provider", "anthropic"])
        self.assertEqual(code, 0)
        self.assertEqual(run_mock.call_args.kwargs["model_provider"], "anthropic")
        self.assertNotIn(token, output.getvalue())


if __name__ == "__main__":
    unittest.main()
