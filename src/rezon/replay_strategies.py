from __future__ import annotations

from collections import Counter
from enum import Enum

from .replay import Disposition, ReplayCandidate, ReplayStrategyOutcome, StrategyInput


class GuardName(str, Enum):
    PROPOSITION_FIDELITY = "proposition_fidelity"
    PROVENANCE_CURRENTNESS = "provenance_currentness"
    ADMISSION_INTEGRITY = "admission_integrity"
    INDEPENDENCE_CONTAMINATION = "independence_contamination"
    FAILURE_VISIBILITY = "failure_visibility"
    AUTHORITY_EFFECT_BOUNDARY = "authority_effect_boundary"


GuardConfig = frozenset[GuardName]
ALL_GUARDS: GuardConfig = frozenset(GuardName)
_GUARD_ORDER = (
    GuardName.PROPOSITION_FIDELITY,
    GuardName.PROVENANCE_CURRENTNESS,
    GuardName.ADMISSION_INTEGRITY,
    GuardName.INDEPENDENCE_CONTAMINATION,
    GuardName.FAILURE_VISIBILITY,
    GuardName.AUTHORITY_EFFECT_BOUNDARY,
)


def _normalized_answer(answer: str) -> str:
    """Normalize incidental whitespace without adding semantic equivalence."""
    return " ".join(answer.split())


def _normalized_request(request: str | None) -> str | None:
    if request is None:
        return None
    return " ".join(request.split())


