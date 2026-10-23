"""Read-only Rezon collective gateway reachability and enrollment probe.

Do not use this as host attestation or authorization to activate ingress.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def probe(base_url: str, episode_id: str, token: str, timeout: float = 5.0) -> dict:
    url = urlsplit(base_url)
    if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError("invalid base URL")
    if url.scheme == "http" and url.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("remote transport must use HTTPS")
    if not episode_id.startswith("collective-") or not episode_id.removeprefix("collective-").isalnum():
        raise ValueError("invalid episode id")
    base = base_url.rstrip("/")
    def request(path: str, authenticated: bool) -> tuple[int, dict]:
        headers = {"Accept": "application/json"}
        if authenticated:
            headers["Authorization"] = "Bearer " + token
        req = Request(base + path, headers=headers, method="GET")
        try:
            response = urlopen(req, timeout=timeout)
        except HTTPError as exc:
            response = exc
        with response:
            raw = response.read(65537)
            if len(raw) > 65536:
                raise ValueError("oversized response")
            try:
                payload = json.loads(raw)
            except (ValueError, UnicodeDecodeError):
                payload = {}
            return response.status, payload if isinstance(payload, dict) else {}
    status, health = request("/healthz", False)
    if status != 200 or health.get("service") != "rezon-collective" or health.get("status") != "ready":
        return {"gateway": "unverified", "health_status": status, "episode": "not_checked"}
    status, episode = request("/v1/episodes/" + episode_id, True)
    if status != 200 or episode.get("episode_id") != episode_id:
        return {"gateway": "reachable", "episode": "unverified", "episode_status": status}
    return {"gateway": "reachable", "episode": "authorized", "episode_id": episode_id,
            "note": "Bearer access is not physical-host or model independence attestation"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--episode", required=True)
    parser.add_argument("--token-env", required=True, help="Name of environment variable holding worker bearer token")
    args = parser.parse_args()
    token = os.environ.get(args.token_env, "")
    if len(token) < 16 or not token.isascii() or not token.isprintable():
        print(json.dumps({"error": "missing_or_invalid_token_environment"}))
        return 2
    try:
        result = probe(args.url, args.episode, token)
    except (ValueError, URLError, TimeoutError, OSError) as exc:
        # Never echo transport exceptions: URLs may contain private infrastructure.
        result = {"gateway": "unverified", "episode": "not_checked", "error_type": type(exc).__name__}
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("episode") == "authorized" else 1


if __name__ == "__main__":
    sys.exit(main())
