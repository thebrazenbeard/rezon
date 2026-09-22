import json

from rezon.cli import main
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.interop import export_run_evidence
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


TRACE_ID = "12121212121212121212121212121212"
SPAN_ID = "3434343434343434"


class Echo:
    node_id = "echo_hypothesis"

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h1",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "cli output",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _evidence():
    episode = Episode("cli")
    episode.add_proposition(
        Proposition(
            "o1",
            "cli",
            PropositionKind.OBSERVATION,
            "cli input",
            source_versions=("source:cli@v1",),
        )
    )
    node = RunnerNode(
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        Echo(),
        VisibilityPolicy(),
    )
    return export_run_evidence(
        EpisodeRunner((node,), budget_limit=1).run(
            episode,
            task_id="cli-task",
        )
    )


def _attr(key, value):
    return {"key": key, "value": {"stringValue": value}}


def _otel(evidence=None):
    attributes = [
        _attr("gen_ai.operation.name", "invoke_workflow"),
        _attr("gen_ai.workflow.name", "cli"),
    ]
    if evidence is not None:
        attributes.extend(
            [
                _attr(
                    "rezon.run_evidence.digest",
                    evidence["evidence_digest"],
                ),
                _attr(
                    "rezon.run_evidence.schema_version",
                    evidence["schema_version"],
                ),
            ]
        )
    return {
        "resourceSpans": [
            {
                "schemaUrl": "https://opentelemetry.io/schemas/1.44.0",
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "traceId": TRACE_ID,
                                "spanId": SPAN_ID,
                                "name": "invoke_workflow cli",
                                "status": {"code": 1},
                                "attributes": attributes,
                            }
                        ]
                    }
                ],
            }
        ]
    }


def _invoke(argv):
    try:
        return main(argv)
    except SystemExit as exc:
        return int(exc.code)


def test_cli_inspects_otlp_genai_json(tmp_path, capsys):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(json.dumps(_otel()), encoding="utf-8")

    assert _invoke(["inspect-otel-genai", str(trace_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["schema_version"] == "rezon.otel-genai-intake.v1"
    assert report["events"][0]["operation"] == "invoke_workflow"


def test_cli_binds_otlp_trace_to_rezon_evidence(tmp_path, capsys):
    evidence = _evidence()
    trace_path = tmp_path / "trace.json"
    evidence_path = tmp_path / "evidence.json"
    trace_path.write_text(json.dumps(_otel(evidence)), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    assert _invoke(
        [
            "bind-otel-evidence",
            str(trace_path),
            str(evidence_path),
        ]
    ) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["binding_status"] == "verified"
    assert report["binding_scope"] == "trace_to_verified_artifact"


def test_cli_otlp_commands_fail_closed_on_invalid_input(tmp_path, capsys):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text('{"not":"otlp"}', encoding="utf-8")

    assert _invoke(["inspect-otel-genai", str(trace_path)]) == 2
    report = json.loads(capsys.readouterr().err)
    assert report["valid"] is False
