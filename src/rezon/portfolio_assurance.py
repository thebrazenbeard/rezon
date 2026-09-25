from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class PortfolioWaveFinding:
    code: str
    severity: str
    subject_id: str | None
    message: str


@dataclass(frozen=True)
class PortfolioWaveAssurance:
    passed: bool
    findings: tuple[PortfolioWaveFinding, ...]
    subject_count: int
    queued_count: int
    held_count: int


_ALLOWED_EFFECT_CEILINGS = {"SOURCE_ONLY", "NO_EFFECT"}
_EXPECTED_INERT_ACTIONS = {
    "PRESERVE_ONLY",
    "REFRESH_IF_REACTIVATED",
}


def assure_project_runner_wave(payload: Mapping[str, object]) -> PortfolioWaveAssurance:
    findings: list[PortfolioWaveFinding] = []
    policy = payload.get("policy")
    raw_items = payload.get("items")
    identities = payload.get("identities")

    if not isinstance(policy, Mapping):
        findings.append(
            PortfolioWaveFinding(
                "WAVE_POLICY_MISSING",
                "BLOCK",
                None,
                "wave policy must be an object",
            )
        )
        policy = {}
    if not isinstance(identities, Mapping):
        findings.append(
            PortfolioWaveFinding(
                "WAVE_IDENTITIES_MISSING",
                "BLOCK",
                None,
                "wave identities must be an object",
            )
        )
        identities = {}
    if not isinstance(raw_items, Sequence) or isinstance(raw_items, (str, bytes)):
        findings.append(
            PortfolioWaveFinding(
                "WAVE_ITEMS_MISSING",
                "BLOCK",
                None,
                "wave items must be an array",
            )
        )
        raw_items = []

    required_false = (
        "priority_is_authority",
    )
    for key in required_false:
        if policy.get(key) is not False:
            findings.append(
                PortfolioWaveFinding(
                    "AUTHORITY_LAUNDERING",
                    "BLOCK",
                    None,
                    f"{key} must be false",
                )
            )

    required_true = (
        "protected_effects_forbidden_without_separate_live_authority",
        "merge_forbidden",
        "deploy_forbidden",
        "credential_or_permission_changes_forbidden",
        "destructive_cleanup_forbidden",
    )
    for key in required_true:
        if policy.get(key) is not True:
            findings.append(
                PortfolioWaveFinding(
                    "PROTECTED_EFFECT_FENCE_MISSING",
                    "BLOCK",
                    None,
                    f"{key} must be true",
                )
            )

    seen: set[tuple[str, str]] = set()
    queued = 0
    held = 0

    for raw in raw_items:
        if not isinstance(raw, Mapping):
            findings.append(
                PortfolioWaveFinding(
                    "ITEM_NOT_OBJECT",
                    "BLOCK",
                    None,
                    "every advancement item must be an object",
                )
            )
            continue

        subject_id = str(raw.get("subject_id", "")).strip()
        subject_kind = str(raw.get("subject_kind", "")).strip()
        identity = (subject_kind, subject_id)
        if not subject_id or not subject_kind:
            findings.append(
                PortfolioWaveFinding(
                    "SUBJECT_IDENTITY_MISSING",
                    "BLOCK",
                    subject_id or None,
                    "advancement item requires subject_kind and subject_id",
                )
            )
            continue
        if identity in seen:
            findings.append(
                PortfolioWaveFinding(
                    "DUPLICATE_SUBJECT",
                    "BLOCK",
                    subject_id,
                    "subject appears more than once in the wave",
                )
            )
        seen.add(identity)

        lead = str(raw.get("lead_identity", "")).strip()
        reviewers_raw = raw.get("reviewer_identities", [])
        reviewers = (
            tuple(str(value) for value in reviewers_raw)
            if isinstance(reviewers_raw, Sequence)
            and not isinstance(reviewers_raw, (str, bytes))
            else ()
        )
        if lead not in identities:
            findings.append(
                PortfolioWaveFinding(
                    "UNKNOWN_LEAD",
                    "BLOCK",
                    subject_id,
                    "lead identity is not declared by the wave",
                )
            )
        if not reviewers:
            findings.append(
                PortfolioWaveFinding(
                    "NO_INDEPENDENT_REVIEW",
                    "BLOCK",
                    subject_id,
                    "queued work requires an explicit independent reviewer",
                )
            )
        if lead in reviewers:
            findings.append(
                PortfolioWaveFinding(
                    "SELF_REVIEW",
                    "BLOCK",
                    subject_id,
                    "lead identity may not be its own reviewer",
                )
            )
        if any(reviewer not in identities for reviewer in reviewers):
            findings.append(
                PortfolioWaveFinding(
                    "UNKNOWN_REVIEWER",
                    "BLOCK",
                    subject_id,
                    "reviewer identity is not declared by the wave",
                )
            )

        effect_ceiling = str(raw.get("effect_ceiling", "")).strip()
        if effect_ceiling not in _ALLOWED_EFFECT_CEILINGS:
            findings.append(
                PortfolioWaveFinding(
                    "EFFECT_CEILING_EXCEEDED",
                    "BLOCK",
                    subject_id,
                    "effect ceiling exceeds source-only advancement",
                )
            )

        state = str(raw.get("execution_state", "")).strip()
        action = str(raw.get("action", "")).strip()
        activity = str(raw.get("activity_state", "")).strip()
        priority = str(raw.get("priority", "")).strip()
        family = str(raw.get("family_id", "")).strip()

        if state == "QUEUED":
            queued += 1
        elif state == "HELD":
            held += 1
        else:
            findings.append(
                PortfolioWaveFinding(
                    "UNKNOWN_EXECUTION_STATE",
                    "BLOCK",
                    subject_id,
                    "execution state must be QUEUED or HELD",
                )
            )

        if activity in {"ARCHIVED", "SUPERSEDED"}:
            if state != "HELD" or action != "PRESERVE_ONLY":
                findings.append(
                    PortfolioWaveFinding(
                        "DEAD_SUBJECT_REACTIVATION",
                        "BLOCK",
                        subject_id,
                        "archived/superseded subjects must remain held and preserve-only",
                    )
                )
            if effect_ceiling != "NO_EFFECT":
                findings.append(
                    PortfolioWaveFinding(
                        "DEAD_SUBJECT_EFFECT",
                        "BLOCK",
                        subject_id,
                        "archived/superseded subjects must have NO_EFFECT ceiling",
                    )
                )

        if state == "HELD" and action not in _EXPECTED_INERT_ACTIONS:
            findings.append(
                PortfolioWaveFinding(
                    "HELD_ACTION_INCONSISTENT",
                    "WARN",
                    subject_id,
                    "held subject has an action that implies active execution",
                )
            )

        if priority == "P0":
            if "REZON" not in reviewers:
                findings.append(
                    PortfolioWaveFinding(
                        "P0_REZON_REVIEW_MISSING",
                        "BLOCK",
                        subject_id,
                        "P0 work requires independent Rezon review",
                    )
                )
            if family in {"vera-runtime", "coordination"} and "ACHILLES" not in reviewers:
                findings.append(
                    PortfolioWaveFinding(
                        "P0_SECURITY_REVIEW_MISSING",
                        "BLOCK",
                        subject_id,
                        "P0 runtime/coordination work requires Achilles review",
                    )
                )

        if family in {"speculative-cognition", "source-critical-research"}:
            if "VOSS" != lead and "VOSS" not in reviewers:
                findings.append(
                    PortfolioWaveFinding(
                        "FORENSIC_REVIEW_MISSING",
                        "BLOCK",
                        subject_id,
                        "speculative/source-critical work requires Voss participation",
                    )
                )

    blockers = tuple(item for item in findings if item.severity == "BLOCK")
    return PortfolioWaveAssurance(
        passed=not blockers,
        findings=tuple(findings),
        subject_count=len(raw_items),
        queued_count=queued,
        held_count=held,
    )



