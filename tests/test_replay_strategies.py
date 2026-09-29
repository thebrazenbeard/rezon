from rezon.replay import Disposition, ReplayCandidate, ReplaySource, StrategyInput
from rezon.replay_strategies import fixed_multipass, single_pass


def _candidate(
    candidate_id: str,
    answer: str | None,
    *,
    failure: str | None = None,
    model_id: str | None = None,
    provider_id: str | None = None,
    source_refs: tuple[str, ...] = (),
) -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=f"worker-{candidate_id}",
        execution_id=f"exec-{candidate_id}",
        answer=answer,
        model_id=model_id,
        provider_id=provider_id,
        source_refs=source_refs,
        failure=failure,
    )


def _input(
    *candidates: ReplayCandidate,
    primary: str,
    sources: tuple[ReplaySource, ...] = (),
) -> StrategyInput:
    return StrategyInput(
        case_id="case-1",
        fixture_version="benchmark-v1.0",
        literal_request="Which answer is supported?",
        primary_candidate_id=primary,
        candidates=tuple(candidates),
        sources=sources,
    )


def test_single_pass_selects_exact_primary_candidate():
    inp = _input(
        _candidate("cand-1", "wrong"),
        _candidate("cand-2", "right"),
        _candidate("cand-3", "wrong"),
        primary="cand-2",
    )

    outcome = single_pass(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "right"
    assert outcome.accepted_candidate_ids == ("cand-2",)
    assert outcome.operation_count == 1


def test_single_pass_fails_closed_when_primary_failed():
    inp = _input(
        _candidate("cand-1", "right"),
        _candidate("cand-2", None, failure="TIMEOUT"),
        primary="cand-2",
    )

    outcome = single_pass(inp)

    assert outcome.disposition is Disposition.FAIL_CLOSED
    assert outcome.answer is None
    assert outcome.accepted_candidate_ids == ()
    assert outcome.rejected_candidate_ids == ("cand-2",)


def test_fixed_multipass_tie_breaks_by_candidate_order():
    inp = _input(
        _candidate("cand-1", " A "),
        _candidate("cand-2", "B"),
        _candidate("cand-3", "B"),
        _candidate("cand-4", "a"),
        primary="cand-3",
    )

    outcome = fixed_multipass(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == " A "
    assert outcome.accepted_candidate_ids == ("cand-1", "cand-4")


def test_fixed_multipass_ignores_failed_and_missing_answer_candidates():
    inp = _input(
        _candidate("cand-1", "A", failure="UNAVAILABLE"),
        _candidate("cand-2", None),
        _candidate("cand-3", "B"),
        primary="cand-1",
    )

    outcome = fixed_multipass(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "B"
    assert outcome.accepted_candidate_ids == ("cand-3",)
    assert set(outcome.rejected_candidate_ids) == {"cand-1", "cand-2"}


def test_fixed_multipass_fails_closed_when_no_candidate_is_eligible():
    inp = _input(
        _candidate("cand-1", None),
        _candidate("cand-2", "A", failure="TIMEOUT"),
        primary="cand-1",
    )

    outcome = fixed_multipass(inp)

    assert outcome.disposition is Disposition.FAIL_CLOSED
    assert outcome.answer is None
    assert outcome.accepted_candidate_ids == ()


def test_fixed_multipass_does_not_use_governance_metadata_to_break_vote():
    source = ReplaySource(
        source_id="source-current",
        source_version="v2",
        admission_status="ADMITTED",
        is_current=True,
        origin_id="origin-authoritative",
    )
    inp = _input(
        _candidate(
            "cand-1",
            "stale-answer",
            model_id="shared-model",
            provider_id="shared-provider",
            source_refs=("source-stale",),
        ),
        _candidate(
            "cand-2",
            "stale-answer",
            model_id="shared-model",
            provider_id="shared-provider",
            source_refs=("source-stale",),
        ),
        _candidate(
            "cand-3",
            "current-answer",
            model_id="independent-model",
            provider_id="independent-provider",
            source_refs=("source-current",),
        ),
        primary="cand-3",
        sources=(source,),
    )

    outcome = fixed_multipass(inp)

    assert outcome.answer == "stale-answer"
    assert outcome.accepted_candidate_ids == ("cand-1", "cand-2")
