"""Reproducible local HTTP/T'Kal end-to-end qualification with ephemeral credentials.

This does not enroll a production worker, attest a host, or authorize effects.
Only a caller-supplied *loopback* model can be contacted.
"""
from __future__ import annotations

import argparse
from http.client import HTTPConnection
import ipaddress
import json
import os
from pathlib import Path
import secrets
import sys
from threading import Thread
from urllib.parse import urlsplit

from .collective import CollectiveStore
from .collective_http import make_server
from .tkal_network import TkalVirtualNetwork
from .worker_client import run as worker_run


class QualificationError(ValueError):
    pass


ROSTER = ("lappy", "vn1", "vn2", "malaphor")
LENSES = {"purist_logic": "vn1", "pragmatism": "vn2", "bridge": "malaphor"}


def _validate_model_url(value: str) -> None:
    if type(value) is not str:
        raise QualificationError("model URL invalid")
    p = urlsplit(value)
    try:
        port = p.port
    except ValueError:
        raise QualificationError("model port invalid") from None
    try:
        loopback = ipaddress.ip_address(p.hostname or "").is_loopback
    except ValueError:
        loopback = p.hostname == "localhost"
    if (p.scheme != "http" or not loopback or port is None or
            p.path not in ("", "/", "/v1", "/v1/") or p.query or
            p.fragment or p.username or p.password):
        raise QualificationError("only loopback model API is permitted")


