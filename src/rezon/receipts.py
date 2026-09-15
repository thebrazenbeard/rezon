from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureState(str, Enum):
    UNAVAILABLE = "unavailable"
    CONFLICT = "conflict"
    INVALID_SUBJECT = "invalid_subject"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    RESOURCE_LIMIT = "resource_limit"
    ATTEMPTED_UNKNOWN = "attempted_unknown"
    CONTRACT_VIOLATION = "contract_violation"


class EffectState(str, Enum):
    PLAN = "plan"
    SOURCE_CREATED = "source_created"
    SOURCE_VERIFIED = "source_verified"
    REVIEWED = "reviewed"
    DELIVERED = "delivered"
    INSTALLED = "installed"
    ACTIVE = "active"
    EFFECT_OBSERVED = "effect_observed"
    QUALIFIED = "qualified"
    CLOSED = "closed"


class AdmissionStatus(str, Enum):
    RETRIEVED_ONLY = "retrieved_only"
    ADMITTED = "admitted"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class IndependenceMetadata:
    executor_id: str | None = None
    model_id: str | None = None
    provider_id: str | None = None
    prompt_lineage: str | None = None
    context_lineage: str | None = None
    saw_other_answer: bool | None = None
    common_evidence_refs: tuple[str, ...] = ()
    independence_basis_refs: tuple[str, ...] = ()

    @property
    def is_demonstrably_independent(self) -> bool:
        return bool(
            self.independence_basis_refs
            and self.saw_other_answer is False
            and not self.common_evidence_refs
            and self.executor_id
            and self.prompt_lineage
            and self.context_lineage
        )


@dataclass(frozen=True)
class RetrievalReceipt:
    retrieval_id: str
    query: str
    source_id: str
    source_version: str | None
    method: str
    returned_refs: tuple[str, ...] = ()
    admission_status: AdmissionStatus = AdmissionStatus.RETRIEVED_ONLY

    def __post_init__(self) -> None:
        if not self.retrieval_id or not self.query or not self.source_id or not self.method:
            raise ValueError("retrieval identity, query, source, and method are required")


@dataclass(frozen=True)
class ResultReceipt:
    task_id: str
    episode_version: str
    accepted_claim_ids: tuple[str, ...] = ()
    rejected_claim_ids: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    failures: tuple[FailureState, ...] = ()
    effect_state: EffectState = EffectState.PLAN
    source_versions: tuple[str, ...] = ()
    execution_ids: tuple[str, ...] = ()
