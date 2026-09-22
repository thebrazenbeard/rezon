import hashlib
import json

import pytest

from rezon.consultation import (
    ConsultationIntakeError,
    inspect_ensemble_consultation,
    consultation_promotion_violations,
)
from rezon.hostile import HostileViolation


def _lattice_like(raw=False):
    payload = {
        "synthesized_response": (
            "**Consensus** (all/most providers):\n"
            "- Use a metadata field for auditability."
        ),
        "convergence_score": 0.83,
        "divergence_findings": [
            "gemini alone: metadata may increase schema complexity"
        ],
        "confidence_signal": "high",
        "providers_consulted": [
            "openai",
            "anthropic",
            "gemini",
            "xai",
            "jan",
        ],
        "providers_failed": [],
        "total_cost_usd": 0.041,
        "total_latency_ms": 4823,
    }
    if raw:
        payload["raw_outputs"] = {
            "openai/gpt-5": {
                "response": "Use metadata for auditability.",
                "error": None,
                "tokens_in": 120,
                "tokens_out": 35,
                "cost_usd": 0.01,
                "latency_ms": 1400,
            },
            "anthropic/claude-sonnet": {
                "response": "A metadata field improves traceability.",
                "error": None,
                "tokens_in": 118,
                "tokens_out": 40,
                "cost_usd": 0.013,
                "latency_ms": 1700,
            },
            "gemini/gemini-2.5-pro": {
                "response": "Metadata helps, but increases schema complexity.",
                "error": None,
                "tokens_in": 119,
                "tokens_out": 44,
                "cost_usd": 0.005,
                "latency_ms": 900,
            },
            "xai/grok-4-fast": {
                "response": "Include metadata for auditability.",
                "error": None,
                "tokens_in": 121,
                "tokens_out": 30,
                "cost_usd": 0.013,
                "latency_ms": 1100,
            },
            "jan/qwen2.5:7b-instruct": {
                "response": "Metadata is useful for audit trails.",
                "error": None,
                "tokens_in": 110,
                "tokens_out": 28,
                "cost_usd": 0.0,
                "latency_ms": 700,
            },
        }
    return payload


def _redigest(report):
    body = {key: value for key, value in report.items() if key != "intake_digest"}
    return hashlib.sha256(
        json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def test_high_reported_convergence_stays_advisory_and_unbound():
    report = inspect_ensemble_consultation(_lattice_like())

    assert report["schema_version"] == "rezon.ensemble-consultation-intake.v1"
    assert report["reported_synthesis"] == {
        "response": (
            "**Consensus** (all/most providers):\n"
            "- Use a metadata field for auditability."
        ),
        "convergence_score": 0.83,
        "confidence_signal": "high",
        "divergence_findings": [
            "gemini alone: metadata may increase schema complexity"
        ],
    }
    assert report["provider_count"] == 5
    assert report["assurance"] == {
        "artifact_structure": "observed",
        "prompt_binding": "unestablished",
        "raw_output_binding": "unestablished",
        "provider_identity": "reported",
        "model_identity": "unestablished",
        "provider_independence": "unestablished",
        "semantic_truth": "unestablished",
        "evidence_status": "advisory_only",
        "authority": "unestablished",
    }
    assert "prompt:not_bound" in report["assurance_gaps"]
    assert "raw_outputs:not_bound" in report["assurance_gaps"]
    assert "provider_independence:not_demonstrated" in report["assurance_gaps"]
    assert "provider_eligibility:not_bound" in report["assurance_gaps"]


def test_raw_outputs_bind_reported_provider_model_outputs_but_not_independence():
    report = inspect_ensemble_consultation(_lattice_like(raw=True))

    assert report["assurance"]["raw_output_binding"] == "observed"
    assert report["assurance"]["model_identity"] == "reported"
    assert report["assurance"]["provider_independence"] == "unestablished"
    assert report["raw_output_count"] == 5
    assert report["raw_output_providers"] == [
        "openai",
        "anthropic",
        "gemini",
        "xai",
        "jan",
    ]
    assert len(report["raw_outputs"]) == 5
    assert all(
        len(item["response_digest"]) == 64
        for item in report["raw_outputs"]
    )


def test_complete_payload_and_normalized_report_are_both_digest_bound():
    first = inspect_ensemble_consultation(_lattice_like())
    changed = _lattice_like()
    changed["providers_failed"] = ["gemini: timeout"]
    second = inspect_ensemble_consultation(changed)

    assert first["source_payload_digest"] != second["source_payload_digest"]
    assert first["intake_digest"] != second["intake_digest"]
    assert first["intake_digest"] == _redigest(first)


def test_partial_failures_are_preserved_not_laundered_as_clean_success():
    payload = _lattice_like()
    payload["providers_consulted"] = ["openai", "anthropic", "jan"]
    payload["providers_failed"] = [
        "gemini: timeout",
        "xai: HTTP 429",
    ]

    report = inspect_ensemble_consultation(payload)

    assert report["providers_failed"] == [
        "gemini: timeout",
        "xai: HTTP 429",
    ]
    assert report["partial_failure_reported"] is True
    assert "provider_failures:reported" in report["assurance_gaps"]


def test_missing_or_partial_raw_outputs_are_distinguished():
    payload = _lattice_like(raw=True)
    del payload["raw_outputs"]["xai/grok-4-fast"]

    report = inspect_ensemble_consultation(payload)

    assert report["assurance"]["raw_output_binding"] == "partial"
    assert report["raw_output_count"] == 4
    assert report["raw_outputs_missing_for_consulted"] == ["xai"]
    assert "raw_outputs:partial" in report["assurance_gaps"]


def test_malformed_provider_and_score_shapes_fail_closed():
    duplicate = _lattice_like()
    duplicate["providers_consulted"].append("openai")
    with pytest.raises(ConsultationIntakeError, match="duplicate provider"):
        inspect_ensemble_consultation(duplicate)

    bad_score = _lattice_like()
    bad_score["convergence_score"] = 1.7
    with pytest.raises(ConsultationIntakeError, match="convergence_score"):
        inspect_ensemble_consultation(bad_score)

    bad_raw_key = _lattice_like(raw=True)
    bad_raw_key["raw_outputs"]["malformed"] = bad_raw_key["raw_outputs"].pop(
        "openai/gpt-5"
    )
    with pytest.raises(ConsultationIntakeError, match="provider/model"):
        inspect_ensemble_consultation(bad_raw_key)


def test_single_provider_convergence_semantics_are_flagged_not_promoted():
    payload = _lattice_like()
    payload["providers_consulted"] = ["jan"]
    payload["convergence_score"] = 0.9
    payload["confidence_signal"] = "high"

    report = inspect_ensemble_consultation(payload)

    assert "convergence:undefined_for_single_provider" in report["assurance_gaps"]
    assert report["assurance"]["evidence_status"] == "advisory_only"


def test_consensus_promotion_is_hostile_without_separate_independence_evidence():
    payload = _lattice_like(raw=True)

    evidence_violations = consultation_promotion_violations(
        payload,
        count_consensus_as_evidence=True,
    )
    authority_violations = consultation_promotion_violations(
        payload,
        use_as_authority=True,
    )

    assert HostileViolation.CORRELATED_CONSENSUS_LAUNDERING in evidence_violations
    assert HostileViolation.ADVISORY_AUTHORITY_LAUNDERING in authority_violations
