from __future__ import annotations


CONSULTATION_INTAKE_SCHEMA = "rezon.ensemble-consultation-intake.v1"


class ConsultationIntakeError(ValueError):
    pass


def inspect_ensemble_consultation(payload: object) -> dict[str, object]:
    raise NotImplementedError("ensemble consultation intake is not implemented")
