"""Authenticated loopback HTTP gateway for concurrent external Rezon workers.

Transport is deliberately separate from the in-process reasoning kernel.
Nonlocal use requires a separately governed authenticated TLS reverse proxy.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
from hashlib import sha256
import json
import re
import secrets
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit

from .collective import (
    CollectiveConflict, CollectiveNotFound, CollectiveStore,
    CollectiveValidationError, ReasoningModel, _agent, synthesize_with_model,
)


class CollectiveHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = True


_CHALLENGE_TTL = 10.0
_MAX_CONSUMED_CHALLENGES = 4096
_READ_PREFLIGHT_DOMAIN = b"rezon-state-read/preflight/v2\0"
_READ_REQUEST_DOMAIN = b"rezon-state-read/request/v2\0"
_READ_RESPONSE_DOMAIN = b"rezon-state-read/response/v2\0"
_EXACT_STATE_PATH = re.compile(r"/v1/episodes/collective-[0-9a-f]{32}/state\Z")


def _read_context(path: str, audience: str, server_nonce: str,
                  client_nonce: str, issued_ms: int, epoch: str) -> bytes:
    return (b"GET\0" + path.encode("ascii") + b"\0" + audience.encode("ascii")
            + b"\0" + bytes.fromhex(server_nonce) + bytes.fromhex(client_nonce)
            + issued_ms.to_bytes(8, "big") + bytes.fromhex(epoch))


def _request_mac_message(context: bytes) -> bytes:
    return _READ_REQUEST_DOMAIN + context


def _response_mac_message(context: bytes, raw: bytes) -> bytes:
    return _READ_RESPONSE_DOMAIN + context + sha256(raw).digest()


class _Handler(BaseHTTPRequestHandler):
    server: CollectiveHTTPServer
    # Close every request. A rejected POST may leave unread bytes and must not
    # share a keep-alive connection with a subsequent request.
    protocol_version = "HTTP/1.0"

    def log_message(self, *_args):
        # No token, model-output or prompt data in HTTP access logs.
        return

    def _local_audience(self) -> str:
        # Actual accepted server socket, never the remotely supplied Host header.
        host, port = self.connection.getsockname()[:2]
        if host != "127.0.0.1" or not isinstance(port, int):
            raise ValueError("non-loopback state read connection")
        return f"{host}:{port}"

    def _json(self, status: int, value: dict) -> None:
        raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        context = getattr(self, "_read_response_context", None)
        if status == 200 and context is not None:
            proof = hmac.new(bytes.fromhex(self.server.read_token),
                _response_mac_message(context, raw), sha256).hexdigest()
            self.send_header("X-Rezon-State-Proof", proof)
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(raw)
        self.close_connection = True

    def _identity(self, *, method: str, path: str) -> tuple[str, str | None] | None:
        # A proxy and this origin may otherwise pick different values from
        # duplicate singleton headers and disagree about the authenticated role.
        authorization = self.headers.get_all("Authorization", [])
        if len(authorization) != 1:
            return None
        header = authorization[0]
        if header.startswith("Rezon-Read-HMAC "):
            if self.server.read_token is None or method != "GET" or not _EXACT_STATE_PATH.fullmatch(path):
                return None
            fields = header[len("Rezon-Read-HMAC "):].split(".")
            if len(fields) != 5:
                return None
            server_nonce, client_nonce, issued_text, epoch, proof = fields
            if any(not re.fullmatch(r"[0-9a-f]{64}", value)
                   for value in (server_nonce, client_nonce, proof)) or not re.fullmatch(
                r"[0-9a-f]{32}", epoch
            ) or not re.fullmatch(r"[1-9][0-9]{0,18}", issued_text):
                return None
            issued_ms = int(issued_text)
            audience = self._local_audience()
            now_ms = int(monotonic() * 1000)
            if epoch != self.server.read_epoch or not 0 <= now_ms - issued_ms <= 10_000:
                return None
            context = _read_context(path, audience, server_nonce, client_nonce,
                                    issued_ms, epoch)
            # Stateless issuance: the MAC binds this exact method, path,
            # socket-local audience, server epoch, and both nonces.
            expected = hmac.new(bytes.fromhex(self.server.read_token),
                _request_mac_message(context), sha256).hexdigest()
            if not hmac.compare_digest(expected, proof):
                return None
            with self.server.read_consumed_lock:
                now = monotonic()
                self.server.read_consumed = {nonce: used
                    for nonce, used in self.server.read_consumed.items()
                    if 0 <= now - used <= _CHALLENGE_TTL}
                if server_nonce in self.server.read_consumed or len(
                    self.server.read_consumed
                ) >= _MAX_CONSUMED_CHALLENGES:
                    return None
                self.server.read_consumed[server_nonce] = now
            self._read_response_context = context
            return ("observer", None)
        if not header.startswith("Bearer ") or not header[7:]:
            return None
        token = header[7:]
        if not token.isascii() or not token.isprintable() or len(token) > 256:
            return None
        if hmac.compare_digest(token, self.server.admin_token):
            return ("admin", None)
        for agent, known_token in self.server.worker_tokens.items():
            if hmac.compare_digest(token, known_token):
                return ("worker", agent)
        return None

    def _body(self) -> dict:
        lengths = self.headers.get_all("Content-Length", [])
        types = self.headers.get_all("Content-Type", [])
        if len(lengths) != 1 or len(types) != 1 or self.headers.get_all("Transfer-Encoding"):
            raise CollectiveValidationError("unambiguous JSON framing required")
        try:
            length = int(lengths[0])
        except ValueError:
            raise CollectiveValidationError("content length required")
        if not 0 <= length <= 65_536:
            raise CollectiveValidationError("invalid request size")
        if types[0].split(";")[0].strip().lower() != "application/json":
            raise CollectiveValidationError("JSON content type required")
        try:
            body = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise CollectiveValidationError("invalid JSON") from None
        if type(body) is not dict:
            raise CollectiveValidationError("expected JSON object")
        return body

    def _dispatch(self, method: str) -> None:
        path = urlsplit(self.path)
        if method == "GET" and path.path == "/healthz" and not path.query:
            self._json(200, {"service": "rezon-collective", "status": "ready"})
            return
        if method == "GET" and path.path == "/v1/read-challenge" and not path.query:
            if self.server.read_token is None:
                self._json(404, {"error": "reader not configured"})
                return
            requested_paths = self.headers.get_all("X-Rezon-State-Path", [])
            requested_client_nonces = self.headers.get_all("X-Rezon-Client-Nonce", [])
            if len(requested_paths) != 1 or not _EXACT_STATE_PATH.fullmatch(requested_paths[0]):
                self._json(400, {"error": "exact state path required"})
                return
            if len(requested_client_nonces) != 1 or not re.fullmatch(
                r"[0-9a-f]{64}", requested_client_nonces[0]
            ):
                self._json(400, {"error": "client nonce required"})
                return
            state_path = requested_paths[0]
            client_nonce = requested_client_nonces[0]
            audience = self._local_audience()
            nonce = secrets.token_hex(32)
            issued_ms = int(monotonic() * 1000)
            epoch = self.server.read_epoch
            context = _read_context(state_path, audience, nonce, client_nonce,
                                    issued_ms, epoch)
            preflight_proof = hmac.new(bytes.fromhex(self.server.read_token),
                _READ_PREFLIGHT_DOMAIN + context, sha256).hexdigest()
            self._json(200, {"server_nonce": nonce, "expires_in_ms": 10000,
                             "audience": audience, "state_path": state_path,
                             "client_nonce": client_nonce, "issued_ms": issued_ms,
                             "epoch": epoch,
                             "proof": preflight_proof})
            return
        identity = self._identity(method=method, path=path.path)
        if identity is None:
            self._json(401, {"error": "unauthorized"})
            return
        role, agent = identity
        segments = path.path.strip("/").split("/")
        if path.query or segments[:2] != ["v1", "episodes"]:
            self._json(404, {"error": "not found"})
            return
        # An observer can fetch only immutable claims about one requested
        # episode. It must never inherit admin creation/synthesis or worker
        # answer/review authority, even if future endpoints are added.
        if role == "observer" and not (
            method == "GET" and len(segments) == 4 and segments[3] == "state"
        ):
            self._json(403, {"error": "read-only state credential"})
            return
        try:
            if method == "POST" and len(segments) == 2:
                if role != "admin":
                    self._json(403, {"error": "admin required"})
                    return
                body = self._body()
                if set(body) != {"prompt", "agents"} or type(body["agents"]) is not list:
                    raise CollectiveValidationError("expected prompt and agent roster")
                if any(type(agent) is not str or agent not in self.server.worker_tokens
                       for agent in body["agents"]):
                    raise CollectiveValidationError("all agents must have configured tokens")
                episode_id = self.server.store.create(body["prompt"], tuple(body["agents"]))
                self._json(201, {"episode_id": episode_id})
                return
            if len(segments) < 3 or len(segments) > 5:
                self._json(404, {"error": "not found"})
                return
            episode_id = segments[2]
            if type(episode_id) is not str or not episode_id.startswith("collective-"):
                self._json(404, {"error": "not found"})
                return
            snapshot = self.server.store.snapshot(episode_id)
            if role == "worker" and agent not in snapshot.agents:
                self._json(403, {"error": "not an episode participant"})
                return
            # Optional authenticated virtual hearing over the existing
            # loopback gateway. No network exposure or host attestation added.
            if len(segments) in (4, 5) and segments[3] == "tkal":
                network = self.server.tkal_network
                if network is None:
                    self._json(404, {"error": "hearing disabled"})
                    return
                if method == "GET" and len(segments) == 4:
                    self._json(200, network.snapshot(episode_id).to_dict())
                    return
                if method == "POST" and len(segments) == 4:
                    if role != "admin":
                        self._json(403, {"error": "admin required"})
                        return
                    body = self._body()
                    if set(body) != {"expected_digest", "proposer", "lenses",
                                     "hypothesis", "falsifier"}:
                        raise CollectiveValidationError("invalid hearing request")
                    view = network.open(episode_id, **body)
                    self._json(201, view.to_dict())
                    return
                if method == "POST" and len(segments) == 5:
                    action = segments[4]
                    body = self._body()
                    if action == "challenges":
                        if role != "worker" or set(body) != {
                            "challenge_id", "target", "question"
                        }:
                            self._json(403, {"error": "worker required or invalid fields"})
                            return
                        view = network.challenge(episode_id, reviewer=agent, **body)
                    elif action == "defenses":
                        if role != "worker" or set(body) != {
                            "challenge_id", "response", "evidence_ref"
                        }:
                            self._json(403, {"error": "worker required or invalid fields"})
                            return
                        view = network.defend(episode_id, defender=agent, **body)
                    elif action == "resolutions":
                        if role != "admin" or set(body) != {
                            "challenge_id", "disposition", "rationale"
                        }:
                            self._json(403, {"error": "admin required or invalid fields"})
                            return
                        view = network.resolve(episode_id, **body)
                    elif action in ("determination", "verdict"):
                        if role != "admin" or set(body) != {"verdict", "rationale"}:
                            self._json(403, {"error": "admin required or invalid fields"})
                            return
                        view = network.determine(episode_id, **body)
                    elif action == "withdrawals":
                        if role != "worker" or set(body) != {"reason"}:
                            self._json(403, {"error": "worker required or invalid fields"})
                            return
                        view = network.withdraw(episode_id, proposer=agent, **body)
                    else:
                        self._json(404, {"error": "unknown hearing action"})
                        return
                    self._json(201, view.to_dict())
                    return
                self._json(404, {"error": "not found"})
                return
            if method == "GET" and len(segments) == 3:
                self._json(200, {"episode_id": episode_id, "prompt": snapshot.prompt,
                                 "agent_id": agent, "answer_submitted": agent in {
                                     c.agent_id for c in snapshot.answers
                                 } if role == "worker" else None})
                return
            if len(segments) != 4:
                self._json(404, {"error": "not found"})
                return
            action = segments[3]
            if method == "GET" and action == "state":
                if role == "worker" and not snapshot.complete:
                    raise CollectiveConflict("peer state withheld until initial round is complete")
                self._json(200, snapshot.to_dict())
                return
            if method == "POST" and action in ("answers", "reviews"):
                if role != "worker":
                    self._json(403, {"error": "worker credential required"})
                    return
                body = self._body()
                if type(body.get("source_refs", [])) is not list:
                    raise CollectiveValidationError("source_refs must be a list")
                refs = tuple(body.get("source_refs", []))
                if action == "answers":
                    if set(body) - {"content", "source_refs"}:
                        raise CollectiveValidationError("unexpected answer fields")
                    result = self.server.store.submit_answer(episode_id, agent,
                        body.get("content"), refs)
                else:
                    if set(body) - {"content", "source_refs", "target_ids"} or (
                        type(body.get("target_ids")) is not list
                    ):
                        raise CollectiveValidationError("invalid review fields")
                    result = self.server.store.submit_review(episode_id, agent,
                        body.get("content"), tuple(body["target_ids"]), refs)
                self._json(201, {"contribution_id": result})
                return
            if method == "POST" and action == "synthesize":
                if role != "admin":
                    self._json(403, {"error": "admin required"})
                    return
                body = self._body()
                if body:
                    raise CollectiveValidationError("synthesis takes no untrusted configuration")
                if self.server.integrator is None:
                    self._json(503, {"error": "integrator not configured"})
                    return
                result = synthesize_with_model(self.server.store, episode_id,
                                               self.server.integrator)
                self._json(201, vars(result))
                return
            self._json(404, {"error": "not found"})
        except CollectiveNotFound:
            self._json(404, {"error": "unknown episode"})
        except CollectiveValidationError:
            self._json(400, {"error": "invalid request or contribution"})
        except CollectiveConflict:
            self._json(409, {"error": "conflict or incomplete reasoning round"})
        except Exception:
            # Provider failures can contain credentials; no exception body leaks.
            self._json(502, {"error": "provider or internal operation failed"})

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")


def make_server(store: CollectiveStore, admin_token: str,
                worker_tokens: dict[str, str],
                integrator: ReasoningModel | None = None,
                *, host: str = "127.0.0.1", port: int = 0,
                tkal_network=None, read_token: str | None = None) -> CollectiveHTTPServer:
    if type(store) is not CollectiveStore or host != "127.0.0.1":
        raise ValueError("collective service binds to IPv4 loopback only")
    if type(admin_token) is not str or not 16 <= len(admin_token) <= 256 or (
        type(worker_tokens) is not dict or not worker_tokens
    ):
        raise ValueError("strong admin and worker tokens required")
    for agent, token in worker_tokens.items():
        _agent(agent)
        if type(token) is not str or not 16 <= len(token) <= 256:
            raise ValueError("strong worker tokens required")
    if read_token is not None and (
        type(read_token) is not str or re.fullmatch(r"[0-9a-f]{64}", read_token) is None
        or len(set(read_token)) < 8
    ):
        raise ValueError("read-only state secret must be 32 random bytes encoded as 64 lowercase hex")
    tokens = (admin_token, *worker_tokens.values()) + (() if read_token is None else (read_token,))
    if any(not token.isascii() or not token.isprintable() or any(c.isspace() for c in token)
           for token in tokens):
        raise ValueError("bearer tokens must be printable ASCII without whitespace")
    if len(set(tokens)) != len(tokens):
        raise ValueError("all credentials must be distinct")
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("invalid port")
    server = CollectiveHTTPServer((host, port), _Handler)
    server.store = store
    server.admin_token = admin_token
    server.read_token = read_token
    server.read_epoch = secrets.token_hex(16)
    server.read_consumed = {}
    server.read_consumed_lock = Lock()
    server.worker_tokens = dict(worker_tokens)
    if tkal_network is not None:
        from .tkal_network import TkalVirtualNetwork
        if type(tkal_network) is not TkalVirtualNetwork or tkal_network.store is not store:
            server.server_close()
            raise ValueError("hearing must share the exact CollectiveStore")
    server.tkal_network = tkal_network
    server.integrator = integrator
    return server
