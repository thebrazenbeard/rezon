"""Archived retrieval concept recovery: lexical hits are NOT admitted evidence."""
import pytest

from rezon.candidate_retrieval import CandidateDocument, search_untrusted_candidates
from rezon.episode import Episode
from rezon.receipts import AdmissionStatus
from rezon.retrieval import RetrievalAdmissionError, admit_retrieval_as_evidence


def _docs():
    return (
        CandidateDocument("file:beta", "semantic retrieval can help rank candidates"),
        CandidateDocument("file:alpha", "retrieval receipts preserve exact provenance"),
        CandidateDocument("file:gamma", "neural models can be evaluated"),
    )


def test_deterministic_ranked_candidates_do_not_claim_authority():
    a = search_untrusted_candidates(
        "retrieval provenance", source_id="repo:public", source_version="sha123",
        documents=_docs(), max_results=2,
    )
    b = search_untrusted_candidates(
        "retrieval provenance", source_id="repo:public", source_version="sha123",
        documents=_docs(), max_results=2,
    )
    assert a == b
    assert a.returned_refs == ("file:alpha", "file:beta")
    assert a.admission_status is AdmissionStatus.RETRIEVED_ONLY
    assert a.verification_refs == ()
    assert a.admission_authority_ref is None
    assert a.currentness_ref is None
    assert a.authoritative_scope is None


def test_retrieved_only_receipt_cannot_be_promoted_by_itself():
    receipt = search_untrusted_candidates(
        "retrieval provenance", source_id="repo:public", source_version="sha123",
        documents=_docs(),
    )
    episode = Episode("session1")
    with pytest.raises(RetrievalAdmissionError):
        admit_retrieval_as_evidence(
            episode, receipt, "e1", "retrieval receipts preserve exact provenance"
        )
    assert episode.snapshot().current_propositions == ()


def test_candidate_content_change_changes_receipt_identity():
    first = search_untrusted_candidates(
        "retrieval", source_id="repo", source_version="same",
        documents=(CandidateDocument("file:a", "retrieval first revision"),),
    )
    changed = search_untrusted_candidates(
        "retrieval", source_id="repo", source_version="same",
        documents=(CandidateDocument("file:a", "retrieval second revision"),),
    )
    assert first.returned_refs == changed.returned_refs
    assert first.retrieval_id != changed.retrieval_id


def test_no_match_yields_empty_unadmitted_receipt():
    receipt = search_untrusted_candidates(
        "orbital", source_id="repo:public", source_version="sha123",
        documents=_docs(),
    )
    assert receipt.returned_refs == ()
    assert receipt.admission_status is AdmissionStatus.RETRIEVED_ONLY


def test_duplicate_reference_and_str_subclass_fail_closed():
    with pytest.raises(ValueError, match="duplicate"):
        search_untrusted_candidates(
            "test", source_id="repo", source_version="s",
            documents=(CandidateDocument("ref", "test"),
                       CandidateDocument("ref", "other")),
        )

    class TrickyStr(str):
        def __eq__(self, other):
            return True

    with pytest.raises((TypeError, ValueError)):
        CandidateDocument(TrickyStr("ref"), "text")
    with pytest.raises((TypeError, ValueError)):
        search_untrusted_candidates(
            "test", source_id=TrickyStr("repo"), source_version="s",
            documents=_docs(),
        )


def test_resource_bounds_and_untrusted_collections():
    with pytest.raises(ValueError, match="max_results"):
        search_untrusted_candidates(
            "test", source_id="repo", source_version="s",
            documents=_docs(), max_results=0,
        )
    with pytest.raises((TypeError, ValueError)):
        search_untrusted_candidates(
            "test", source_id="repo", source_version="s",
            documents=list(_docs()), max_results=1,
        )
    with pytest.raises(ValueError, match="too long"):
        CandidateDocument("ref", "A" * 16385)
    with pytest.raises(ValueError, match="too long"):
        search_untrusted_candidates(
            "Q" * 4097, source_id="repo", source_version="s",
            documents=_docs(),
        )


def test_no_network_disk_model_or_authority_side_effects(tmp_path):
    receipt = search_untrusted_candidates(
        "retrieval", source_id="repo", source_version="pinned",
        documents=(CandidateDocument("a", "retrieval"),),
    )
    assert receipt.source_version == "pinned"
    assert not list(tmp_path.iterdir())
