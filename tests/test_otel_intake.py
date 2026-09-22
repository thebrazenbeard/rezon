import hashlib
import json

import pytest

from rezon.otel import OTelIntakeError, inspect_otel_export


TRACE_A = "11111111111111111111111111111111"
TRACE_B = "22222222222222222222222222222222"


def _value(kind, value):
    return {kind: value}


def _attr(key, kind, value):
    return {"key": key, "value": _value(kind, value)}


def _microsoft_like_payload():
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        _attr("service.name", "stringValue", "agent-framework"),
                        _attr("service.version", "stringValue", "1.19.0"),
                    ],
                    "droppedAttributesCount": 0,
                },
                "scopeSpans": [
                    {
                        "scope": {
                            "name": "agent_framework",
                            "version": "1.19.0",
                            "attributes": [
                                _attr("scope.role", "stringValue", "workflow"),
                            ],
                            "droppedAttributesCount": 0,
                        },
                        "schemaUrl": "https://opentelemetry.io/schemas/1.44.0",
                        "spans": [
                            {
                                "traceId": TRACE_A,
                                "spanId": "aaaaaaaaaaaaaaaa",
                                "name": "workflow.run",
                                "kind": 1,
                                "traceState": "vendor=value",
                                "flags": 1,
                                "status": {"code": 1},
                                "attributes": [
                                    _attr("workflow.id", "stringValue", "wf-1"),
                                    _attr("max_iterations", "intValue", "100"),
                                    _attr("streaming", "boolValue", True),
                                ],
                            },
                            {
                                "traceId": TRACE_A,
                                "spanId": "bbbbbbbbbbbbbbbb",
                                "parentSpanId": "aaaaaaaaaaaaaaaa",
                                "name": "executor.process upper",
                                "kind": 1,
                                "status": {"code": 1},
                                "attributes": [
                                    _attr("executor.id", "stringValue", "upper"),
                                    _attr("executor.type", "stringValue", "UpperCaseExecutor"),
                                    _attr(
                                        "source.executors",
                                        "arrayValue",
                                        {
                                            "values": [
                                                {"stringValue": "start"},
                                                {"stringValue": "router"},
                                            ]
                                        },
                                    ),
                                    _attr(
                                        "metadata",
                                        "kvlistValue",
                                        {
                                            "values": [
                                                {
                                                    "key": "attempt",
                                                    "value": {"intValue": "1"},
                                                },
                                                {
                                                    "key": "accepted",
                                                    "value": {"boolValue": True},
                                                },
                                            ]
                                        },
                                    ),
                                ],
                                "events": [
                                    {
                                        "name": "executor.started",
                                        "attributes": [
                                            _attr("sequence", "intValue", "1"),
                                        ],
                                        "droppedAttributesCount": 0,
                                    }
                                ],
                            },
                        ],
                    }
                ]
            },
            {
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "traceId": TRACE_B,
                                "spanId": "cccccccccccccccc",
                                "name": "ordinary.background",
                                "status": {"code": 0},
                                "attributes": [],
                            }
                        ]
                    }
                ]
            },
        ]
    }


