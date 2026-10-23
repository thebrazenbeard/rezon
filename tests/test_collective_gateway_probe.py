"""Safety and protocol checks for the read-only gateway probe."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import io
import json

SPEC = importlib.util.spec_from_file_location(
    "collective_gateway_probe", Path(__file__).resolve().parents[1] / "scripts" / "collective_gateway_probe.py")
probe_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe_module)


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self.raw = io.BytesIO(json.dumps(payload).encode())
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, size):
        return self.raw.read(size)


class GatewayProbeTest(unittest.TestCase):
    def test_rejects_insecure_remote_before_network(self):
        with patch.object(probe_module, "urlopen") as opened:
            with self.assertRaises(ValueError):
                probe_module.probe("http://example.com:8765", "collective-" + "a"*32, "x" * 20)
            opened.assert_not_called()

    def test_success_requires_both_service_and_authenticated_episode(self):
        episode = "collective-" + "a"*32
        with patch.object(probe_module, "urlopen", side_effect=[
            FakeResponse(200, {"service": "rezon-collective", "status": "ready"}),
            FakeResponse(200, {"episode_id": episode, "agent_id": "lappy"}),
        ]) as opened:
            result = probe_module.probe("http://127.0.0.1:8765", episode, "secret" * 4)
        self.assertEqual(result["episode"], "authorized")
        self.assertEqual(opened.call_count, 2)
        self.assertIsNone(opened.call_args_list[0].args[0].get_header("Authorization"))
        self.assertEqual(opened.call_args_list[1].args[0].get_header("Authorization"), "Bearer " + "secret" * 4)

    def test_unrelated_listener_never_claims_rezon(self):
        with patch.object(probe_module, "urlopen", return_value=FakeResponse(200, {"status": "ready"})) as opened:
            result = probe_module.probe("http://127.0.0.1:8765", "collective-" + "a"*32, "secret" * 4)
        self.assertEqual(result["gateway"], "unverified")
        self.assertEqual(opened.call_count, 1)

    def test_admin_access_is_not_worker_enrollment(self):
        with patch.object(probe_module, "urlopen", side_effect=[
            FakeResponse(200, {"service": "rezon-collective", "status": "ready"}),
            FakeResponse(200, {"episode_id": "collective-" + "a"*32, "agent_id": None}),
        ]):
            result = probe_module.probe("https://private.example", "collective-" + "a"*32, "secret" * 4)
        self.assertEqual(result["episode"], "unverified")

    def test_wrong_episode_never_claims_authorization(self):
        with patch.object(probe_module, "urlopen", side_effect=[
            FakeResponse(200, {"service": "rezon-collective", "status": "ready"}),
            FakeResponse(200, {"episode_id": "collective-" + "b"*32}),
        ]):
            result = probe_module.probe("https://private.example", "collective-" + "a"*32, "secret" * 4)
        self.assertEqual(result["episode"], "unverified")


if __name__ == "__main__":
    unittest.main()
