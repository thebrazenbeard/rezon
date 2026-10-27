"""Explicit opt-in CLI for the Rezon collective reasoning prototype."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .collective import (
    CollectiveStore, run_independent_models, run_peer_reviews, synthesize_with_model,
)
from .collective_http import make_server
from .collective_evidence import import_dossier
from .providers import AnthropicModel, OpenAICompatibleModel


def _load_config(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ValueError("model configuration must be a JSON object")
    return value


def _model(spec: dict):
    if type(spec) is not dict or not {"provider", "agent_id", "model", "base_url", "api_key_env"}.issubset(spec):
        raise ValueError("invalid model specification")
    if set(spec) - {"provider", "agent_id", "model", "base_url", "api_key_env", "allow_insecure_http", "timeout_seconds", "max_tokens", "reasoning_effort"}:
        raise ValueError("unexpected model specification fields")
    if type(spec["api_key_env"]) is not str or not spec["api_key_env"]:
        raise ValueError("API key environment-variable name required")
    secret = os.environ.get(spec["api_key_env"])
    if not secret:
        raise ValueError("model API-key environment variable not set")
    insecure = spec.get("allow_insecure_http", False)
    if type(insecure) is not bool:
        raise ValueError("allow_insecure_http must be boolean")
    args = (spec["agent_id"], spec["model"], spec["base_url"], secret)
    timeout = spec.get("timeout_seconds", 30.0)
    if spec["provider"] == "openai_compatible":
        return OpenAICompatibleModel(*args, allow_insecure_http=insecure,
            timeout_seconds=timeout, max_tokens=spec.get("max_tokens"),
            reasoning_effort=spec.get("reasoning_effort"))
    if spec["provider"] == "anthropic":
        if "max_tokens" in spec or "reasoning_effort" in spec:
            raise ValueError("unsupported Anthropic model options")
        return AnthropicModel(*args, allow_insecure_http=insecure, timeout_seconds=timeout)
    raise ValueError("unknown provider type")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Opt-in Rezon collaborative reasoning")
    sub = parser.add_subparsers(dest="command", required=True)
    server = sub.add_parser("serve", help="Start authenticated loopback agent gateway")
    server.add_argument("--db", type=Path, required=True)
    server.add_argument("--port", type=int, default=8765)
    server.add_argument("--integrator-config", type=Path)
    server.add_argument("--tkal", action="store_true",
                        help="Enable virtual Tkal hearings on existing loopback gateway")
    run = sub.add_parser("run", help="Run independent providers concurrently and synthesize")
    run.add_argument("--db", type=Path, required=True)
    run.add_argument("--prompt", required=True)
    run.add_argument("--models-config", type=Path, required=True)
    run.add_argument("--integrator-config", type=Path, required=True)
    imported = sub.add_parser("import-findings", help="Import an externally authored, unverified agent dossier")
    imported.add_argument("--db", type=Path, required=True)
    imported.add_argument("--manifest", type=Path, required=True)
    synthesis = sub.add_parser("synthesize-episode", help="Use a real configured model to synthesize a complete episode")
    synthesis.add_argument("--db", type=Path, required=True)
    synthesis.add_argument("--episode-id", required=True)
    synthesis.add_argument("--integrator-config", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        store = CollectiveStore(args.db)
        if args.command == "import-findings":
            # Explicit local file import only; no automatic Blotter access,
            # remote publication, model calls, or manufactured findings.
            if args.manifest.stat().st_size > 1_000_000:
                raise ValueError("dossier is too large")
            episode_id = import_dossier(store, _load_config(args.manifest))
            snap = store.snapshot(episode_id)
            print(json.dumps({"episode_id": episode_id, "complete": snap.complete,
                              "answers": len(snap.answers), "reviews": len(snap.reviews),
                              "input_digest": snap.digest,
                              "status": "external_agent_claims_unverified"}, sort_keys=True))
            return 0
        if args.command == "synthesize-episode":
            integrator = _model(_load_config(args.integrator_config))
            item = synthesize_with_model(store, args.episode_id, integrator)
            print(json.dumps({"episode_id": args.episode_id, "input_digest": item.input_digest,
                              "synthesis": item.content, "status": item.status}, sort_keys=True))
            return 0
        if args.command == "serve":
            admin_token = os.environ.get("REZON_COLLECTIVE_ADMIN_TOKEN", "")
            read_token = os.environ.get("REZON_COLLECTIVE_STATE_READ_TOKEN") or None
            worker_json = os.environ.get("REZON_COLLECTIVE_WORKER_TOKENS_JSON", "")
            worker_tokens = json.loads(worker_json)
            integrator = _model(_load_config(args.integrator_config)) if args.integrator_config else None
            if args.tkal:
                from .tkal_network import TkalVirtualNetwork
                hearing = TkalVirtualNetwork(store)
            else:
                hearing = None
            instance = make_server(store, admin_token, worker_tokens, integrator,
                                   port=args.port, tkal_network=hearing,
                                   read_token=read_token)
            try:
                print(f"Rezon collective gateway listening on 127.0.0.1:{instance.server_port}")
                instance.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                instance.server_close()
            return 0
        config = _load_config(args.models_config)
        specs = config.get("models")
        if type(specs) is not list or not specs:
            raise ValueError("models config must contain a nonempty models list")
        models = tuple(_model(spec) for spec in specs)
        integrator = _model(_load_config(args.integrator_config))
        episode_id = store.create(args.prompt, tuple(model.agent_id for model in models))
        results = run_independent_models(store, episode_id, models)
        snapshot = store.snapshot(episode_id)
        if not snapshot.complete:
            print(json.dumps({"episode_id": episode_id, "worker_results": results,
                              "complete": False}, sort_keys=True))
            return 2
        review_results = run_peer_reviews(store, episode_id, models)
        if any(status.startswith("failed:") for status in review_results.values()):
            print(json.dumps({"episode_id": episode_id, "worker_results": results,
                              "review_results": review_results, "complete": False}, sort_keys=True))
            return 2
        synthesis = synthesize_with_model(store, episode_id, integrator)
        print(json.dumps({"episode_id": episode_id, "worker_results": results,
                          "review_results": review_results,
                          "complete": True, "input_digest": synthesis.input_digest,
                          "synthesis": synthesis.content,
                          "status": synthesis.status}, sort_keys=True))
        return 0
    except Exception as exc:
        # Never print arbitrary provider exception text, or configured tokens.
        print(f"collective operation failed: {type(exc).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
