from __future__ import annotations

from pathlib import Path

from rezon.replay import load_replay_cases
from rezon.replay_metrics import evaluate_strategy
from rezon.replay_strategies import fixed_multipass, rezon_guarded, single_pass


FIXTURE = Path(__file__).parent / "fixtures" / "benchmark_v1.json"


def test_frozen_corpus_preserves_narrow_replay_safety_gain_and_known_gaps():
    cases = load_replay_cases(FIXTURE)

    single = evaluate_strategy(cases, single_pass)
    fixed = evaluate_strategy(cases, fixed_multipass)
    guarded = evaluate_strategy(cases, rezon_guarded)

    assert single.case_count == fixed.case_count == guarded.case_count == 15

    # Semantic outcomes remain separate; no composite or prestige score is used.
    assert single.disposition_correct == 13
    assert fixed.disposition_correct == 14
    assert guarded.disposition_correct == 14

    assert single.answer_correct == 3
    assert fixed.answer_correct == 4
    assert guarded.answer_correct == 11

    assert single.false_accepts == 11
    assert fixed.false_accepts == 9
    assert guarded.false_accepts == 2

    # The remaining guarded false accepts are deliberate benchmark pressure:
    # omitted contradiction and malformed semantic receipt are not guarded yet.
    assert guarded.required_violation_detections == 11
    assert guarded.required_violation_detections_found == 9
    assert guarded.required_violation_detection_recall == 9 / 11

    # Guarded replay closes the currently modeled currentness/correlation/failure/
    # authority laundering paths while preserving the two integration gaps above.
    assert guarded.provenance_currentness_violations_accepted == 0
    assert guarded.correlated_consensus_laundering_accepted == 0
    assert guarded.hidden_failure_acceptance == 0
    assert guarded.authority_effect_promotion_errors == 0

    assert single.provenance_currentness_violations_accepted == 2
    assert single.correlated_consensus_laundering_accepted == 2
    assert single.hidden_failure_acceptance == 2
    assert single.authority_effect_promotion_errors == 1

    assert fixed.provenance_currentness_violations_accepted == 2
    assert fixed.correlated_consensus_laundering_accepted == 2
    assert fixed.hidden_failure_acceptance == 0
    assert fixed.authority_effect_promotion_errors == 1

    # Extra orchestration work is visible rather than hidden in a quality score.
    assert single.operation_count == 15
    assert fixed.operation_count == 29
    assert guarded.operation_count == 29
