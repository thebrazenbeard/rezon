"""Bounded HTTP adapters for independently configured language-model endpoints."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .collective import _agent


class ProviderError(RuntimeError):
    pass


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


def _request(url: str, headers: dict[str, str], body: dict, timeout: float) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, method="POST", headers={
        **headers, "Content-Type": "application/json", "Accept": "application/json",
    })
    try:
        # Never follow a redirect carrying Authorization or API-key headers.
        with build_opener(_NoRedirect).open(request, timeout=timeout) as response:
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
            raise ProviderError("missing chat completion content") from None
        return _completion(content)


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
            raise ProviderError("invalid Anthropic message content") from None
        return _completion(content)
