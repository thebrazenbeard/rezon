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
_TRUSTED_DISPOSITION_AUTHORITY_PREFIXES = ("policy:", "receipt:", "review:", "runtime:")


@dataclass(frozen=True)
class IndependenceMetadata:
    executor_id: str | None = None
    model_id: str | None = None
    provider_id: str | None = None
    prompt_lineage: str | None = None
    context_lineage: str | None = None
    saw_other_answer: bool | None = None
    common_evidence_refs: tuple[str, ...] = ()
    consumed_evidence_refs: tuple[str, ...] = ()
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
        if self.model_id == other.model_id:
            return False
        if self.provider_id == other.provider_id:
            return False
        if self.prompt_lineage == other.prompt_lineage:
            return False
        if self.context_lineage == other.context_lineage:
            return False
        if set(self.common_evidence_refs) & set(other.common_evidence_refs):
            return False
        if set(self.consumed_evidence_refs) & set(other.consumed_evidence_refs):
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
    saw_other_answer: bool | None = None
    common_evidence_refs: tuple[str, ...] | None = None
    consumed_evidence_refs: tuple[str, ...] | None = None

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
        if any(not ref for ref in self.verification_refs):
            raise ValueError("independence verification refs must be non-empty")
        for refs in (self.common_evidence_refs, self.consumed_evidence_refs):
            if refs is not None and any(not ref for ref in refs):
                raise ValueError("independence evidence refs must be non-empty")


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
            ) != (
                metadata.executor_id,
                metadata.model_id,
                metadata.provider_id,
                metadata.prompt_lineage,
                metadata.context_lineage,
            ):
                continue
            if evidence.saw_other_answer is not metadata.saw_other_answer:
                continue
            if evidence.saw_other_answer is not False:
                continue
            if evidence.common_evidence_refs is None:
                continue
            if tuple(evidence.common_evidence_refs) != tuple(metadata.common_evidence_refs):
                continue
            if evidence.consumed_evidence_refs is None:
                continue
            if tuple(evidence.consumed_evidence_refs) != tuple(metadata.consumed_evidence_refs):
                continue
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
class ClaimDispositionEvidence:
    disposition_id: str
    task_id: str
    episode_version: str
    issuer_execution_id: str
    accepted_claim_ids: tuple[str, ...]
    rejected_claim_ids: tuple[str, ...]
    authority_ref: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((
            self.disposition_id,
            self.task_id,
            self.episode_version,
            self.issuer_execution_id,
            self.authority_ref,
            self.evidence_refs,
        )):
            raise ValueError("claim disposition evidence must be complete")
        if not self.authority_ref.startswith(_TRUSTED_DISPOSITION_AUTHORITY_PREFIXES):
            raise ValueError("claim disposition authority must use a governed namespace")
        if any(not claim_id for claim_id in self.accepted_claim_ids):
            raise ValueError("accepted claim IDs must be non-empty")
        if any(not claim_id for claim_id in self.rejected_claim_ids):
            raise ValueError("rejected claim IDs must be non-empty")
        if any(not ref for ref in self.evidence_refs):
            raise ValueError("claim disposition evidence refs must be non-empty")
        if len(self.accepted_claim_ids) != len(set(self.accepted_claim_ids)):
            raise ValueError("accepted claim IDs must be unique")
        if len(self.rejected_claim_ids) != len(set(self.rejected_claim_ids)):
            raise ValueError("rejected claim IDs must be unique")
        overlap = set(self.accepted_claim_ids) & set(self.rejected_claim_ids)
        if overlap:
            raise ValueError(
                f"disposition evidence cannot accept and reject the same claim: {sorted(overlap)}"
            )


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
    claim_disposition_complete: bool = True
    claim_disposition_evidence: ClaimDispositionEvidence | None = None

    def __post_init__(self) -> None:
        if not self.task_id or not self.episode_version:
            raise ValueError("result receipt requires exact task_id and episode_version")
        overlap = set(self.accepted_claim_ids) & set(self.rejected_claim_ids)
        if overlap:
            raise ValueError(f"claims cannot be both accepted and rejected: {sorted(overlap)}")
        unresolved_claims = tuple(
            item
            for item in self.unresolved
            if item.startswith("claim_disposition:")
        )
        if self.claim_disposition_complete and unresolved_claims:
            raise ValueError(
                "claim_disposition_complete cannot coexist with unresolved claim disposition"
            )

        has_disposition = bool(self.accepted_claim_ids or self.rejected_claim_ids)
        evidence = self.claim_disposition_evidence
        if has_disposition and evidence is None:
            raise ValueError(
                "accepted/rejected claim disposition requires governed disposition evidence"
            )
        if evidence is not None:
            if evidence.task_id != self.task_id:
                raise ValueError("claim disposition evidence task_id does not match receipt")
            if evidence.episode_version != self.episode_version:
                raise ValueError(
                    "claim disposition evidence episode_version does not match receipt"
                )
            if evidence.issuer_execution_id not in self.execution_ids:
                raise ValueError(
                    "claim disposition evidence issuer must be a receipt execution"
                )
            if evidence.accepted_claim_ids != self.accepted_claim_ids:
                raise ValueError(
                    "accepted claim IDs must exactly match disposition evidence"
                )
            if evidence.rejected_claim_ids != self.rejected_claim_ids:
                raise ValueError(
                    "rejected claim IDs must exactly match disposition evidence"
                )
        if self.effect_state is not EffectState.PLAN:
            raise ValueError(
                "ResultReceipt is non-promotional and may report PLAN only; "
                "higher lifecycle/effect states require a separately governed transition artifact"
            )
