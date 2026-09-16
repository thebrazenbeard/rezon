from __future__ import annotations

import dataclasses
import json

import pytest

from rezon.replay import (
    Disposition,
    ReplayCandidate,
    ReplayCase,
    ReplaySource,
    ReplayStrategyOutcome,
    ReplayValidationError,
    StrategyInput,
    load_replay_cases,
)


def _candidate(candidate_id: str = "cand-a") -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=f"worker-{candidate_id}",
        execution_id=f"exec-{candidate_id}",
        answer="A",
        solved_request="Is A true?",
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="prompt-a",
        context_lineage="context-a",
    )


def _source(source_id: str = "source-a") -> ReplaySource:
    return ReplaySource(
        source_id=source_id,
        source_version="v1",
        locator=f"fixture://{source_id}",
        admission_status="admitted",
        currentness_status="current",
        origin_id="origin-a",
    )


def _case(**overrides) -> ReplayCase:
    candidate = _candidate()
    values = dict(
        case_id="case-a",
        fixture_version="benchmark-v1.0",
        fixture_provenance="fixture:test",
        literal_request="Is A true?",
        primary_candidate_id="cand-a",
        gold_disposition=Disposition.ANSWER,
        gold_answer="A",
        expected_violations=(),
        candidates=(candidate,),
        sources=(),
    )
    values.update(overrides)
    return ReplayCase(**values)


def test_disposition_surface_is_exact_and_stable():
    assert {item.value for item in Disposition} == {
        "answer",
        "abstain",
        "fail_closed",
    }


def test_answer_case_requires_gold_answer():
    case = _case(gold_answer=None)
    with pytest.raises(ReplayValidationError, match="gold answer"):
        case.validate()


@pytest.mark.parametrize("disposition", [Disposition.ABSTAIN, Disposition.FAIL_CLOSED])
def test_non_answer_gold_disposition_rejects_gold_answer(disposition):
    case = _case(gold_disposition=disposition, gold_answer="A")
    with pytest.raises(ReplayValidationError, match="non-answer"):
        case.validate()


def test_strategy_input_structurally_excludes_evaluator_only_fields():
    case = _case(expected_violations=("PROVENANCE_CURRENTNESS",))
    projected = case.to_strategy_input()

    assert isinstance(projected, StrategyInput)
    field_names = {field.name for field in dataclasses.fields(projected)}
    assert "gold_disposition" not in field_names
    assert "gold_answer" not in field_names
    assert "expected_violations" not in field_names
    assert "fixture_provenance" not in field_names
    assert projected.case_id == "case-a"
    assert projected.fixture_version == "benchmark-v1.0"
    assert projected.literal_request == "Is A true?"
    assert projected.primary_candidate_id == "cand-a"
    assert projected.candidates == case.candidates
    assert projected.sources == case.sources


def test_projection_is_a_new_frozen_value_without_evaluator_back_reference():
    projected = _case().to_strategy_input()
    assert dataclasses.is_dataclass(projected)
    with pytest.raises(dataclasses.FrozenInstanceError):
        projected.literal_request = "changed"  # type: ignore[misc]
    assert not hasattr(projected, "replay_case")
    assert not hasattr(projected, "evaluator")


def test_case_validation_rejects_missing_identity_request_and_fixture_metadata():
    with pytest.raises(ReplayValidationError):
        _case(case_id="").validate()
    with pytest.raises(ReplayValidationError):
        _case(fixture_version="").validate()
    with pytest.raises(ReplayValidationError):
        _case(fixture_provenance="").validate()
    with pytest.raises(ReplayValidationError):
        _case(literal_request="").validate()


def test_case_validation_rejects_duplicate_candidate_and_source_ids():
    duplicate_candidate = _candidate("cand-a")
    with pytest.raises(ReplayValidationError, match="duplicate candidate"):
        _case(candidates=(_candidate("cand-a"), duplicate_candidate)).validate()

    with pytest.raises(ReplayValidationError, match="duplicate source"):
        _case(sources=(_source("source-a"), _source("source-a"))).validate()


def test_case_validation_requires_primary_candidate_to_exist():
    with pytest.raises(ReplayValidationError, match="primary candidate"):
        _case(primary_candidate_id="missing").validate()


