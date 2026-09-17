from __future__ import annotations

from rezon.replay import Disposition, ReplayCandidate, ReplaySource, StrategyInput
from rezon.replay_strategies import ALL_GUARDS, GuardName, rezon_guarded


LITERAL = "Which answer is correct?"


def _candidate(
    candidate_id: str = "cand-a",
    answer: str | None = "A",
    *,
    solved_request: str | None = LITERAL,
    worker_id: str | None = None,
    execution_id: str | None = None,
    source_refs: tuple[str, ...] = (),
    model_id: str | None = None,
    provider_id: str | None = None,
    prompt_lineage: str | None = None,
    context_lineage: str | None = None,
    saw_candidate_ids: tuple[str, ...] = (),
    common_evidence_refs: tuple[str, ...] = (),
    failures: tuple[str, ...] = (),
    effect_claims: tuple[str, ...] = (),
    authority_claims: tuple[str, ...] = (),
    advisory_signals: tuple[tuple[str, float], ...] = (),
) -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=worker_id or f"worker-{candidate_id}",
        execution_id=execution_id or f"exec-{candidate_id}",
        answer=answer,
        solved_request=solved_request,
        source_refs=source_refs,
        model_id=model_id or f"model-{candidate_id}",
        provider_id=provider_id or f"provider-{candidate_id}",
        prompt_lineage=prompt_lineage or f"prompt-{candidate_id}",
        context_lineage=context_lineage or f"context-{candidate_id}",
        saw_candidate_ids=saw_candidate_ids,
        common_evidence_refs=common_evidence_refs,
        failures=failures,
        effect_claims=effect_claims,
        authority_claims=authority_claims,
        advisory_signals=advisory_signals,
    )


def _source(
    source_id: str,
    *,
    admission: str = "admitted",
    currentness: str = "current",
) -> ReplaySource:
    return ReplaySource(
        source_id=source_id,
        source_version="v1",
        locator=f"fixture://{source_id}",
        admission_status=admission,
        currentness_status=currentness,
        origin_id=f"origin-{source_id}",
    )


def _input(
    *candidates: ReplayCandidate,
    sources: tuple[ReplaySource, ...] = (),
) -> StrategyInput:
    return StrategyInput(
        case_id="guard-case",
        fixture_version="benchmark-v1.0",
        literal_request=LITERAL,
        primary_candidate_id=candidates[0].candidate_id,
        candidates=tuple(candidates),
        sources=sources,
    )


def _without(guard: GuardName):
    return frozenset(item for item in ALL_GUARDS if item is not guard)


def _assert_guard_blocks_and_ablation_passes(
    inp: StrategyInput,
    guard: GuardName,
    *,
    answer: str = "A",
):
    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(inp, guards=_without(guard))

    assert guarded.disposition is Disposition.FAIL_CLOSED
    assert guard.value in guarded.detected_violations
    assert ablated.disposition is Disposition.ANSWER
    assert ablated.answer == answer


def test_proposition_fidelity_guard_is_independently_ablatable():
    inp = _input(_candidate(solved_request="A different proposition"))
    _assert_guard_blocks_and_ablation_passes(inp, GuardName.PROPOSITION_FIDELITY)


def test_provenance_currentness_guard_is_independently_ablatable_even_with_high_confidence():
    source = _source("source-a", currentness="stale")
    candidate = _candidate(
        source_refs=("source-a",),
        advisory_signals=(("confidence", 0.9999), ("path_score", 1.0)),
    )
    inp = _input(candidate, sources=(source,))
    _assert_guard_blocks_and_ablation_passes(inp, GuardName.PROVENANCE_CURRENTNESS)


def test_admission_integrity_guard_is_independently_ablatable():
    source = _source("source-a", admission="retrieved_only", currentness="current")
    inp = _input(_candidate(source_refs=("source-a",)), sources=(source,))
    _assert_guard_blocks_and_ablation_passes(inp, GuardName.ADMISSION_INTEGRITY)


def test_failure_visibility_guard_is_independently_ablatable():
    inp = _input(_candidate(failures=("worker-partial-failure",)))
    _assert_guard_blocks_and_ablation_passes(inp, GuardName.FAILURE_VISIBILITY)


def test_authority_effect_boundary_guard_is_independently_ablatable():
    inp = _input(
        _candidate(
            authority_claims=("may-deploy",),
            effect_claims=("active", "qualified"),
            advisory_signals=(("confidence", 1.0),),
        )
    )
    _assert_guard_blocks_and_ablation_passes(inp, GuardName.AUTHORITY_EFFECT_BOUNDARY)


def test_independence_contamination_guard_rejects_correlated_consensus_and_is_ablatable():
    correlated = (
        _candidate(
            "cand-a",
            model_id="model-a",
            provider_id="shared-provider",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
        ),
        _candidate(
            "cand-b",
            model_id="model-b",
            provider_id="shared-provider",
            prompt_lineage="prompt-b",
            context_lineage="context-b",
        ),
    )
    inp = _input(*correlated)
    _assert_guard_blocks_and_ablation_passes(inp, GuardName.INDEPENDENCE_CONTAMINATION)


def test_clean_consensus_is_not_rejected_merely_for_worker_count_or_same_answer():
    inp = _input(
        _candidate(
            "cand-a",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
        ),
        _candidate(
            "cand-b",
            model_id="model-b",
            provider_id="provider-b",
            prompt_lineage="prompt-b",
            context_lineage="context-b",
        ),
    )

    outcome = rezon_guarded(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "A"
    assert outcome.detected_violations == ()
    assert outcome.accepted_candidate_ids == ("cand-a", "cand-b")


def test_insufficient_evidence_does_not_invent_an_answer():
    inp = _input(_candidate(answer=None))

    outcome = rezon_guarded(inp)

    assert outcome.disposition is Disposition.FAIL_CLOSED
    assert outcome.answer is None
    assert outcome.accepted_candidate_ids == ()


def test_candidate_exposure_and_common_evidence_are_independence_contamination():
    inp = _input(
        _candidate(
            "cand-a",
            saw_candidate_ids=("cand-b",),
            common_evidence_refs=("evidence-shared",),
        ),
        _candidate("cand-b"),
    )

    outcome = rezon_guarded(inp)

    assert outcome.disposition is Disposition.FAIL_CLOSED
    assert GuardName.INDEPENDENCE_CONTAMINATION.value in outcome.detected_violations
