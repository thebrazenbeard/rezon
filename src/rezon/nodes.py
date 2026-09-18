from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .envelopes import TaskEnvelope, TaskSpecification
from .epistemics import Hyperrelation, Proposition, PropositionKind
from .receipts import FailureState, IndependenceMetadata


class VerificationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


_DEFAULT_INDEPENDENCE_BLIND_KINDS = (
    PropositionKind.HYPOTHESIS,
    PropositionKind.CLAIM,
    PropositionKind.DECISION,
)


@dataclass(frozen=True)
class NodeDescriptor:
    node_id: str
    permitted_output_kinds: tuple[PropositionKind, ...]
    accepted_input_kinds: tuple[PropositionKind, ...] = ()
    mandatory_verification: bool = False
    independence_required: bool = False
    required_authority: tuple[str, ...] = ()
    permitted_relation_types: tuple[str, ...] = ()
    verification_target_ids: tuple[str, ...] = ()
    independence_blind_kinds: tuple[PropositionKind, ...] = _DEFAULT_INDEPENDENCE_BLIND_KINDS
    independence_blind_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        if any(not relation_type for relation_type in self.permitted_relation_types):
            raise ValueError("permitted relation types must be non-empty")
        if self.mandatory_verification and not self.verification_target_ids:
            raise ValueError("mandatory verification requires explicit target IDs")
        if any(not target_id for target_id in self.verification_target_ids):
            raise ValueError("verification target IDs must be non-empty")
        if any(not proposition_id for proposition_id in self.independence_blind_ids):
            raise ValueError("independence blind IDs must be non-empty")


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
    task_specification: TaskSpecification | None = None


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    node_id: str
    emitted_propositions: tuple[Proposition, ...] = ()
    emitted_relations: tuple[Hyperrelation, ...] = ()
    failures: tuple[FailureState, ...] = ()
    source_refs: tuple[str, ...] = ()
    source_versions: tuple[str, ...] = ()
    verification_status: VerificationStatus | None = None
    verification_target_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.verification_status is not None and not self.verification_target_ids:
            raise ValueError("verification status requires explicit target IDs")