def test_structurally_valid_suspicious_candidate_claims_remain_representable():
    suspicious = ReplayCandidate(
        candidate_id="cand-a",
        worker_id="worker-a",
        execution_id="exec-a",
        answer="A",
        solved_request="A different proposition",
        source_refs=("source-stale",),
        evidence_refs=("evidence-unadmitted",),
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="prompt-shared",
        context_lineage="context-shared",
        saw_candidate_ids=("cand-b",),
        common_evidence_refs=("evidence-shared",),
        failures=("worker-timeout-hidden",),
        receipt_claims=("verified",),
        effect_claims=("active", "qualified"),
        authority_claims=("may-deploy",),
        advisory_signals=(("confidence", 0.999), ("novelty", 1.0)),
    )
    case = _case(candidates=(suspicious,))

    case.validate()
    projected = case.to_strategy_input()
    assert projected.candidates[0] == suspicious


def test_replay_strategy_outcome_is_replay_specific_and_frozen():
    outcome = ReplayStrategyOutcome(
        disposition=Disposition.ABSTAIN,
        answer=None,
        accepted_candidate_ids=(),
        rejected_candidate_ids=("cand-a",),
        detected_violations=("PROVENANCE_CURRENTNESS",),
        unresolved=("source-currentness",),
        operation_count=1,
        trace=("consulted:cand-a",),
    )
    assert outcome.disposition is Disposition.ABSTAIN
    with pytest.raises(dataclasses.FrozenInstanceError):
        outcome.answer = "A"  # type: ignore[misc]


def test_loader_rejects_duplicate_case_ids(tmp_path):
    payload = {
        "fixture_version": "benchmark-v1.0",
        "fixture_provenance": "fixture:test",
        "cases": [
            {
                "case_id": "case-a",
                "literal_request": "Is A true?",
                "primary_candidate_id": "cand-a",
                "gold_disposition": "answer",
                "gold_answer": "A",
                "expected_violations": [],
                "candidates": [
                    {
                        "candidate_id": "cand-a",
                        "worker_id": "worker-a",
                        "execution_id": "exec-a",
                        "answer": "A",
                        "solved_request": "Is A true?",
                        "model_id": "model-a",
                        "provider_id": "provider-a",
                    }
                ],
                "sources": [],
            },
            {
                "case_id": "case-a",
                "literal_request": "Is B true?",
                "primary_candidate_id": "cand-b",
                "gold_disposition": "abstain",
                "gold_answer": None,
                "expected_violations": [],
                "candidates": [
                    {
                        "candidate_id": "cand-b",
                        "worker_id": "worker-b",
                        "execution_id": "exec-b",
                        "answer": None,
                    }
                ],
                "sources": [],
            },
        ],
    }
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ReplayValidationError, match="duplicate case"):
        load_replay_cases(path)


def test_loader_materializes_explicit_source_and_candidate_metadata(tmp_path):
    payload = {
        "fixture_version": "benchmark-v1.0",
        "fixture_provenance": "fixture:test",
        "cases": [
            {
                "case_id": "case-a",
                "literal_request": "Is A true?",
                "primary_candidate_id": "cand-a",
                "gold_disposition": "answer",
                "gold_answer": "A",
                "expected_violations": ["PROVENANCE_CURRENTNESS"],
                "candidates": [
                    {
                        "candidate_id": "cand-a",
                        "worker_id": "worker-a",
                        "execution_id": "exec-a",
                        "answer": "A",
                        "solved_request": "Is A true?",
                        "source_refs": ["source-a"],
                        "evidence_refs": ["evidence-a"],
                        "model_id": "model-a",
                        "provider_id": "provider-a",
                        "prompt_lineage": "prompt-a",
                        "context_lineage": "context-a",
                        "saw_candidate_ids": ["cand-b"],
                        "common_evidence_refs": ["evidence-shared"],
                        "failures": ["worker-partial"],
                        "receipt_claims": ["verified"],
                        "effect_claims": ["active"],
                        "authority_claims": ["may-write"],
                        "advisory_signals": {"confidence": 0.97},
                    }
                ],
                "sources": [
                    {
                        "source_id": "source-a",
                        "source_version": "v7",
                        "locator": "fixture://source-a",
                        "admission_status": "retrieved_only",
                        "currentness_status": "stale",
                        "origin_id": "origin-a",
                    }
                ],
            }
        ],
    }
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    cases = load_replay_cases(path)
    assert len(cases) == 1
    case = cases[0]
    assert case.fixture_version == "benchmark-v1.0"
    assert case.fixture_provenance == "fixture:test"
    assert case.sources[0].source_version == "v7"
    assert case.sources[0].admission_status == "retrieved_only"
    assert case.candidates[0].source_refs == ("source-a",)
    assert case.candidates[0].advisory_signals == (("confidence", 0.97),)
    assert case.expected_violations == ("PROVENANCE_CURRENTNESS",)


def test_loader_rejects_non_object_fixture_root(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([{"case_id": "case-a"}]), encoding="utf-8")

    with pytest.raises(ReplayValidationError, match="fixture root"):
        load_replay_cases(path)
