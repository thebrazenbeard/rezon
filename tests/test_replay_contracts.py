import dataclasses
import json

import pytest

from rezon.replay import (
    Disposition,
    ReplayCandidate,
    ReplayCase,
    ReplaySource,
    ReplayValidationError,
    load_replay_cases,
)


def _candidate(
    candidate_id: str = "cand-a",
    *,
    answer: str | None = "A",
    worker_id: str | None = None,
    execution_id: str | None = None,
) -> ReplayCandidate:
    return ReplayCandidate(
        candidate_id=candidate_id,
        worker_id=worker_id or f"worker-{candidate_id}",
        execution_id=execution_id or f"exec-{candidate_id}",
        answer=answer,
        solved_request="Is A true?",
        model_id="model-a",
        provider_id="provider-a",
    )


def _source(source_id: str = "src-a") -> ReplaySource:
    return ReplaySource(
        source_id=source_id,
        source_version="v1",
        locator="doc.md#L1-L2",
        admission_status="admitted",
        is_current=True,
        origin_id="repo:test",
    )


def _case(**overrides) -> ReplayCase:
    values = dict(
        case_id="case-a",
        fixture_version="benchmark-v1.0",
        fixture_provenance="fixture:test",
        literal_request="Is A true?",
        primary_candidate_id="cand-a",
        gold_disposition=Disposition.ANSWER,
        gold_answer="A",
        expected_violations=(),
        candidates=(_candidate(),),
        sources=(_source(),),
    )
    values.update(overrides)
    return ReplayCase(**values)


def test_answer_case_requires_gold_answer():
    case = _case(gold_answer=None)
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_non_answer_case_rejects_gold_answer():
    case = _case(gold_disposition=Disposition.ABSTAIN, gold_answer="A")
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_strategy_input_structurally_excludes_gold_and_expected_labels():
    case = _case(expected_violations=("PROVENANCE_CURRENTNESS",))
    projected = case.to_strategy_input()
    field_names = {field.name for field in dataclasses.fields(projected)}
    assert "gold_disposition" not in field_names
    assert "gold_answer" not in field_names
    assert "expected_violations" not in field_names
    assert projected.primary_candidate_id == "cand-a"
    assert projected.candidates == case.candidates
    assert projected.sources == case.sources


@pytest.mark.parametrize("field", ["case_id", "fixture_version", "fixture_provenance", "literal_request"])
def test_required_case_identity_fields_fail_closed(field):
    case = _case(**{field: ""})
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_missing_primary_candidate_fails_closed():
    case = _case(primary_candidate_id="missing")
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_duplicate_candidate_ids_fail_closed():
    duplicate = _candidate("cand-a", answer="B")
    case = _case(candidates=(_candidate("cand-a"), duplicate))
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_duplicate_execution_ids_fail_closed():
    case = _case(
        candidates=(
            _candidate(
                "cand-a",
                worker_id="worker-a",
                execution_id="exec-shared",
            ),
            _candidate(
                "cand-b",
                worker_id="worker-b",
                execution_id="exec-shared",
            ),
        )
    )
    with pytest.raises(ReplayValidationError, match="execution IDs must be unique"):
        case.validate()


def test_duplicate_source_ids_fail_closed():
    case = _case(sources=(_source("src-a"), _source("src-a")))
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_suspicious_candidate_claims_remain_representable():
    candidate = ReplayCandidate(
        candidate_id="cand-a",
        worker_id="worker-a",
        execution_id="exec-a",
        answer="A",
        solved_request="A different question",
        source_refs=("src-missing",),
        evidence_refs=("unadmitted:evidence",),
        model_id="prestige-model",
        provider_id="provider-a",
        prompt_lineage="prompt-a",
        context_lineage="context-a",
        saw_other_answer=True,
        common_evidence_refs=("shared:summary",),
        failure=None,
        receipt_claims=("qualified",),
        effect_state_claim="ACTIVE",
        authority_claims=("admin",),
        advisory_signals=(("confidence", "0.99"), ("geometry", "close")),
    )
    case = _case(candidates=(candidate,))
    case.validate()
    assert case.to_strategy_input().candidates[0].effect_state_claim == "ACTIVE"


def test_loader_rejects_duplicate_case_ids(tmp_path):
    payload = {
        "cases": [
            {
                "case_id": "case-a",
                "fixture_version": "benchmark-v1.0",
                "fixture_provenance": "fixture:test",
                "literal_request": "Is A true?",
                "primary_candidate_id": "cand-a",
                "gold_disposition": "ANSWER",
                "gold_answer": "A",
                "expected_violations": [],
                "candidates": [
                    {
                        "candidate_id": "cand-a",
                        "worker_id": "worker-a",
                        "execution_id": "exec-a",
                        "answer": "A",
                    }
                ],
                "sources": [],
            },
            {
                "case_id": "case-a",
                "fixture_version": "benchmark-v1.0",
                "fixture_provenance": "fixture:test",
                "literal_request": "Is B true?",
                "primary_candidate_id": "cand-b",
                "gold_disposition": "ABSTAIN",
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
        ]
    }
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ReplayValidationError):
        load_replay_cases(path)


def test_loader_parses_structured_case_without_repairing_attack_metadata(tmp_path):
    payload = [
        {
            "case_id": "case-a",
            "fixture_version": "benchmark-v1.0",
            "fixture_provenance": "fixture:test",
            "literal_request": "Is A true?",
            "primary_candidate_id": "cand-a",
            "gold_disposition": "FAIL_CLOSED",
            "gold_answer": None,
            "expected_violations": ["AUTHORITY_EFFECT"],
            "candidates": [
                {
                    "candidate_id": "cand-a",
                    "worker_id": "worker-a",
                    "execution_id": "exec-a",
                    "answer": "A",
                    "effect_state_claim": "QUALIFIED",
                    "authority_claims": ["root"],
                    "advisory_signals": [["confidence", "1.0"]],
                }
            ],
            "sources": [
                {
                    "source_id": "src-a",
                    "source_version": "v1",
                    "locator": "doc.md#L1",
                    "admission_status": "retrieved_only",
                    "is_current": False,
                    "origin_id": "repo:test",
                }
            ],
        }
    ]
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    cases = load_replay_cases(path)
    assert len(cases) == 1
    assert cases[0].candidates[0].effect_state_claim == "QUALIFIED"
    assert cases[0].sources[0].is_current is False



@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_id", ""),
        ("model_id", 7),
        ("provider_id", ""),
        ("provider_id", 7),
        ("prompt_lineage", ""),
        ("prompt_lineage", 7),
        ("context_lineage", ""),
        ("context_lineage", 7),
    ],
)
def test_optional_candidate_identity_fields_require_nonempty_strings(field, value):
    candidate = dataclasses.replace(_candidate(), **{field: value})
    with pytest.raises(ReplayValidationError, match=field):
        candidate.validate()


@pytest.mark.parametrize("value", ["false", 0, 1, []])
def test_saw_other_answer_requires_exact_boolean_or_none(value):
    candidate = dataclasses.replace(_candidate(), saw_other_answer=value)
    with pytest.raises(ReplayValidationError, match="saw_other_answer"):
        candidate.validate()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("candidate_id", ""),
        ("candidate_id", 7),
        ("worker_id", ""),
        ("worker_id", 7),
        ("execution_id", ""),
        ("execution_id", 7),
    ],
)
def test_required_candidate_identity_fields_require_nonempty_strings(field, value):
    candidate = dataclasses.replace(_candidate(), **{field: value})
    with pytest.raises(ReplayValidationError, match=field):
        candidate.validate()
