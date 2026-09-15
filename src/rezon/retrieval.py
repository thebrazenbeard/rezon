from __future__ import annotations

from dataclasses import dataclass

from .episode import Episode
from .epistemics import Proposition, PropositionKind
from .receipts import AdmissionStatus, RetrievalReceipt


class RetrievalAdmissionError(ValueError):
    pass


@dataclass(frozen=True)
class RetrievalAdmissionEvidence:
    source_id: str
    source_version: str
    admission_authority_ref: str
    verification_refs: tuple[str, ...]
    currentness_ref: str
    authoritative_scope: str

    def __post_init__(self) -> None:
        if not all((
            self.source_id,
            self.source_version,
            self.admission_authority_ref,
            self.verification_refs,
            self.currentness_ref,
            self.authoritative_scope,
        )):
            raise ValueError("retrieval admission evidence must be complete")


@dataclass(frozen=True)
class RetrievalAdmissionPolicy:
    verified_admissions: tuple[RetrievalAdmissionEvidence, ...]

    def verify(self, receipt: RetrievalReceipt) -> RetrievalAdmissionEvidence | None:
        for evidence in self.verified_admissions:
            if (evidence.source_id, evidence.source_version) == (receipt.source_id, receipt.source_version):
                return evidence
        return None


def admit_retrieval_as_evidence(
    episode: Episode,
    receipt: RetrievalReceipt,
    proposition_id: str,
    content: str,
    *,
    policy: RetrievalAdmissionPolicy | None = None,
) -> Proposition:
    if receipt.admission_status is not AdmissionStatus.ADMITTED:
        raise RetrievalAdmissionError("retrieved material has not been admitted as evidence")
    if not receipt.source_version:
        raise RetrievalAdmissionError("admitted evidence requires an exact source version")
    if policy is None:
        raise RetrievalAdmissionError("retrieval admission requires an external admission policy")
    verified = policy.verify(receipt)
    if verified is None:
        raise RetrievalAdmissionError("retrieval source/version lacks independent admission evidence")
    evidence = Proposition(
        proposition_id=proposition_id,
        episode_id=episode.episode_id,
        kind=PropositionKind.EVIDENCE,
        content=content,
        source_refs=(
            f"{receipt.source_id}@{receipt.source_version}",
            *receipt.returned_refs,
            f"retrieval:{receipt.retrieval_id}",
            f"admission:{verified.admission_authority_ref}",
            f"currentness:{verified.currentness_ref}",
            *verified.verification_refs,
        ),
    )
    episode.add_proposition(evidence)
    return evidence
