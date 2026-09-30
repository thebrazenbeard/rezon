from __future__ import annotations

import argparse
import json
from pathlib import Path

from rezon.portfolio_assurance import assure_project_runner_wave


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Rezon assurance over a Project Runner advancement-wave JSON file."
    )
    parser.add_argument("wave", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.wave.read_text(encoding="utf-8"))
    result = assure_project_runner_wave(payload)
    output = {
        "passed": result.passed,
        "subject_count": result.subject_count,
        "queued_count": result.queued_count,
        "held_count": result.held_count,
        "findings": [
            {
                "code": finding.code,
                "severity": finding.severity,
                "subject_id": finding.subject_id,
                "message": finding.message,
            }
            for finding in result.findings
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
