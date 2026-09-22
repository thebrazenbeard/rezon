import hashlib
import json

import pytest

import rezon.otel_genai as otel_genai
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.interop import export_run_evidence
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


TRACE_ID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
WORKFLOW_SPAN_ID = "bbbbbbbbbbbbbbbb"


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
                    "bound output",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _evidence():
    episode = Episode("bound")
    episode.add_proposition(
        Proposition(
            "o1",
            "bound",
            PropositionKind.OBSERVATION,
            "bound input",
            source_versions=("source:bound@v1",),
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
            task_id="bound-task",
        )
    )


def _attr(key, value):
    return {"key": key, "value": {"stringValue": value}}


def _otel(evidence, *, digest=None, schema=None, duplicate=False):
    digest = digest or evidence["evidence_digest"]
    schema = schema or evidence["schema_version"]
    spans = [
        {
            "traceId": TRACE_ID,
            "spanId": WORKFLOW_SPAN_ID,
            "name": "invoke_workflow bound",
            "status": {"code": 1},
            "attributes": [
                _attr("gen_ai.operation.name", "invoke_workflow"),
                _attr("gen_ai.workflow.name", "bound"),
                _attr("rezon.run_evidence.digest", digest),
                _attr("rezon.run_evidence.schema_version", schema),
            ],
        }
    ]
    if duplicate:
        spans.append(
            {
                "traceId": TRACE_ID,
                "spanId": "cccccccccccccccc",
                "name": "invoke_workflow second",
                "status": {"code": 1},
                "attributes": [
                    _attr("gen_ai.operation.name", "invoke_workflow"),
                    _attr("gen_ai.workflow.name", "second"),
                    _attr("rezon.run_evidence.digest", digest),
                    _attr("rezon.run_evidence.schema_version", schema),
                ],
            }
        )
    return {"resourceSpans": [{"scopeSpans": [{"spans": spans}]}]}


def _bind(otel_payload, evidence_payload):
    binding = getattr(otel_genai, "bind_otel_genai_to_run_evidence", None)
    assert callable(binding), "OTLP-to-Rezon evidence binding is not implemented"
    return binding(otel_payload, evidence_payload)


def _redigest(evidence):
    body = {key: value for key, value in evidence.items() if key != "evidence_digest"}
    evidence["evidence_digest"] = hashlib.sha256(
        json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def test_binds_structurally_valid_otel_workflow_to_verified_rezon_evidence():
    evidence = _evidence()

    binding = _bind(_otel(evidence), evidence)

    assert binding["binding_status"] == "verified"
    assert binding["trace_ids"] == [TRACE_ID]
    assert binding["evidence_digest"] == evidence["evidence_digest"]
    assert binding["evidence_schema_version"] == evidence["schema_version"]
    assert binding["evidence_effect_state"] == "plan"
    assert binding["authority"] == "unestablished"
    assert binding["effect_completion"] == "unestablished"


def test_rejects_structurally_valid_trace_with_substituted_evidence():
    evidence = _evidence()

    with pytest.raises(otel_genai.OTelGenAIIntakeError, match="digest"):
        _bind(_otel(evidence, digest="0" * 64), evidence)


def test_rejects_missing_or_ambiguous_rezon_evidence_anchor():
    evidence = _evidence()
    missing = _otel(evidence)
    missing["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["attributes"] = [
        _attr("gen_ai.operation.name", "invoke_workflow"),
        _attr("gen_ai.workflow.name", "bound"),
    ]

    with pytest.raises(otel_genai.OTelGenAIIntakeError, match="anchor"):
        _bind(missing, evidence)

    with pytest.raises(otel_genai.OTelGenAIIntakeError, match="exactly one"):
        _bind(_otel(evidence, duplicate=True), evidence)


def test_rejects_trace_schema_claim_that_disagrees_with_verified_artifact():
    evidence = _evidence()

    with pytest.raises(otel_genai.OTelGenAIIntakeError, match="schema"):
        _bind(_otel(evidence, schema="rezon.run-evidence.v999"), evidence)


def test_rejects_tampered_evidence_even_when_trace_anchor_is_redigested_to_match():
    evidence = _evidence()
    evidence["receipt"]["execution_ids"] = []
    evidence["receipt"]["execution_output_digests"] = []
    evidence["receipt"]["execution_producer_ids"] = []
    _redigest(evidence)

    with pytest.raises(otel_genai.OTelGenAIIntakeError, match="verification"):
        _bind(_otel(evidence), evidence)


def test_verified_binding_preserves_unresolved_telemetry_assurance_gaps():
    evidence = _evidence()
    otel = _otel(evidence)
    workflow = otel["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    workflow["droppedAttributesCount"] = 1

    binding = _bind(otel, evidence)

    assert binding["binding_status"] == "verified"
    assert binding["binding_scope"] == "trace_to_verified_artifact"
    assert binding["telemetry_source_payload_digest"]
    assert binding["telemetry_intake_digest"]
    assert "semantic_convention_version:unbound" in (
        binding["telemetry_assurance_gaps"]
    )
    assert "telemetry_attributes:dropped" in binding["telemetry_assurance_gaps"]
    assert binding["authority"] == "unestablished"
    assert binding["effect_completion"] == "unestablished"


def test_binding_digest_changes_when_bound_telemetry_changes():
    evidence = _evidence()
    first_otel = _otel(evidence)
    second_otel = _otel(evidence)
    second_otel["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["status"] = {
        "code": 2
    }

    first = _bind(first_otel, evidence)
    second = _bind(second_otel, evidence)

    assert first["evidence_digest"] == second["evidence_digest"]
    assert first["telemetry_intake_digest"] != second["telemetry_intake_digest"]
    assert first["binding_digest"] != second["binding_digest"]


def test_binding_rejects_ambiguous_multi_trace_genai_batch():
    evidence = _evidence()
    otel = _otel(evidence)
    otel["resourceSpans"].append(
        {
            "scopeSpans": [
                {
                    "spans": [
                        {
                            "traceId": "dddddddddddddddddddddddddddddddd",
                            "spanId": "eeeeeeeeeeeeeeee",
                            "name": "invoke_agent unrelated",
                            "status": {"code": 1},
                            "attributes": [
                                _attr("gen_ai.operation.name", "invoke_agent"),
                                _attr("gen_ai.agent.name", "unrelated"),
                            ],
                        }
                    ]
                }
            ]
        }
    )

    with pytest.raises(
        otel_genai.OTelGenAIIntakeError,
        match="exactly one GenAI trace",
    ):
        _bind(otel, evidence)
