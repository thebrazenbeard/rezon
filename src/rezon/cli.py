from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .audit import verify_run_evidence
from .interop import RunEvidenceError


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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command != "verify-evidence":
        return 2

    try:
        payload = json.loads(args.path.read_text(encoding="utf-8"))
        report = verify_run_evidence(payload)
    except (OSError, json.JSONDecodeError, RunEvidenceError) as exc:
        print(
            json.dumps({"valid": False, "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
