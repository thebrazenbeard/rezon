from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum


class ResolutionPlanningError(ValueError):
    pass


class ResolutionLevel(IntEnum):
    L0_EXACT = 0
    L1_HIGH_FIDELITY = 1
    L2_SEMANTIC = 2
    L3_ABSTRACT = 3


class ResolutionPlanStatus(StrEnum):
    PROMOTE = "PROMOTE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"


def _require_text(value: object, label: str) -> str:
    if type(value) is not str or not value:
        raise ResolutionPlanningError(f"{label} must be a non-empty exact str")
    return value


def _require_nonnegative_int(value: object, label: str) -> int:
    if type(value) is not int or isinstance(value, bool) or value < 0:
        raise ResolutionPlanningError(f"{label} must be a non-negative exact int")
    return value


@dataclass(frozen=True, slots=True)
class ResolutionFault:
    proposition_or_subtask: str
    evidence_ref: str
    available_resolution: ResolutionLevel
    required_resolution: ResolutionLevel
    exactness_required: bool
    reason: str
    expected_information_gain: int

    def __post_init__(self) -> None:
        _require_text(self.proposition_or_subtask, "proposition_or_subtask")
        _require_text(self.evidence_ref, "evidence_ref")
        _require_text(self.reason, "reason")
        if type(self.available_resolution) is not ResolutionLevel:
            raise ResolutionPlanningError(
                "available_resolution must be an exact ResolutionLevel"
            )
        if type(self.required_resolution) is not ResolutionLevel:
            raise ResolutionPlanningError(
                "required_resolution must be an exact ResolutionLevel"
            )
        if type(self.exactness_required) is not bool:
            raise ResolutionPlanningError(
                "exactness_required must be an exact bool"
            )
        _require_nonnegative_int(
            self.expected_information_gain,
            "expected_information_gain",
        )
        if self.required_resolution >= self.available_resolution:
            raise ResolutionPlanningError(
                "resolution fault must request higher fidelity than available"
            )
        if (
            self.exactness_required
            and self.required_resolution is not ResolutionLevel.L0_EXACT
        ):
            raise ResolutionPlanningError(
                "exactness_required faults must request L0_EXACT"
            )


@dataclass(frozen=True, slots=True)
class ResolutionOffer:
    evidence_ref: str
    resolution: ResolutionLevel
    byte_cost: int
    exact_backing_available: bool

    def __post_init__(self) -> None:
        _require_text(self.evidence_ref, "evidence_ref")
        if type(self.resolution) is not ResolutionLevel:
            raise ResolutionPlanningError(
                "resolution must be an exact ResolutionLevel"
            )
        _require_nonnegative_int(self.byte_cost, "byte_cost")
        if type(self.exact_backing_available) is not bool:
            raise ResolutionPlanningError(
                "exact_backing_available must be an exact bool"
            )


@dataclass(frozen=True, slots=True)
class ResolutionPlan:
    status: ResolutionPlanStatus
    evidence_ref: str
    requested_resolution: ResolutionLevel
    exactness_required: bool
    estimated_bytes: int
    reason: str


def plan_resolution_fault(
    fault: ResolutionFault,
    offers: tuple[ResolutionOffer, ...],
    *,
    byte_budget: int,
) -> ResolutionPlan:
    if type(fault) is not ResolutionFault:
        raise ResolutionPlanningError(
            "fault must be an exact ResolutionFault"
        )
    if type(offers) is not tuple:
        raise ResolutionPlanningError("offers must be an exact tuple")
    for offer in offers:
        if type(offer) is not ResolutionOffer:
            raise ResolutionPlanningError(
                "offers must contain exact ResolutionOffer values"
            )
    _require_nonnegative_int(byte_budget, "byte_budget")

    matching = [
        offer
        for offer in offers
        if offer.evidence_ref == fault.evidence_ref
        and offer.resolution is fault.required_resolution
        and (
            not fault.exactness_required
            or offer.exact_backing_available
        )
    ]
    matching.sort(
        key=lambda offer: (
            offer.byte_cost,
            offer.evidence_ref,
            int(offer.resolution),
        )
    )

    if not matching:
        return ResolutionPlan(
            status=ResolutionPlanStatus.INSUFFICIENT_EVIDENCE,
            evidence_ref=fault.evidence_ref,
            requested_resolution=fault.required_resolution,
            exactness_required=fault.exactness_required,
            estimated_bytes=0,
            reason=(
                "no offer can satisfy the requested resolution and "
                "exactness requirement"
            ),
        )

    selected = matching[0]
    if selected.byte_cost > byte_budget:
        return ResolutionPlan(
            status=ResolutionPlanStatus.BUDGET_EXCEEDED,
            evidence_ref=fault.evidence_ref,
            requested_resolution=fault.required_resolution,
            exactness_required=fault.exactness_required,
            estimated_bytes=selected.byte_cost,
            reason="required promotion exceeds the available byte budget",
        )

    return ResolutionPlan(
        status=ResolutionPlanStatus.PROMOTE,
        evidence_ref=fault.evidence_ref,
        requested_resolution=fault.required_resolution,
        exactness_required=fault.exactness_required,
        estimated_bytes=selected.byte_cost,
        reason="promote only the implicated evidence to requested resolution",
    )