@dataclass(frozen=True)
class PortfolioAdmissionAssurance:
    passed: bool
    findings: tuple[PortfolioWaveFinding, ...]
    selected_count: int
    deferred_count: int


def assure_project_runner_admission_plan(
    payload: Mapping[str, object],
) -> PortfolioAdmissionAssurance:
    findings: list[PortfolioWaveFinding] = []
    if payload.get("mode") != "PORTFOLIO_WAVE_ADMISSION_PLAN_V1":
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_MODE_MISMATCH",
                "BLOCK",
                None,
                "admission payload mode is not the governed V1 plan",
            )
        )
    if payload.get("execution_authority") is not False:
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_AUTHORITY_LAUNDERING",
                "BLOCK",
                None,
                "admission plan must explicitly deny execution authority",
            )
        )
    if payload.get("protected_effects_authorized") is not False:
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_EFFECT_AUTHORITY",
                "BLOCK",
                None,
                "admission plan must explicitly deny protected-effect authority",
            )
        )

    summary = payload.get("summary")
    selected_raw = payload.get("selected")
    deferred_raw = payload.get("deferred")
    if not isinstance(summary, Mapping):
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_SUMMARY_MISSING",
                "BLOCK",
                None,
                "admission summary must be an object",
            )
        )
        summary = {}
    if not isinstance(selected_raw, Sequence) or isinstance(
        selected_raw, (str, bytes)
    ):
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_SELECTED_MISSING",
                "BLOCK",
                None,
                "selected admission items must be an array",
            )
        )
        selected_raw = []
    if not isinstance(deferred_raw, Sequence) or isinstance(
        deferred_raw, (str, bytes)
    ):
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_DEFERRED_MISSING",
                "BLOCK",
                None,
                "deferred admission items must be an array",
            )
        )
        deferred_raw = []

    try:
        max_parallel = int(summary.get("max_parallel", 0))
        max_per_identity = int(summary.get("max_per_identity", 0))
    except (TypeError, ValueError):
        max_parallel = 0
        max_per_identity = 0
    if max_parallel < 1 or max_per_identity < 1:
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_BUDGET_INVALID",
                "BLOCK",
                None,
                "admission budgets must be positive",
            )
        )
    if len(selected_raw) > max_parallel:
        findings.append(
            PortfolioWaveFinding(
                "GLOBAL_BUDGET_EXCEEDED",
                "BLOCK",
                None,
                "selected subjects exceed max_parallel",
            )
        )

    leads: dict[str, int] = {}
    collision_owner: dict[str, str] = {}
    subject_seen: set[tuple[str, str]] = set()
    for raw in selected_raw:
        if not isinstance(raw, Mapping):
            findings.append(
                PortfolioWaveFinding(
                    "SELECTED_ITEM_NOT_OBJECT",
                    "BLOCK",
                    None,
                    "selected admission item must be an object",
                )
            )
            continue
        subject_id = str(raw.get("subject_id", "")).strip()
        subject_kind = str(raw.get("subject_kind", "")).strip()
        lead = str(raw.get("lead_identity", "")).strip()
        identity = (subject_kind, subject_id)
        if identity in subject_seen:
            findings.append(
                PortfolioWaveFinding(
                    "DUPLICATE_ADMISSION_SUBJECT",
                    "BLOCK",
                    subject_id or None,
                    "subject is selected more than once",
                )
            )
        subject_seen.add(identity)
        leads[lead] = leads.get(lead, 0) + 1
        if leads[lead] > max_per_identity:
            findings.append(
                PortfolioWaveFinding(
                    "IDENTITY_BUDGET_EXCEEDED",
                    "BLOCK",
                    subject_id or None,
                    "selected subjects exceed max_per_identity",
                )
            )

        raw_keys = raw.get("collision_keys", [])
        keys = (
            tuple(str(value).strip().lower() for value in raw_keys)
            if isinstance(raw_keys, Sequence)
            and not isinstance(raw_keys, (str, bytes))
            else ()
        )
        if not keys or any(not key for key in keys):
            findings.append(
                PortfolioWaveFinding(
                    "COLLISION_KEY_MISSING",
                    "BLOCK",
                    subject_id or None,
                    "every selected subject needs non-empty collision keys",
                )
            )
        for key in keys:
            previous = collision_owner.get(key)
            if previous is not None:
                findings.append(
                    PortfolioWaveFinding(
                        "ADMISSION_COLLISION",
                        "BLOCK",
                        subject_id or None,
                        f"collision key {key} is already selected by {previous}",
                    )
                )
            else:
                collision_owner[key] = subject_id

    selected_count = len(selected_raw)
    deferred_count = len(deferred_raw)
    if summary.get("selected") != selected_count:
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_SELECTED_COUNT_MISMATCH",
                "BLOCK",
                None,
                "summary selected count does not match payload",
            )
        )
    if summary.get("deferred") != deferred_count:
        findings.append(
            PortfolioWaveFinding(
                "ADMISSION_DEFERRED_COUNT_MISMATCH",
                "BLOCK",
                None,
                "summary deferred count does not match payload",
            )
        )

    occupied_raw = summary.get("occupied_collision_keys", [])
    occupied = {
        str(value).strip().lower()
        for value in occupied_raw
        if str(value).strip()
    } if isinstance(occupied_raw, Sequence) and not isinstance(
        occupied_raw, (str, bytes)
    ) else set()
    leaked = occupied.intersection(collision_owner)
    if leaked:
        findings.append(
            PortfolioWaveFinding(
                "OCCUPIED_COLLISION_ADMITTED",
                "BLOCK",
                None,
                "selected work reuses an occupied collision key",
            )
        )

    blockers = tuple(item for item in findings if item.severity == "BLOCK")
    return PortfolioAdmissionAssurance(
        passed=not blockers,
        findings=tuple(findings),
        selected_count=selected_count,
        deferred_count=deferred_count,
    )
