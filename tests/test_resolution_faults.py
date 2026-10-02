from __future__ import annotations

import importlib

import pytest


def _resolution():
    try:
        return importlib.import_module("rezon.resolution")
    except ModuleNotFoundError:
        pytest.fail("rezon.resolution is missing")


def _fault(module, **overrides):
    values = {
        "proposition_or_subtask": "verify exact callback identifier",
        "evidence_ref": "evidence:callback",
        "available_resolution": module.ResolutionLevel.L2_SEMANTIC,
        "required_resolution": module.ResolutionLevel.L0_EXACT,
        "exactness_required": True,
        "reason": "exact identifier required",
        "expected_information_gain": 10,
    }
    values.update(overrides)
    return module.ResolutionFault(**values)


def _offer(module, evidence_ref, resolution, byte_cost, *, exact_backing_available):
    return module.ResolutionOffer(
        evidence_ref=evidence_ref,
        resolution=resolution,
        byte_cost=byte_cost,
        exact_backing_available=exact_backing_available,
    )


def test_exact_fault_promotes_only_implicated_evidence():
    module = _resolution()
    fault = _fault(module)
    offers = (
        _offer(
            module,
            "evidence:irrelevant",
            module.ResolutionLevel.L0_EXACT,
            20,
            exact_backing_available=True,
        ),
        _offer(
            module,
            "evidence:callback",
            module.ResolutionLevel.L0_EXACT,
            42,
            exact_backing_available=True,
        ),
    )

    plan = module.plan_resolution_fault(
        fault,
        offers,
        byte_budget=100,
    )

    assert plan.status is module.ResolutionPlanStatus.PROMOTE
    assert plan.evidence_ref == "evidence:callback"
    assert plan.requested_resolution is module.ResolutionLevel.L0_EXACT
    assert plan.estimated_bytes == 42
    assert plan.exactness_required is True


def test_exact_fault_stays_unresolved_without_verified_exact_backing():
    module = _resolution()
    fault = _fault(module)
    offers = (
        _offer(
            module,
            "evidence:callback",
            module.ResolutionLevel.L0_EXACT,
            42,
            exact_backing_available=False,
        ),
        _offer(
            module,
            "evidence:callback",
            module.ResolutionLevel.L1_HIGH_FIDELITY,
            18,
            exact_backing_available=True,
        ),
    )

    plan = module.plan_resolution_fault(
        fault,
        offers,
        byte_budget=100,
    )

    assert plan.status is module.ResolutionPlanStatus.INSUFFICIENT_EVIDENCE
    assert plan.evidence_ref == "evidence:callback"
    assert plan.requested_resolution is module.ResolutionLevel.L0_EXACT
    assert plan.estimated_bytes == 0


def test_exact_fault_fails_closed_when_promotion_exceeds_budget():
    module = _resolution()
    fault = _fault(module)
    offers = (
        _offer(
            module,
            "evidence:callback",
            module.ResolutionLevel.L0_EXACT,
            101,
            exact_backing_available=True,
        ),
    )

    plan = module.plan_resolution_fault(
        fault,
        offers,
        byte_budget=100,
    )

    assert plan.status is module.ResolutionPlanStatus.BUDGET_EXCEEDED
    assert plan.estimated_bytes == 101


def test_planner_is_deterministic_across_offer_order():
    module = _resolution()
    fault = _fault(
        module,
        available_resolution=module.ResolutionLevel.L3_ABSTRACT,
        required_resolution=module.ResolutionLevel.L1_HIGH_FIDELITY,
        exactness_required=False,
    )
    first = _offer(
        module,
        "evidence:callback",
        module.ResolutionLevel.L1_HIGH_FIDELITY,
        30,
        exact_backing_available=False,
    )
    second = _offer(
        module,
        "evidence:callback",
        module.ResolutionLevel.L0_EXACT,
        50,
        exact_backing_available=True,
    )

    left = module.plan_resolution_fault(
        fault,
        (first, second),
        byte_budget=100,
    )
    right = module.plan_resolution_fault(
        fault,
        (second, first),
        byte_budget=100,
    )

    assert left == right
    assert left.status is module.ResolutionPlanStatus.PROMOTE
    assert left.requested_resolution is module.ResolutionLevel.L1_HIGH_FIDELITY
    assert left.estimated_bytes == 30


def test_exactness_required_demands_l0_exact_resolution():
    module = _resolution()

    with pytest.raises(module.ResolutionPlanningError, match="L0_EXACT"):
        _fault(
            module,
            required_resolution=module.ResolutionLevel.L1_HIGH_FIDELITY,
            exactness_required=True,
        )


def test_resolution_fault_must_request_higher_fidelity_than_available():
    module = _resolution()

    with pytest.raises(module.ResolutionPlanningError, match="higher fidelity"):
        _fault(
            module,
            available_resolution=module.ResolutionLevel.L1_HIGH_FIDELITY,
            required_resolution=module.ResolutionLevel.L2_SEMANTIC,
            exactness_required=False,
        )


def test_package_exports_resolution_planning_api():
    import rezon

    assert rezon.ResolutionFault is not None
    assert rezon.ResolutionOffer is not None
    assert rezon.ResolutionPlan is not None
    assert rezon.plan_resolution_fault is not None
