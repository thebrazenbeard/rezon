from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any


class ReplayValidationError(ValueError):
    """Raised when a replay fixture violates the structural benchmark contract."""


class Disposition(str, Enum):
    ANSWER = "answer"
    ABSTAIN = "abstain"
    FAIL_CLOSED = "fail_closed"


def _required_text(value: str | None, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReplayValidationError(f"{label} is required")


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ReplayValidationError(f"{label} must be a list of strings")
    return tuple(value)


def _reject_unknown_keys(record: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise ReplayValidationError(f"{label} contains unknown fields: {unknown}")


@dataclass(frozen=True)
class ReplaySource:
    source_id: str
    source_version: str | None
    locator: str
    admission_status: str
    currentness_status: str
    origin_id: str

    def validate(self) -> None:
        _required_text(self.source_id, "source_id")
        if self.source_version is not None:
            _required_text(self.source_version, "source_version")
        _required_text(self.locator, "source locator")
        _required_text(self.admission_status, "source admission_status")
        _required_text(self.currentness_status, "source currentness_status")
        _required_text(self.origin_id, "source origin_id")


@dataclass(frozen=True)
class ReplayCandidate:
    candidate_id: str
    worker_id: str
    execution_id: str
    answer: str | None
    solved_request: str | None = None
    source_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    model_id: str | None = None
    provider_id: str | None = None
    prompt_lineage: str | None = None
    context_lineage: str | None = None
    saw_candidate_ids: tuple[str, ...] = ()
    common_evidence_refs: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    receipt_claims: tuple[str, ...] = ()
    effect_claims: tuple[str, ...] = ()
    authority_claims: tuple[str, ...] = ()
    advisory_signals: tuple[tuple[str, float], ...] = ()

    def validate(self) -> None:
        _required_text(self.candidate_id, "candidate_id")
        _required_text(self.worker_id, "worker_id")
        _required_text(self.execution_id, "execution_id")
        if self.answer is not None and not isinstance(self.answer, str):
            raise ReplayValidationError("candidate answer must be a string or null")
        if self.solved_request is not None and not isinstance(self.solved_request, str):
            raise ReplayValidationError("candidate solved_request must be a string or null")
        for label, items in (
            ("source_refs", self.source_refs),
            ("evidence_refs", self.evidence_refs),
            ("saw_candidate_ids", self.saw_candidate_ids),
            ("common_evidence_refs", self.common_evidence_refs),
            ("failures", self.failures),
            ("receipt_claims", self.receipt_claims),
            ("effect_claims", self.effect_claims),
            ("authority_claims", self.authority_claims),
        ):
            if any(not isinstance(item, str) for item in items):
                raise ReplayValidationError(f"candidate {label} must contain strings")
        for name, value in self.advisory_signals:
            _required_text(name, "advisory signal name")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ReplayValidationError("advisory signal values must be numeric")


@dataclass(frozen=True)
class StrategyInput:
    case_id: str
    fixture_version: str
    literal_request: str
    primary_candidate_id: str
    candidates: tuple[ReplayCandidate, ...]
    sources: tuple[ReplaySource, ...]


@dataclass(frozen=True)
class ReplayCase:
    case_id: str
    fixture_version: str
    fixture_provenance: str
    literal_request: str
    primary_candidate_id: str
    gold_disposition: Disposition
    gold_answer: str | None
    expected_violations: tuple[str, ...]
    candidates: tuple[ReplayCandidate, ...]
    sources: tuple[ReplaySource, ...]

    def validate(self) -> None:
        _required_text(self.case_id, "case_id")
        _required_text(self.fixture_version, "fixture_version")
        _required_text(self.fixture_provenance, "fixture_provenance")
        _required_text(self.literal_request, "literal_request")
        _required_text(self.primary_candidate_id, "primary candidate")

        if not isinstance(self.gold_disposition, Disposition):
            raise ReplayValidationError("gold disposition must be a Disposition")
        if self.gold_disposition is Disposition.ANSWER:
            if not isinstance(self.gold_answer, str) or not self.gold_answer:
                raise ReplayValidationError("answer cases require a gold answer")
        elif self.gold_answer is not None:
            raise ReplayValidationError("non-answer gold dispositions must not carry a gold answer")

        if any(not isinstance(item, str) for item in self.expected_violations):
            raise ReplayValidationError("expected_violations must contain strings")

        candidate_ids: set[str] = set()
        for candidate in self.candidates:
            if not isinstance(candidate, ReplayCandidate):
                raise ReplayValidationError("candidates must be ReplayCandidate values")
            candidate.validate()
            if candidate.candidate_id in candidate_ids:
                raise ReplayValidationError(f"duplicate candidate id: {candidate.candidate_id}")
            candidate_ids.add(candidate.candidate_id)

        if self.primary_candidate_id not in candidate_ids:
            raise ReplayValidationError(
                f"primary candidate does not exist: {self.primary_candidate_id}"
            )

        source_ids: set[str] = set()
        for source in self.sources:
            if not isinstance(source, ReplaySource):
                raise ReplayValidationError("sources must be ReplaySource values")
            source.validate()
            if source.source_id in source_ids:
                raise ReplayValidationError(f"duplicate source id: {source.source_id}")
            source_ids.add(source.source_id)

    def to_strategy_input(self) -> StrategyInput:
        self.validate()
        return StrategyInput(
            case_id=self.case_id,
            fixture_version=self.fixture_version,
            literal_request=self.literal_request,
            primary_candidate_id=self.primary_candidate_id,
            candidates=tuple(self.candidates),
            sources=tuple(self.sources),
        )


@dataclass(frozen=True)
class ReplayStrategyOutcome:
    disposition: Disposition
    answer: str | None = None
    accepted_candidate_ids: tuple[str, ...] = ()
    rejected_candidate_ids: tuple[str, ...] = ()
    detected_violations: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    operation_count: int = 0
    token_count: int | None = None
    provider_cost: float | None = None
    latency_ms: float | None = None
    trace: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, Disposition):
            raise ReplayValidationError("strategy disposition must be a Disposition")
        if self.disposition is Disposition.ANSWER:
            if not isinstance(self.answer, str) or not self.answer:
                raise ReplayValidationError("ANSWER outcomes require an answer")
        elif self.answer is not None:
            raise ReplayValidationError("non-answer outcomes must not carry an answer")
        if self.operation_count < 0:
            raise ReplayValidationError("operation_count cannot be negative")
        if self.token_count is not None and self.token_count < 0:
            raise ReplayValidationError("token_count cannot be negative")
        if self.provider_cost is not None and self.provider_cost < 0:
            raise ReplayValidationError("provider_cost cannot be negative")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ReplayValidationError("latency_ms cannot be negative")


def _parse_source(record: Any, index: int) -> ReplaySource:
    if not isinstance(record, dict):
        raise ReplayValidationError(f"source[{index}] must be an object")
    allowed = {
        "source_id",
        "source_version",
        "locator",
        "admission_status",
        "currentness_status",
        "origin_id",
    }
    _reject_unknown_keys(record, allowed, f"source[{index}]")
    source = ReplaySource(
        source_id=record.get("source_id"),
        source_version=record.get("source_version"),
        locator=record.get("locator"),
        admission_status=record.get("admission_status"),
        currentness_status=record.get("currentness_status"),
        origin_id=record.get("origin_id"),
    )
    source.validate()
    return source


def _parse_candidate(record: Any, index: int) -> ReplayCandidate:
    if not isinstance(record, dict):
        raise ReplayValidationError(f"candidate[{index}] must be an object")
    allowed = {
        "candidate_id",
        "worker_id",
        "execution_id",
        "answer",
        "solved_request",
        "source_refs",
        "evidence_refs",
        "model_id",
        "provider_id",
        "prompt_lineage",
        "context_lineage",
        "saw_candidate_ids",
        "common_evidence_refs",
        "failures",
        "receipt_claims",
        "effect_claims",
        "authority_claims",
        "advisory_signals",
    }
    _reject_unknown_keys(record, allowed, f"candidate[{index}]")

    advisory_raw = record.get("advisory_signals", {})
    if advisory_raw is None:
        advisory_raw = {}
    if not isinstance(advisory_raw, dict):
        raise ReplayValidationError("candidate advisory_signals must be an object")
    advisory_signals: list[tuple[str, float]] = []
    for key in sorted(advisory_raw):
        value = advisory_raw[key]
        if not isinstance(key, str) or isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReplayValidationError("candidate advisory_signals must map strings to numbers")
        advisory_signals.append((key, float(value)))

    candidate = ReplayCandidate(
        candidate_id=record.get("candidate_id"),
        worker_id=record.get("worker_id"),
        execution_id=record.get("execution_id"),
        answer=record.get("answer"),
        solved_request=record.get("solved_request"),
        source_refs=_string_tuple(record.get("source_refs"), "candidate source_refs"),
        evidence_refs=_string_tuple(record.get("evidence_refs"), "candidate evidence_refs"),
        model_id=record.get("model_id"),
        provider_id=record.get("provider_id"),
        prompt_lineage=record.get("prompt_lineage"),
        context_lineage=record.get("context_lineage"),
        saw_candidate_ids=_string_tuple(record.get("saw_candidate_ids"), "candidate saw_candidate_ids"),
        common_evidence_refs=_string_tuple(
            record.get("common_evidence_refs"), "candidate common_evidence_refs"
        ),
        failures=_string_tuple(record.get("failures"), "candidate failures"),
        receipt_claims=_string_tuple(record.get("receipt_claims"), "candidate receipt_claims"),
        effect_claims=_string_tuple(record.get("effect_claims"), "candidate effect_claims"),
        authority_claims=_string_tuple(record.get("authority_claims"), "candidate authority_claims"),
        advisory_signals=tuple(advisory_signals),
    )
    candidate.validate()
    return candidate


def _parse_case(
    record: Any,
    fixture_version: str,
    fixture_provenance: str,
    index: int,
) -> ReplayCase:
    if not isinstance(record, dict):
        raise ReplayValidationError(f"case[{index}] must be an object")
    allowed = {
        "case_id",
        "literal_request",
        "primary_candidate_id",
        "gold_disposition",
        "gold_answer",
        "expected_violations",
        "candidates",
        "sources",
    }
    _reject_unknown_keys(record, allowed, f"case[{index}]")

    try:
        disposition = Disposition(record.get("gold_disposition"))
    except (TypeError, ValueError) as exc:
        raise ReplayValidationError("case gold_disposition is invalid") from exc

    candidates_raw = record.get("candidates", [])
    sources_raw = record.get("sources", [])
    if not isinstance(candidates_raw, list):
        raise ReplayValidationError("case candidates must be a list")
    if not isinstance(sources_raw, list):
        raise ReplayValidationError("case sources must be a list")

    case = ReplayCase(
        case_id=record.get("case_id"),
        fixture_version=fixture_version,
        fixture_provenance=fixture_provenance,
        literal_request=record.get("literal_request"),
        primary_candidate_id=record.get("primary_candidate_id"),
        gold_disposition=disposition,
        gold_answer=record.get("gold_answer"),
        expected_violations=_string_tuple(
            record.get("expected_violations"), "case expected_violations"
        ),
        candidates=tuple(
            _parse_candidate(candidate, candidate_index)
            for candidate_index, candidate in enumerate(candidates_raw)
        ),
        sources=tuple(
            _parse_source(source, source_index)
            for source_index, source in enumerate(sources_raw)
        ),
    )
    case.validate()
    return case


def load_replay_cases(path: str | Path) -> tuple[ReplayCase, ...]:
    fixture_path = Path(path)
    try:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReplayValidationError(f"unable to load replay fixture: {fixture_path}") from exc

    if not isinstance(payload, dict):
        raise ReplayValidationError("fixture root must be an object")
    _reject_unknown_keys(
        payload,
        {"fixture_version", "fixture_provenance", "cases"},
        "fixture root",
    )

    fixture_version = payload.get("fixture_version")
    fixture_provenance = payload.get("fixture_provenance")
    _required_text(fixture_version, "fixture_version")
    _required_text(fixture_provenance, "fixture_provenance")

    case_records = payload.get("cases")
    if not isinstance(case_records, list):
        raise ReplayValidationError("fixture cases must be a list")

    cases: list[ReplayCase] = []
    seen_case_ids: set[str] = set()
    for index, record in enumerate(case_records):
        case = _parse_case(record, fixture_version, fixture_provenance, index)
        if case.case_id in seen_case_ids:
            raise ReplayValidationError(f"duplicate case id: {case.case_id}")
        seen_case_ids.add(case.case_id)
        cases.append(case)

    return tuple(cases)
