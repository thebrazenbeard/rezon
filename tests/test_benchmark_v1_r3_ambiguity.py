from rezon.replay import Disposition, ReplayCandidate, ReplaySource, StrategyInput
from rezon.replay_strategies import rezon_guarded


def _candidate(candidate_id: str, answer: str, source_id: str, suffix: str) -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=f"worker-{suffix}",
        execution_id=f"exec-{suffix}",
        answer=answer,
        solved_request="Which answer is supported?",
        source_refs=(source_id,),
        model_id=f"model-{suffix}",
        provider_id=f"provider-{suffix}",
        prompt_lineage=f"prompt-{suffix}",
        context_lineage=f"context-{suffix}",
    )


def _source(source_id: str, suffix: str) -> ReplaySource:
    return ReplaySource(
        source_id=source_id,
        source_version="v1",
        locator=f"fixture:r3:{suffix}",
        admission_status="ADMITTED",
        is_current=True,
        origin_id=f"origin-{suffix}",
    )


def _input(*candidates: ReplayCandidate) -> StrategyInput:
    return StrategyInput(
        case_id="r3-tied-disagreement",
        fixture_version="benchmark-v1.0",
        literal_request="Which answer is supported?",
        primary_candidate_id=candidates[0].candidate_id,
        candidates=tuple(candidates),
        sources=(
            _source("source-a", "a"),
            _source("source-b", "b"),
        ),
    )


def test_rezon_guarded_preserves_ambiguity_on_tied_eligible_disagreement():
    first = _candidate("candidate-a", "A", "source-a", "a")
    second = _candidate("candidate-b", "B", "source-b", "b")

    outcome = rezon_guarded(_input(first, second))

    assert outcome.disposition is Disposition.ABSTAIN
    assert outcome.answer is None
    assert outcome.accepted_candidate_ids == ()
    assert "eligible_answer_tie" in outcome.unresolved


def test_rezon_guarded_tied_disagreement_is_candidate_order_invariant():
    first = _candidate("candidate-a", "A", "source-a", "a")
    second = _candidate("candidate-b", "B", "source-b", "b")

    forward = rezon_guarded(_input(first, second))
    reverse = rezon_guarded(_input(second, first))

    assert forward.disposition is reverse.disposition is Disposition.ABSTAIN
    assert forward.answer is reverse.answer is None
    assert forward.accepted_candidate_ids == reverse.accepted_candidate_ids == ()
    assert set(forward.rejected_candidate_ids) == set(reverse.rejected_candidate_ids)
    assert forward.unresolved == reverse.unresolved == ("eligible_answer_tie",)
