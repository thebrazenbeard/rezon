import pytest

from rezon.replay import (
    ReplayCandidate,
    ReplaySource,
    ReplayValidationError,
    StrategyInput,
)
from rezon.replay_strategies import rezon_guarded


def _candidate() -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id="candidate-r4-collision",
        worker_id="worker-r4-collision",
        execution_id="exec-r4-collision",
        answer="30",
        solved_request="What is the current approved timeout?",
        source_refs=("dup",),
        model_id="model-r4-collision",
        provider_id="provider-r4-collision",
        prompt_lineage="prompt-r4-collision",
        context_lineage="context-r4-collision",
    )


def _source(*, admitted: str, current: bool) -> ReplaySource:
    return ReplaySource(
        source_id="dup",
        source_version="v1",
        locator=f"fixture:{admitted}:{current}",
        admission_status=admitted,
        is_current=current,
        origin_id="origin-r4-collision",
    )


def _input(sources: tuple[ReplaySource, ...]) -> StrategyInput:
    candidate = _candidate()
    return StrategyInput(
        case_id="r4-source-collision",
        fixture_version="benchmark-v1.0",
        literal_request="What is the current approved timeout?",
        primary_candidate_id=candidate.candidate_id,
        candidates=(candidate,),
        sources=sources,
    )


def test_duplicate_source_identity_fails_closed_regardless_of_order():
    bad = _source(admitted="RETRIEVED_UNADMITTED", current=False)
    good = _source(admitted="ADMITTED", current=True)

    for sources in ((bad, good), (good, bad)):
        with pytest.raises(
            ReplayValidationError,
            match="source IDs must be unique",
        ):
            rezon_guarded(_input(sources))
