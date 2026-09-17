from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Iterable

from .replay import Disposition, ReplayCase, ReplayStrategyOutcome, StrategyInput


Strategy = Callable[[StrategyInput], ReplayStrategyOutcome]


_DETECTION_ALIASES = {
    "proposition_fidelity": "PROPOSITION_TYPING",
    "provenance_currentness": "PROVENANCE_CURRENTNESS",
    "admission_integrity": "INPUT_RETRIEVAL",
    "independence_contamination": "INDEPENDENCE_CONTAMINATION",
    "failure_visibility": "FAILURE_HANDLING",
    "authority_effect_boundary": "AUTHORITY_EFFECT",
}


def _label(value: str) -> str:
    normalized = value.strip()
    return _DETECTION_ALIASES.get(normalized.lower(), normalized.upper())


def _normalized_answer(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(value.split())


@dataclass(frozen=True)
class StrategyMetrics:
    strategy_name: str
    case_count: int = 0
    disposition_correct: int = 0
    answer_attempts_on_answer_cases: int = 0
    answer_correct: int = 0
    false_accepts: int = 0
    false_rejects: int = 0
    false_abstains: int = 0
    unsupported_acceptance: int = 0
    provenance_currentness_violations_accepted: int = 0
    correlated_consensus_laundering_accepted: int = 0
    hidden_failure_acceptance: int = 0
    authority_effect_promotion_errors: int = 0
    required_violation_detections: int = 0
    required_violation_detections_found: int = 0
    operation_count: int = 0
    token_count: int = 0
    provider_cost: float = 0.0
    reported_latency_ms: float = 0.0
    wall_clock_seconds: float = 0.0

    @property
    def required_violation_detection_recall(self) -> float:
        if self.required_violation_detections == 0:
            return 1.0
        return self.required_violation_detections_found / self.required_violation_detections


@dataclass(frozen=True)
class PairwiseDelta:
    strategy_a: str
    strategy_b: str
    case_count: int
    disposition_correct: int
    answer_attempts_on_answer_cases: int
    answer_correct: int
    false_accepts: int
    false_rejects: int
    false_abstains: int
    unsupported_acceptance: int
    provenance_currentness_violations_accepted: int
    correlated_consensus_laundering_accepted: int
    hidden_failure_acceptance: int
    authority_effect_promotion_errors: int
    required_violation_detections: int
    required_violation_detections_found: int
    required_violation_detection_recall: float
    operation_count: int
    token_count: int
    provider_cost: float
    reported_latency_ms: float
    wall_clock_seconds: float


def evaluate_strategy(
    cases: Iterable[ReplayCase],
    strategy: Strategy,
) -> StrategyMetrics:
    case_count = 0
    disposition_correct = 0
    answer_attempts = 0
    answer_correct = 0
    false_accepts = 0
    false_rejects = 0
    false_abstains = 0
    unsupported_acceptance = 0
    provenance_accepted = 0
    correlated_accepted = 0
    hidden_failure_accepted = 0
    authority_effect_errors = 0
    required_detections = 0
    detections_found = 0
    operation_count = 0
    token_count = 0
    provider_cost = 0.0
    reported_latency_ms = 0.0
    wall_clock_seconds = 0.0

    for case in cases:
        # This projection is the evaluator/strategy trust boundary. Gold labels and
        # expected violations never cross it.
        strategy_input = case.to_strategy_input()
        started = perf_counter()
        outcome = strategy(strategy_input)
        wall_clock_seconds += perf_counter() - started
        if not isinstance(outcome, ReplayStrategyOutcome):
            raise TypeError("strategy must return ReplayStrategyOutcome")

        case_count += 1
        operation_count += outcome.operation_count
        if outcome.token_count is not None:
            token_count += outcome.token_count
        if outcome.provider_cost is not None:
            provider_cost += outcome.provider_cost
        if outcome.latency_ms is not None:
            reported_latency_ms += outcome.latency_ms

        if outcome.disposition is case.gold_disposition:
            disposition_correct += 1

        gold_answer = _normalized_answer(case.gold_answer)
        outcome_answer = _normalized_answer(outcome.answer)
        is_answer_case = case.gold_disposition is Disposition.ANSWER
        is_false_accept = False

        if is_answer_case and outcome.disposition is Disposition.ANSWER:
            answer_attempts += 1
            if outcome_answer == gold_answer:
                answer_correct += 1
            else:
                false_accepts += 1
                is_false_accept = True
        elif not is_answer_case and outcome.disposition is Disposition.ANSWER:
            false_accepts += 1
            is_false_accept = True

        if is_answer_case and outcome.disposition is Disposition.FAIL_CLOSED:
            false_rejects += 1
        if is_answer_case and outcome.disposition is Disposition.ABSTAIN:
            false_abstains += 1

        expected = {_label(item) for item in case.expected_violations}
        detected = {_label(item) for item in outcome.detected_violations}
        required_detections += len(expected)
        detections_found += len(expected & detected)

        if is_false_accept:
            if "UNSUPPORTED_CLAIM" in expected or "UNSUPPORTED_ACCEPTANCE" in expected:
                unsupported_acceptance += 1
            if "PROVENANCE_CURRENTNESS" in expected:
                provenance_accepted += 1
            if "INDEPENDENCE_CONTAMINATION" in expected:
                correlated_accepted += 1
            if "FAILURE_HANDLING" in expected:
                hidden_failure_accepted += 1
            if "AUTHORITY_EFFECT" in expected:
                authority_effect_errors += 1

    strategy_name = getattr(strategy, "__name__", strategy.__class__.__name__)
    return StrategyMetrics(
        strategy_name=strategy_name,
        case_count=case_count,
        disposition_correct=disposition_correct,
        answer_attempts_on_answer_cases=answer_attempts,
        answer_correct=answer_correct,
        false_accepts=false_accepts,
        false_rejects=false_rejects,
        false_abstains=false_abstains,
        unsupported_acceptance=unsupported_acceptance,
        provenance_currentness_violations_accepted=provenance_accepted,
        correlated_consensus_laundering_accepted=correlated_accepted,
        hidden_failure_acceptance=hidden_failure_accepted,
        authority_effect_promotion_errors=authority_effect_errors,
        required_violation_detections=required_detections,
        required_violation_detections_found=detections_found,
        operation_count=operation_count,
        token_count=token_count,
        provider_cost=provider_cost,
        reported_latency_ms=reported_latency_ms,
        wall_clock_seconds=wall_clock_seconds,
    )


def compare_reports(a: StrategyMetrics, b: StrategyMetrics) -> PairwiseDelta:
    """Return independent B-minus-A metric deltas; never collapse them to a score."""
    return PairwiseDelta(
        strategy_a=a.strategy_name,
        strategy_b=b.strategy_name,
        case_count=b.case_count - a.case_count,
        disposition_correct=b.disposition_correct - a.disposition_correct,
        answer_attempts_on_answer_cases=(
            b.answer_attempts_on_answer_cases - a.answer_attempts_on_answer_cases
        ),
        answer_correct=b.answer_correct - a.answer_correct,
        false_accepts=b.false_accepts - a.false_accepts,
        false_rejects=b.false_rejects - a.false_rejects,
        false_abstains=b.false_abstains - a.false_abstains,
        unsupported_acceptance=b.unsupported_acceptance - a.unsupported_acceptance,
        provenance_currentness_violations_accepted=(
            b.provenance_currentness_violations_accepted
            - a.provenance_currentness_violations_accepted
        ),
        correlated_consensus_laundering_accepted=(
            b.correlated_consensus_laundering_accepted
            - a.correlated_consensus_laundering_accepted
        ),
        hidden_failure_acceptance=(
            b.hidden_failure_acceptance - a.hidden_failure_acceptance
        ),
        authority_effect_promotion_errors=(
            b.authority_effect_promotion_errors - a.authority_effect_promotion_errors
        ),
        required_violation_detections=(
            b.required_violation_detections - a.required_violation_detections
        ),
        required_violation_detections_found=(
            b.required_violation_detections_found
            - a.required_violation_detections_found
        ),
        required_violation_detection_recall=(
            b.required_violation_detection_recall
            - a.required_violation_detection_recall
        ),
        operation_count=b.operation_count - a.operation_count,
        token_count=b.token_count - a.token_count,
        provider_cost=b.provider_cost - a.provider_cost,
        reported_latency_ms=b.reported_latency_ms - a.reported_latency_ms,
        wall_clock_seconds=b.wall_clock_seconds - a.wall_clock_seconds,
    )
