from rezon.replay import (
    Disposition,
    ReplayCandidate,
    ReplayCase,
    ReplayStrategyOutcome,
    StrategyInput,
)
from rezon.replay_metrics import compare_reports, evaluate_strategy


def _candidate(answer: str = "A") -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id="cand-1",
        worker_id="worker-1",
        execution_id="exec-1",
        answer=answer,
    )


def _case(
    case_id: str,
    gold_disposition: Disposition,
    *,
    gold_answer: str | None = None,
    expected_violations: tuple[str, ...] = (),
) -> ReplayCase:
    return ReplayCase(
        case_id=case_id,
        fixture_version="benchmark-v1.0",
        fixture_provenance="fixture:test",
        literal_request="Question?",
        primary_candidate_id="cand-1",
        gold_disposition=gold_disposition,
        gold_answer=gold_answer,
        expected_violations=expected_violations,
        candidates=(_candidate(),),
        sources=(),
    )


def test_evaluator_projects_gold_free_strategy_input():
    case = _case("clean", Disposition.ANSWER, gold_answer="A")

    def strategy(inp: StrategyInput) -> ReplayStrategyOutcome:
        assert isinstance(inp, StrategyInput)
        assert not hasattr(inp, "gold_disposition")
        assert not hasattr(inp, "gold_answer")
        assert not hasattr(inp, "expected_violations")
        return ReplayStrategyOutcome(
            disposition=Disposition.ANSWER,
            answer="A",
            operation_count=3,
        )

    metrics = evaluate_strategy((case,), strategy, strategy_name="projected")

    assert metrics.total_cases == 1
    assert metrics.disposition_correct == 1
    assert metrics.answer_attempts == 1
    assert metrics.answer_correct == 1
    assert metrics.operation_count == 3


def test_metrics_account_for_semantic_failures_separately():
    cases = (
        _case("clean", Disposition.ANSWER, gold_answer="A"),
        _case(
            "wrong",
            Disposition.ANSWER,
            gold_answer="B",
            expected_violations=("UNSUPPORTED_CLAIM",),
        ),
        _case(
            "stale",
            Disposition.ABSTAIN,
            expected_violations=("PROVENANCE_CURRENTNESS",),
        ),
        _case(
            "correlated",
            Disposition.FAIL_CLOSED,
            expected_violations=("INDEPENDENCE_CONTAMINATION",),
        ),
        _case(
            "hidden-failure",
            Disposition.ABSTAIN,
            expected_violations=("FAILURE_VISIBILITY",),
        ),
        _case(
            "authority",
            Disposition.ABSTAIN,
            expected_violations=("AUTHORITY_EFFECT_BOUNDARY",),
        ),
        _case("false-abstain", Disposition.ANSWER, gold_answer="C"),
        _case("false-reject", Disposition.ANSWER, gold_answer="D"),
    )

    def strategy(inp: StrategyInput) -> ReplayStrategyOutcome:
        if inp.case_id == "clean":
            return ReplayStrategyOutcome(Disposition.ANSWER, "A", operation_count=1)
        if inp.case_id == "wrong":
            return ReplayStrategyOutcome(Disposition.ANSWER, "A", operation_count=2)
        if inp.case_id in {
            "stale",
            "correlated",
            "hidden-failure",
            "authority",
        }:
            return ReplayStrategyOutcome(Disposition.ANSWER, "A", operation_count=3)
        if inp.case_id == "false-abstain":
            return ReplayStrategyOutcome(Disposition.ABSTAIN, operation_count=4)
        return ReplayStrategyOutcome(Disposition.FAIL_CLOSED, operation_count=5)

    metrics = evaluate_strategy(cases, strategy, strategy_name="broken")

    assert metrics.total_cases == 8
    assert metrics.disposition_correct == 2
    assert metrics.answer_attempts == 2
    assert metrics.answer_correct == 1
    assert metrics.false_accepts == 5
    assert metrics.false_abstains == 1
    assert metrics.false_rejects == 1
    assert metrics.unsupported_acceptance == 1
    assert metrics.provenance_currentness_accepted == 1
    assert metrics.correlated_consensus_laundering_accepted == 1
    assert metrics.hidden_failure_acceptance == 1
    assert metrics.authority_effect_promotion_errors == 1
    assert metrics.required_violation_total == 5
    assert metrics.required_violation_hits == 0
    assert metrics.operation_count == 24


