from __future__ import annotations

from rezon.replay import Disposition, ReplayCandidate, ReplaySource, StrategyInput
from rezon.replay_strategies import fixed_multipass, single_pass


def _candidate(
    candidate_id: str,
    answer: str | None,
    *,
    failures: tuple[str, ...] = (),
    source_refs: tuple[str, ...] = (),
    common_evidence_refs: tuple[str, ...] = (),
    authority_claims: tuple[str, ...] = (),
    effect_claims: tuple[str, ...] = (),
) -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=f"worker-{candidate_id}",
        execution_id=f"exec-{candidate_id}",
        answer=answer,
        solved_request="Which answer is correct?",
        source_refs=source_refs,
        model_id=f"model-{candidate_id}",
        provider_id=f"provider-{candidate_id}",
        prompt_lineage=f"prompt-{candidate_id}",
        context_lineage=f"context-{candidate_id}",
        common_evidence_refs=common_evidence_refs,
        failures=failures,
        authority_claims=authority_claims,
        effect_claims=effect_claims,
    )


def _input(
    *candidates: ReplayCandidate,
    primary: str,
    sources: tuple[ReplaySource, ...] = (),
) -> StrategyInput:
    return StrategyInput(
        case_id="case-baseline",
        fixture_version="benchmark-v1.0",
        literal_request="Which answer is correct?",
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
    assert outcome.rejected_candidate_ids == ()
    assert outcome.operation_count == 1
    assert "cand-2" in " ".join(outcome.trace)


def test_single_pass_fails_closed_when_primary_has_no_answer():
    inp = _input(
        _candidate("cand-1", "other"),
        _candidate("cand-2", None),
        primary="cand-2",
    )

    outcome = single_pass(inp)

    assert outcome.disposition is Disposition.FAIL_CLOSED
    assert outcome.answer is None
    assert outcome.accepted_candidate_ids == ()
    assert outcome.rejected_candidate_ids == ("cand-2",)


def test_fixed_multipass_tie_breaks_by_earliest_eligible_candidate_order():
    inp = _input(
        _candidate("cand-1", "A"),
        _candidate("cand-2", "B"),
        _candidate("cand-3", "B"),
        _candidate("cand-4", "A"),
        primary="cand-3",
    )

    outcome = fixed_multipass(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "A"
    assert outcome.accepted_candidate_ids == ("cand-1", "cand-4")


def test_fixed_multipass_excludes_explicit_failures_and_no_answer_candidates():
    inp = _input(
        _candidate("cand-1", "A", failures=("timeout",)),
        _candidate("cand-2", None),
        _candidate("cand-3", "B"),
        _candidate("cand-4", "B"),
        primary="cand-1",
    )

    outcome = fixed_multipass(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "B"
    assert outcome.accepted_candidate_ids == ("cand-3", "cand-4")
    assert outcome.rejected_candidate_ids == ("cand-1", "cand-2")


def test_fixed_multipass_fails_closed_when_no_candidate_is_eligible():
    inp = _input(
        _candidate("cand-1", None),
        _candidate("cand-2", "A", failures=("worker-failed",)),
        primary="cand-1",
    )

    outcome = fixed_multipass(inp)

    assert outcome.disposition is Disposition.FAIL_CLOSED
    assert outcome.answer is None
    assert outcome.accepted_candidate_ids == ()
    assert outcome.rejected_candidate_ids == ("cand-1", "cand-2")


def test_fixed_multipass_normalizes_whitespace_but_not_case_or_wording():
    inp = _input(
        _candidate("cand-1", "  Alpha   Beta  "),
        _candidate("cand-2", "Alpha Beta"),
        _candidate("cand-3", "alpha beta"),
        primary="cand-3",
    )

    outcome = fixed_multipass(inp)

    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "Alpha Beta"
    assert outcome.accepted_candidate_ids == ("cand-1", "cand-2")


def test_baselines_do_not_use_governance_metadata_to_improve_selection():
    stale_source = ReplaySource(
        source_id="source-stale",
        source_version="v0",
        locator="fixture://stale",
        admission_status="retrieved_only",
        currentness_status="stale",
        origin_id="origin-stale",
    )
    suspicious_primary = _candidate(
        "cand-1",
        "A",
        source_refs=("source-stale",),
        common_evidence_refs=("shared",),
        authority_claims=("may-deploy",),
        effect_claims=("qualified",),
    )
    clean_minorities = (
        _candidate("cand-2", "B"),
        _candidate("cand-3", "B"),
    )
    inp = _input(
        suspicious_primary,
        *clean_minorities,
        primary="cand-1",
        sources=(stale_source,),
    )

    single = single_pass(inp)
    fixed = fixed_multipass(inp)

    assert single.answer == "A"
    assert fixed.answer == "B"
    assert "PROVENANCE_CURRENTNESS" not in fixed.detected_violations
    assert "AUTHORITY_EFFECT_BOUNDARY" not in fixed.detected_violations
