import json
from pathlib import Path

from rezon.benchmark import BenchmarkCase, StrategyOutcome, run_benchmark
from rezon.hostile import HostileViolation, audit_hostile_case


def test_each_hostile_fixture_trips_its_declared_semantic_violation():
    cases = json.loads(Path("tests/fixtures/hostile_cases.json").read_text())
    for case in cases:
        violations = audit_hostile_case(case)
        assert HostileViolation(case["expected"]) in violations, case["case_id"]


def test_clean_control_does_not_trip_hostile_audit():
    control = {
        "literal_request": "prove A",
        "solved_request": "prove A",
        "source_version": "v2",
        "required_source_version": "v2",
        "source_generation": 5,
        "required_min_generation": 5,
        "evidence_origins": ["s1", "s2"],
        "declared_independent_evidence_count": 2,
        "consensus_counted_as_evidence": False,
        "worker_independence": [True, True],
        "authority_basis": "explicit_policy",
        "receipt": {"task_id": "t1", "episode_version": "e1@3"},
        "reported_clean_success": False,
        "failures": [],
    }
    assert audit_hostile_case(control) == ()


def test_benchmark_compares_strategies_without_confusing_execution_count_with_correctness():
    cases = (
        BenchmarkCase("c1", "A", {"input": 1}),
        BenchmarkCase("c2", "B", {"input": 2}),
    )

    def simple(case):
        return StrategyOutcome(answer="A", unsupported_claim_count=1, execution_count=1)

    def guarded(case):
        return StrategyOutcome(answer=case.gold_answer, unsupported_claim_count=0, execution_count=3)

    report = run_benchmark(cases, {"simple": simple, "guarded": guarded})
    assert report["simple"].correct == 1
    assert report["guarded"].correct == 2
    assert report["guarded"].executions == 6
    assert report["guarded"].unsupported_claims == 0


def test_benchmark_preserves_strategy_failures_as_failures():
    case = (BenchmarkCase("c1", "A", {}),)
    report = run_benchmark(
        case,
        {"broken": lambda _: StrategyOutcome(answer=None, failures=("unavailable",), execution_count=1)},
    )
    assert report["broken"].failures == 1
    assert report["broken"].correct == 0