def test_unadmitted_evidence_acceptance_counts_as_unsupported_acceptance():
    case = _case(
        "unadmitted",
        Disposition.ABSTAIN,
        expected_violations=("ADMISSION_INTEGRITY",),
    )

    def strategy(_inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(Disposition.ANSWER, "A")

    metrics = evaluate_strategy((case,), strategy, strategy_name="broken-admission")

    assert metrics.false_accepts == 1
    assert metrics.unsupported_acceptance == 1


def test_unmeasured_wall_clock_is_unknown_not_zero():
    case = _case("clean", Disposition.ANSWER, gold_answer="A")

    def strategy(_inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(Disposition.ANSWER, "A")

    metrics = evaluate_strategy((case,), strategy, strategy_name="unmeasured")

    assert metrics.wall_clock_seconds is None


def test_wall_clock_total_requires_measurement_for_every_case():
    cases = (
        _case("a", Disposition.ANSWER, gold_answer="A"),
        _case("b", Disposition.ANSWER, gold_answer="A"),
    )

    def fully_measured(_inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(
            Disposition.ANSWER,
            "A",
            wall_clock_seconds=0.25,
        )

    measured = evaluate_strategy(cases, fully_measured, strategy_name="measured")
    assert measured.wall_clock_seconds == 0.5

    def partly_measured(inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(
            Disposition.ANSWER,
            "A",
            wall_clock_seconds=0.25 if inp.case_id == "a" else None,
        )

    partial = evaluate_strategy(cases, partly_measured, strategy_name="partial")
    assert partial.wall_clock_seconds is None


def test_required_violation_detection_recall_counts_explicit_hits():
    case = _case(
        "stale",
        Disposition.ABSTAIN,
        expected_violations=("PROVENANCE_CURRENTNESS", "ADMISSION_INTEGRITY"),
    )

    def strategy(_inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(
            disposition=Disposition.ABSTAIN,
            violations_detected=("PROVENANCE_CURRENTNESS",),
        )

    metrics = evaluate_strategy((case,), strategy, strategy_name="partial-detector")

    assert metrics.required_violation_total == 2
    assert metrics.required_violation_hits == 1
    assert metrics.required_violation_recall == 0.5


def test_always_abstain_is_penalized_on_clean_answer_cases():
    cases = (
        _case("a", Disposition.ANSWER, gold_answer="A"),
        _case("b", Disposition.ANSWER, gold_answer="B"),
    )

    def always_abstain(_inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(disposition=Disposition.ABSTAIN)

    metrics = evaluate_strategy(cases, always_abstain, strategy_name="always-abstain")

    assert metrics.false_abstains == len(cases)
    assert metrics.disposition_correct == 0


def test_pairwise_delta_preserves_individual_metric_dimensions():
    clean = (_case("clean", Disposition.ANSWER, gold_answer="A"),)

    def good(_inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(Disposition.ANSWER, "A", operation_count=5)

    def bad(_inp: StrategyInput) -> ReplayStrategyOutcome:
        return ReplayStrategyOutcome(Disposition.ABSTAIN, operation_count=1)

    good_metrics = evaluate_strategy(clean, good, strategy_name="good")
    bad_metrics = evaluate_strategy(clean, bad, strategy_name="bad")
    delta = compare_reports(good_metrics, bad_metrics)
    values = dict(delta.deltas)

    assert delta.left_strategy == "good"
    assert delta.right_strategy == "bad"
    assert values["false_abstains"] == -1
    assert values["operation_count"] == 4
    assert values["wall_clock_seconds"] is None
    assert "disposition_accuracy" in values
