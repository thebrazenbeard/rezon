"""Disposable explicit-origin model completion worker for a total wall deadline.

Receives secrets on stdin, never in argv. Caller kills this process on timeout.
"""

import json
import sys

from .providers import ProviderError, _request_origin


def main() -> None:
    try:
        raw = sys.stdin.buffer.read(8_500_001)
        if len(raw) > 8_500_000:
            raise ValueError("oversized completion request")
        payload = json.loads(raw)
        if (type(payload) is not dict or set(payload) !=
                {"url", "headers", "body", "timeout"}
                or type(payload["url"]) is not str
                or type(payload["headers"]) is not dict
                or type(payload["body"]) is not dict
                or type(payload["timeout"]) not in (int, float)):
            raise ValueError("invalid completion request")
        result = _request_origin(payload["url"], payload["headers"],
                                 payload["body"], payload["timeout"])
        response = {"result": result}
    except ProviderError as exc:
        response = {"error": str(exc)}
    except (ValueError, TypeError, RecursionError, UnicodeError):
        response = {"error": "invalid completion request"}
    output = json.dumps(response, ensure_ascii=False).encode("utf-8")
    if len(output) > 1_100_000:
        raise SystemExit(1)
    sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
