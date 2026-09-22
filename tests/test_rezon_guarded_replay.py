from rezon.replay import Disposition, ReplayCandidate, ReplaySource, StrategyInput
from rezon.replay_strategies import (
    ALL_GUARDS,
    GuardConfig,
    GuardName,
    rezon_guarded,
)


def _source(
    source_id: str = "source-1",
    *,
    admitted: str = "ADMITTED",
    current: bool = True,
) -> ReplaySource:
    return ReplaySource(
        source_id=source_id,
        source_version="v1",
        locator=f"fixture:{source_id}",
        admission_status=admitted,
        is_current=current,
        origin_id=f"origin:{source_id}",
    )


def _candidate(
    candidate_id: str = "cand-1",
    *,
    worker_id: str | None = None,
    execution_id: str | None = None,
    answer: str | None = "A",
    solved_request: str | None = "What is current?",
    source_refs: tuple[str, ...] = ("source-1",),
    model_id: str | None = "model-1",
    provider_id: str | None = "provider-1",
    prompt_lineage: str | None = "prompt-1",
    context_lineage: str | None = "context-1",
    saw_other_answer: bool | None = False,
    common_evidence_refs: tuple[str, ...] = (),
    failure: str | None = None,
    effect_state_claim: str | None = None,
    authority_claims: tuple[str, ...] = (),
    advisory_signals: tuple[tuple[str, object], ...] = (),
) -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=worker_id or f"worker-{candidate_id}",
        execution_id=execution_id or f"exec-{candidate_id}",
        answer=answer,
        solved_request=solved_request,
        source_refs=source_refs,
        model_id=model_id,
        provider_id=provider_id,
        prompt_lineage=prompt_lineage,
        context_lineage=context_lineage,
        saw_other_answer=saw_other_answer,
        common_evidence_refs=common_evidence_refs,
        failure=failure,
        effect_state_claim=effect_state_claim,
        authority_claims=authority_claims,
        advisory_signals=advisory_signals,
    )


def _input(
    *candidates: ReplayCandidate,
    sources: tuple[ReplaySource, ...] = (_source(),),
) -> StrategyInput:
    return StrategyInput(
        case_id="case-guard",
        fixture_version="benchmark-v1.0",
        literal_request="What is current?",
        primary_candidate_id=candidates[0].candidate_id,
        candidates=tuple(candidates),
        sources=sources,
    )


def _without(guard: GuardName) -> GuardConfig:
    return ALL_GUARDS.without(guard)


def test_guard_config_exposes_all_six_named_controls():
    assert ALL_GUARDS.enabled == frozenset(GuardName)
    assert len(ALL_GUARDS.enabled) == 6


def test_proposition_fidelity_guard_blocks_literal_request_substitution():
    inp = _input(_candidate(solved_request="Answer a different question"))

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(inp, guards=_without(GuardName.PROPOSITION_FIDELITY))

    assert guarded.disposition is Disposition.ABSTAIN
    assert "PROPOSITION_FIDELITY" in guarded.violations_detected
    assert ablated.disposition is Disposition.ANSWER


def test_provenance_currentness_guard_blocks_stale_source():
    inp = _input(_candidate(), sources=(_source(current=False),))

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(inp, guards=_without(GuardName.PROVENANCE_CURRENTNESS))

    assert guarded.disposition is Disposition.ABSTAIN
    assert "PROVENANCE_CURRENTNESS" in guarded.violations_detected
    assert ablated.disposition is Disposition.ANSWER


def test_admission_integrity_guard_blocks_unadmitted_source():
    inp = _input(
        _candidate(),
        sources=(_source(admitted="RETRIEVED_UNADMITTED"),),
    )

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(inp, guards=_without(GuardName.ADMISSION_INTEGRITY))

    assert guarded.disposition is Disposition.ABSTAIN
    assert "ADMISSION_INTEGRITY" in guarded.violations_detected
    assert ablated.disposition is Disposition.ANSWER


def test_independence_guard_blocks_correlated_consensus():
    inp = _input(
        _candidate(
            "cand-1",
            model_id="shared-model",
            provider_id="shared-provider",
            prompt_lineage="shared-prompt",
            context_lineage="shared-context",
            common_evidence_refs=("evidence-shared",),
        ),
        _candidate(
            "cand-2",
            model_id="shared-model",
            provider_id="shared-provider",
            prompt_lineage="shared-prompt",
            context_lineage="shared-context",
            common_evidence_refs=("evidence-shared",),
        ),
    )

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(inp, guards=_without(GuardName.INDEPENDENCE_CONTAMINATION))

    assert guarded.disposition is Disposition.ABSTAIN
    assert "INDEPENDENCE_CONTAMINATION" in guarded.violations_detected
    assert ablated.disposition is Disposition.ANSWER


def test_failure_visibility_guard_does_not_hide_failed_peer_behind_answer():
    inp = _input(
        _candidate("cand-1", answer="A"),
        _candidate("cand-2", answer=None, failure="UNAVAILABLE"),
    )

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(inp, guards=_without(GuardName.FAILURE_VISIBILITY))

    assert guarded.disposition is Disposition.ABSTAIN
    assert "FAILURE_VISIBILITY" in guarded.violations_detected
    assert "cand-2:UNAVAILABLE" in guarded.unresolved
    assert ablated.disposition is Disposition.ANSWER


