"""Disposable, one-request process for bounded catalog probing.

The parent terminates this process if an endpoint trickles bytes beyond the
wall deadline. Config and token arrive through stdin, never command arguments;
stdout contains only a boolean claim, never secrets or remote response text.
"""

from __future__ import annotations

import json
import sys

from .providers import _probe_catalog_origin


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(8193)
        if len(raw) > 8192:
            return 2
        config = json.loads(raw)
        if type(config) is not dict or set(config) != {
            "base_url", "model", "api_key", "allow_insecure_http", "timeout_seconds",
        }:
            return 2
        if (type(config["base_url"]) is not str or type(config["model"]) is not str
                or type(config["api_key"]) is not str
                or type(config["allow_insecure_http"]) is not bool
                or type(config["timeout_seconds"]) not in (float, int)):
            return 2
        advertised = _probe_catalog_origin(**config)
        sys.stdout.write(json.dumps({"advertised": advertised}, separators=(",", ":")))
        return 0
    except Exception:
        # Untrusted endpoint text and secrets must never appear in a traceback.
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
