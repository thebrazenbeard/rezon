"""Fail-closed probes for the older VN2 gateway's liveness vocabulary.

These are synthetic HTTP responses, not requests to a real host. A legacy
``/healthz`` response reporting ``ready`` cannot establish current readiness.
"""

import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "gateway_probe_legacy_contract",
    Path(__file__).resolve().parents[1] / "scripts" / "collective_gateway_probe.py",
)
probe_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe_module)


class SyntheticReply:
    def __init__(self, status: int, payload: dict):
        self.status = status
        self._stream = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, limit: int):
        return self._stream.read(limit)


class DeployedLegacyContractTests(unittest.TestCase):
    _episode = "collective-" + "a" * 32
    _token = "synthetic-worker-credential-123456"

    def test_legacy_health_ready_never_qualifies_a_gateway_or_transmits_bearer(self):
        # The older VN2 service reported this exact health vocabulary; it
        # predates the modern liveness/readiness separation.
        legacy = {"service": "rezon-collective", "status": "ready"}
        with patch.object(probe_module, "urlopen", return_value=SyntheticReply(200, legacy)) as opened:
            result = probe_module.probe("http://127.0.0.1:18765", self._episode, self._token)

        self.assertEqual(result, {
            "gateway": "unverified", "health_status": 200,
            "episode": "not_checked",
        })
        self.assertEqual(opened.call_count, 1)
        request = opened.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:18765/healthz")
        self.assertIsNone(request.get_header("Authorization"))

    def test_modern_liveness_does_not_promote_failed_authenticated_readiness(self):
        with patch.object(probe_module, "urlopen", side_effect=[
            SyntheticReply(200, {"service": "rezon-collective", "status": "alive"}),
            SyntheticReply(401, {"error": "unauthorized"}),
        ]) as opened:
            result = probe_module.probe("http://127.0.0.1:18765", self._episode, self._token)

        self.assertEqual(result, {
            "gateway": "reachable", "readiness": "unavailable",
            "readiness_status": 401, "episode": "not_checked",
        })
        self.assertEqual(opened.call_count, 2)
        self.assertEqual(opened.call_args_list[1].args[0].get_header("Authorization"),
                         "Bearer " + self._token)
        self.assertFalse(any("/v1/episodes/" in call.args[0].full_url
                             for call in opened.call_args_list))


if __name__ == "__main__":
    unittest.main()
