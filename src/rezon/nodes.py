from __future__ import annotations

from dataclasses import dataclass

from .envelopes import TaskEnvelope
from .epistemics import Hyperrelation, Proposition, PropositionKind
from .receipts import FailureState, IndependenceMetadata


@dataclass(frozen=True)
class NodeDescriptor:
    node_id: str
    permitted_output_kinds: tuple[PropositionKind, ...]
    accepted_input_kinds: tuple[PropositionKind, ...] = ()
    mandatory_verification: bool = False
    independence_required: bool = False
    required_authority: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")


@dataclass(frozen=True)
class ExecutionView:
    execution_id: str
    episode_version: str
    propositions: tuple[Proposition, ...]
    relations: tuple[Hyperrelation, ...]
    blinded_proposition_ids: tuple[str, ...] = ()
    blinded_relation_ids: tuple[str, ...] = ()
    independence: IndependenceMetadata = IndependenceMetadata()
    task_envelope: TaskEnvelope | None = None


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    node_id: str
    emitted_propositions: tuple[Proposition, ...] = ()
    emitted_relations: tuple[Hyperrelation, ...] = ()
    failures: tuple[FailureState, ...] = ()
    source_refs: tuple[str, ...] = ()
    source_versions: tuple[str, ...] = ()
