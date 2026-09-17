from __future__ import annotations

from collections import Counter

from .replay import Disposition, ReplayCandidate, ReplayStrategyOutcome, StrategyInput


def _normalized_answer(answer: str) -> str:
    """Normalize incidental whitespace without adding semantic equivalence."""
    return " ".join(answer.split())


def _fail_closed(*, rejected: tuple[str, ...], trace: tuple[str, ...], operations: int) -> ReplayStrategyOutcome:
    return ReplayStrategyOutcome(
        disposition=Disposition.FAIL_CLOSED,
        answer=None,
        accepted_candidate_ids=(),
        rejected_candidate_ids=rejected,
        operation_count=operations,
        trace=trace,
    )


def single_pass(strategy_input: StrategyInput) -> ReplayStrategyOutcome:
    """Return the exact designated primary candidate without governance inspection."""
    primary: ReplayCandidate | None = next(
        (
            candidate
            for candidate in strategy_input.candidates
            if candidate.candidate_id == strategy_input.primary_candidate_id
        ),
        None,
    )
    if primary is None:
        return _fail_closed(
            rejected=(),
            trace=(f"primary_missing:{strategy_input.primary_candidate_id}",),
            operations=0,
        )

    if primary.answer is None or not _normalized_answer(primary.answer):
        return _fail_closed(
            rejected=(primary.candidate_id,),
            trace=(f"primary_no_answer:{primary.candidate_id}",),
            operations=1,
        )

    answer = _normalized_answer(primary.answer)
    return ReplayStrategyOutcome(
        disposition=Disposition.ANSWER,
        answer=answer,
        accepted_candidate_ids=(primary.candidate_id,),
        rejected_candidate_ids=(),
        operation_count=1,
        trace=(f"primary_selected:{primary.candidate_id}",),
    )


def fixed_multipass(strategy_input: StrategyInput) -> ReplayStrategyOutcome:
    """Apply deterministic exact-answer voting over eligible frozen candidates.

    Eligibility intentionally ignores governance metadata other than explicit
    execution failures. Answer matching normalizes whitespace only; it does not
    perform semantic equivalence, case folding, provenance checks, or authority
    checks.
    """
    eligible: list[tuple[ReplayCandidate, str]] = []
    rejected: list[str] = []
    trace: list[str] = []

    for candidate in strategy_input.candidates:
        if candidate.failures:
            rejected.append(candidate.candidate_id)
            trace.append(f"excluded_failure:{candidate.candidate_id}")
            continue
        if candidate.answer is None:
            rejected.append(candidate.candidate_id)
            trace.append(f"excluded_no_answer:{candidate.candidate_id}")
            continue
        normalized = _normalized_answer(candidate.answer)
        if not normalized:
            rejected.append(candidate.candidate_id)
            trace.append(f"excluded_no_answer:{candidate.candidate_id}")
            continue
        eligible.append((candidate, normalized))
        trace.append(f"counted:{candidate.candidate_id}")

    operations = len(strategy_input.candidates)
    if not eligible:
        return _fail_closed(
            rejected=tuple(rejected),
            trace=tuple(trace) + ("no_eligible_candidate",),
            operations=operations,
        )

    counts = Counter(answer for _, answer in eligible)
    highest = max(counts.values())
    winning_answers = {answer for answer, count in counts.items() if count == highest}

    # Fixture order is the deterministic tie breaker.
    winner = next(answer for _, answer in eligible if answer in winning_answers)
    accepted = tuple(
        candidate.candidate_id
        for candidate, answer in eligible
        if answer == winner
    )
    rejected_ids = tuple(
        candidate.candidate_id
        for candidate in strategy_input.candidates
        if candidate.candidate_id not in set(accepted)
    )

    return ReplayStrategyOutcome(
        disposition=Disposition.ANSWER,
        answer=winner,
        accepted_candidate_ids=accepted,
        rejected_candidate_ids=rejected_ids,
        operation_count=operations,
        trace=tuple(trace) + (f"selected:{winner}",),
    )
