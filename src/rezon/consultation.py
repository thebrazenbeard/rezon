from __future__ import annotations


CONSULTATION_INTAKE_SCHEMA = "rezon.ensemble-consultation-intake.v1"


class ConsultationIntakeError(ValueError):
    pass


def inspect_ensemble_consultation(payload: object) -> dict[str, object]:
    raise NotImplementedError("ensemble consultation intake is not implemented")


def consultation_promotion_violations(
    payload: object,
    *,
    count_consensus_as_evidence: bool = False,
    use_as_authority: bool = False,
):
    raise NotImplementedError("consultation promotion audit is not implemented")
