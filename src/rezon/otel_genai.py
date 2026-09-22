from __future__ import annotations


OTEL_GENAI_INTAKE_SCHEMA = "rezon.otel-genai-intake.v1"


class OTelGenAIIntakeError(ValueError):
    pass


def inspect_otel_genai_export(payload: object) -> dict[str, object]:
    """Inspect OTLP/JSON GenAI spans without promoting telemetry into authority."""
    raise NotImplementedError("OTel GenAI intake is not implemented")
