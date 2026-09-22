import json

from rezon.cli import main


def _invoke(argv):
    try:
        return main(argv)
    except SystemExit as exc:
        return int(exc.code)


def test_cli_inspects_ensemble_consultation_without_promoting_confidence(
    tmp_path,
    capsys,
):
    payload = {
        "synthesized_response": "Consensus answer",
        "convergence_score": 0.91,
        "divergence_findings": [],
        "confidence_signal": "high",
        "providers_consulted": ["openai", "anthropic"],
        "providers_failed": [],
        "total_cost_usd": 0.02,
        "total_latency_ms": 1000,
    }
    path = tmp_path / "consultation.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert _invoke(["inspect-consultation", str(path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["reported_synthesis"]["confidence_signal"] == "high"
    assert report["assurance"]["evidence_status"] == "advisory_only"
    assert report["assurance"]["authority"] == "unestablished"


def test_cli_consultation_fails_closed_on_bad_shape(tmp_path, capsys):
    path = tmp_path / "consultation.json"
    path.write_text('{"convergence_score": 0.9}', encoding="utf-8")

    assert _invoke(["inspect-consultation", str(path)]) == 2
    report = json.loads(capsys.readouterr().err)
    assert report["valid"] is False
