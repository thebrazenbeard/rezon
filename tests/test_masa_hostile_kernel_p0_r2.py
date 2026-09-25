import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.executors import EchoHypothesisExecutor
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest
from rezon.receipts import (
    AdmissionStatus,
    EffectState,
    FailureState,
    IndependenceMetadata,
    ResultReceipt,
    RetrievalReceipt,
)
from rezon.retrieval import (
    RetrievalAdmissionError,
    RetrievalAdmissionEvidence,
    RetrievalAdmissionPolicy,
    admit_retrieval_as_evidence,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _p(pid, kind, content=None, producer=None, source_refs=()):
    return Proposition(
        proposition_id=pid,
        episode_id="e1",
        kind=kind,
        content=content or pid,
        source_refs=tuple(source_refs),
        producer_execution_id=producer,
    )


def _trusted_retrieval_policy():
    return RetrievalAdmissionPolicy((RetrievalAdmissionEvidence(
        source_id="repo:policy",
        source_version="v2",
        admission_authority_ref="review:admission-1",
        verification_refs=("receipt:digest-verified",),
        currentness_ref="receipt:current-head",
        authoritative_scope="policy/current",
    ),))


def test_retrieval_admission_must_bind_the_actual_promoted_content():
    """One admitted source/version must not attest arbitrary caller-supplied text."""
    ep = Episode("e1")
    receipt = RetrievalReceipt(
        retrieval_id="ret1",
        query="current policy",
        source_id="repo:policy",
        source_version="v2",
        method="exact_ref",
        returned_refs=("policy.md#L10",),
        admission_status=AdmissionStatus.ADMITTED,
    )
    with pytest.raises(RetrievalAdmissionError):
        admit_retrieval_as_evidence(
            ep,
            receipt,
            "ev1",
            "fabricated text not content-bound to policy.md#L10",
            policy=_trusted_retrieval_policy(),
        )


def test_new_relation_cannot_reference_a_retracted_proposition():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM, "A"))
    ep.add_proposition(_p("b", PropositionKind.CLAIM, "not A"))
    ep.retract_proposition("a", "superseded")

    stale_relation = Hyperrelation(
        relation_id="r-after-retract",
        episode_id="e1",
        relation_type="contradicts",
        participants=(Participant("a", "left"), Participant("b", "right")),
    )
    with pytest.raises(EpisodeInvariantError):
        ep.add_relation(stale_relation)


def test_failed_execution_result_cannot_mutate_canonical_episode_state():
    ep = Episode("e1")
    descriptor = NodeDescriptor("generator", (PropositionKind.HYPOTHESIS,))
    result = ExecutionResult(
        execution_id="x1",
        node_id="generator",
        emitted_propositions=(
            _p("h-failed", PropositionKind.HYPOTHESIS, "bad partial result", producer="x1"),
        ),
        failures=(FailureState.CONTRACT_VIOLATION,),
    )
    with pytest.raises(AdmissionError):
        admit_execution_result(
            ep,
            descriptor,
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(ep.snapshot()),
            expected_execution_id="x1",
        )
    assert ep.snapshot().current_propositions == ()


def test_independence_required_cannot_claim_independence_while_peer_answer_is_visible():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION, "machine stopped"))
    ep.add_proposition(_p("h-peer", PropositionKind.HYPOTHESIS, "peer answer", producer="peer-exec"))

    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=EchoHypothesisExecutor(),
        visibility=VisibilityPolicy(),
        independence=IndependenceMetadata(
            executor_id="independent-generator",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt:fresh",
            context_lineage="context:claimed-fresh",
            saw_other_answer=False,
            independence_basis_refs=("policy:blind-peer-answer",),
        ),
    )

    outcome = EpisodeRunner((node,), budget_limit=2).run(ep, task_id="t-independent-visible")
    record = outcome.trace.records[0]
    assert (
        FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
        or "h-peer" not in record.visible_proposition_ids
        or record.independence_demonstrated is False
    )


def test_pairwise_independence_does_not_treat_unknown_provider_as_evidence_of_difference():
    a = IndependenceMetadata(
        executor_id="worker-a",
        model_id="same-model",
        provider_id=None,
        prompt_lineage="prompt:a",
        context_lineage="context:a",
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-a",),
    )
    b = IndependenceMetadata(
        executor_id="worker-b",
        model_id="same-model",
        provider_id=None,
        prompt_lineage="prompt:b",
        context_lineage="context:b",
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-b",),
    )
    assert not a.demonstrably_independent_from(b)


def test_worker_output_requires_exact_producer_execution_provenance():
    ep = Episode("e1")
    descriptor = NodeDescriptor("generator", (PropositionKind.HYPOTHESIS,))
    result = ExecutionResult(
        execution_id="x1",
        node_id="generator",
        emitted_propositions=(
            _p("h-unattributed", PropositionKind.HYPOTHESIS, "no producer id", producer=None),
        ),
    )
    with pytest.raises(AdmissionError):
        admit_execution_result(
            ep,
            descriptor,
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(ep.snapshot()),
            expected_execution_id="x1",
        )


def test_node_accepted_input_kinds_are_enforced_at_runtime():
    ep = Episode("e1")
    ep.add_proposition(_p("ev1", PropositionKind.EVIDENCE, "retrieved evidence"))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            accepted_input_kinds=(PropositionKind.OBSERVATION,),
        ),
        executor=EchoHypothesisExecutor(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=2).run(ep, task_id="t-input-contract")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert not any(p.kind is PropositionKind.HYPOTHESIS for p in ep.snapshot().current_propositions)


def test_bare_result_receipt_cannot_self_promote_to_qualified():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t1",
            episode_version="e1@0",
            effect_state=EffectState.QUALIFIED,
            execution_ids=(),
            source_versions=(),
            accepted_claim_ids=(),
        )


def test_result_receipt_exposes_source_version_used_by_execution():
    ep = Episode("e1")
    ep.add_proposition(Proposition(
        "ev1",
        "e1",
        PropositionKind.EVIDENCE,
        "policy says X",
        source_refs=("repo:policy@v2",),
        source_versions=("repo:policy@v2",),
    ))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=EchoHypothesisExecutor(),
        visibility=VisibilityPolicy(),
    )
    envelope = TaskEnvelope(task_id="t-source", literal_request="reason from current policy")
    outcome = EpisodeRunner((node,), budget_limit=2).run(
        ep,
        task_id="t-source",
        task_envelope=envelope,
    )
    assert "repo:policy@v2" in outcome.receipt.source_versions
