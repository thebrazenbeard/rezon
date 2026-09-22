from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rezon.replay import load_replay_cases
from rezon.replay_experiments import digest_strategy_inputs
from rezon.replay_metrics import compare_reports, evaluate_strategy
from rezon.replay_strategies import fixed_multipass, rezon_guarded, single_pass


DOES_NOT_PROVE = [
    "independent benchmark performance",
    "generalization beyond the frozen manually authored corpus",
    "live external runtime behavior",
    "live provider or model quality",
    "universal external-runtime compatibility",
    "producer authenticity",
    "worker independence beyond fixture-visible bindings",
    "semantic truth outside the frozen fixture labels",
    "deployment, installation, authorization, or external effect completion",
]


def _metrics(metrics):
    return {
        "total_cases": metrics.total_cases,
        "disposition_correct": metrics.disposition_correct,
        "disposition_accuracy": metrics.disposition_accuracy,
        "answer_attempts": metrics.answer_attempts,
        "answer_correct": metrics.answer_correct,
        "answer_accuracy": metrics.answer_accuracy,
        "false_accepts": metrics.false_accepts,
        "false_rejects": metrics.false_rejects,
        "false_abstains": metrics.false_abstains,
        "unsupported_acceptance": metrics.unsupported_acceptance,
        "provenance_currentness_accepted": metrics.provenance_currentness_accepted,
        "correlated_consensus_laundering_accepted": (
            metrics.correlated_consensus_laundering_accepted
        ),
        "hidden_failure_acceptance": metrics.hidden_failure_acceptance,
        "authority_effect_promotion_errors": metrics.authority_effect_promotion_errors,
        "required_violation_hits": metrics.required_violation_hits,
        "required_violation_total": metrics.required_violation_total,
        "required_violation_recall": metrics.required_violation_recall,
        "operation_count": metrics.operation_count,
        "wall_clock_seconds": metrics.wall_clock_seconds,
    }


def build_report(path: Path, *, code_version: str) -> dict[str, object]:
    raw = path.read_bytes()
    cases = load_replay_cases(path)
    versions = {case.fixture_version for case in cases}
    if versions != {"external-assurance-v1.0"}:
        raise ValueError(
            "external assurance evaluation requires external-assurance-v1.0"
        )

    strategies = {
        "trace_only_primary": single_pass,
        "ungoverned_exact_vote": fixed_multipass,
        "rezon_guarded": rezon_guarded,
    }
    results = {
        name: evaluate_strategy(cases, strategy, strategy_name=name)
        for name, strategy in strategies.items()
    }

    pairs = (
        ("rezon_guarded", "trace_only_primary"),
        ("rezon_guarded", "ungoverned_exact_vote"),
    )

    return {
        "evaluation": "rezon-assurance-regression-v1",
        "evaluation_classification": "internal_manual_adversarial_regression",
        "independent_evaluation": False,
        "pre_registered_before_guard_design": False,
        "external_runtime_evidence": False,
        "fixture_version": "external-assurance-v1.0",
        "fixture_path": str(path),
        "fixture_sha256": hashlib.sha256(raw).hexdigest(),
        "strategy_input_digest": digest_strategy_inputs(cases),
        "code_version": code_version,
        "case_count": len(cases),
        "strategies": {
            name: _metrics(results[name])
            for name in strategies
        },
        "pairwise_deltas": [
            {
                "left_strategy": left,
                "right_strategy": right,
                "deltas": dict(compare_reports(results[left], results[right]).deltas),
            }
            for left, right in pairs
        ],
        "does_not_prove": DOES_NOT_PROVE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run Rezon internal manually authored adversarial assurance regression V1"
        )
    )
    parser.add_argument(
        "fixture",
        type=Path,
        nargs="?",
        default=Path("tests/fixtures/external_assurance_v1.json"),
    )
    parser.add_argument("--code-version", required=True)
    args = parser.parse_args()

    report = build_report(args.fixture, code_version=args.code_version)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
