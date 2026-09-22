from __future__ import annotations


OTEL_INTAKE_SCHEMA = "rezon.otel-intake.v1"


class OTelIntakeError(ValueError):
    pass


def inspect_otel_export(payload: object) -> dict[str, object]:
    """Inspect generic OTLP/JSON traces without assigning semantic meaning."""
    raise NotImplementedError("generic OTLP intake is not implemented")
