from __future__ import annotations

from collections import Counter

from .replay import Disposition, ReplayCandidate, ReplayStrategyOutcome, StrategyInput


def _normalize_answer(answer: str) -> str:
    return " ".join(answer.split()).casefold()


def _candidate_by_id(strategy_input: StrategyInput, candidate_id: str) -> ReplayCandidate | None:
    for candidate in strategy_input.candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    return None


def single_pass(strategy_input: StrategyInput) -> ReplayStrategyOutcome:
    """Return only the designated primary candidate, with no cross-worker governance."""
    candidate = _candidate_by_id(strategy_input, strategy_input.primary_candidate_id)
    if candidate is None:
        return ReplayStrategyOutcome(
            disposition=Disposition.FAIL_CLOSED,
            rejected_candidate_ids=(strategy_input.primary_candidate_id,),
            unresolved=("primary_candidate_missing",),
            operation_count=1,
            trace=(f"primary:{strategy_input.primary_candidate_id}:missing",),
        )
    if candidate.failure is not None or candidate.answer is None:
        reason = candidate.failure or "missing_answer"
        return ReplayStrategyOutcome(
            disposition=Disposition.FAIL_CLOSED,
            rejected_candidate_ids=(candidate.candidate_id,),
            unresolved=(reason,),
            operation_count=1,
            trace=(f"primary:{candidate.candidate_id}:ineligible:{reason}",),
        )
    return ReplayStrategyOutcome(
        disposition=Disposition.ANSWER,
        answer=candidate.answer,
        accepted_candidate_ids=(candidate.candidate_id,),
        operation_count=1,
        trace=(f"primary:{candidate.candidate_id}:selected",),
    )


def fixed_multipass(strategy_input: StrategyInput) -> ReplayStrategyOutcome:
    """Use a fixed deterministic exact-answer vote without epistemic governance."""
    eligible: list[ReplayCandidate] = []
    rejected: list[str] = []
    normalized_answers: list[str] = []

    for candidate in strategy_input.candidates:
        if candidate.failure is not None or candidate.answer is None:
            rejected.append(candidate.candidate_id)
            continue
        eligible.append(candidate)
        normalized_answers.append(_normalize_answer(candidate.answer))

    operation_count = len(strategy_input.candidates)
    if not eligible:
        return ReplayStrategyOutcome(
            disposition=Disposition.FAIL_CLOSED,
            rejected_candidate_ids=tuple(rejected),
            unresolved=("no_eligible_candidates",),
            operation_count=operation_count,
            trace=tuple(
                f"candidate:{candidate.candidate_id}:ineligible"
                for candidate in strategy_input.candidates
            ),
        )

    counts = Counter(normalized_answers)
    highest_count = max(counts.values())
    winning_normalized = next(
        normalized
        for normalized in normalized_answers
        if counts[normalized] == highest_count
    )
    accepted = tuple(
        candidate.candidate_id
        for candidate, normalized in zip(eligible, normalized_answers)
        if normalized == winning_normalized
    )
    rejected.extend(
        candidate.candidate_id
        for candidate, normalized in zip(eligible, normalized_answers)
        if normalized != winning_normalized
    )
    representative = next(
        candidate.answer
        for candidate, normalized in zip(eligible, normalized_answers)
        if normalized == winning_normalized
    )

    return ReplayStrategyOutcome(
        disposition=Disposition.ANSWER,
        answer=representative,
        accepted_candidate_ids=accepted,
        rejected_candidate_ids=tuple(rejected),
        operation_count=operation_count,
        trace=tuple(
            f"candidate:{candidate.candidate_id}:eligible:{normalized}"
            for candidate, normalized in zip(eligible, normalized_answers)
        ),
    )
