from rezon.replay import Disposition, ReplayCandidate, ReplaySource, StrategyInput
from rezon.replay_strategies import ALL_GUARDS, GuardName, rezon_guarded


def test_guarded_currentness_fails_closed_when_cited_source_currentness_is_unknown():
    source = ReplaySource(
        source_id="source-unknown-currentness",
        source_version="v1",
        locator="fixture:r4:unknown-currentness",
        admission_status="ADMITTED",
        is_current=None,
        origin_id="origin-r4",
    )
    candidate = ReplayCandidate(
        candidate_id="candidate-r4",
        worker_id="worker-r4",
        execution_id="exec-r4",
        answer="30",
        solved_request="What is the current approved timeout?",
        source_refs=(source.source_id,),
        model_id="model-r4",
        provider_id="provider-r4",
        prompt_lineage="prompt-r4",
        context_lineage="context-r4",
    )
    strategy_input = StrategyInput(
        case_id="r4-unknown-currentness",
        fixture_version="benchmark-v1.0",
        literal_request="What is the current approved timeout?",
        primary_candidate_id=candidate.candidate_id,
        candidates=(candidate,),
        sources=(source,),
    )

    guarded = rezon_guarded(strategy_input)
    currentness_ablated = rezon_guarded(
        strategy_input,
        guards=ALL_GUARDS.without(GuardName.PROVENANCE_CURRENTNESS),
    )

    assert guarded.disposition is Disposition.ABSTAIN
    assert guarded.answer is None
    assert guarded.accepted_candidate_ids == ()
    assert guarded.rejected_candidate_ids == (candidate.candidate_id,)
    assert "PROVENANCE_CURRENTNESS" in guarded.violations_detected
    assert currentness_ablated.disposition is Disposition.ANSWER
    assert currentness_ablated.answer == "30"