def test_authority_effect_guard_blocks_candidate_self_promotion():
    inp = _input(
        _candidate(
            effect_state_claim="ACTIVE",
            authority_claims=("SELF_AUTHORIZED",),
        )
    )

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(inp, guards=_without(GuardName.AUTHORITY_EFFECT_BOUNDARY))

    assert guarded.disposition is Disposition.ABSTAIN
    assert "AUTHORITY_EFFECT_BOUNDARY" in guarded.violations_detected
    assert ablated.disposition is Disposition.ANSWER


def test_clean_control_answers_with_all_guards_enabled():
    inp = _input(_candidate())

    outcome = rezon_guarded(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "A"
    assert outcome.violations_detected == ()
    assert outcome.accepted_candidate_ids == ("cand-1",)


def test_insufficient_answer_material_does_not_invent_certainty():
    inp = _input(_candidate(answer=None))

    outcome = rezon_guarded(inp)

    assert outcome.disposition is Disposition.ABSTAIN
    assert outcome.answer is None
    assert outcome.accepted_candidate_ids == ()


def test_advisory_signals_do_not_override_authority_effect_boundary():
    inp = _input(
        _candidate(
            effect_state_claim="QUALIFIED",
            authority_claims=("MODEL_CONFIDENCE",),
            advisory_signals=(("confidence", 0.999), ("path_score", 1000.0)),
        )
    )

    outcome = rezon_guarded(inp)

    assert outcome.disposition is Disposition.ABSTAIN
    assert "AUTHORITY_EFFECT_BOUNDARY" in outcome.violations_detected



def test_independence_guard_fails_closed_when_multiworker_lineage_is_unbound():
    inp = _input(
        _candidate(
            "cand-1",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage=None,
            context_lineage=None,
        ),
        _candidate(
            "cand-2",
            model_id="model-b",
            provider_id="provider-b",
            prompt_lineage=None,
            context_lineage=None,
        ),
    )

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(
        inp,
        guards=_without(GuardName.INDEPENDENCE_CONTAMINATION),
    )

    assert guarded.disposition is Disposition.ABSTAIN
    assert "INDEPENDENCE_CONTAMINATION" in guarded.violations_detected
    assert any(
        item.startswith("independence_unestablished:")
        for item in guarded.unresolved
    )
    assert ablated.disposition is Disposition.ANSWER


def test_independence_guard_accepts_explicitly_distinct_multiworker_lineage():
    inp = _input(
        _candidate(
            "cand-1",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
        ),
        _candidate(
            "cand-2",
            model_id="model-b",
            provider_id="provider-b",
            prompt_lineage="prompt-b",
            context_lineage="context-b",
        ),
    )

    outcome = rezon_guarded(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "A"
    assert "INDEPENDENCE_CONTAMINATION" not in outcome.violations_detected



def test_shared_source_refs_are_surfaced_without_false_worker_contamination():
    inp = _input(
        _candidate(
            "cand-1",
            source_refs=("source-1",),
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
            common_evidence_refs=(),
        ),
        _candidate(
            "cand-2",
            source_refs=("source-1",),
            model_id="model-b",
            provider_id="provider-b",
            prompt_lineage="prompt-b",
            context_lineage="context-b",
            common_evidence_refs=(),
        ),
    )

    guarded = rezon_guarded(inp)

    assert guarded.disposition is Disposition.ANSWER
    assert "INDEPENDENCE_CONTAMINATION" not in guarded.violations_detected
    assert any(
        item == "independence:shared_source_ref:source-1"
        for item in guarded.trace
    )
    assert "shared_evidence_overlap:source-1" in guarded.unresolved



def test_duplicate_execution_identity_fails_structural_validation():
    inp = _input(
        _candidate(
            "cand-1",
            worker_id="worker-a",
            execution_id="exec-shared",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
        ),
        _candidate(
            "cand-2",
            worker_id="worker-b",
            execution_id="exec-shared",
            model_id="model-b",
            provider_id="provider-b",
            prompt_lineage="prompt-b",
            context_lineage="context-b",
        ),
    )

    import pytest
    from rezon.replay import ReplayValidationError

    with pytest.raises(ReplayValidationError, match="execution IDs must be unique"):
        rezon_guarded(inp)


def test_independence_guard_blocks_same_worker_across_distinct_executions():
    inp = _input(
        _candidate(
            "cand-1",
            worker_id="worker-shared",
            execution_id="exec-a",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
        ),
        _candidate(
            "cand-2",
            worker_id="worker-shared",
            execution_id="exec-b",
            model_id="model-b",
            provider_id="provider-b",
            prompt_lineage="prompt-b",
            context_lineage="context-b",
        ),
    )

    guarded = rezon_guarded(inp)
    ablated = rezon_guarded(
        inp,
        guards=_without(GuardName.INDEPENDENCE_CONTAMINATION),
    )

    assert guarded.disposition is Disposition.ABSTAIN
    assert "INDEPENDENCE_CONTAMINATION" in guarded.violations_detected
    assert any(
        item == "guard:independence_contamination:correlated:reject:cand-1"
        for item in guarded.trace
    )
    assert any(
        item == "guard:independence_contamination:correlated:reject:cand-2"
        for item in guarded.trace
    )
    assert ablated.disposition is Disposition.ANSWER
