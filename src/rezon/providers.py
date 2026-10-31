"""Bounded HTTP adapters for independently configured language-model endpoints."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .collective import _agent


class ProviderError(RuntimeError):
    pass


class ProviderOutcomeUnknown(ProviderError):
    """A sent request may have completed remotely; do not retry it blindly."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _endpoint(base_url: str, suffix: str, allow_insecure_http: bool) -> str:
    if type(base_url) is not str:
        raise ValueError("endpoint must be a URL")
    parsed = urlsplit(base_url)
    if parsed.scheme not in ("https", "http") or not parsed.hostname or (
        parsed.username is not None or parsed.password is not None
        or parsed.query or parsed.fragment
    ):
        raise ValueError("invalid provider endpoint")
    try:
        parsed.port
    except ValueError as exc:
        raise ValueError("invalid provider port") from exc
    if parsed.scheme == "http" and not allow_insecure_http:
        try:
            local = ipaddress.ip_address(parsed.hostname).is_loopback
        except ValueError:
            local = parsed.hostname.lower() == "localhost"
        if not local:
            raise ValueError("remote provider endpoint requires HTTPS")
    path = parsed.path.rstrip("/")
    if not path:
        path = "/v1"
    if not path.endswith(suffix):
        path += suffix
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def _completion(value: object) -> str:
    if type(value) is not str or not value.strip() or len(value) > 32_768:
        raise ProviderError("provider returned invalid or oversized text")
    return value


def _request_origin(url: str, headers: dict[str, str], body: dict, timeout: float) -> dict:
    """Perform only the explicitly configured POST in the disposable child."""
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, method="POST", headers={
        **headers, "Content-Type": "application/json", "Accept": "application/json",
    })
    try:
        # A redirect guard alone cannot prevent HTTP(S)_PROXY from receiving a
        # credential before the first response. Use the configured origin only.
        with build_opener(ProxyHandler({}), _NoRedirect).open(request, timeout=timeout) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ProviderError("provider response too large")
            parsed = json.loads(raw)
    except HTTPError as exc:
        raise ProviderError(f"provider HTTP status {exc.code}") from None
    except (URLError, TimeoutError, OSError) as exc:
        raise ProviderError(f"provider transport failure: {type(exc).__name__}") from None
    except (ValueError, UnicodeError):
        raise ProviderError("invalid provider JSON") from None
    if type(parsed) is not dict:
        raise ProviderError("invalid provider response shape")
    return parsed


def _communicate_bounded(child: subprocess.Popen, serialized: bytes,
                         deadline: float, *, max_stdout: int = 1_100_000) -> bytes:
    """Drain stdout concurrently with stdin, retaining at most max_stdout bytes.

    `Popen.communicate` accumulates a child's entire stdout before the caller
    can examine its size. That turns a compromised child into an arbitrary
    memory amplifier. Two disposable daemon threads avoid cross-platform
    `select` limitations on Windows pipes; the parent retains deadline and
    kill/reap custody in its surrounding finally block.
    """
    output = bytearray()
    read_done = threading.Event()
    write_done = threading.Event()
    status: dict[str, bool] = {"oversized": False, "reader_error": False,
                               "writer_error": False}

    def reader() -> None:
        try:
            while True:
                # read1 returns currently available data instead of waiting
                # for a full chunk from a slow-dripping child process.
                block = child.stdout.read1(65_536)
                if not block:
                    break
                if len(output) + len(block) > max_stdout:
                    status["oversized"] = True
                    break
                output.extend(block)
        except (OSError, ValueError):
            status["reader_error"] = True
        finally:
            read_done.set()

    def writer() -> None:
        try:
            view = memoryview(serialized)
            for offset in range(0, len(view), 65_536):
                child.stdin.write(view[offset:offset + 65_536])
                child.stdin.flush()
        except (OSError, ValueError):
            status["writer_error"] = True
        finally:
            try:
                child.stdin.close()
            except OSError:
                pass
            write_done.set()

    threads = (
        threading.Thread(target=reader, name="rezon-bounded-stdout", daemon=True),
        threading.Thread(target=writer, name="rezon-bounded-stdin", daemon=True),
    )
    for thread in threads:
        thread.start()
    while True:
        if status["oversized"]:
            raise ProviderOutcomeUnknown("completion child stdout limit exceeded; outcome unknown")
        if status["reader_error"] or status["writer_error"]:
            raise ProviderOutcomeUnknown("completion child pipe failed; outcome unknown")
        if read_done.is_set() and write_done.is_set() and child.poll() is not None:
            return bytes(output)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ProviderOutcomeUnknown("completion total deadline exceeded; outcome unknown")
        read_done.wait(min(0.01, remaining))


