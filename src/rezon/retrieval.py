from __future__ import annotations

from .episode import Episode
from .epistemics import Proposition, PropositionKind
from .receipts import AdmissionStatus, RetrievalReceipt


class RetrievalAdmissionError(ValueError):
    pass


def admit_retrieval_as_evidence(
    episode: Episode, receipt: RetrievalReceipt, proposition_id: str, content: str
) -> Proposition:
    if receipt.admission_status is not AdmissionStatus.ADMITTED:
        raise RetrievalAdmissionError("retrieved material has not been admitted as evidence")
    if not receipt.source_version:
        raise RetrievalAdmissionError("admitted evidence requires an exact source version")
    evidence = Proposition(
        proposition_id=proposition_id,
        episode_id=episode.episode_id,
        kind=PropositionKind.EVIDENCE,
        content=content,
        source_refs=(
            f"{receipt.source_id}@{receipt.source_version}",
            *receipt.returned_refs,
            f"retrieval:{receipt.retrieval_id}",
        ),
    )
    episode.add_proposition(evidence)
    return evidence
