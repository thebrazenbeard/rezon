import pytest

from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.executors import ContradictionScannerExecutor, EchoHypothesisExecutor, FalsifierExecutor
from rezon.nodes import ExecutionView
from rezon.receipts import AdmissionStatus, IndependenceMetadata, RetrievalReceipt
from rezon.retrieval import RetrievalAdmissionError, admit_retrieval_as_evidence


def _view(props=(), relations=(), execution_id="x1"):
    return ExecutionView(
        execution_id=execution_id,
        episode_version="e1@1",
        propositions=tuple(props),
        relations=tuple(relations),
        independence=IndependenceMetadata(),
    )


def test_retrieved_only_material_cannot_become_evidence():
    ep = Episode("e1")
    receipt = RetrievalReceipt(
        "ret1", "policy", "repo:policy", "abc123", "exact_ref", ("policy.md#10",), AdmissionStatus.RETRIEVED_ONLY
    )
    with pytest.raises(RetrievalAdmissionError):
        admit_retrieval_as_evidence(ep, receipt, "ev1", "policy says X")
    assert ep.snapshot().current_propositions == ()


def test_admitted_versioned_retrieval_can_create_evidence_with_provenance():
    ep = Episode("e1")
    receipt = RetrievalReceipt(
        "ret1", "policy", "repo:policy", "abc123", "exact_ref", ("policy.md#10",), AdmissionStatus.ADMITTED
    )
    evidence = admit_retrieval_as_evidence(ep, receipt, "ev1", "policy says X")
    assert evidence.kind is PropositionKind.EVIDENCE
    assert evidence.source_refs == ("repo:policy@abc123", "policy.md#10", "retrieval:ret1")


def test_unversioned_retrieval_fails_closed_even_if_marked_admitted():
    ep = Episode("e1")
    receipt = RetrievalReceipt(
        "ret1", "policy", "repo:policy", None, "semantic_search", ("hit:1",), AdmissionStatus.ADMITTED
    )
    with pytest.raises(RetrievalAdmissionError):
        admit_retrieval_as_evidence(ep, receipt, "ev1", "maybe current")


def test_echo_generator_emits_hypothesis_not_evidence():
    obs = Proposition("o1", "e1", PropositionKind.OBSERVATION, "machine stopped")
    result = EchoHypothesisExecutor().execute(_view((obs,), execution_id="xg"), "e1")
    assert len(result.emitted_propositions) == 1
    emitted = result.emitted_propositions[0]
    assert emitted.kind is PropositionKind.HYPOTHESIS
    assert emitted.producer_execution_id == "xg"
    assert emitted.source_refs == ("o1",)


def test_contradiction_scanner_reports_only_explicit_contradiction_relations():
    a = Proposition("a", "e1", PropositionKind.CLAIM, "A")
    b = Proposition("b", "e1", PropositionKind.CLAIM, "not A")
    relation = Hyperrelation(
        "r1", "e1", "contradicts", (Participant("a", "left"), Participant("b", "right"))
    )
    result = ContradictionScannerExecutor().execute(_view((a, b), (relation,), "xc"), "e1")
    assert result.emitted_propositions[0].kind is PropositionKind.TEST_RESULT
    assert result.emitted_propositions[0].source_refs == ("r1",)


def test_falsifier_requires_explicit_contradictory_test_result():
    h = Proposition("h1", "e1", PropositionKind.HYPOTHESIS, "motor is healthy")
    test_result = Proposition("t1", "e1", PropositionKind.TEST_RESULT, "motor winding is open")
    relation = Hyperrelation(
        "r1", "e1", "contradicts", (Participant("t1", "result"), Participant("h1", "target"))
    )
    no_relation = FalsifierExecutor("h1").execute(_view((h, test_result), execution_id="xf0"), "e1")
    assert no_relation.emitted_propositions == ()
    with_relation = FalsifierExecutor("h1").execute(_view((h, test_result), (relation,), "xf1"), "e1")
    assert with_relation.emitted_propositions[0].kind is PropositionKind.CLAIM
    assert with_relation.emitted_propositions[0].source_refs == ("t1", "r1")