def _request(url: str, headers: dict[str, str], body: dict, timeout: float) -> dict:
    """Enforce one monotonic deadline across connection and slow-drip response.

    urllib socket timeouts apply to each blocking receive, so a server may
    trickle bytes forever. A separately killable child protects the caller's
    deadline without a non-killable background thread or inherited descriptors.
    """
    if type(timeout) not in (int, float) or not 0 < timeout <= 300:
        raise ValueError("invalid completion timeout")
    # Account for serialization as well as child launch, network and response.
    # A budget consumed before the child is started proves no POST was sent.
    start = time.monotonic()
    try:
        serialized = json.dumps({
            "url": url, "headers": headers, "body": body, "timeout": timeout,
        }, ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError, RecursionError, UnicodeError):
        raise ProviderError("invalid completion request") from None
    if len(serialized) > 8_500_000:
        raise ProviderError("completion request too large")
    if time.monotonic() - start >= timeout:
        raise ProviderError("completion deadline expired before dispatch")
    # -I ignores ambient PYTHONPATH and user site; module path is explicitly
    # pinned to the currently imported provider source rather than cwd.
    package_parent = str(Path(__file__).resolve().parent.parent)
    child_script = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from rezon._completion_request_child import main; main()"
    )
    # Python -I still inherits the entire parent process environment unless
    # env is explicitly supplied. No model key, proxy, Python startup hooks,
    # provider token, credential-store or arbitrary inherited env is needed.
    child_env: dict[str, str] = {}
    if os.name == "nt":
        # Windows may require its system root when initializing side-by-side
        # assemblies. This is the only ambient OS variable admitted here.
        system_root = os.environ.get("SystemRoot")
        if system_root:
            child_env["SystemRoot"] = system_root

    child = None
    private_workdir = None
    try:
        # Avoid giving the child access to a potentially user-writable or
        # secret-bearing caller worktree. The resolved module source is passed
        # explicitly in argv and remains independent of this empty directory.
        private_workdir = tempfile.TemporaryDirectory(prefix="rezon-completion-")
        if time.monotonic() - start >= timeout:
            raise ProviderError("completion deadline expired before dispatch")
        child = subprocess.Popen(
            [sys.executable, "-I", "-c", child_script, package_parent],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, close_fds=True,
            env=child_env, cwd=private_workdir.name,
        )
        output = _communicate_bounded(child, serialized, start + timeout)
    except ProviderOutcomeUnknown:
        raise
    except (OSError, RuntimeError, ValueError):
        # A successfully spawned child may already have dispatched its POST.
        if child is not None:
            raise ProviderOutcomeUnknown("completion child failed; outcome unknown") from None
        raise ProviderError("completion child unavailable before dispatch") from None
    finally:
        # Includes KeyboardInterrupt / task cancellation (BaseException).
        # Preserve the caller's interruption signal but never strand the
        # local network-capable subprocess. Child death does not roll back a
        # request already received at the origin.
        if child is not None:
            try:
                if child.poll() is None:
                    child.kill()
            except OSError:
                pass
            try:
                child.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired):
                pass
            for stream in (child.stdin, child.stdout):
                try:
                    if stream is not None and not stream.closed:
                        stream.close()
                except OSError:
                    pass
        if private_workdir is not None:
            try:
                private_workdir.cleanup()
            except OSError:
                pass
    if child.returncode != 0 or len(output) > 1_100_000:
        raise ProviderOutcomeUnknown("completion child failed after dispatch; outcome unknown")
    try:
        result = json.loads(output)
    except (UnicodeError, ValueError, RecursionError):
        raise ProviderOutcomeUnknown("invalid completion child result; outcome unknown") from None
    if type(result) is not dict or set(result) not in ({"result"}, {"error"}):
        raise ProviderOutcomeUnknown("invalid completion child result; outcome unknown")
    if "error" in result:
        if type(result["error"]) is not str or len(result["error"]) > 256:
            raise ProviderOutcomeUnknown("invalid completion child result; outcome unknown")
        raise ProviderOutcomeUnknown("provider completion failed; outcome unknown")
    if type(result["result"]) is not dict:
        raise ProviderOutcomeUnknown("invalid completion child result; outcome unknown")
    return result["result"]


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate catalog field")
        result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class ModelAvailabilityReceipt:
    """An endpoint's catalog claim, never proof of a loaded or independent model."""

    agent_id: str
    model_id: str
    advertised: bool
    evidence_class: str = "ENDPOINT_CATALOG_UNATTESTED"
    host_identity_verified: bool = False
    inference_verified: bool = False
    authority: str = "NONE"


