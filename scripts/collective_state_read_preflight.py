"""Credential-free, read-only preflight for an opt-in PORTAL/Rezon V2 observer.

This checks an exact clean source checkout and a single anonymous loopback
challenge. It deliberately CANNOT authenticate the returned HMAC, read an
episode, qualify another host, or authorize a service upgrade/deployment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
from time import monotonic


_REVISION = re.compile(r"[0-9a-f]{40}\Z")
_EPISODE = re.compile(r"collective-[0-9a-f]{32}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_HEX32 = re.compile(r"[0-9a-f]{32}\Z")
_MAX_WIRE = 8192
_TIMEOUT = 3.0


def _valid_target(port: int, episode_id: str) -> None:
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("port must be a numeric TCP port")
    if type(episode_id) is not str or _EPISODE.fullmatch(episode_id) is None:
        raise ValueError("one exact Rezon episode id is required")


def source_revision_verified(source_checkout: Path, expected_head: str) -> bool:
    """Reject dirty or wrong-version source; never modify or fetch checkout."""
    if type(expected_head) is not str or _REVISION.fullmatch(expected_head) is None:
        raise ValueError("an exact 40-character source commit is required")
    try:
        root = Path(source_checkout).resolve(strict=True)
        if not root.is_dir():
            return False
        top_level = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True, timeout=_TIMEOUT,
        )
        if Path(top_level.stdout.strip()).resolve() != root:
            return False
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=_TIMEOUT,
        )
        if head.stdout.strip() != expected_head:
            return False
        # Include staged, unstaged and untracked (non-ignored) additions so a
        # source overlay cannot silently masquerade as an exact Git checkout.
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
            check=True, capture_output=True, timeout=_TIMEOUT,
        )
        return status.stdout == b""
    except (OSError, subprocess.SubprocessError, ValueError):
        return False


def validate_response(
    wire: bytes, port: int, episode_id: str, client_nonce: str,
) -> tuple[bool, int | None]:
    """Check transport framing and challenge shape, never HMAC authenticity."""
    if type(wire) is not bytes or len(wire) > _MAX_WIRE:
        return False, None
    header, separator, body = wire.partition(b"\r\n\r\n")
    if not separator or len(body) > 4096:
        return False, None
    lines = header.split(b"\r\n")
    if not lines or re.fullmatch(rb"HTTP/1\.[01] [0-9]{3} [^\r\n]*", lines[0]) is None:
        return False, None
    status = int(lines[0].split(b" ", 2)[1])
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if b":" not in line or line.startswith((b" ", b"\t")):
            return False, status
        name, value = line.split(b":", 1)
        try:
            key = name.decode("ascii").lower()
            decoded = value.strip().decode("ascii")
        except UnicodeDecodeError:
            return False, status
        if re.fullmatch(r"[a-z0-9-]+", key) is None or key in headers:
            return False, status
        headers[key] = decoded
    if ("transfer-encoding" in headers or
            re.fullmatch(r"[0-9]{1,5}", headers.get("content-length", "")) is None or
            int(headers["content-length"]) != len(body)):
        return False, status
    if status != 200:
        return False, status
    if headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
        return False, status
    def no_duplicate_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
        fields: dict[str, object] = {}
        for key, value in pairs:
            if key in fields:
                raise ValueError("duplicate challenge field")
            fields[key] = value
        return fields

    try:
        challenge = json.loads(body.decode("utf-8"), object_pairs_hook=no_duplicate_fields)
    except (UnicodeError, ValueError):
        return False, status
    if type(challenge) is not dict:
        return False, status
    if set(challenge) != {
        "server_nonce", "epoch", "proof", "issued_ms", "expires_in_ms",
        "state_path", "client_nonce", "audience",
    }:
        return False, status
    expected_path = f"/v1/episodes/{episode_id}/state"
    valid = (
        type(challenge.get("server_nonce")) is str
        and _HEX64.fullmatch(challenge["server_nonce"]) is not None
        and type(challenge.get("epoch")) is str
        and _HEX32.fullmatch(challenge["epoch"]) is not None
        and type(challenge.get("proof")) is str
        and _HEX64.fullmatch(challenge["proof"]) is not None
        and type(challenge.get("issued_ms")) is int
        and 0 < challenge["issued_ms"] < 2**64
        and challenge.get("expires_in_ms") == 10_000
        and challenge.get("state_path") == expected_path
        and challenge.get("client_nonce") == client_nonce
        and challenge.get("audience") == f"127.0.0.1:{port}"
    )
    return bool(valid), status


def probe_challenge(port: int, episode_id: str) -> tuple[bool, int | None]:
    """One bounded, no-credential GET to numeric loopback; never follow URLs."""
    _valid_target(port, episode_id)
    client_nonce = secrets.token_hex(32)
    path = f"/v1/episodes/{episode_id}/state"
    request = (
        f"GET /v1/read-challenge HTTP/1.0\r\nHost: 127.0.0.1:{port}\r\n"
        f"X-Rezon-State-Path: {path}\r\n"
        f"X-Rezon-Client-Nonce: {client_nonce}\r\n"
        "Accept: application/json\r\nConnection: close\r\n\r\n"
    ).encode("ascii")
    deadline = monotonic() + _TIMEOUT
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=_TIMEOUT) as connection:
            connection.settimeout(max(0.001, deadline - monotonic()))
            connection.sendall(request)
            wire = bytearray()
            while True:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return False, None
                connection.settimeout(remaining)
                chunk = connection.recv(min(2048, _MAX_WIRE + 1 - len(wire)))
                if not chunk:
                    break
                wire.extend(chunk)
                if len(wire) > _MAX_WIRE:
                    return False, None
    except (OSError, TimeoutError):
        return False, None
    return validate_response(bytes(wire), port, episode_id, client_nonce)


def qualify(source_checkout: Path, expected_head: str,
            port: int, episode_id: str) -> dict[str, object]:
    """Preflight only; a passing result is *not* deployment qualification."""
    _valid_target(port, episode_id)
    source_ok = source_revision_verified(source_checkout, expected_head)
    challenge_ok, status = probe_challenge(port, episode_id) if source_ok else (False, None)
    return {
        "schema": "REZON_VN2_STATE_READ_PREFLIGHT_V1",
        "status": "CHALLENGE_ONLY" if source_ok and challenge_ok else "HOLD",
        "source_revision_verified": source_ok,
        "challenge_shape_valid": challenge_ok,
        "http_status": status,
        "authenticated_state_verified": False,
        "independent_host_verified": False,
        "activation_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--episode", required=True)
    args = parser.parse_args(argv)
    try:
        result = qualify(args.source_checkout, args.expected_head,
                         args.port, args.episode)
    except ValueError:
        result = {"schema": "REZON_VN2_STATE_READ_PREFLIGHT_V1", "status": "HOLD",
                  "error": "invalid_preflight_configuration", "activation_authorized": False}
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("status") == "CHALLENGE_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
