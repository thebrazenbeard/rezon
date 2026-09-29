from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .audit import verify_run_evidence
from .consultation import (
    ConsultationIntakeError,
    inspect_ensemble_consultation,
)
from .interop import RunEvidenceError
from .otel import OTelIntakeError, inspect_otel_export
from .otel_genai import (
    OTelGenAIIntakeError,
    bind_otel_genai_to_run_evidence,
    inspect_otel_genai_export,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rezon",
        description="Rezon portable reasoning-evidence utilities",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    verify = commands.add_parser(
        "verify-evidence",
        help="verify a rezon.run-evidence.v1 JSON artifact",
    )
    verify.add_argument("path", type=Path)

    inspect_consultation = commands.add_parser(
        "inspect-consultation",
        help="inspect external ensemble consultation without trust promotion",
    )
    inspect_consultation.add_argument("path", type=Path)

    inspect_generic_otel = commands.add_parser(
        "inspect-otel",
        help="inspect generic OTLP/JSON telemetry without semantic promotion",
    )
    inspect_generic_otel.add_argument("path", type=Path)

    inspect_otel = commands.add_parser(
        "inspect-otel-genai",
        help="inspect OTLP/JSON GenAI telemetry without trust promotion",
    )
    inspect_otel.add_argument("path", type=Path)

    bind_otel = commands.add_parser(
        "bind-otel-evidence",
        help="bind OTLP/JSON workflow telemetry to verified Rezon evidence",
    )
    bind_otel.add_argument("trace_path", type=Path)
    bind_otel.add_argument("evidence_path", type=Path)
    return parser


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    try:
        if args.command == "verify-evidence":
            report = verify_run_evidence(_load_json(args.path))
        elif args.command == "inspect-consultation":
            report = inspect_ensemble_consultation(_load_json(args.path))
        elif args.command == "inspect-otel":
            report = inspect_otel_export(_load_json(args.path))
        elif args.command == "inspect-otel-genai":
            report = inspect_otel_genai_export(_load_json(args.path))
        elif args.command == "bind-otel-evidence":
            report = bind_otel_genai_to_run_evidence(
                _load_json(args.trace_path),
                _load_json(args.evidence_path),
            )
        else:
            return 2
    except (
        OSError,
        json.JSONDecodeError,
        RunEvidenceError,
        ConsultationIntakeError,
        OTelIntakeError,
        OTelGenAIIntakeError,
    ) as exc:
        print(
            json.dumps({"valid": False, "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
