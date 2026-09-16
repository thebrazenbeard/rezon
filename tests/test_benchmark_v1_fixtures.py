import dataclasses
from pathlib import Path

from rezon.replay import Disposition, load_replay_cases


FIXTURE_PATH = Path("tests/fixtures/benchmark_v1.json")
REQUIRED_CLASSES = {
    "PROPOSITION_FIDELITY",
    "PROVENANCE_CURRENTNESS",
    "VALID_PREFIX_ROLLBACK",
    "DUPLICATE_EVIDENCE",
    "INDEPENDENCE_CONTAMINATION",
    "ADMISSION_INTEGRITY",
    "AUTHORITY_EFFECT_BOUNDARY",
    "CONTRADICTION_OMISSION",
    "FAILURE_VISIBILITY",
    "MANDATORY_VERIFICATION_UNAVAILABLE",
    "MALFORMED_RECEIPT",
    "INSUFFICIENT_EVIDENCE",
}


def _cases():
    return load_replay_cases(FIXTURE_PATH)


def test_fixture_exists_and_uses_frozen_v1_version():
    assert FIXTURE_PATH.exists()
    cases = _cases()
    assert cases
    assert {case.fixture_version for case in cases} == {"benchmark-v1.0"}
    assert all(case.fixture_provenance for case in cases)


def test_fixture_covers_every_required_attack_class_and_clean_controls():
    cases = _cases()
    labels = {
        label
        for case in cases
        for label in case.expected_violations
    }
    assert REQUIRED_CLASSES <= labels

    clean_answers = [
        case
        for case in cases
        if not case.expected_violations
        and case.gold_disposition is Disposition.ANSWER
    ]
    assert len(clean_answers) >= 2
    assert any(case.gold_disposition is Disposition.ABSTAIN for case in cases)
    assert any(case.gold_disposition is Disposition.FAIL_CLOSED for case in cases)


def test_gold_answer_population_is_not_outnumbered_by_non_answer_population():
    cases = _cases()
    answer_cases = [case for case in cases if case.gold_disposition is Disposition.ANSWER]
    non_answer_cases = [case for case in cases if case.gold_disposition is not Disposition.ANSWER]

    assert len(answer_cases) >= len(non_answer_cases)


def test_strategy_projection_contains_no_evaluator_gold_or_violation_labels():
    forbidden = {"gold_disposition", "gold_answer", "expected_violations"}
    for case in _cases():
        projected = case.to_strategy_input()
        field_names = {field.name for field in dataclasses.fields(projected)}
        assert forbidden.isdisjoint(field_names)
        rendered = repr(projected)
        for label in case.expected_violations:
            assert label not in rendered


def test_fixture_ids_are_neutral_and_do_not_encode_attack_labels():
    cases = _cases()
    forbidden_fragments = {
        "stale",
        "rollback",
        "duplicate",
        "correlated",
        "unadmitted",
        "authority",
        "contradiction",
        "failure",
        "verifier",
        "malformed",
        "insufficient",
        "clean",
        "substitution",
    }
    for case in cases:
        identifiers = [case.case_id, case.primary_candidate_id]
        identifiers.extend(candidate.candidate_id for candidate in case.candidates)
        identifiers.extend(source.source_id for source in case.sources)
        for identifier in identifiers:
            lowered = identifier.casefold()
            assert all(fragment not in lowered for fragment in forbidden_fragments)


def test_fixture_case_ids_are_unique_and_payloads_validate():
    cases = _cases()
    assert len({case.case_id for case in cases}) == len(cases)
    for case in cases:
        case.validate()
        assert case.to_strategy_input().case_id == case.case_id


def test_all_three_strategies_can_execute_every_frozen_case():
    from rezon.replay_strategies import fixed_multipass, rezon_guarded, single_pass

    for case in _cases():
        strategy_input = case.to_strategy_input()
        for strategy in (single_pass, fixed_multipass, rezon_guarded):
            outcome = strategy(strategy_input)
            assert outcome.disposition in set(Disposition)
