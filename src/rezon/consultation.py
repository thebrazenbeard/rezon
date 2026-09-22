from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math
from typing import Any

from .hostile import HostileViolation, audit_hostile_case


CONSULTATION_INTAKE_SCHEMA = "rezon.ensemble-consultation-intake.v1"


class ConsultationIntakeError(ValueError):
    pass


def _canonical_digest(value: object) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ConsultationIntakeError(
            "consultation artifact must be canonically JSON-serializable"
        ) from exc
    return sha256(encoded).hexdigest()


def _dict(value: object, name: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise ConsultationIntakeError(f"{name} must be an exact object")
    return value


def _list(value: object, name: str) -> list[Any]:
    if type(value) is not list:
        raise ConsultationIntakeError(f"{name} must be an exact list")
    return value


def _string(value: object, name: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str or (not allow_empty and not value):
        qualifier = "string" if allow_empty else "non-empty string"
        raise ConsultationIntakeError(f"{name} must be an exact {qualifier}")
    return value


def _strings(value: object, name: str) -> list[str]:
    return [
        _string(item, f"{name}[{index}]")
        for index, item in enumerate(_list(value, name))
    ]


def _nonnegative_number(value: object, name: str) -> float:
    if type(value) not in (int, float):
        raise ConsultationIntakeError(f"{name} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0:
        raise ConsultationIntakeError(
            f"{name} must be finite and non-negative"
        )
    return numeric


def _nonnegative_int(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ConsultationIntakeError(
            f"{name} must be a non-negative exact integer"
        )
    return value


def _convergence_score(value: object) -> float | None:
    if value is None:
        return None
    if type(value) not in (int, float):
        raise ConsultationIntakeError(
            "convergence_score must be null or numeric"
        )
    score = float(value)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ConsultationIntakeError(
            "convergence_score must be within [0, 1]"
        )
    return score


def _raw_output(
    key: object,
    value: object,
) -> dict[str, object]:
    raw_key = _string(key, "raw_outputs key")
    if "/" not in raw_key:
        raise ConsultationIntakeError(
            "raw_outputs keys must use provider/model form"
        )
    provider, model = raw_key.split("/", 1)
    if not provider or not model:
        raise ConsultationIntakeError(
            "raw_outputs keys must use non-empty provider/model form"
        )

    item = _dict(value, f"raw_outputs[{raw_key!r}]")
    response = _string(
        item.get("response", ""),
        f"raw_outputs[{raw_key!r}].response",
        allow_empty=True,
    )
    error = item.get("error")
    if error is not None:
        error = _string(
            error,
            f"raw_outputs[{raw_key!r}].error",
        )

    tokens_in = _nonnegative_int(
        item.get("tokens_in", 0),
        f"raw_outputs[{raw_key!r}].tokens_in",
    )
    tokens_out = _nonnegative_int(
        item.get("tokens_out", 0),
        f"raw_outputs[{raw_key!r}].tokens_out",
    )
    cost = _nonnegative_number(
        item.get("cost_usd", 0.0),
        f"raw_outputs[{raw_key!r}].cost_usd",
    )
    latency = _nonnegative_int(
        item.get("latency_ms", 0),
        f"raw_outputs[{raw_key!r}].latency_ms",
    )

    return {
        "provider": provider,
        "model": model,
        "response_digest": _canonical_digest(response),
        "error": error,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "reported_cost_usd": cost,
        "reported_latency_ms": latency,
    }


def inspect_ensemble_consultation(payload: object) -> dict[str, object]:
    """Inspect an external multi-model consultation artifact.

    Reported convergence and confidence are preserved as advisory metadata.
    Provider names, model labels, and raw outputs do not establish worker
    independence, semantic truth, evidence status, or authority.
    """

    root = _dict(payload, "consultation artifact")
    source_payload_digest = _canonical_digest(root)

    synthesized_response = _string(
        root.get("synthesized_response"),
        "synthesized_response",
        allow_empty=True,
    )
    convergence_score = _convergence_score(
        root.get("convergence_score")
    )
    divergence_findings = _strings(
        root.get("divergence_findings"),
        "divergence_findings",
    )
    confidence_signal = _string(
        root.get("confidence_signal"),
        "confidence_signal",
    )

    providers_consulted = _strings(
        root.get("providers_consulted"),
        "providers_consulted",
    )
    consulted_counts = Counter(providers_consulted)
    providers_failed = _strings(
        root.get("providers_failed"),
        "providers_failed",
    )
    reported_cost = _nonnegative_number(
        root.get("total_cost_usd"),
        "total_cost_usd",
    )
    reported_latency = _nonnegative_int(
        root.get("total_latency_ms"),
        "total_latency_ms",
    )

    raw_present = "raw_outputs" in root
    raw_items: list[dict[str, object]] = []
    raw_success_counts: Counter[str] = Counter()
    if raw_present:
        raw_map = _dict(root["raw_outputs"], "raw_outputs")
        parsed = [
            _raw_output(raw_key, raw_value)
            for raw_key, raw_value in raw_map.items()
        ]

        # Canonical normalized order: first appearance of each reported
        # provider, then model name; non-consulted providers sort afterwards.
        provider_order: dict[str, int] = {}
        for index, provider in enumerate(providers_consulted):
            provider_order.setdefault(provider, index)
        raw_items = sorted(
            parsed,
            key=lambda item: (
                provider_order.get(
                    item["provider"],
                    len(provider_order),
                ),
                item["provider"],
                item["model"],
            ),
        )
        raw_success_counts.update(
            item["provider"]
            for item in raw_items
            if item["error"] is None
        )

        for provider, observed_successes in raw_success_counts.items():
            expected_successes = consulted_counts[provider]
            if observed_successes > expected_successes:
                raise ConsultationIntakeError(
                    "successful raw worker is not represented by "
                    f"providers_consulted for provider {provider!r}"
                )

    missing_raw: list[str] = []
    for provider, expected_successes in consulted_counts.items():
        deficit = expected_successes - raw_success_counts[provider]
        if raw_present and deficit > 0:
            # When raw outputs are present, a reported consulted member must
            # have a corresponding successful raw worker. An error record is
            # not a successful consulted response.
            provider_raw = [
                item
                for item in raw_items
                if item["provider"] == provider
            ]
            if provider_raw and all(
                item["error"] is not None for item in provider_raw
            ):
                raise ConsultationIntakeError(
                    f"consulted provider {provider!r} has only raw error outputs"
                )
        missing_raw.extend([provider] * max(deficit, 0))

    if not raw_present or not raw_items:
        raw_binding = "unestablished"
    elif missing_raw:
        raw_binding = "partial"
    else:
        raw_binding = "observed"

    raw_failure_count = sum(
        1 for item in raw_items if item["error"] is not None
    )

    skipped_present = "providers_skipped" in root
    providers_skipped = (
        _strings(root["providers_skipped"], "providers_skipped")
        if skipped_present
        else []
    )
    single_provider_reported = root.get("single_provider")
    if single_provider_reported is not None and type(single_provider_reported) is not bool:
        raise ConsultationIntakeError(
            "single_provider must be an exact boolean when present"
        )

    assurance_gaps = [
        "prompt:not_bound",
        "system_prompt:not_bound",
        "request_configuration:not_bound",
        "synthesis_method:not_bound",
        "privacy_tier:not_bound",
        "provider_independence:not_demonstrated",
        "semantic_truth:not_established_by_consultation",
        "authority:not_established_by_consultation",
    ]

    if raw_binding == "unestablished":
        assurance_gaps.append("raw_outputs:not_bound")
    elif raw_binding == "partial":
        assurance_gaps.append("raw_outputs:partial")

    if not skipped_present:
        assurance_gaps.append("provider_eligibility:not_bound")

    if providers_failed:
        assurance_gaps.append("provider_failures:reported")
    if raw_present and raw_failure_count != len(providers_failed):
        assurance_gaps.append("provider_failures:top_level_mismatch")

    if len(providers_consulted) <= 1 and convergence_score is not None:
        assurance_gaps.append(
            "convergence:undefined_for_single_provider"
        )
    if providers_consulted and len(set(providers_consulted)) == 1:
        assurance_gaps.append("provider_diversity:single_provider")

    body: dict[str, object] = {
        "schema_version": CONSULTATION_INTAKE_SCHEMA,
        "source_payload_digest": source_payload_digest,
        "reported_synthesis": {
            "response": synthesized_response,
            "convergence_score": convergence_score,
            "confidence_signal": confidence_signal,
            "divergence_findings": divergence_findings,
        },
        "providers_consulted": providers_consulted,
        "consultation_member_count": len(providers_consulted),
        "provider_count": len(set(providers_consulted)),
        "providers_failed": providers_failed,
        "partial_failure_reported": bool(providers_failed),
        "raw_failure_count": raw_failure_count,
        "providers_skipped": providers_skipped,
        "provider_eligibility_reported": skipped_present,
        "single_provider_reported": single_provider_reported,
        "reported_total_cost_usd": reported_cost,
        "reported_total_latency_ms": reported_latency,
        "raw_outputs": raw_items,
        "raw_output_count": len(raw_items),
        "raw_worker_count": len(raw_items),
        "raw_output_workers": [
            f"{item['provider']}/{item['model']}"
            for item in raw_items
        ],
        "raw_output_providers": [
            item["provider"] for item in raw_items
        ],
        "raw_outputs_missing_for_consulted": missing_raw,
        "assurance": {
            "artifact_structure": "observed",
            "prompt_binding": "unestablished",
            "raw_output_binding": raw_binding,
            "provider_identity": "reported",
            "model_identity": (
                "reported" if raw_items else "unestablished"
            ),
            "provider_independence": "unestablished",
            "semantic_truth": "unestablished",
            "evidence_status": "advisory_only",
            "authority": "unestablished",
        },
        "assurance_gaps": assurance_gaps,
    }
    return {
        **body,
        "intake_digest": _canonical_digest(body),
    }


def consultation_promotion_violations(
    payload: object,
    *,
    count_consensus_as_evidence: bool = False,
    use_as_authority: bool = False,
) -> tuple[HostileViolation, ...]:
    """Audit attempted promotion of consultation synthesis.

    The consultation artifact itself cannot demonstrate worker independence.
    Any independent-evidence qualification must come from separately governed
    evidence rather than provider labels or a convergence score.
    """

    inspect_ensemble_consultation(payload)

    case: dict[str, object] = {}
    if count_consensus_as_evidence:
        case["consensus_counted_as_evidence"] = True
        case["worker_independence"] = None
    if use_as_authority:
        case["authority_basis"] = "consensus"
    return audit_hostile_case(case)
