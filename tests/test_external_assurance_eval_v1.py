import json
from pathlib import Path
import subprocess
import sys

from rezon.replay import load_replay_cases
from rezon.replay_metrics import evaluate_strategy
from rezon.replay_strategies import fixed_multipass, rezon_guarded, single_pass


FIXTURE = Path("tests/fixtures/external_assurance_v1.json")
SCRIPT = Path("scripts/run_external_assurance_eval_v1.py")


def _metrics():
    cases = load_replay_cases(FIXTURE)
    return {
        "trace_only_primary": evaluate_strategy(
            cases,
            single_pass,
            strategy_name="trace_only_primary",
        ),
        "ungoverned_exact_vote": evaluate_strategy(
            cases,
            fixed_multipass,
            strategy_name="ungoverned_exact_vote",
        ),
        "rezon_guarded": evaluate_strategy(
            cases,
            rezon_guarded,
            strategy_name="rezon_guarded",
        ),
    }


def test_external_assurance_fixture_has_clean_controls_and_attack_coverage():
    cases = load_replay_cases(FIXTURE)

    assert len(cases) == 10
    assert sum(case.gold_disposition.value == "ANSWER" for case in cases) == 2
    assert sum(case.gold_disposition.value != "ANSWER" for case in cases) == 8
    assert {
        violation
        for case in cases
        for violation in case.expected_violations
    } == {
        "PROPOSITION_FIDELITY",
        "PROVENANCE_CURRENTNESS",
        "ADMISSION_INTEGRITY",
        "INDEPENDENCE_CONTAMINATION",
        "FAILURE_VISIBILITY",
        "AUTHORITY_EFFECT_BOUNDARY",
    }


def test_external_assurance_comparison_exposes_detection_value_and_false_blocks():
    metrics = _metrics()

    trace = metrics["trace_only_primary"]
    vote = metrics["ungoverned_exact_vote"]
    guarded = metrics["rezon_guarded"]

    assert trace.total_cases == vote.total_cases == guarded.total_cases == 10

    assert trace.disposition_correct == 2
    assert vote.disposition_correct == 2
    assert trace.false_accepts == 8
    assert vote.false_accepts == 8
    assert trace.required_violation_recall == 0.0
    assert vote.required_violation_recall == 0.0

    assert guarded.disposition_correct == 10
    assert guarded.false_accepts == 0
    assert guarded.false_rejects == 0
    assert guarded.false_abstains == 0
    assert guarded.required_violation_hits == 8
    assert guarded.required_violation_total == 8
    assert guarded.required_violation_recall == 1.0
    assert guarded.answer_correct == 2
    assert guarded.answer_attempts == 2

    assert guarded.operation_count > trace.operation_count
    assert guarded.operation_count > vote.operation_count


def test_external_assurance_runner_emits_bound_nonpromotional_report():
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(FIXTURE),
            "--code-version",
            "test-exact-head",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    report = json.loads(completed.stdout)

    assert report["evaluation"] == "rezon-external-assurance-v1"
    assert report["fixture_version"] == "external-assurance-v1.0"
    assert report["code_version"] == "test-exact-head"
    assert report["case_count"] == 10
    assert len(report["fixture_sha256"]) == 64
    assert len(report["strategy_input_digest"]) == 64
    assert set(report["strategies"]) == {
        "trace_only_primary",
        "ungoverned_exact_vote",
        "rezon_guarded",
    }
    assert report["strategies"]["rezon_guarded"]["false_accepts"] == 0
    assert report["strategies"]["trace_only_primary"]["false_accepts"] == 8
    assert report["strategies"]["ungoverned_exact_vote"]["false_accepts"] == 8
    assert report["strategies"]["rezon_guarded"]["false_abstains"] == 0
    assert report["does_not_prove"]
    assert "winner" not in report
    assert "best_strategy" not in report
