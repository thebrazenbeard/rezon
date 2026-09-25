import pytest

from rezon.episode import Episode
from rezon.receipts import AdmissionStatus, RetrievalReceipt
from rezon.retrieval import (
    RetrievalAdmissionError,
    RetrievalAdmissionEvidence,
    RetrievalAdmissionPolicy,
    admit_retrieval_as_evidence,
    digest_retrieved_content,
)


CONTENT = "policy says X"
LOCATOR = "policy.md#10"
SCOPE = "policy/current"


def _attempt(source_id, source_version):
    episode = Episode("e1")
    receipt = RetrievalReceipt(
        retrieval_id="ret1",
        query="policy",
        source_id=source_id,
        source_version=source_version,
        method="exact_ref",
        returned_refs=(LOCATOR,),
        admission_status=AdmissionStatus.ADMITTED,
    )
    evidence = RetrievalAdmissionEvidence(
        source_id=source_id,
        source_version=source_version,
        admission_authority_ref="review:admission-1",
        verification_refs=("receipt:digest-verified",),
        currentness_ref="receipt:current-head",
        authoritative_scope=SCOPE,
        content_digest=digest_retrieved_content(CONTENT),
        locator_refs=(LOCATOR,),
    )
    before = episode.snapshot()
    with pytest.raises(RetrievalAdmissionError):
        admit_retrieval_as_evidence(
            episode,
            receipt,
            "ev1",
            CONTENT,
            policy=RetrievalAdmissionPolicy((evidence,)),
            required_scope=SCOPE,
        )
    assert episode.snapshot() == before


def test_source_id_cannot_contain_source_version_binding_separator():
    _attempt("repo:a@b", "c")


def test_source_version_cannot_contain_source_version_binding_separator():
    _attempt("repo:a", "b@c")
