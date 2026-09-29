from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def test_independence_required_worker_cannot_receive_auxiliary_context_refs():
    class EnvelopeContextReader:
        def execute(self, view, episode_id):
            leaked = view.task_envelope.context_refs[0]
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-envelope-leak",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content=f"copied:{leaked}",
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    metadata = IndependenceMetadata(
        executor_id="exec-independent",
        model_id="model-independent",
        provider_id="provider-independent",
        prompt_lineage="prompt-independent",
        context_lineage="context-independent",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r9-envelope-context",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r9-envelope-context",
            executor_id="exec-independent",
            model_id="model-independent",
            provider_id="provider-independent",
            prompt_lineage="prompt-independent",
            context_lineage="context-independent",
            verification_refs=("review:r9-envelope-context",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    envelope = TaskEnvelope(
        task_id="t-r9-envelope-context",
        literal_request="generate an independent hypothesis",
        context_refs=("peer-answer:H1",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=EnvelopeContextReader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )
    episode = Episode("e1")

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert outcome.trace.records
    assert outcome.trace.records[0].independence_demonstrated is False
    assert (
        outcome.trace.records[0].executor_task_specification_digest
        == envelope.to_task_specification().digest
    )
    assert "h-envelope-leak" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_independence_required_worker_can_receive_task_spec_without_context_refs():
    class TaskSpecReader:
        def execute(self, view, episode_id):
            envelope = view.task_specification
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-task-spec",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content=(
                            f"{envelope.literal_request}|"
                            f"{envelope.subject_refs[0]}|"
                            f"{envelope.constraints[0]}"
                        ),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    metadata = IndependenceMetadata(
        executor_id="exec-task-spec",
        model_id="model-task-spec",
        provider_id="provider-task-spec",
        prompt_lineage="prompt-task-spec",
        context_lineage="context-task-spec",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r9-task-spec",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r9-task-spec",
            executor_id="exec-task-spec",
            model_id="model-task-spec",
            provider_id="provider-task-spec",
            prompt_lineage="prompt-task-spec",
            context_lineage="context-task-spec",
            verification_refs=("review:r9-task-spec",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    envelope = TaskEnvelope(
        task_id="t-r9-task-spec",
        literal_request="generate a bounded independent hypothesis",
        subject_refs=("subject:1",),
        constraints=("must-be-bounded",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=TaskSpecReader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )
    episode = Episode("e1")

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    assert outcome.receipt.failures == ()
    assert outcome.trace.records
    assert outcome.trace.records[0].independence_demonstrated is True
    admitted = {
        proposition.proposition_id: proposition.content
        for proposition in episode.snapshot().current_propositions
    }
    assert admitted["h-task-spec"] == (
        "generate a bounded independent hypothesis|subject:1|must-be-bounded"
    )
