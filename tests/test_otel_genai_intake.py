import hashlib
import json

import pytest

from rezon.otel_genai import OTelGenAIIntakeError, inspect_otel_genai_export


TRACE_ID = "0123456789abcdef0123456789abcdef"
WORKFLOW_SPAN_ID = "1111111111111111"
AGENT_SPAN_ID = "2222222222222222"
TOOL_SPAN_ID = "3333333333333333"


def _attr(key, value):
    return {"key": key, "value": {"stringValue": value}}


def _payload():
    return {
        "resourceSpans": [
            {
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "traceId": TRACE_ID,
                                "spanId": WORKFLOW_SPAN_ID,
                                "name": "invoke_workflow research",
                                "status": {"code": 1},
                                "attributes": [
                                    _attr("gen_ai.operation.name", "invoke_workflow"),
                                    _attr("gen_ai.workflow.name", "research"),
                                ],
                            },
                            {
                                "traceId": TRACE_ID,
                                "spanId": AGENT_SPAN_ID,
                                "parentSpanId": WORKFLOW_SPAN_ID,
                                "name": "invoke_agent skeptic",
                                "status": {"code": 1},
                                "attributes": [
                                    _attr("gen_ai.operation.name", "invoke_agent"),
                                    _attr("gen_ai.agent.name", "skeptic"),
                                    _attr("gen_ai.provider.name", "openai"),
                                ],
                            },
                            {
                                "traceId": TRACE_ID,
                                "spanId": TOOL_SPAN_ID,
                                "parentSpanId": AGENT_SPAN_ID,
                                "name": "execute_tool search",
                                "status": {"code": 1},
                                "attributes": [
                                    _attr("gen_ai.operation.name", "execute_tool"),
                                    _attr("gen_ai.tool.name", "search"),
                                ],
                            },
                            {
                                "traceId": TRACE_ID,
                                "spanId": "4444444444444444",
                                "name": "ordinary http span",
                                "status": {"code": 1},
                                "attributes": [_attr("http.request.method", "GET")],
                            },
                        ]
                    }
                ]
            }
        ]
    }


def _redigest(report):
    body = {key: value for key, value in report.items() if key != "intake_digest"}
    encoded = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_inspects_otlp_json_genai_spans_without_flattening_hierarchy():
    report = inspect_otel_genai_export(_payload())

    assert report["schema_version"] == "rezon.otel-genai-intake.v1"
    assert report["semconv_stability"] == "development"
    assert report["schema_urls"] == []
    assert "semantic_convention_version:unbound" in report["assurance_gaps"]
    assert report["trace_ids"] == [TRACE_ID]
    assert report["ignored_span_count"] == 1

    events = report["events"]
    assert [event["operation"] for event in events] == [
        "invoke_workflow",
        "invoke_agent",
        "execute_tool",
    ]
    assert events[0]["subject_name"] == "research"
    assert events[1]["subject_name"] == "skeptic"
    assert events[1]["provider_name"] == "openai"
    assert events[2]["subject_name"] == "search"
    assert events[1]["parent_span_id"] == WORKFLOW_SPAN_ID
    assert events[2]["parent_span_id"] == AGENT_SPAN_ID

    assert report["intake_digest"] == _redigest(report)


def test_successful_tool_telemetry_does_not_establish_rezon_authority_or_effect_truth():
    report = inspect_otel_genai_export(_payload())

    tool = report["events"][2]
    assert tool["status"] == "ok"
    assert tool["execution_observed"] is True

    assert report["assurance"] == {
        "telemetry_structure": "observed",
        "provenance": "unestablished",
        "source_currentness": "unestablished",
        "worker_independence": "unestablished",
        "authority": "unestablished",
        "effect_completion": "unestablished",
    }
    assert "authority:not_established_by_otel" in report["assurance_gaps"]
    assert "effect_completion:not_established_by_otel" in report["assurance_gaps"]


def test_schema_url_is_preserved_when_exporter_provides_one():
    payload = _payload()
    payload["resourceSpans"][0]["schemaUrl"] = "https://opentelemetry.io/schemas/1.44.0"

    report = inspect_otel_genai_export(payload)

    assert report["schema_urls"] == ["https://opentelemetry.io/schemas/1.44.0"]
    assert "semantic_convention_version:unbound" not in report["assurance_gaps"]


