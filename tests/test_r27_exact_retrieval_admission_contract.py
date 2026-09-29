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
SOURCE = "repo:policy"
VERSION = "abc123"
LOCATOR = "policy.md#10"
SCOPE = "policy/current"


class EvilStr(str):
    def __new__(cls, value, target):
        obj = str.__new__(cls, value)
        obj.target = target
        return obj

    def __eq__(self, other):
        return str(other) == self.target

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.target)


class ReceiptSubclass(RetrievalReceipt):
    pass


class EvidenceSubclass(RetrievalAdmissionEvidence):
    pass


class PolicySubclass(RetrievalAdmissionPolicy):
    def verify(self, receipt, content, required_scope):
        return _good_evidence(content)


class DuckPolicy:
    def verify(self, receipt, content, required_scope):
        return _good_evidence(content)


def _receipt(cls=RetrievalReceipt):
    return cls(
        retrieval_id="ret1",
        query="policy",
        source_id=SOURCE,
        source_version=VERSION,
        method="exact_ref",
        returned_refs=(LOCATOR,),
        admission_status=AdmissionStatus.ADMITTED,
    )


def _good_evidence(content=CONTENT, cls=RetrievalAdmissionEvidence, **changes):
    values = dict(
        source_id=SOURCE,
        source_version=VERSION,
        admission_authority_ref="review:admission-1",
        verification_refs=("receipt:digest-verified",),
        currentness_ref="receipt:current-head",
        authoritative_scope=SCOPE,
        content_digest=digest_retrieved_content(content),
        locator_refs=(LOCATOR,),
    )
    values.update(changes)
    return cls(**values)


def _reject(policy, *, receipt=None, required_scope=SCOPE):
    episode = Episode("e1")
    before = episode.snapshot()
    with pytest.raises(RetrievalAdmissionError):
        admit_retrieval_as_evidence(
            episode,
            _receipt() if receipt is None else receipt,
            "ev1",
            CONTENT,
            policy=policy,
            required_scope=required_scope,
        )
    assert episode.snapshot() == before


def test_duck_policy_cannot_self_authorize_retrieval():
    _reject(DuckPolicy())


def test_policy_subclass_cannot_override_verification_semantics():
    _reject(PolicySubclass((_good_evidence(),)))


def test_retrieval_receipt_subclass_is_rejected():
    _reject(RetrievalAdmissionPolicy((_good_evidence(),)), receipt=_receipt(ReceiptSubclass))


def test_retrieval_evidence_subclass_is_rejected():
    _reject(RetrievalAdmissionPolicy((_good_evidence(cls=EvidenceSubclass),)))


def test_policy_admissions_must_be_exact_tuple():
    _reject(RetrievalAdmissionPolicy([_good_evidence()]))


def test_forged_evidence_source_id_cannot_match_receipt():
    evidence = _good_evidence(source_id=EvilStr("forged-source", SOURCE))
    _reject(RetrievalAdmissionPolicy((evidence,)))


def test_forged_evidence_source_version_cannot_match_receipt():
    evidence = _good_evidence(source_version=EvilStr("forged-version", VERSION))
    _reject(RetrievalAdmissionPolicy((evidence,)))


def test_forged_evidence_scope_cannot_match_required_scope():
    evidence = _good_evidence(authoritative_scope=EvilStr("forged-scope", SCOPE))
    _reject(RetrievalAdmissionPolicy((evidence,)))


def test_forged_content_digest_cannot_match_actual_content_digest():
    actual = digest_retrieved_content(CONTENT)
    evidence = _good_evidence(content_digest=EvilStr("forged-digest", actual))
    _reject(RetrievalAdmissionPolicy((evidence,)))


def test_forged_evidence_locator_cannot_authorize_returned_ref():
    evidence = _good_evidence(locator_refs=(EvilStr("forged-locator", LOCATOR),))
    _reject(RetrievalAdmissionPolicy((evidence,)))


def test_required_scope_must_be_exact_string():
    _reject(
        RetrievalAdmissionPolicy((_good_evidence(),)),
        required_scope=EvilStr("forged-required-scope", SCOPE),
    )