def _probe_catalog_origin(base_url: str, model: str, api_key: str,
                          allow_insecure_http: bool, timeout_seconds: float) -> bool:
    """Run only inside the disposable catalog probe child process.

    This endpoint claim is not host/process attestation. The parent enforces
    the total deadline by terminating this child on timeout.
    """
    url = _endpoint(base_url, "/models", allow_insecure_http)
    request = Request(url, method="GET", headers={
        "Authorization": "Bearer " + api_key,
        "Accept": "application/json",
    })
    try:
        # No environment HTTP_PROXY/HTTPS_PROXY, no redirects carrying secrets.
        opener = build_opener(ProxyHandler({}), _NoRedirect)
        with opener.open(request, timeout=timeout_seconds) as response:
            if response.status != 200:
                raise ProviderError("catalog request failed")
            raw = response.read(131_073)
            if len(raw) > 131_072:
                raise ProviderError("catalog response over limit")
            parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                                parse_constant=lambda _value: (_ for _ in ()).throw(ValueError()))
    except (HTTPError, URLError, TimeoutError, OSError):
        raise ProviderError("catalog request failed") from None
    except (ValueError, UnicodeError, RecursionError):
        raise ProviderError("invalid model catalog") from None
    if type(parsed) is not dict or type(parsed.get("data")) is not list:
        raise ProviderError("invalid model catalog")
    entries = parsed["data"]
    if len(entries) > 256:
        raise ProviderError("catalog too many models")
    ids: set[str] = set()
    for entry in entries:
        if (type(entry) is not dict or type(entry.get("id")) is not str
                or not entry["id"] or len(entry["id"]) > 512):
            raise ProviderError("invalid model catalog")
        model_id = entry["id"]
        try:
            model_id.encode("utf-8")
        except UnicodeError:
            raise ProviderError("invalid model catalog") from None
        if model_id in ids:
            raise ProviderError("duplicate catalog model")
        ids.add(model_id)
    return model in ids


