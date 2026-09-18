from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PropositionKind(str, Enum):
    OBSERVATION = "observation"
    EVIDENCE = "evidence"
    CLAIM = "claim"
    HYPOTHESIS = "hypothesis"
    ASSUMPTION = "assumption"
    QUESTION = "question"
    PREDICTION = "prediction"
    TEST = "test"
    TEST_RESULT = "test_result"
    DECISION = "decision"


class SupportKind(str, Enum):
    DIRECT_OBSERVATION = "direct_observation"
    RETRIEVED_SOURCE = "retrieved_source"
    DETERMINISTIC_DERIVATION = "deterministic_derivation"
    MODEL_JUDGMENT = "model_judgment"
    HEURISTIC = "heuristic"


@dataclass(frozen=True)
class Proposition:
    proposition_id: str
    episode_id: str
    kind: PropositionKind
    content: str
    source_refs: tuple[str, ...] = ()
    producer_execution_id: str | None = None
    confidence: float | None = None
    source_versions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.proposition_id or not self.episode_id or not self.content:
            raise ValueError("proposition_id, episode_id, and content are required")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")
        if any(not version for version in self.source_versions):
            raise ValueError("source versions must be non-empty")
        if len(self.source_versions) != len(set(self.source_versions)):
            raise ValueError("source versions must be unique")


@dataclass(frozen=True)
class Participant:
    ref_id: str
    role: str

    def __post_init__(self) -> None:
        if not self.ref_id or not self.role:
            raise ValueError("participant ref_id and role are required")


@dataclass(frozen=True)
class Hyperrelation:
    relation_id: str
    episode_id: str
    relation_type: str
    participants: tuple[Participant, ...]
    source_refs: tuple[str, ...] = ()
    producer_execution_id: str | None = None
    source_versions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.relation_id or not self.episode_id or not self.relation_type:
            raise ValueError("relation identity and type are required")
        if not self.participants:
            raise ValueError("hyperrelation requires at least one participant")
        if any(not version for version in self.source_versions):
            raise ValueError("source versions must be non-empty")
        if len(self.source_versions) != len(set(self.source_versions)):
            raise ValueError("source versions must be unique")


@dataclass(frozen=True)
class Support:
    support_id: str
    proposition_id: str
    kind: SupportKind
    source_refs: tuple[str, ...] = ()