def test_invalid_or_duplicate_otlp_span_identity_fails_closed():
    invalid = _payload()
    invalid["resourceSpans"][0]["scopeSpans"][0]["spans"][1]["spanId"] = "xyz"

    with pytest.raises(OTelGenAIIntakeError, match="spanId"):
        inspect_otel_genai_export(invalid)

    duplicate = _payload()
    duplicate["resourceSpans"][0]["scopeSpans"][0]["spans"][2]["spanId"] = AGENT_SPAN_ID

    with pytest.raises(OTelGenAIIntakeError, match="duplicate"):
        inspect_otel_genai_export(duplicate)


def test_non_otlp_shapes_fail_closed_instead_of_guessing():
    with pytest.raises(OTelGenAIIntakeError, match="resourceSpans"):
        inspect_otel_genai_export({"spans": []})


def test_preserves_standard_retrieval_operation_instead_of_silently_ignoring_it():
    payload = _payload()
    retrieval = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][3]
    retrieval["name"] = "retrieval vector-search"
    retrieval["attributes"] = [
        _attr("gen_ai.operation.name", "retrieval"),
        _attr("gen_ai.provider.name", "openai"),
    ]

    report = inspect_otel_genai_export(payload)

    assert report["ignored_span_count"] == 0
    assert report["events"][-1]["operation"] == "retrieval"
    assert report["events"][-1]["provider_name"] == "openai"


def test_preserves_custom_genai_operation_without_pretending_it_is_standard():
    payload = _payload()
    custom = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][3]
    custom["name"] = "custom reasoning stage"
    custom["attributes"] = [
        _attr("gen_ai.operation.name", "vendor_reasoning_stage"),
    ]

    report = inspect_otel_genai_export(payload)

    assert report["ignored_span_count"] == 0
    assert report["events"][-1]["operation"] == "vendor_reasoning_stage"


def test_duplicate_otlp_attribute_keys_fail_closed():
    payload = _payload()
    workflow = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    workflow["attributes"].append(
        _attr("gen_ai.operation.name", "invoke_workflow")
    )

    with pytest.raises(OTelGenAIIntakeError, match="duplicate attribute"):
        inspect_otel_genai_export(payload)


def test_duplicate_attribute_key_rejected_even_when_first_value_is_not_string():
    payload = _payload()
    workflow = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    workflow["attributes"].insert(
        0,
        {
            "key": "gen_ai.operation.name",
            "value": {"intValue": "1"},
        },
    )

    with pytest.raises(OTelGenAIIntakeError, match="duplicate attribute"):
        inspect_otel_genai_export(payload)


def test_schema_binding_is_evaluated_per_genai_event_not_globally():
    payload = _payload()
    payload["resourceSpans"][0]["schemaUrl"] = (
        "https://opentelemetry.io/schemas/1.44.0"
    )
    payload["resourceSpans"].append(
        {
            "scopeSpans": [
                {
                    "spans": [
                        {
                            "traceId": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                            "spanId": "ffffffffffffffff",
                            "name": "invoke_agent unbound",
                            "status": {"code": 1},
                            "attributes": [
                                _attr("gen_ai.operation.name", "invoke_agent"),
                                _attr("gen_ai.agent.name", "unbound"),
                            ],
                        }
                    ]
                }
            ]
        }
    )

    report = inspect_otel_genai_export(payload)

    assert report["events"][0]["schema_url"] == (
        "https://opentelemetry.io/schemas/1.44.0"
    )
    assert report["events"][-1]["schema_url"] is None
    assert "semantic_convention_version:unbound" in report["assurance_gaps"]


def test_malformed_string_semantic_attribute_fails_closed():
    payload = _payload()
    workflow = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    workflow["attributes"][0] = {
        "key": "gen_ai.operation.name",
        "value": {"intValue": "1"},
    }

    with pytest.raises(OTelGenAIIntakeError, match="gen_ai.operation.name"):
        inspect_otel_genai_export(payload)


def test_dropped_span_attributes_are_reported_as_assurance_incompleteness():
    payload = _payload()
    agent = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][1]
    agent["droppedAttributesCount"] = 2

    report = inspect_otel_genai_export(payload)

    assert report["events"][1]["dropped_attributes_count"] == 2
    assert "telemetry_attributes:dropped" in report["assurance_gaps"]
