from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from rezon.replay import load_replay_cases
from rezon.replay_experiments import (
    digest_strategy_inputs,
    run_guard_ablation,
    run_label_permutation_control,
    run_order_permutations,
)
from rezon.replay_metrics import StrategyMetrics, compare_reports, evaluate_strategy
from rezon.replay_strategies import fixed_multipass, rezon_guarded, single_pass


DOES_NOT_PROVE = [
    "live end-to-end reasoning superiority",
    "provider or model quality",
    "deployment, installation, activation, or runtime effect",
    "general reasoning improvement outside this frozen replay population",
]


def _metric_vector(metrics: StrategyMetrics) -> dict[str, object]:
    return {
        "semantic": {
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
        },
        "cost": {
            "operation_count": metrics.operation_count,
            "wall_clock_seconds": metrics.wall_clock_seconds,
        },
    }


def _pairwise_payload(left: StrategyMetrics, right: StrategyMetrics) -> dict[str, object]:
    delta = compare_reports(left, right)
    return {
        "left_strategy": delta.left_strategy,
        "right_strategy": delta.right_strategy,
        "deltas": dict(delta.deltas),
    }


def build_report(
    fixture_path: Path,
    *,
    seed: int,
    code_version: str,
) -> dict[str, object]:
    fixture_bytes = fixture_path.read_bytes()
    cases = load_replay_cases(fixture_path)
    versions = {case.fixture_version for case in cases}
    if len(versions) != 1:
        raise ValueError("Benchmark V1 requires exactly one fixture version per run")
    fixture_version = next(iter(versions))

    strategies = {
        "single_pass": single_pass,
        "fixed_multipass": fixed_multipass,
        "rezon_guarded": rezon_guarded,
    }
    metrics = {
        name: evaluate_strategy(cases, strategy, strategy_name=name)
        for name, strategy in strategies.items()
    }

    strategy_names = tuple(strategies)
    pairwise = [
        _pairwise_payload(metrics[strategy_names[left]], metrics[strategy_names[right]])
        for left in range(len(strategy_names))
        for right in range(left + 1, len(strategy_names))
    ]

    ablations = run_guard_ablation(cases)
    order_results = run_order_permutations(
        cases,
        rezon_guarded,
        strategy_name="rezon_guarded",
        seeds=(seed, seed + 1),
    )
    label_result = run_label_permutation_control(
        cases,
        rezon_guarded,
        strategy_name="rezon_guarded",
        seed=seed,
    )

    return {
        "benchmark": "rezon-benchmark-v1-layer1",
        "fixture_version": fixture_version,
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "code_version": code_version,
        "case_count": len(cases),
        "strategy_input_digest": digest_strategy_inputs(cases),
        "strategies": {
            name: _metric_vector(metrics[name])
            for name in strategy_names
        },
        "pairwise_deltas": pairwise,
        "guard_ablation": [
            {
                "removed_guard": result.removed_guard.value,
                "strategy_input_digest": result.strategy_input_digest,
                "metrics": _metric_vector(result.metrics),
            }
            for result in ablations
        ],
        "order_permutations": [
            {
                "seed": result.seed,
                "permutation_id": result.permutation_id,
                "case_order": list(result.case_order),
                "strategy_input_digest": result.strategy_input_digest,
                "metrics": _metric_vector(result.metrics),
            }
            for result in order_results
        ],
        "label_permutation": {
            "seed": label_result.seed,
            "permutation_id": label_result.permutation_id,
            "before_strategy_input_digest": label_result.before_strategy_input_digest,
            "after_strategy_input_digest": label_result.after_strategy_input_digest,
            "original_metrics": _metric_vector(label_result.original_metrics),
            "permuted_metrics": _metric_vector(label_result.permuted_metrics),
        },
        "does_not_prove": DOES_NOT_PROVE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Rezon Benchmark V1 Layer 1 replay")
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--code-version", required=True)
    args = parser.parse_args()

    report = build_report(
        args.fixture,
        seed=args.seed,
        code_version=args.code_version,
    )
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