def qualify(output: Path, *, model: str | None = None,
            model_url: str = "http://127.0.0.1:11435/v1",
            max_tokens: int = 120) -> dict:
    """Exercise real loopback HTTP, real persistent SQLite and optional local model."""
    path = Path(output)
    if path.exists():
        raise QualificationError("output path already exists")
    if type(max_tokens) is not int or not 1 <= max_tokens <= 1024:
        raise QualificationError("invalid bounded model token count")
    if model is not None:
        if type(model) is not str or not model.strip():
            raise QualificationError("invalid model name")
        _validate_model_url(model_url)
    path.mkdir(parents=True, mode=0o700)
    if os.name == "posix":
        path.chmod(0o700)
    store = CollectiveStore(path / "qual.sqlite3")
    network = TkalVirtualNetwork(store)
    tokens = {role: secrets.token_urlsafe(32) for role in ROSTER}
    admin = secrets.token_urlsafe(32)
    if len(set([admin, *tokens.values()])) != 5:
        raise QualificationError("nonunique temporary credentials")
    server = make_server(store, admin, tokens, port=0, tkal_network=network)
    if server.server_address[0] != "127.0.0.1":
        raise QualificationError("nonloopback gateway")
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    gateway = "http://127.0.0.1:" + str(server.server_port)

    def api(route: str, role: str | None = None,
            method: str = "GET", data: dict | None = None) -> tuple[int, dict]:
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=12)
        headers = {"Content-Type": "application/json"}
        if role is not None:
            headers["Authorization"] = "Bearer " + (
                admin if role == "admin" else tokens[role]
            )
        try:
            conn.request(method, route, body=json.dumps(data).encode()
                         if data is not None else None, headers=headers)
            res = conn.getresponse()
            raw = res.read(1_000_001)
            if len(raw) > 1_000_000:
                raise QualificationError("response over limit")
            return res.status, json.loads(raw) if raw else {}
        finally:
            conn.close()

    episode_id = None
    try:
        assert api("/healthz")[0] == 200
        assert api("/v1/episodes/collective-" + "0" * 32)[0] == 401
        prompt = ("Does a 90-day in-house technician training intervention "
                  "reduce unplanned downtime 20% under matched equipment controls?")
        expected_roster = list(ROSTER)
        body = {"prompt": prompt, "agents": expected_roster}
        assert api("/v1/episodes", "vn1", "POST", body)[0] == 403
        status, created = api("/v1/episodes", "admin", "POST", body)
        assert status == 201
        episode_id = created["episode_id"]
        root = "/v1/episodes/" + episode_id
        assert api(root + "/state", "lappy")[0] == 409

        if model is not None:
            receipt = worker_run("answer", gateway, episode_id, tokens["vn2"],
                                 model_id=model, model_url=model_url,
                                 model_api_key="qualification-loopback-only",
                                 timeout=120, max_tokens=max_tokens)
            assert receipt["contribution_id"] == "answer:vn2"
            assert receipt["gateway_status"] == "ACCEPTED_UNATTESTED"
        else:
            assert api(root + "/answers", "vn2", "POST", {
                "content": "TEST FIXTURE vn2: evaluate counterfactual baseline.",
                "source_refs": []})[0] == 201
        for role in ("lappy", "vn1", "malaphor"):
            status, submitted = api(root + "/answers", role, "POST", {
                "content": "TEST FIXTURE " + role +
                    ": preregistered matched control, safety stops, confounders.",
                "source_refs": []})
            assert status == 201 and submitted["contribution_id"] == "answer:" + role
        status, view = api(root + "/state", "vn1")
        assert status == 200 and view["complete"] is True
        assert len(view["answers"]) == 4
        assert api(root + "/reviews", "vn1", "POST", {
            "content": "invalid self-review", "target_ids": ["answer:vn1"],
            "source_refs": []})[0] == 400
        for role in ROSTER:
            targets = ["answer:" + peer for peer in ROSTER if peer != role]
            status, review = api(root + "/reviews", role, "POST", {
                "content": "TEST REVIEW " + role + ": challenge unjustified controls.",
                "target_ids": targets, "source_refs": []})
            assert status == 201 and review["contribution_id"] == "review:" + role
        assert api(root + "/answers", "vn1", "POST", {
            "content": "conflicting replay", "source_refs": []})[0] == 409
        initial = store.snapshot(episode_id)
        assert len(initial.answers) == len(initial.reviews) == 4
        assert all(len(r.target_ids) == 3 and "answer:" + r.agent_id not in
                   r.target_ids for r in initial.reviews)

        hearing = root + "/tkal"
        proposed = {
            "expected_digest": initial.digest, "proposer": "lappy",
            "lenses": dict(LENSES),
            "hypothesis": "Training improves controlled downtime outcomes.",
            "falsifier": "Held-out matched controls do not confirm benefit.",
        }
        assert api(hearing, "vn1", "POST", proposed)[0] == 403
        assert api(hearing, "admin", "POST", proposed)[0] == 201
        verdict = {"verdict": "SUSTAIN", "rationale": "premature"}
        assert api(hearing + "/determination", "admin", "POST", verdict)[0] == 409
        assert api(hearing + "/challenges", "lappy", "POST", {
            "challenge_id": "invalid", "target": "vn1",
            "question": "Role spoof attempt"})[0] == 400

        for lens, role in LENSES.items():
            challenge = "qualification-" + lens
            assert api(hearing + "/challenges", role, "POST", {
                "challenge_id": challenge, "target": "lappy",
                "question": "What controlled evidence supports this lens?"})[0] == 201
            impostor = "vn2" if role != "vn2" else "vn1"
            assert api(hearing + "/defenses", impostor, "POST", {
                "challenge_id": challenge, "response": "forged defense",
                "evidence_ref": "test:forged"})[0] == 400
            assert api(hearing + "/resolutions", "admin", "POST", {
                "challenge_id": challenge, "disposition": "ANSWERED",
                "rationale": "without a defense"})[0] == 409
            assert api(hearing + "/defenses", "lappy", "POST", {
                "challenge_id": challenge,
                "response": "TEST FIXTURE: no causal empirical evidence provided.",
                "evidence_ref": "test:synthetic"})[0] == 201
            assert api(hearing + "/resolutions", "admin", "POST", {
                "challenge_id": challenge, "disposition": "ANSWERED",
                "rationale": "Response attributed, not evidence of efficacy."})[0] == 201

        status, decision = api(hearing + "/determination", "admin", "POST", {
            "verdict": "REFINE", "rationale":
                "Auth and protocol mechanics tested; effectiveness unproven."})
        assert status == 201 and decision["verdict"] == "REFINE"
        assert api(hearing + "/challenges", "vn1", "POST", {
            "challenge_id": "late", "target": "lappy",
            "question": "Forbidden late challenge"})[0] == 409
        saved_digest = initial.digest
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=8)

    assert episode_id is not None
    reopened_store = CollectiveStore(path / "qual.sqlite3")
    reopened = reopened_store.snapshot(episode_id)
    persisted_hearing = TkalVirtualNetwork(reopened_store).snapshot(episode_id)
    assert reopened.complete and len(reopened.answers) == len(reopened.reviews) == 4
    assert reopened.digest == saved_digest
    assert persisted_hearing.verdict == "REFINE"
    assert len(persisted_hearing.challenges) == 3
    assert all(c["disposition"] == "ANSWERED" and c["response"]
               for c in persisted_hearing.challenges)

    report = {
        "qualification": "ISOLATED_TKAL_REFINE",
        "episode_id": episode_id,
        "answer_count": 4, "review_count": 4, "challenges": 3,
        "defenses": 3, "verdict": persisted_hearing.verdict,
        "live_model_calls": int(model is not None),
        "fixture_answer_count": 3 if model is not None else 4,
        "unauthenticated_denied": True, "self_review_denied": True,
        "self_challenge_denied": True, "premature_verdict_denied": True,
        "unanswered_resolution_denied": True, "closed_hearing_denied": True,
        "persisted_reopen": True, "state_digest": saved_digest,
        "production_credential_access": False, "host_attestation": False,
        "independence_verified": False, "authority": "NONE",
    }
    (path / "report.json").write_text(json.dumps(report, sort_keys=True,
                                indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Isolated authentic HTTP TKIK protocol test")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", help="Optional real LOCAL OpenAI-compatible model ID")
    parser.add_argument("--model-url", default="http://127.0.0.1:11435/v1")
    parser.add_argument("--max-tokens", type=int, default=120)
    args = parser.parse_args(argv)
    try:
        report = qualify(args.output, model=args.model,
                         model_url=args.model_url, max_tokens=args.max_tokens)
    except Exception as exc:
        # Do not leak provider or transport details that could contain secrets.
        print("isolated qualification FAILED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
