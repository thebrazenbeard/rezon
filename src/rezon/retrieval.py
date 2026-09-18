from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .episode import Episode
from .epistemics import Proposition, PropositionKind
from .receipts import AdmissionStatus, RetrievalReceipt


class RetrievalAdmissionError(ValueError):
    pass


def digest_retrieved_content(content: str) -> str:
    if not content:
        raise ValueError("retrieved content cannot be empty")
    return sha256(content.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RetrievalAdmissionEvidence:
    source_id: str
    source_version: str
    admission_authority_ref: str
    verification_refs: tuple[str, ...]
    currentness_ref: str
    authoritative_scope: str
    content_digest: str | None = None
    locator_refs: tuple[str, ...] = ()

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

    def verify(
        self,
        receipt: RetrievalReceipt,
        content: str,
        required_scope: str | None,
    ) -> RetrievalAdmissionEvidence | None:
        if not required_scope:
            return None
        content_digest = digest_retrieved_content(content)
        returned_refs = set(receipt.returned_refs)
        for evidence in self.verified_admissions:
            if (evidence.source_id, evidence.source_version) != (
                receipt.source_id,
                receipt.source_version,
            ):
                continue
            if evidence.authoritative_scope != required_scope:
                continue
            if not evidence.content_digest or evidence.content_digest != content_digest:
                continue
            if not returned_refs or not returned_refs.issubset(set(evidence.locator_refs)):
                continue
            return evidence
        return None


def admit_retrieval_as_evidence(
    episode: Episode,
    receipt: RetrievalReceipt,
    proposition_id: str,
    content: str,
    *,
    policy: RetrievalAdmissionPolicy | None = None,
    required_scope: str | None = None,
) -> Proposition:
    if receipt.admission_status is not AdmissionStatus.ADMITTED:
        raise RetrievalAdmissionError("retrieved material has not been admitted as evidence")
    if not receipt.source_version:
        raise RetrievalAdmissionError("admitted evidence requires an exact source version")
    if policy is None:
        raise RetrievalAdmissionError("retrieval admission requires an external admission policy")
    if not required_scope:
        raise RetrievalAdmissionError("retrieval admission requires an explicit authoritative scope")
    verified = policy.verify(receipt, content, required_scope)
    if verified is None:
        raise RetrievalAdmissionError(
            "retrieval content/locator/source/version/scope lacks exact independent admission evidence"
        )
    evidence = Proposition(
        proposition_id=proposition_id,
        episode_id=episode.episode_id,
        kind=PropositionKind.EVIDENCE,
        content=content,
        source_refs=(
            f"{receipt.source_id}@{receipt.source_version}",
            *receipt.returned_refs,
            f"content-sha256:{verified.content_digest}",
            f"scope:{verified.authoritative_scope}",
            f"retrieval:{receipt.retrieval_id}",
            f"admission:{verified.admission_authority_ref}",
            f"currentness:{verified.currentness_ref}",
            *verified.verification_refs,
        ),
        source_versions=(f"{receipt.source_id}@{receipt.source_version}",),
    )
    episode.add_proposition(evidence)
    return evidence
