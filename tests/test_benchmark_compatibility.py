from rezon.benchmark import (
    BenchmarkCase,
    BenchmarkMetrics,
    StrategyOutcome as LegacyStrategyOutcome,
    run_benchmark,
)
from rezon.replay import Disposition, ReplayStrategyOutcome


def test_legacy_and_replay_outcomes_remain_distinct_types():
    legacy = LegacyStrategyOutcome(answer="A", execution_count=2)
    replay = ReplayStrategyOutcome(
        disposition=Disposition.ANSWER,
        answer="A",
        operation_count=2,
    )

    assert type(legacy) is LegacyStrategyOutcome
    assert type(replay) is ReplayStrategyOutcome
    assert LegacyStrategyOutcome is not ReplayStrategyOutcome
    assert not hasattr(legacy, "disposition")
    assert not hasattr(replay, "execution_count")


def test_legacy_benchmark_preserves_existing_counting_semantics():
    cases = (
        BenchmarkCase("c1", "A", {"input": 1}),
        BenchmarkCase("c2", "B", {"input": 2}),
        BenchmarkCase("c3", None, {"input": 3}),
    )

    def strategy(case: BenchmarkCase) -> LegacyStrategyOutcome:
        if case.case_id == "c1":
            return LegacyStrategyOutcome(
                answer="A",
                unsupported_claim_count=1,
                execution_count=1,
            )
        if case.case_id == "c2":
            return LegacyStrategyOutcome(
                answer="wrong",
                unsupported_claim_count=0,
                execution_count=2,
            )
        return LegacyStrategyOutcome(
            answer=None,
            execution_count=3,
            failures=("unavailable",),
        )

    metrics = run_benchmark(cases, {"legacy": strategy})["legacy"]

    assert isinstance(metrics, BenchmarkMetrics)
    assert metrics.total == 3
    assert metrics.correct == 1
    assert metrics.failures == 1
    assert metrics.executions == 6
    assert metrics.unsupported_claims == 1
