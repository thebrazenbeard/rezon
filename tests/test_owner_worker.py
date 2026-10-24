"""Operator-local credential enrollment; no live credentials or external provider calls."""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import io
import json
import secrets
import unittest
from unittest.mock import patch, call, MagicMock

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server
from rezon import owner_worker


@contextmanager
def sample_gateway():
    with TemporaryDirectory() as temp:
        store = CollectiveStore(Path(temp) / "episodes.db")
        tokens = {r: secrets.token_urlsafe(32)
                  for r in ("lappy", "vn1", "vn2", "malaphor")}
        server = make_server(store, secrets.token_urlsafe(32), tokens)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            episode = store.create("One real authenticated identity check",
                                   ("lappy", "vn1", "vn2", "malaphor"))
            yield "http://127.0.0.1:" + str(server.server_port), episode, tokens
        finally:
            server.shutdown()
            server.server_close()
            thread.join(5)


class EnrollmentTests(unittest.TestCase):
    def test_no_interactive_terminal_refuses_to_prompt_or_store(self):
        with (patch("rezon.owner_worker.sys.stdin") as stdin,
              patch("rezon.owner_worker.getpass.getpass") as prompt,
              patch("rezon.owner_worker.client_run") as network,
              patch("rezon.owner_worker.credential_store.save") as save):
            stdin.isatty.return_value = False
            with self.assertRaises(owner_worker.EnrollmentError):
                owner_worker.enroll("vn1", "https://vn2.tail86ea75.ts.net",
                                    "collective-"+"a"*32)
            prompt.assert_not_called()
            network.assert_not_called()
            save.assert_not_called()

    def test_owner_enrollment_verifies_exact_role_before_saving(self):
        with sample_gateway() as (gateway, episode, tokens), \
             patch("rezon.owner_worker._interactive", return_value=True), \
             patch("rezon.owner_worker.getpass.getpass", return_value=tokens["vn1"]), \
             patch("rezon.owner_worker.credential_store.save") as save:
            result = owner_worker.enroll("vn1", gateway, episode)
        save.assert_called_once_with("vn1", tokens["vn1"])
        self.assertEqual(result["agent_id"], "vn1")
        self.assertTrue(result["enrolled"])
        self.assertNotIn(tokens["vn1"], json.dumps(result))

    def test_cross_role_token_is_not_enrolled(self):
        with sample_gateway() as (gateway, episode, tokens), \
             patch("rezon.owner_worker._interactive", return_value=True), \
             patch("rezon.owner_worker.getpass.getpass", return_value=tokens["lappy"]), \
             patch("rezon.owner_worker.credential_store.save") as save:
            with self.assertRaises(owner_worker.EnrollmentError):
                owner_worker.enroll("vn1", gateway, episode)
        save.assert_not_called()

    def test_enrollment_rejects_invalid_role_and_missing_token(self):
        with patch("rezon.owner_worker._interactive", return_value=True), \
             patch("rezon.owner_worker.getpass.getpass", return_value=""):
            with self.assertRaises(owner_worker.EnrollmentError):
                owner_worker.enroll("lappy", "https://vn2.tail86ea75.ts.net",
                                    "collective-"+"a"*32)
        with patch("rezon.owner_worker._interactive", return_value=True), \
             patch("rezon.owner_worker.getpass.getpass") as prompt:
            with self.assertRaises(owner_worker.EnrollmentError):
                owner_worker.enroll("admin", "https://vn2.tail86ea75.ts.net",
                                    "collective-"+"a"*32)
            prompt.assert_not_called()

    def test_missing_vault_credential_fails_closed_before_network(self):
        with patch("rezon.owner_worker.credential_store.load", side_effect=owner_worker.credential_store.CredentialError("no credential")), \
             patch("rezon.owner_worker.client_run") as run:
            with self.assertRaises(owner_worker.EnrollmentError):
                owner_worker.execute("answer", "vn1", "https://vn2.tail86ea75.ts.net",
                                     "collective-"+"a"*32, model_id="gemma3:1b")
            run.assert_not_called()

    def test_execute_rechecks_role_before_model_inference_or_submission(self):
        token = "a-fake-test-only-token-123456789"
        with patch("rezon.owner_worker.credential_store.load", return_value=token), \
             patch("rezon.owner_worker.client_run", return_value={"agent_id": "malaphor"}) as run:
            with self.assertRaises(owner_worker.EnrollmentError):
                owner_worker.execute("answer", "lappy", "https://vn2.tail86ea75.ts.net",
                                     "collective-"+"a"*32, model_id="qwen3:4b-instruct")
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0], "status")

    def test_execute_propagates_exact_client_result_with_no_retries(self):
        token = "a-fake-test-only-token-123456789"
        receipt = {"contribution_id":"answer:vn1", "agent_id":"vn1"}
        with patch("rezon.owner_worker.credential_store.load", return_value=token), \
             patch("rezon.owner_worker.client_run", side_effect=[
                 {"agent_id":"vn1","answer_submitted":False}, receipt]) as run:
            result = owner_worker.execute("answer", "vn1",
                "https://vn2.tail86ea75.ts.net", "collective-"+"a"*32,
                model_id="gemma3:1b", model_key="loopback-model-placeholder",
                max_tokens=240)
        self.assertEqual(result, receipt)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0], "answer")
        self.assertEqual(run.call_args.kwargs["max_tokens"], 240)
        self.assertNotIn(token, json.dumps(result))

    def test_linux_store_passes_secret_by_stdin_not_argv(self):
        fake = type("Proc", (), {"returncode":0, "stdout":""})()
        with patch("rezon.credential_store.sys.platform", "linux"), \
             patch("rezon.credential_store.subprocess.run", return_value=fake) as run:
            owner_worker.credential_store.save("vn1", "fake-secret-123456789012345")
        argv = run.call_args.args[0]
        self.assertEqual(argv[0:2], ["secret-tool", "store"])
        self.assertNotIn("fake-secret-123456789012345", " ".join(argv))
        self.assertEqual(run.call_args.kwargs["input"], "fake-secret-123456789012345\n")
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_linux_missing_secret_service_never_falls_back_to_plaintext_file(self):
        with patch("rezon.credential_store.sys.platform", "linux"), \
             patch("rezon.credential_store.subprocess.run", side_effect=FileNotFoundError), \
             patch("builtins.open") as open_file:
            with self.assertRaises(owner_worker.credential_store.CredentialError):
                owner_worker.credential_store.save("vn1", "fake-secret-123456789012345")
            open_file.assert_not_called()

    def test_linux_python_secret_service_store_when_secret_tool_missing(self):
        secret = "synthetic-only-test-1234567890"
        module = MagicMock()
        collection = module.get_default_collection.return_value
        collection.is_locked.return_value = False
        with (patch("rezon.credential_store.sys.platform", "linux"),
              patch("rezon.credential_store.subprocess.run", side_effect=FileNotFoundError),
              patch.dict("sys.modules", {"secretstorage": module}),
              patch("builtins.open") as opened):
            owner_worker.credential_store.save("vn2", secret)
        collection.create_item.assert_called_once_with(
            "Rezon worker vn2",
            {"service": "rezon-tkik", "role": "vn2"},
            secret.encode("ascii"),
            replace=True,
        )
        opened.assert_not_called()

    def test_linux_python_secret_service_load_when_secret_tool_missing(self):
        secret = "synthetic-only-test-1234567890"
        module = MagicMock()
        item = MagicMock()
        item.is_locked.return_value = False
        item.get_secret.return_value = secret.encode("ascii")
        module.search_items.return_value = [item]
        with (patch("rezon.credential_store.sys.platform", "linux"),
              patch("rezon.credential_store.subprocess.run", side_effect=FileNotFoundError),
              patch.dict("sys.modules", {"secretstorage": module})):
            result = owner_worker.credential_store.load("vn2")
        self.assertEqual(result, secret)
        module.search_items.assert_called_once_with(
            module.dbus_init.return_value,
            {"service": "rezon-tkik", "role": "vn2"},
        )

    def test_cli_never_logs_prompted_token_in_failure(self):
        secret = "fake-secret-token-for-tests-abcdef"
        with patch("rezon.owner_worker._interactive", return_value=True), \
             patch("rezon.owner_worker.getpass.getpass", return_value=secret), \
             patch("rezon.owner_worker.client_run", side_effect=ValueError(secret)), \
             patch("rezon.owner_worker.sys.stderr", new_callable=io.StringIO) as stderr:
            rc = owner_worker.main(["enroll","--role","vn1",
                "--gateway","https://vn2.tail86ea75.ts.net",
                "--episode","collective-"+"a"*32])
        self.assertEqual(rc, 2)
        self.assertNotIn(secret, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
