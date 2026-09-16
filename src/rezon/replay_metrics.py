from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Callable

from .replay import Disposition, ReplayCase, ReplayStrategyOutcome, StrategyInput


StrategyCallable = Callable[[StrategyInput], ReplayStrategyOutcome]


def _normalize_answer(answer: str) -> str:
    return " ".join(answer.split()).casefold()


@dataclass(frozen=True)
class StrategyMetrics:
    strategy_name: str
    total_cases: int
    disposition_correct: int
    answer_attempts: int
    answer_correct: int
    false_accepts: int
    false_rejects: int
    false_abstains: int
    unsupported_acceptance: int
    provenance_currentness_accepted: int
    correlated_consensus_laundering_accepted: int
    hidden_failure_acceptance: int
    authority_effect_promotion_errors: int
    required_violation_hits: int
    required_violation_total: int
    operation_count: int
    wall_clock_seconds: float

    @property
    def disposition_accuracy(self) -> float:
        return self.disposition_correct / self.total_cases if self.total_cases else 0.0

    @property
    def answer_accuracy(self) -> float:
        return self.answer_correct / self.answer_attempts if self.answer_attempts else 0.0

    @property
    def required_violation_recall(self) -> float:
        if not self.required_violation_total:
            return 0.0
        return self.required_violation_hits / self.required_violation_total


@dataclass(frozen=True)
class PairwiseDelta:
    left_strategy: str
    right_strategy: str
    deltas: tuple[tuple[str, float | int], ...]


_VIOLATION_METRIC_MAP = {
    "UNSUPPORTED_CLAIM": "unsupported_acceptance",
    "PROVENANCE_CURRENTNESS": "provenance_currentness_accepted",
    "INDEPENDENCE_CONTAMINATION": "correlated_consensus_laundering_accepted",
    "FAILURE_VISIBILITY": "hidden_failure_acceptance",
    "AUTHORITY_EFFECT_BOUNDARY": "authority_effect_promotion_errors",
}


def evaluate_strategy(
    cases: tuple[ReplayCase, ...],
    strategy: StrategyCallable,
    *,
    strategy_name: str,
) -> StrategyMetrics:
    disposition_correct = 0
    answer_attempts = 0
    answer_correct = 0
    false_accepts = 0
    false_rejects = 0
    false_abstains = 0
    violation_acceptance = {metric: 0 for metric in _VIOLATION_METRIC_MAP.values()}
    required_violation_hits = 0
    required_violation_total = 0
    operation_count = 0
    wall_clock_seconds = 0.0

    for case in cases:
        case.validate()
        strategy_input = case.to_strategy_input()
        outcome = strategy(strategy_input)

        if outcome.disposition is case.gold_disposition:
            disposition_correct += 1

        if case.gold_disposition is Disposition.ANSWER:
            if outcome.disposition is Disposition.ANSWER:
                answer_attempts += 1
                if (
                    outcome.answer is not None
                    and case.gold_answer is not None
                    and _normalize_answer(outcome.answer) == _normalize_answer(case.gold_answer)
                ):
                    answer_correct += 1
                else:
                    false_accepts += 1
            elif outcome.disposition is Disposition.ABSTAIN:
                false_abstains += 1
            elif outcome.disposition is Disposition.FAIL_CLOSED:
                false_rejects += 1
        elif outcome.disposition is Disposition.ANSWER:
            false_accepts += 1

        detected = set(outcome.violations_detected)
        expected = set(case.expected_violations)
        required_violation_total += len(case.expected_violations)
        required_violation_hits += len(expected.intersection(detected))

        if outcome.disposition is Disposition.ANSWER:
            for violation in expected:
                metric_name = _VIOLATION_METRIC_MAP.get(violation)
                if metric_name is not None:
                    violation_acceptance[metric_name] += 1

        operation_count += outcome.operation_count
        if outcome.wall_clock_seconds is not None:
            wall_clock_seconds += outcome.wall_clock_seconds

    return StrategyMetrics(
        strategy_name=strategy_name,
        total_cases=len(cases),
        disposition_correct=disposition_correct,
        answer_attempts=answer_attempts,
        answer_correct=answer_correct,
        false_accepts=false_accepts,
        false_rejects=false_rejects,
        false_abstains=false_abstains,
        unsupported_acceptance=violation_acceptance["unsupported_acceptance"],
        provenance_currentness_accepted=violation_acceptance["provenance_currentness_accepted"],
        correlated_consensus_laundering_accepted=violation_acceptance[
            "correlated_consensus_laundering_accepted"
        ],
        hidden_failure_acceptance=violation_acceptance["hidden_failure_acceptance"],
        authority_effect_promotion_errors=violation_acceptance[
            "authority_effect_promotion_errors"
        ],
        required_violation_hits=required_violation_hits,
        required_violation_total=required_violation_total,
        operation_count=operation_count,
        wall_clock_seconds=wall_clock_seconds,
    )


def compare_reports(left: StrategyMetrics, right: StrategyMetrics) -> PairwiseDelta:
    numeric_names = [
        field.name
        for field in fields(StrategyMetrics)
        if field.name != "strategy_name"
    ]
    numeric_names.extend(
        ("disposition_accuracy", "answer_accuracy", "required_violation_recall")
    )
    deltas = tuple(
        (name, getattr(left, name) - getattr(right, name))
        for name in numeric_names
    )
    return PairwiseDelta(
        left_strategy=left.strategy_name,
        right_strategy=right.strategy_name,
        deltas=deltas,
    )
