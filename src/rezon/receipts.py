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


_TRUSTED_INDEPENDENCE_BASIS_PREFIXES = ("policy:", "receipt:", "review:", "runtime:")


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
        """Whether the claim is complete enough to be externally verified.

        Prefix shape is only a claim-format check. The runner does not trust it by
        itself; independence-required execution also needs a matching external
        IndependenceVerificationPolicy.
        """
        basis_well_formed = bool(self.independence_basis_refs) and all(
            ref.startswith(_TRUSTED_INDEPENDENCE_BASIS_PREFIXES)
            for ref in self.independence_basis_refs
        )
        return bool(
            basis_well_formed
            and self.saw_other_answer is False
            and not self.common_evidence_refs
            and self.executor_id
            and self.model_id
            and self.provider_id
            and self.prompt_lineage
            and self.context_lineage
        )

    def demonstrably_independent_from(self, other: "IndependenceMetadata") -> bool:
        if not self.is_demonstrably_independent or not other.is_demonstrably_independent:
            return False
        if self.executor_id == other.executor_id:
            return False
        if (self.model_id, self.provider_id) == (other.model_id, other.provider_id):
            return False
        if self.prompt_lineage == other.prompt_lineage:
            return False
        if self.context_lineage == other.context_lineage:
            return False
        if set(self.common_evidence_refs) & set(other.common_evidence_refs):
            return False
        return True


@dataclass(frozen=True)
class IndependenceVerificationEvidence:
    basis_ref: str
    executor_id: str
    model_id: str
    provider_id: str
    prompt_lineage: str
    context_lineage: str
    verification_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((
            self.basis_ref,
            self.executor_id,
            self.model_id,
            self.provider_id,
            self.prompt_lineage,
            self.context_lineage,
            self.verification_refs,
        )):
            raise ValueError("independence verification evidence must be complete")
        if not self.basis_ref.startswith(_TRUSTED_INDEPENDENCE_BASIS_PREFIXES):
            raise ValueError("independence verification basis must use a governed namespace")


@dataclass(frozen=True)
class IndependenceVerificationPolicy:
    verified_evidence: tuple[IndependenceVerificationEvidence, ...]

    def verify(self, metadata: IndependenceMetadata) -> bool:
        if not metadata.is_demonstrably_independent:
            return False
        claimed_basis = set(metadata.independence_basis_refs)
        for evidence in self.verified_evidence:
            if evidence.basis_ref not in claimed_basis:
                continue
            if (
                evidence.executor_id,
                evidence.model_id,
                evidence.provider_id,
                evidence.prompt_lineage,
                evidence.context_lineage,
            ) == (
                metadata.executor_id,
                metadata.model_id,
                metadata.provider_id,
                metadata.prompt_lineage,
                metadata.context_lineage,
            ):
                return True
        return False


@dataclass(frozen=True)
class RetrievalReceipt:
    retrieval_id: str
    query: str
    source_id: str
    source_version: str | None
    method: str
    returned_refs: tuple[str, ...] = ()
    admission_status: AdmissionStatus = AdmissionStatus.RETRIEVED_ONLY
    admission_authority_ref: str | None = None
    verification_refs: tuple[str, ...] = ()
    currentness_ref: str | None = None
    authoritative_scope: str | None = None

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
    task_envelope_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.task_id or not self.episode_version:
            raise ValueError("result receipt requires exact task_id and episode_version")
        overlap = set(self.accepted_claim_ids) & set(self.rejected_claim_ids)
        if overlap:
            raise ValueError(f"claims cannot be both accepted and rejected: {sorted(overlap)}")
        if self.effect_state is not EffectState.PLAN:
            raise ValueError(
                "ResultReceipt is a reasoning-result artifact and cannot self-promote lifecycle/effect state; use separate governed transition evidence"
            )
