import json

from rezon.cli import main


def _payload():
    return {
        "resourceSpans": [
            {
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "traceId": "1234567890abcdef1234567890abcdef",
                                "spanId": "1234567890abcdef",
                                "name": "workflow.run",
                                "status": {"code": 1},
                                "attributes": [
                                    {
                                        "key": "workflow.id",
                                        "value": {"stringValue": "wf-cli"},
                                    }
                                ],
                            }
                        ]
                    }
                ]
            }
        ]
    }


def _invoke(argv):
    try:
        return main(argv)
    except SystemExit as exc:
        return int(exc.code)


def test_cli_inspects_generic_otlp_json(tmp_path, capsys):
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(_payload()), encoding="utf-8")

    assert _invoke(["inspect-otel", str(path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["schema_version"] == "rezon.otel-intake.v1"
    assert report["span_count"] == 1
    assert report["spans"][0]["attributes"]["workflow.id"] == "wf-cli"


def test_cli_generic_otlp_fails_closed(tmp_path, capsys):
    path = tmp_path / "trace.json"
    path.write_text('{"spans":[]}', encoding="utf-8")

    assert _invoke(["inspect-otel", str(path)]) == 2
    report = json.loads(capsys.readouterr().err)
    assert report["valid"] is False
