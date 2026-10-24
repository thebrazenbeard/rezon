"""Explicit, owner-local Rezon enrollment; no remote credential distribution.

An owner provides their assigned bearer in a private local terminal.
Before storing it in the OS vault, Rezon's real gateway must confirm that
the token is bound to the EXACT requested worker role and episode.
Every later one-shot action re-verifies that role before model execution.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys

from . import credential_store
from .worker_client import OutcomeUnknown, run as client_run


class EnrollmentError(ValueError):
    pass


def _role(role: str) -> None:
    try:
        credential_store.validate_role(role)
    except credential_store.CredentialError:
        raise EnrollmentError("invalid worker role") from None


def _verify(role: str, gateway: str, episode: str, token: str,
            timeout: int = 40) -> dict:
    try:
        status = client_run("status", gateway, episode, token, timeout=timeout)
    except Exception:
        raise EnrollmentError("gateway refused worker identity verification") from None
    if (type(status) is not dict or status.get("agent_id") != role or
            (status.get("episode_id") is not None and
             status.get("episode_id") != episode)):
        raise EnrollmentError("enrolled credential does not match required role")
    return status


def enroll(role: str, gateway: str, episode: str) -> dict:
    """Owner must perform this in a local terminal; no secret ever returned."""
    _role(role)
    token = getpass.getpass("Assigned " + role + " worker bearer (hidden): ")
    try:
        credential_store.validate_token(token)
        _verify(role, gateway, episode, token)
        credential_store.save(role, token)
    except (credential_store.CredentialError, EnrollmentError):
        raise EnrollmentError("worker enrollment verification or storage failed") from None
    return {"agent_id": role, "episode_id": episode, "enrolled": True,
            "authority": "NONE", "host_independence_verified": False}


def execute(action: str, role: str, gateway: str, episode: str,
            model_id: str | None = None,
            model_url: str = "http://127.0.0.1:11434/v1",
            model_key: str | None = None, timeout: int = 120,
            max_tokens: int = 240) -> dict:
    """One explicit request: status -> optional model inference -> one POST."""
    _role(role)
    if action not in ("status", "answer", "review"):
        raise EnrollmentError("invalid worker operation")
    try:
        token = credential_store.load(role)
    except credential_store.CredentialError:
        raise EnrollmentError("worker role is not enrolled locally") from None
    state = _verify(role, gateway, episode, token, timeout=timeout)
    if action == "status":
        return state
    return client_run(action, gateway, episode, token,
                      model_id=model_id, model_url=model_url,
                      model_api_key=model_key, timeout=timeout,
                      max_tokens=max_tokens)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Operator-local role-bound Rezon worker enrollment"
    )
    p.add_argument("action", choices=("enroll", "status", "answer", "review"))
    p.add_argument("--role", required=True, choices=sorted(credential_store.ROLES))
    p.add_argument("--gateway", required=True)
    p.add_argument("--episode", required=True)
    p.add_argument("--model")
    p.add_argument("--model-url", default="http://127.0.0.1:11434/v1")
    p.add_argument("--model-key-env", default="REZON_MODEL_API_KEY")
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--max-tokens", type=int, default=240)
    args = p.parse_args(argv)
    try:
        if args.action == "enroll":
            result = enroll(args.role, args.gateway, args.episode)
        else:
            result = execute(args.action, args.role, args.gateway,
                             args.episode, model_id=args.model,
                             model_url=args.model_url,
                             model_key=os.environ.get(args.model_key_env),
                             timeout=args.timeout, max_tokens=args.max_tokens)
    except OutcomeUnknown:
        print("OUTCOME_UNKNOWN: read server state before any retry", file=sys.stderr)
        return 3
    except Exception:
        # Never echo provider errors, gateway payloads, or credential values.
        print("owner worker operation failed", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
