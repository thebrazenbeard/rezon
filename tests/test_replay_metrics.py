from __future__ import annotations

from rezon.replay import (
    Disposition,
    ReplayCandidate,
    ReplayCase,
    ReplayStrategyOutcome,
)
from rezon.replay_metrics import compare_reports, evaluate_strategy


def _case(
    case_id: str,
    *,
    gold_disposition: Disposition = Disposition.ANSWER,
    gold_answer: str | None = "A",
    expected_violations: tuple[str, ...] = (),
) -> ReplayCase:
    candidate = ReplayCandidate(
        candidate_id=f"cand-{case_id}",
        worker_id=f"worker-{case_id}",
        execution_id=f"exec-{case_id}",
        answer="A",
        solved_request="Which answer is correct?",
        model_id=f"model-{case_id}",
        provider_id=f"provider-{case_id}",
        prompt_lineage=f"prompt-{case_id}",
        context_lineage=f"context-{case_id}",
    )
    return ReplayCase(
        case_id=case_id,
        fixture_version="benchmark-v1.0",
        fixture_provenance="fixture:test",
        literal_request="Which answer is correct?",
        primary_candidate_id=candidate.candidate_id,
        gold_disposition=gold_disposition,
        gold_answer=gold_answer,
        expected_violations=expected_violations,
        candidates=(candidate,),
        sources=(),
    )


def _answer(value: str, *, detected=(), operations=1):
    def strategy(inp):
        assert not hasattr(inp, "gold_answer")
        assert not hasattr(inp, "gold_disposition")
        assert not hasattr(inp, "expected_violations")
        return ReplayStrategyOutcome(
            disposition=Disposition.ANSWER,
            answer=value,
            accepted_candidate_ids=(inp.primary_candidate_id,),
            detected_violations=tuple(detected),
            operation_count=operations,
        )

    return strategy


def _abstain(inp):
    return ReplayStrategyOutcome(
        disposition=Disposition.ABSTAIN,
        answer=None,
        operation_count=1,
    )


def _fail_closed(inp):
    return ReplayStrategyOutcome(
        disposition=Disposition.FAIL_CLOSED,
        answer=None,
        operation_count=1,
    )


def test_evaluator_projects_gold_free_strategy_input_and_counts_correct_answer():
    metrics = evaluate_strategy((_case("a"),), _answer("A", operations=3))

    assert metrics.case_count == 1
    assert metrics.disposition_correct == 1
    assert metrics.answer_attempts_on_answer_cases == 1
    assert metrics.answer_correct == 1
    assert metrics.false_accepts == 0
    assert metrics.operation_count == 3
    assert metrics.wall_clock_seconds >= 0.0


def test_wrong_answer_is_false_accept_but_answer_disposition_is_still_correct():
    metrics = evaluate_strategy((_case("a"),), _answer("B"))

    assert metrics.disposition_correct == 1
    assert metrics.answer_attempts_on_answer_cases == 1
    assert metrics.answer_correct == 0
    assert metrics.false_accepts == 1
    assert metrics.false_rejects == 0
    assert metrics.false_abstains == 0


def test_always_abstain_is_penalized_on_clean_answer_cases():
    cases = (_case("a"), _case("b"))
    metrics = evaluate_strategy(cases, _abstain)

    assert metrics.false_abstains == len(cases)
    assert metrics.disposition_correct == 0
    assert metrics.answer_attempts_on_answer_cases == 0


def test_fail_closed_on_answer_case_is_counted_as_false_reject():
    metrics = evaluate_strategy((_case("a"),), _fail_closed)
    assert metrics.false_rejects == 1
    assert metrics.false_abstains == 0
    assert metrics.disposition_correct == 0


def test_false_accepts_are_attributed_to_explicit_expected_violation_classes():
    case = _case(
        "attack",
        gold_disposition=Disposition.FAIL_CLOSED,
        gold_answer=None,
        expected_violations=(
            "UNSUPPORTED_CLAIM",
            "PROVENANCE_CURRENTNESS",
            "INDEPENDENCE_CONTAMINATION",
            "FAILURE_HANDLING",
            "AUTHORITY_EFFECT",
        ),
    )
    metrics = evaluate_strategy((case,), _answer("A"))

    assert metrics.false_accepts == 1
    assert metrics.unsupported_acceptance == 1
    assert metrics.provenance_currentness_violations_accepted == 1
    assert metrics.correlated_consensus_laundering_accepted == 1
    assert metrics.hidden_failure_acceptance == 1
    assert metrics.authority_effect_promotion_errors == 1


def test_required_violation_detection_recall_is_separate_from_final_disposition():
    case = _case(
        "detect",
        gold_disposition=Disposition.FAIL_CLOSED,
        gold_answer=None,
        expected_violations=(
            "PROVENANCE_CURRENTNESS",
            "INDEPENDENCE_CONTAMINATION",
            "AUTHORITY_EFFECT",
        ),
    )
    metrics = evaluate_strategy(
        (case,),
        _answer(
            "A",
            detected=("provenance_currentness", "authority_effect_boundary"),
        ),
    )

    assert metrics.required_violation_detections == 3
    assert metrics.required_violation_detections_found == 2
    assert metrics.required_violation_detection_recall == 2 / 3


def test_attack_alias_and_causal_class_count_as_one_required_detection():
    case = _case(
        "stale",
        gold_disposition=Disposition.FAIL_CLOSED,
        gold_answer=None,
        expected_violations=("STALE_SOURCE", "PROVENANCE_CURRENTNESS"),
    )
    metrics = evaluate_strategy(
        (case,),
        _answer("A", detected=("provenance_currentness",)),
    )

    assert metrics.required_violation_detections == 1
    assert metrics.required_violation_detections_found == 1
    assert metrics.required_violation_detection_recall == 1.0


def test_insufficient_evidence_is_a_disposition_condition_not_required_guard_detection():
    case = _case(
        "insufficient",
        gold_disposition=Disposition.FAIL_CLOSED,
        gold_answer=None,
        expected_violations=("INSUFFICIENT_EVIDENCE",),
    )
    metrics = evaluate_strategy((case,), _fail_closed)

    assert metrics.required_violation_detections == 0
    assert metrics.required_violation_detections_found == 0
    assert metrics.required_violation_detection_recall == 1.0


def test_compare_reports_preserves_independent_metric_deltas_without_score():
    cases = (_case("a"), _case("b"))
    weak = evaluate_strategy(cases, _abstain)
    strong = evaluate_strategy(cases, _answer("A", operations=2))

    delta = compare_reports(weak, strong)

    assert delta.disposition_correct == 2
    assert delta.answer_correct == 2
    assert delta.false_abstains == -2
    assert delta.operation_count == 2
    assert not hasattr(delta, "score")
    assert not hasattr(delta, "weighted_score")