def _redigest(report):
    body = {key: value for key, value in report.items() if key != "intake_digest"}
    return hashlib.sha256(
        json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def test_generic_intake_preserves_multi_trace_workflow_topology_without_semantic_promotion():
    report = inspect_otel_export(_microsoft_like_payload())

    assert report["schema_version"] == "rezon.otel-intake.v1"
    assert report["trace_ids"] == [TRACE_A, TRACE_B]
    assert report["span_count"] == 3

    workflow, executor, background = report["spans"]
    assert workflow["span_name"] == "workflow.run"
    assert workflow["trace_state"] == "vendor=value"
    assert workflow["flags"] == 1
    assert workflow["resource_attributes"] == {
        "service.name": "agent-framework",
        "service.version": "1.19.0",
    }
    assert workflow["instrumentation_scope"] == {
        "name": "agent_framework",
        "version": "1.19.0",
        "attributes": {"scope.role": "workflow"},
        "dropped_attributes_count": 0,
    }
    assert workflow["attributes"]["workflow.id"] == "wf-1"
    assert workflow["attributes"]["max_iterations"] == 100
    assert workflow["attributes"]["streaming"] is True

    assert executor["parent_span_id"] == "aaaaaaaaaaaaaaaa"
    assert executor["attributes"]["executor.id"] == "upper"
    assert executor["attributes"]["source.executors"] == ["start", "router"]
    assert executor["attributes"]["metadata"] == {
        "attempt": 1,
        "accepted": True,
    }
    assert executor["events"] == [
        {
            "name": "executor.started",
            "time_unix_nano": 0,
            "attributes": {"sequence": 1},
            "dropped_attributes_count": 0,
        }
    ]

    assert background["semantic_classification"] == "unclassified"
    assert report["assurance"] == {
        "telemetry_structure": "observed",
        "semantic_meaning": "unestablished",
        "provenance": "unestablished",
        "source_currentness": "unestablished",
        "worker_independence": "unestablished",
        "authority": "unestablished",
        "effect_completion": "unestablished",
    }


def test_generic_intake_binds_complete_source_payload_and_normalized_view():
    first_payload = _microsoft_like_payload()
    second_payload = _microsoft_like_payload()
    second_payload["resourceSpans"][1]["scopeSpans"][0]["spans"][0]["name"] = (
        "ordinary.background.changed"
    )

    first = inspect_otel_export(first_payload)
    second = inspect_otel_export(second_payload)

    assert first["source_payload_digest"] != second["source_payload_digest"]
    assert first["intake_digest"] != second["intake_digest"]
    assert first["intake_digest"] == _redigest(first)


def test_generic_intake_reports_schema_and_dropped_attribute_gaps_per_span():
    payload = _microsoft_like_payload()
    payload["resourceSpans"][0]["scopeSpans"][0]["spans"][1][
        "droppedAttributesCount"
    ] = 2

    report = inspect_otel_export(payload)

    assert report["spans"][0]["schema_url"] == (
        "https://opentelemetry.io/schemas/1.44.0"
    )
    assert report["spans"][2]["schema_url"] is None
    assert "telemetry_schema:unbound" in report["assurance_gaps"]
    assert "telemetry_attributes:dropped" in report["assurance_gaps"]


def test_generic_intake_rejects_duplicate_attribute_keys_at_span_and_nested_kvlist():
    span_duplicate = _microsoft_like_payload()
    span = span_duplicate["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    span["attributes"].append(_attr("workflow.id", "stringValue", "wf-2"))

    with pytest.raises(OTelIntakeError, match="duplicate attribute"):
        inspect_otel_export(span_duplicate)

    nested_duplicate = _microsoft_like_payload()
    metadata = nested_duplicate["resourceSpans"][0]["scopeSpans"][0]["spans"][1][
        "attributes"
    ][3]["value"]["kvlistValue"]["values"]
    metadata.append({"key": "attempt", "value": {"intValue": "2"}})

    with pytest.raises(OTelIntakeError, match="duplicate attribute"):
        inspect_otel_export(nested_duplicate)


def test_generic_intake_rejects_invalid_identity_and_malformed_attribute_values():
    invalid_id = _microsoft_like_payload()
    invalid_id["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["spanId"] = "bad"

    with pytest.raises(OTelIntakeError, match="spanId"):
        inspect_otel_export(invalid_id)

    invalid_value = _microsoft_like_payload()
    invalid_value["resourceSpans"][0]["scopeSpans"][0]["spans"][0][
        "attributes"
    ][0]["value"] = {"stringValue": "wf-1", "intValue": "1"}

    with pytest.raises(OTelIntakeError, match="exactly one OTLP value kind"):
        inspect_otel_export(invalid_value)


def test_generic_intake_rejects_non_otlp_json_enum_names():
    invalid_kind = _microsoft_like_payload()
    invalid_kind["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["kind"] = (
        "SPAN_KIND_INTERNAL"
    )

    with pytest.raises(OTelIntakeError, match="span.kind"):
        inspect_otel_export(invalid_kind)

    invalid_status = _microsoft_like_payload()
    invalid_status["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["status"] = {
        "code": "STATUS_CODE_OK"
    }

    with pytest.raises(OTelIntakeError, match="status.code"):
        inspect_otel_export(invalid_status)


def test_generic_intake_rejects_all_zero_trace_and_span_ids():
    zero_trace = _microsoft_like_payload()
    zero_trace["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["traceId"] = (
        "0" * 32
    )

    with pytest.raises(OTelIntakeError, match="traceId"):
        inspect_otel_export(zero_trace)

    zero_span = _microsoft_like_payload()
    zero_span["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["spanId"] = (
        "0" * 16
    )

    with pytest.raises(OTelIntakeError, match="spanId"):
        inspect_otel_export(zero_span)


def test_resource_schema_does_not_masquerade_as_span_schema_binding():
    payload = _microsoft_like_payload()
    payload["resourceSpans"][1]["schemaUrl"] = (
        "https://opentelemetry.io/schemas/1.44.0"
    )

    report = inspect_otel_export(payload)
    background = report["spans"][2]

    assert background["resource_schema_url"] == (
        "https://opentelemetry.io/schemas/1.44.0"
    )
    assert background["schema_url"] is None
    assert "telemetry_schema:unbound" in report["assurance_gaps"]


def test_protojson_numeric_forms_and_base64_bytes_are_decoded():
    payload = _microsoft_like_payload()
    workflow = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    workflow["flags"] = "1e0"
    workflow["droppedAttributesCount"] = "2"
    workflow["attributes"].extend(
        [
            _attr("scientific_int", "intValue", "1e2"),
            _attr("string_double", "doubleValue", "1.25e2"),
            _attr("binary_payload", "bytesValue", "aGVsbG8"),
        ]
    )

    report = inspect_otel_export(payload)
    observed = report["spans"][0]

    assert observed["flags"] == 1
    assert observed["dropped_attributes_count"] == 2
    assert observed["attributes"]["scientific_int"] == 100
    assert observed["attributes"]["string_double"] == 125.0
    assert observed["attributes"]["binary_payload"] == {
        "bytes_base64": "aGVsbG8"
    }


def test_protojson_numeric_bounds_and_invalid_base64_fail_closed():
    int_overflow = _microsoft_like_payload()
    int_overflow["resourceSpans"][0]["scopeSpans"][0]["spans"][0][
        "attributes"
    ].append(
        _attr("overflow", "intValue", str(2**63))
    )
    with pytest.raises(OTelIntakeError, match="intValue"):
        inspect_otel_export(int_overflow)

    invalid_bytes = _microsoft_like_payload()
    invalid_bytes["resourceSpans"][0]["scopeSpans"][0]["spans"][0][
        "attributes"
    ].append(
        _attr("binary_payload", "bytesValue", "%%%not-base64%%%")
    )
    with pytest.raises(OTelIntakeError, match="bytesValue"):
        inspect_otel_export(invalid_bytes)

    count_overflow = _microsoft_like_payload()
    count_overflow["resourceSpans"][0]["scopeSpans"][0]["spans"][0][
        "droppedEventsCount"
    ] = str(2**32)
    with pytest.raises(OTelIntakeError, match="droppedEventsCount"):
        inspect_otel_export(count_overflow)


def test_span_timing_event_time_link_flags_and_drop_counts_are_preserved():
    payload = _microsoft_like_payload()
    executor = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][1]
    executor["startTimeUnixNano"] = "100"
    executor["endTimeUnixNano"] = 200
    executor["droppedEventsCount"] = "2"
    executor["droppedLinksCount"] = 1
    executor["events"][0]["timeUnixNano"] = "150"
    executor["links"] = [
        {
            "traceId": TRACE_B,
            "spanId": "dddddddddddddddd",
            "traceState": "vendor=value",
            "flags": "1",
            "attributes": [],
            "droppedAttributesCount": 0,
        }
    ]

    report = inspect_otel_export(payload)
    observed = report["spans"][1]

    assert observed["start_time_unix_nano"] == 100
    assert observed["end_time_unix_nano"] == 200
    assert observed["events"][0]["time_unix_nano"] == 150
    assert observed["links"][0]["flags"] == 1
    assert observed["dropped_events_count"] == 2
    assert observed["dropped_links_count"] == 1
    assert "telemetry_events:dropped" in report["assurance_gaps"]
    assert "telemetry_links:dropped" in report["assurance_gaps"]


def test_invalid_span_timing_fails_closed_and_missing_timing_is_visible():
    backwards = _microsoft_like_payload()
    span = backwards["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    span["startTimeUnixNano"] = "200"
    span["endTimeUnixNano"] = "100"

    with pytest.raises(OTelIntakeError, match="endTimeUnixNano"):
        inspect_otel_export(backwards)

    report = inspect_otel_export(_microsoft_like_payload())
    assert "telemetry_timing:unbound" in report["assurance_gaps"]


def test_empty_instrumentation_scope_identity_is_valid_unknown_state():
    payload = _microsoft_like_payload()
    scope = payload["resourceSpans"][0]["scopeSpans"][0]["scope"]
    scope["name"] = ""
    scope["version"] = ""

    report = inspect_otel_export(payload)

    assert report["spans"][0]["instrumentation_scope"]["name"] == ""
    assert report["spans"][0]["instrumentation_scope"]["version"] == ""
