from __future__ import annotations

from pathlib import Path
import re

from rezon.replay import Disposition, ReplayStrategyOutcome, load_replay_cases
from rezon.replay_strategies import fixed_multipass, rezon_guarded, single_pass


FIXTURE = Path(__file__).parent / "fixtures" / "benchmark_v1.json"
REQUIRED_CLASSES = {
    "PROPOSITION_SUBSTITUTION",
    "STALE_SOURCE",
    "ROLLBACK_SOURCE",
    "DUPLICATE_EVIDENCE",
    "CORRELATED_CONSENSUS",
    "RETRIEVED_UNADMITTED_EVIDENCE",
    "ADVISORY_SIGNAL_AUTHORITY",
    "OMITTED_CONTRADICTION",
    "PARTIAL_WORKER_FAILURE",
    "MANDATORY_VERIFIER_UNAVAILABLE",
    "MALFORMED_SEMANTIC_RECEIPT",
    "INSUFFICIENT_EVIDENCE",
}


def _neutral(value: str, prefix: str) -> bool:
    return re.fullmatch(rf"{prefix}\d{{3}}", value) is not None


def test_fixture_contains_every_required_spec_class_and_mixed_gold_dispositions():
    cases = load_replay_cases(FIXTURE)

    observed = {
        label
        for case in cases
        for label in case.expected_violations
        if label in REQUIRED_CLASSES
    }
    assert observed == REQUIRED_CLASSES
    assert {case.fixture_version for case in cases} == {"benchmark-v1.0"}
    assert all(case.fixture_provenance for case in cases)
    assert any(case.gold_disposition is Disposition.ANSWER for case in cases)
    assert any(case.gold_disposition is not Disposition.ANSWER for case in cases)


def test_fixture_has_multiple_clean_answer_controls_to_penalize_reject_everything():
    cases = load_replay_cases(FIXTURE)
    clean_answers = [
        case
        for case in cases
        if not case.expected_violations
        and case.gold_disposition is Disposition.ANSWER
    ]
    assert len(clean_answers) >= 3


def test_fixture_ids_are_neutral_numeric_tokens_not_attack_labels():
    cases = load_replay_cases(FIXTURE)

    for case in cases:
        assert _neutral(case.case_id, "c")
        for candidate in case.candidates:
            assert _neutral(candidate.candidate_id, "p")
            assert _neutral(candidate.worker_id, "w")
            assert _neutral(candidate.execution_id, "e")
            assert candidate.model_id is None or _neutral(candidate.model_id, "m")
            assert candidate.provider_id is None or _neutral(candidate.provider_id, "v")
        for source in case.sources:
            assert _neutral(source.source_id, "s")
            assert _neutral(source.origin_id, "o")


def test_projected_strategy_inputs_expose_no_gold_or_expected_label_fields():
    cases = load_replay_cases(FIXTURE)

    for case in cases:
        strategy_input = case.to_strategy_input()
        names = set(vars(strategy_input))
        assert all("gold" not in name for name in names)
        assert all("expected" not in name for name in names)
        assert not hasattr(strategy_input, "gold_answer")
        assert not hasattr(strategy_input, "gold_disposition")
        assert not hasattr(strategy_input, "expected_violations")
        if case.expected_violations:
            assert case.expected_violations not in tuple(vars(strategy_input).values())


def test_all_three_strategies_run_every_frozen_case_without_live_dependencies():
    cases = load_replay_cases(FIXTURE)

    for case in cases:
        strategy_input = case.to_strategy_input()
        for strategy in (single_pass, fixed_multipass, rezon_guarded):
            outcome = strategy(strategy_input)
            assert isinstance(outcome, ReplayStrategyOutcome)
