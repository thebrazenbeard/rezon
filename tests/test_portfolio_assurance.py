from rezon.portfolio_assurance import assure_project_runner_wave


def _base_wave():
    return {
        "identities": {
            "ONE": "orchestrator",
            "REZON": "assurance",
            "ACHILLES": "security",
            "VOSS": "forensic",
        },
        "policy": {
            "protected_effects_forbidden_without_separate_live_authority": True,
            "merge_forbidden": True,
            "deploy_forbidden": True,
            "credential_or_permission_changes_forbidden": True,
            "destructive_cleanup_forbidden": True,
            "priority_is_authority": False,
        },
        "items": [
            {
                "subject_kind": "repository",
                "subject_id": "runner",
                "priority": "P0",
                "family_id": "portfolio-spine",
                "activity_state": "ACTIVE",
                "lead_identity": "ONE",
                "reviewer_identities": ["REZON", "VOSS"],
                "action": "EXECUTE_FRONTIER",
                "execution_state": "QUEUED",
                "effect_ceiling": "SOURCE_ONLY",
            },
            {
                "subject_kind": "repository",
                "subject_id": "runtime",
                "priority": "P0",
                "family_id": "vera-runtime",
                "activity_state": "ACTIVE",
                "lead_identity": "ONE",
                "reviewer_identities": ["REZON", "ACHILLES"],
                "action": "EXECUTE_FRONTIER",
                "execution_state": "QUEUED",
                "effect_ceiling": "SOURCE_ONLY",
            },
            {
                "subject_kind": "repository",
                "subject_id": "old",
                "priority": "P4",
                "family_id": "portfolio-spine",
                "activity_state": "SUPERSEDED",
                "lead_identity": "ONE",
                "reviewer_identities": ["REZON"],
                "action": "PRESERVE_ONLY",
                "execution_state": "HELD",
                "effect_ceiling": "NO_EFFECT",
            },
        ],
    }


def _codes(result):
    return {finding.code for finding in result.findings}


def test_valid_wave_passes():
    result = assure_project_runner_wave(_base_wave())
    assert result.passed is True
    assert result.subject_count == 3
    assert result.queued_count == 2
    assert result.held_count == 1


def test_priority_cannot_be_authority():
    wave = _base_wave()
    wave["policy"]["priority_is_authority"] = True
    result = assure_project_runner_wave(wave)
    assert result.passed is False
    assert "AUTHORITY_LAUNDERING" in _codes(result)


def test_protected_effect_fence_is_required():
    wave = _base_wave()
    wave["policy"]["merge_forbidden"] = False
    result = assure_project_runner_wave(wave)
    assert result.passed is False
    assert "PROTECTED_EFFECT_FENCE_MISSING" in _codes(result)


def test_lead_cannot_review_itself():
    wave = _base_wave()
    wave["items"][0]["reviewer_identities"] = ["ONE", "REZON"]
    result = assure_project_runner_wave(wave)
    assert result.passed is False
    assert "SELF_REVIEW" in _codes(result)


def test_p0_requires_rezon():
    wave = _base_wave()
    wave["items"][0]["reviewer_identities"] = ["VOSS"]
    result = assure_project_runner_wave(wave)
    assert result.passed is False
    assert "P0_REZON_REVIEW_MISSING" in _codes(result)


def test_p0_runtime_requires_security_review():
    wave = _base_wave()
    wave["items"][1]["reviewer_identities"] = ["REZON", "VOSS"]
    result = assure_project_runner_wave(wave)
    assert result.passed is False
    assert "P0_SECURITY_REVIEW_MISSING" in _codes(result)


def test_archived_or_superseded_subject_cannot_be_reactivated():
    wave = _base_wave()
    wave["items"][2]["execution_state"] = "QUEUED"
    wave["items"][2]["action"] = "EXECUTE_FRONTIER"
    wave["items"][2]["effect_ceiling"] = "SOURCE_ONLY"
    result = assure_project_runner_wave(wave)
    assert result.passed is False
    codes = _codes(result)
    assert "DEAD_SUBJECT_REACTIVATION" in codes
    assert "DEAD_SUBJECT_EFFECT" in codes


def test_speculative_work_requires_voss_participation():
    wave = _base_wave()
    wave["items"][0].update(
        {
            "subject_id": "speculative",
            "priority": "P2",
            "family_id": "speculative-cognition",
            "lead_identity": "ONE",
            "reviewer_identities": ["REZON", "ACHILLES"],
        }
    )
    result = assure_project_runner_wave(wave)
    assert result.passed is False
    assert "FORENSIC_REVIEW_MISSING" in _codes(result)
