from dataclasses import replace

from rezon.replay import Disposition, ReplayCandidate, ReplayCase, ReplaySource
from rezon.replay_experiments import (
    digest_strategy_inputs,
    run_guard_ablation,
    run_label_permutation_control,
    run_order_permutations,
)
from rezon.replay_strategies import GuardName, rezon_guarded


def _candidate(candidate_id: str, answer: str, **kwargs) -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=f"worker-{candidate_id}",
        execution_id=f"exec-{candidate_id}",
        answer=answer,
        solved_request="What is current?",
        model_id=kwargs.get("model_id", f"model-{candidate_id}"),
        provider_id=kwargs.get("provider_id", f"provider-{candidate_id}"),
        prompt_lineage=kwargs.get("prompt_lineage", f"prompt-{candidate_id}"),
        context_lineage=kwargs.get("context_lineage", f"context-{candidate_id}"),
        source_refs=kwargs.get("source_refs", ()),
        common_evidence_refs=kwargs.get("common_evidence_refs", ()),
        failure=kwargs.get("failure"),
        effect_state_claim=kwargs.get("effect_state_claim"),
        authority_claims=kwargs.get("authority_claims", ()),
    )


def _case(
    case_id: str,
    *,
    gold: Disposition = Disposition.ANSWER,
    gold_answer: str | None = "A",
    expected: tuple[str, ...] = (),
    candidates: tuple[ReplayCandidate, ...] | None = None,
    sources: tuple[ReplaySource, ...] = (),
) -> ReplayCase:
    candidates = candidates or (_candidate(f"{case_id}-a", "A"),)
    return ReplayCase(
        case_id=case_id,
        fixture_version="benchmark-v1.0",
        fixture_provenance="fixture:test",
        literal_request="What is current?",
        primary_candidate_id=candidates[0].candidate_id,
        gold_disposition=gold,
        gold_answer=gold_answer if gold is Disposition.ANSWER else None,
        expected_violations=expected,
        candidates=candidates,
        sources=sources,
    )


def test_order_permutation_preserves_deterministic_metrics():
    cases = (
        _case("case-a", gold_answer="A"),
        _case("case-b", gold=Disposition.ABSTAIN, gold_answer=None, candidates=(_candidate("case-b-a", "B", effect_state_claim="ACTIVE"),)),
        _case("case-c", gold_answer="A"),
    )

    results = run_order_permutations(
        cases,
        rezon_guarded,
        strategy_name="rezon_guarded",
        seeds=(11, 29),
    )

    assert len(results) == 2
    assert {result.seed for result in results} == {11, 29}
    assert all(result.permutation_id for result in results)
    for result in results:
        assert result.metrics == result.reference_metrics
        assert result.strategy_input_digest == digest_strategy_inputs(cases)


def test_guard_ablation_changes_only_guard_configuration_and_exposes_target_case():
    source = ReplaySource(
        source_id="src-a",
        source_version="v1",
        locator="fixture:src-a",
        admission_status="ADMITTED",
        is_current=False,
        origin_id="origin-a",
    )
    case = _case(
        "case-a",
        gold=Disposition.ABSTAIN,
        gold_answer=None,
        expected=("PROVENANCE_CURRENTNESS",),
        candidates=(_candidate("case-a-a", "A", source_refs=("src-a",)),),
        sources=(source,),
    )
    original_digest = digest_strategy_inputs((case,))

    results = run_guard_ablation((case,))
    by_guard = {result.removed_guard: result for result in results}

    assert set(by_guard) == set(GuardName)
    assert all(result.strategy_input_digest == original_digest for result in results)
    assert by_guard[GuardName.PROVENANCE_CURRENTNESS].metrics.false_accepts == 1
    for guard, result in by_guard.items():
        if guard is not GuardName.PROVENANCE_CURRENTNESS:
            assert result.metrics.false_accepts == 0


def test_label_permutation_changes_only_evaluator_labels_and_preserves_strategy_inputs():
    cases = (
        _case("case-a", gold=Disposition.ANSWER, gold_answer="A"),
        _case("case-b", gold=Disposition.ABSTAIN, gold_answer=None, expected=("PROVENANCE_CURRENTNESS",)),
        _case("case-c", gold=Disposition.FAIL_CLOSED, gold_answer=None, expected=("FAILURE_VISIBILITY",)),
    )
    before = digest_strategy_inputs(cases)

    result = run_label_permutation_control(
        cases,
        rezon_guarded,
        strategy_name="rezon_guarded",
        seed=20260916,
    )

    assert result.seed == 20260916
    assert result.permutation_id
    assert result.before_strategy_input_digest == before
    assert result.after_strategy_input_digest == before
    assert result.permuted_labels != result.original_labels


def test_label_permutation_breaks_an_apparently_perfect_semantic_result():
    cases = (
        _case("case-a", gold=Disposition.ANSWER, gold_answer="A"),
        _case(
            "case-b",
            gold=Disposition.ABSTAIN,
            gold_answer=None,
            expected=("AUTHORITY_EFFECT_BOUNDARY",),
            candidates=(_candidate("case-b-a", "B", effect_state_claim="ACTIVE"),),
        ),
        _case(
            "case-c",
            gold=Disposition.ABSTAIN,
            gold_answer=None,
            expected=("PROPOSITION_FIDELITY",),
            candidates=(replace(_candidate("case-c-a", "C"), solved_request="Different request"),),
        ),
    )

    result = run_label_permutation_control(
        cases,
        rezon_guarded,
        strategy_name="rezon_guarded",
        seed=7,
    )

    assert result.original_metrics.disposition_accuracy == 1.0
    assert result.permuted_metrics.disposition_accuracy < 1.0