def _messages(values: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    if type(values) is not tuple or not values or len(values) > 32:
        raise ValueError("invalid model messages")
    result = []
    for item in values:
        if type(item) is not dict or set(item) != {"role", "content"} or (
            item["role"] not in ("system", "user", "assistant")
            or type(item["content"]) is not str
            or not item["content"] or len(item["content"]) > 250_000
        ):
            raise ValueError("invalid model message")
        result.append({"role": item["role"], "content": item["content"]})
    return result


@dataclass(frozen=True)
class OpenAICompatibleModel:
    """OpenAI-style chat completions, including compatible local servers."""

    agent_id: str
    model: str
    base_url: str
    api_key: str
    timeout_seconds: float = 30.0
    allow_insecure_http: bool = False
    max_tokens: int | None = None
    reasoning_effort: str | None = None

    def __post_init__(self):
        _agent(self.agent_id)
        if type(self.model) is not str or not self.model:
            raise ValueError("model is required")
        if type(self.api_key) is not str or not self.api_key:
            raise ValueError("API key is required")
        if type(self.timeout_seconds) not in (int, float) or not 0 < self.timeout_seconds <= 300:
            raise ValueError("invalid timeout")
        if self.max_tokens is not None and (type(self.max_tokens) is not int or not 1 <= self.max_tokens <= 16384):
            raise ValueError("invalid max tokens")
        if self.reasoning_effort is not None and (type(self.reasoning_effort) is not str or not 1 <= len(self.reasoning_effort) <= 32):
            raise ValueError("invalid reasoning effort")
        _endpoint(self.base_url, "/chat/completions", self.allow_insecure_http)

    def complete(self, messages: tuple[dict[str, str], ...]) -> str:
        body = {"model": self.model, "messages": _messages(messages), "stream": False}
        if self.max_tokens is not None:
            body["max_tokens"] = self.max_tokens
        if self.reasoning_effort is not None:
            body["reasoning_effort"] = self.reasoning_effort
        response = _request(
            _endpoint(self.base_url, "/chat/completions", self.allow_insecure_http),
            {"Authorization": f"Bearer {self.api_key}"}, body,
            self.timeout_seconds,
        )
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise ProviderOutcomeUnknown(
                "provider returned unusable chat completion after dispatch; outcome unknown"
            ) from None
        try:
            return _completion(content)
        except ProviderError:
            raise ProviderOutcomeUnknown(
                "provider returned unusable chat completion after dispatch; outcome unknown"
            ) from None

    def probe_availability(self, *, timeout_seconds: float = 5.0) -> ModelAvailabilityReceipt:
        """One bounded read-only `/v1/models` probe; never promotes endpoint claims.

        This does not authenticate the process/host running the endpoint, prove
        the advertised model is loaded, or reserve memory for a later inference.
        """
        if (type(timeout_seconds) not in (float, int)
                or not 0 < timeout_seconds <= 10):
            raise ValueError("invalid bounded catalog timeout")
        # Validate before spawning a child or transferring a credential.
        _endpoint(self.base_url, "/models", self.allow_insecure_http)
        if (len(self.base_url) > 2048 or len(self.model) > 512
                or len(self.api_key) > 512):
            raise ValueError("oversized catalog configuration")
        serialized = json.dumps({
            "base_url": self.base_url, "model": self.model,
            "api_key": self.api_key, "allow_insecure_http": self.allow_insecure_http,
            "timeout_seconds": timeout_seconds,
        }).encode("utf-8")
        start = time.monotonic()
        child = None
        private_workdir = None
        try:
            private_workdir = tempfile.TemporaryDirectory(prefix="rezon-catalog-")
            if time.monotonic() - start >= timeout_seconds:
                raise ProviderError("catalog deadline exceeded before child launch")
            # An isolated -I Python must receive the currently reviewed module
            # source explicitly; its empty cwd and env provide no imports.
            package_parent = str(Path(__file__).resolve().parent.parent)
            child_script = (
                "import sys; sys.path.insert(0, sys.argv[1]); "
                "from rezon._catalog_probe_child import main; raise SystemExit(main())"
            )
            child_env: dict[str, str] = {}
            if os.name == "nt":
                system_root = os.environ.get("SystemRoot")
                if system_root:
                    child_env["SystemRoot"] = system_root
            child = subprocess.Popen(
                [sys.executable, "-I", "-c", child_script, package_parent],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, close_fds=True,
                env=child_env, cwd=private_workdir.name,
            )
            output = _communicate_bounded(
                child, serialized, start + timeout_seconds, max_stdout=1024,
            )
        except ProviderOutcomeUnknown:
            # Catalog is a read-only, unauthenticated availability claim. Its
            # failure is generic rather than a POST replay ambiguity.
            raise ProviderError("catalog deadline, output or child failure") from None
        except ProviderError:
            raise
        except (OSError, RuntimeError, ValueError):
            raise ProviderError("catalog child unavailable") from None
        finally:
            # Includes caller interruption. A child timeout cannot strand a
            # credential-carrying catalog subprocess or its pipe handles.
            if child is not None:
                try:
                    if child.poll() is None:
                        child.kill()
                except OSError:
                    pass
                try:
                    child.wait(timeout=1)
                except (OSError, subprocess.TimeoutExpired):
                    pass
                for stream in (child.stdin, child.stdout):
                    try:
                        if stream is not None and not stream.closed:
                            stream.close()
                    except OSError:
                        pass
            if private_workdir is not None:
                try:
                    private_workdir.cleanup()
                except OSError:
                    pass
        if child.returncode != 0 or len(output) > 1024:
            raise ProviderError("catalog request failed")
        try:
            response = json.loads(output)
        except (ValueError, UnicodeError):
            raise ProviderError("invalid catalog child result") from None
        if (type(response) is not dict or set(response) != {"advertised"}
                or type(response["advertised"]) is not bool):
            raise ProviderError("invalid catalog child result")
        return ModelAvailabilityReceipt(self.agent_id, self.model, response["advertised"])


@dataclass(frozen=True)
class AnthropicModel:
    """Anthropic Messages API adapter with explicit system/message separation."""

    agent_id: str
    model: str
    base_url: str
    api_key: str
    timeout_seconds: float = 30.0
    allow_insecure_http: bool = False
    max_tokens: int = 2048

    def __post_init__(self):
        _agent(self.agent_id)
        if type(self.model) is not str or not self.model or type(self.api_key) is not str or not self.api_key:
            raise ValueError("model and API key are required")
        if not 0 < self.timeout_seconds <= 300 or type(self.max_tokens) is not int or not 0 < self.max_tokens <= 8192:
            raise ValueError("invalid provider bounds")
        _endpoint(self.base_url, "/messages", self.allow_insecure_http)

    def complete(self, messages: tuple[dict[str, str], ...]) -> str:
        values = _messages(messages)
        system = "\n".join(v["content"] for v in values if v["role"] == "system")
        conversational = [v for v in values if v["role"] != "system"]
        if not conversational:
            raise ValueError("Anthropic request requires a user/assistant message")
        body = {"model": self.model, "max_tokens": self.max_tokens,
                "messages": conversational}
        if system:
            body["system"] = system
        response = _request(
            _endpoint(self.base_url, "/messages", self.allow_insecure_http),
            {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
            body, self.timeout_seconds,
        )
        try:
            blocks = response["content"]
            if type(blocks) is not list:
                raise TypeError
            content = "\n".join(item["text"] for item in blocks if item["type"] == "text")
        except (KeyError, TypeError):
            raise ProviderOutcomeUnknown(
                "provider returned unusable Anthropic completion after dispatch; outcome unknown"
            ) from None
        try:
            return _completion(content)
        except ProviderError:
            raise ProviderOutcomeUnknown(
                "provider returned unusable Anthropic completion after dispatch; outcome unknown"
            ) from None
