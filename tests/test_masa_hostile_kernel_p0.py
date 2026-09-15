import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.executors import EchoHypothesisExecutor
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    AdmissionStatus,
    EffectState,
    FailureState,
    IndependenceMetadata,
    ResultReceipt,
    RetrievalReceipt,
)
from rezon.retrieval import RetrievalAdmissionError, admit_retrieval_as_evidence
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.scheduler import Budget, DeterministicScheduler, ScheduleAction
from rezon.visibility import VisibilityPolicy


def _p(pid, kind, content=None, producer=None, confidence=None):
    return Proposition(
        pid,
        "e1",
        kind,
        content or pid,
        producer_execution_id=producer,
        confidence=confidence,
    )


def test_correlated_workers_cannot_self_certify_independence():
    a = IndependenceMetadata(
        executor_id="worker-a",
        model_id="same-model",
        provider_id="same-provider",
        prompt_lineage="shared-prompt",
        context_lineage="shared-context",
        saw_other_answer=False,
        independence_basis_refs=("self:asserted-a",),
    )
    b = IndependenceMetadata(
        executor_id="worker-b",
        model_id="same-model",
        provider_id="same-provider",
        prompt_lineage="shared-prompt",
        context_lineage="shared-context",
        saw_other_answer=False,
        independence_basis_refs=("self:asserted-b",),
    )
    assert not (a.is_demonstrably_independent and b.is_demonstrably_independent)


def test_independence_required_node_fails_closed_without_demonstrated_independence():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION, "machine stopped"))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=EchoHypothesisExecutor(),
        visibility=VisibilityPolicy(),
        independence=IndependenceMetadata(),
    )
    outcome = EpisodeRunner((node,), budget_limit=2).run(ep, task_id="t-independent")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert outcome.trace.records == ()


def test_runner_rejects_forged_execution_identity_and_provenance():
    class ForgingExecutor:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            forged = Proposition(
                proposition_id="forged-hypothesis",
                episode_id=episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="forged",
                producer_execution_id="forged-execution-id",
            )
            return ExecutionResult(
                execution_id="forged-execution-id",
                node_id=self.node_id,
                emitted_propositions=(forged,),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION, "machine stopped"))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=ForgingExecutor(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-forge")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "forged-hypothesis" not in {p.proposition_id for p in ep.snapshot().current_propositions}


def test_model_output_cannot_be_admitted_as_evidence_without_external_support():
    ep = Episode("e1")
    descriptor = NodeDescriptor("model", (PropositionKind.EVIDENCE,))
    result = ExecutionResult(
        execution_id="x1",
        node_id="model",
        emitted_propositions=(
            Proposition(
                proposition_id="ev-model",
                episode_id="e1",
                kind=PropositionKind.EVIDENCE,
                content="model says this is evidence",
                producer_execution_id="x1",
            ),
        ),
    )
    with pytest.raises(AdmissionError):
        admit_execution_result(ep, descriptor, result)


def test_retrieval_receipt_cannot_self_promote_unverified_material_to_evidence():
    ep = Episode("e1")
    forged = RetrievalReceipt(
        retrieval_id="ret-forged",
        query="current policy",
        source_id="repo:policy",
        source_version="stale-v1",
        method="semantic_search",
        returned_refs=("hit:1",),
        admission_status=AdmissionStatus.ADMITTED,
    )
    with pytest.raises(RetrievalAdmissionError):
        admit_retrieval_as_evidence(ep, forged, "ev1", "forged admission")


def test_result_receipt_rejects_same_claim_as_accepted_and_rejected():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t1",
            episode_version="e1@1",
            accepted_claim_ids=("p1",),
            rejected_claim_ids=("p1",),
        )


def test_result_receipt_cannot_claim_qualified_with_unresolved_failure():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t1",
            episode_version="e1@1",
            unresolved=("verification:missing",),
            failures=(FailureState.INSUFFICIENT_EVIDENCE,),
            effect_state=EffectState.QUALIFIED,
        )


def test_worker_exception_becomes_typed_receipt_instead_of_aborting_run():
    class CrashingExecutor:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            raise RuntimeError("worker crashed")

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION, "machine stopped"))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=CrashingExecutor(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=2).run(ep, task_id="t-crash")
    assert FailureState.ATTEMPTED_UNKNOWN in outcome.receipt.failures
    assert outcome.receipt.unresolved


def test_retracted_proposition_cannot_leave_current_contradiction_that_drives_scheduler():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM, "A"))
    ep.add_proposition(_p("b", PropositionKind.CLAIM, "not A"))
    ep.add_relation(
        Hyperrelation(
            "r1",
            "e1",
            "contradicts",
            (Participant("a", "left"), Participant("b", "right")),
        )
    )
    ep.retract_proposition("a", "superseded")
    nodes = (NodeDescriptor("contradiction_scanner", (PropositionKind.TEST_RESULT,)),)
    decision = DeterministicScheduler().next(ep.snapshot(), nodes, (), Budget(2, 0))
    assert decision.action is ScheduleAction.TERMINATE
    assert decision.reason == "no_applicable_rule"