def _fail_closed(
    *,
    rejected: tuple[str, ...],
    trace: tuple[str, ...],
    operations: int,
    detected_violations: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
) -> ReplayStrategyOutcome:
    return ReplayStrategyOutcome(
        disposition=Disposition.FAIL_CLOSED,
        answer=None,
        accepted_candidate_ids=(),
        rejected_candidate_ids=rejected,
        detected_violations=detected_violations,
        unresolved=unresolved,
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
    accepted_set = set(accepted)
    rejected_ids = tuple(
        candidate.candidate_id
        for candidate in strategy_input.candidates
        if candidate.candidate_id not in accepted_set
    )

    return ReplayStrategyOutcome(
        disposition=Disposition.ANSWER,
        answer=winner,
        accepted_candidate_ids=accepted,
        rejected_candidate_ids=rejected_ids,
        operation_count=operations,
        trace=tuple(trace) + (f"selected:{winner}",),
    )


def _independence_contaminated_ids(strategy_input: StrategyInput) -> set[str]:
    contaminated: set[str] = set()
    candidates = strategy_input.candidates
    by_id = {candidate.candidate_id: candidate for candidate in candidates}

    for candidate in candidates:
        for seen_id in candidate.saw_candidate_ids:
            contaminated.add(candidate.candidate_id)
            if seen_id in by_id:
                contaminated.add(seen_id)
        if candidate.common_evidence_refs:
            contaminated.add(candidate.candidate_id)

    for index, left in enumerate(candidates):
        for right in candidates[index + 1 :]:
            left_lineage = (
                left.worker_id,
                left.execution_id,
                left.model_id,
                left.provider_id,
                left.prompt_lineage,
                left.context_lineage,
            )
            right_lineage = (
                right.worker_id,
                right.execution_id,
                right.model_id,
                right.provider_id,
                right.prompt_lineage,
                right.context_lineage,
            )
            incomplete = any(item is None or item == "" for item in left_lineage + right_lineage)
            shared_lineage = any(a == b for a, b in zip(left_lineage, right_lineage))
            shared_evidence = bool(
                set(left.common_evidence_refs) & set(right.common_evidence_refs)
            )
            direct_exposure = (
                right.candidate_id in left.saw_candidate_ids
                or left.candidate_id in right.saw_candidate_ids
            )
            if incomplete or shared_lineage or shared_evidence or direct_exposure:
                contaminated.add(left.candidate_id)
                contaminated.add(right.candidate_id)

    return contaminated


def _candidate_guard_violations(
    strategy_input: StrategyInput,
    candidate: ReplayCandidate,
    enabled: GuardConfig,
    independence_contaminated: set[str],
) -> tuple[GuardName, ...]:
    violations: list[GuardName] = []
    sources = {source.source_id: source for source in strategy_input.sources}

    if GuardName.PROPOSITION_FIDELITY in enabled:
        if _normalized_request(candidate.solved_request) != _normalized_request(
            strategy_input.literal_request
        ):
            violations.append(GuardName.PROPOSITION_FIDELITY)

    if GuardName.PROVENANCE_CURRENTNESS in enabled:
        if any(
            source_ref not in sources
            or sources[source_ref].currentness_status != "current"
            for source_ref in candidate.source_refs
        ):
            violations.append(GuardName.PROVENANCE_CURRENTNESS)

    if GuardName.ADMISSION_INTEGRITY in enabled:
        if any(
            source_ref not in sources
            or sources[source_ref].admission_status != "admitted"
            for source_ref in candidate.source_refs
        ):
            violations.append(GuardName.ADMISSION_INTEGRITY)

    if (
        GuardName.INDEPENDENCE_CONTAMINATION in enabled
        and candidate.candidate_id in independence_contaminated
    ):
        violations.append(GuardName.INDEPENDENCE_CONTAMINATION)

    if GuardName.FAILURE_VISIBILITY in enabled and candidate.failures:
        violations.append(GuardName.FAILURE_VISIBILITY)

    if GuardName.AUTHORITY_EFFECT_BOUNDARY in enabled:
        if candidate.authority_claims or candidate.effect_claims:
            violations.append(GuardName.AUTHORITY_EFFECT_BOUNDARY)

    return tuple(violations)


def rezon_guarded(
    strategy_input: StrategyInput,
    guards: GuardConfig = ALL_GUARDS,
) -> ReplayStrategyOutcome:
    """Integrate frozen candidates with explicit independently ablatable guards."""
    enabled = frozenset(guards)
    if any(not isinstance(guard, GuardName) for guard in enabled):
        raise ValueError("guards must contain GuardName values")

    independence_contaminated = _independence_contaminated_ids(strategy_input)
    eligible: list[tuple[ReplayCandidate, str]] = []
    rejected_ids: list[str] = []
    detected: list[GuardName] = []
    trace: list[str] = []

    for candidate in strategy_input.candidates:
        violations = _candidate_guard_violations(
            strategy_input,
            candidate,
            enabled,
            independence_contaminated,
        )
        if violations:
            rejected_ids.append(candidate.candidate_id)
            for guard in _GUARD_ORDER:
                if guard in violations and guard not in detected:
                    detected.append(guard)
            trace.extend(
                f"guard_reject:{guard.value}:{candidate.candidate_id}"
                for guard in violations
            )
            continue

        if candidate.answer is None or not _normalized_answer(candidate.answer):
            rejected_ids.append(candidate.candidate_id)
            trace.append(f"no_answer:{candidate.candidate_id}")
            continue

        eligible.append((candidate, _normalized_answer(candidate.answer)))
        trace.append(f"eligible:{candidate.candidate_id}")

    operations = len(strategy_input.candidates)
    detected_values = tuple(guard.value for guard in detected)
    if not eligible:
        return _fail_closed(
            rejected=tuple(rejected_ids),
            trace=tuple(trace) + ("no_guarded_candidate",),
            operations=operations,
            detected_violations=detected_values,
            unresolved=("no_guarded_candidate",),
        )

    counts = Counter(answer for _, answer in eligible)
    highest = max(counts.values())
    winning_answers = {answer for answer, count in counts.items() if count == highest}
    winner = next(answer for _, answer in eligible if answer in winning_answers)
    accepted = tuple(
        candidate.candidate_id
        for candidate, answer in eligible
        if answer == winner
    )
    accepted_set = set(accepted)
    rejected = tuple(
        candidate.candidate_id
        for candidate in strategy_input.candidates
        if candidate.candidate_id not in accepted_set
    )

    return ReplayStrategyOutcome(
        disposition=Disposition.ANSWER,
        answer=winner,
        accepted_candidate_ids=accepted,
        rejected_candidate_ids=rejected,
        detected_violations=detected_values,
        unresolved=(),
        operation_count=operations,
        trace=tuple(trace) + (f"selected:{winner}",),
    )
