from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _independence():
    metadata = IndependenceMetadata(
        executor_id="exec-r11",
        model_id="model-r11",
        provider_id="provider-r11",
        prompt_lineage="prompt-r11",
        context_lineage="context-r11",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r11-task-spec",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r11-task-spec",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r11-task-spec",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    return metadata, policy


def test_strong_independence_cannot_observe_original_task_id():
    original_task_id = "peer-answer:H4"

    class TaskIdProbe:
        def execute(self, view, episode_id):
            envelope = view.task_envelope
            if envelope is not None and getattr(envelope, "task_id", None) == original_task_id:
                return ExecutionResult(
                    execution_id=view.execution_id,
                    node_id="echo_hypothesis",
                    emitted_propositions=(
                        Proposition(
                            "h-task-id-leak",
                            episode_id,
                            PropositionKind.HYPOTHESIS,
                            f"copied:{envelope.task_id}",
                            producer_execution_id=view.execution_id,
                        ),
                    ),
                )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
            )

    metadata, policy = _independence()
    envelope = TaskEnvelope(
        task_id=original_task_id,
        literal_request="generate an independent hypothesis",
        subject_refs=("subject:1",),
        constraints=("bounded",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=TaskIdProbe(),
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
    assert outcome.trace.records[0].independence_demonstrated is True
    assert "h-task-id-leak" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_strong_independence_still_receives_task_defining_specification():
    class TaskSpecProbe:
        def execute(self, view, episode_id):
            spec = getattr(view, "task_specification", None) or view.task_envelope
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        "h-task-spec",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        "|".join((
                            spec.literal_request,
                            spec.subject_refs[0],
                            spec.constraints[0],
                        )),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    metadata, policy = _independence()
    envelope = TaskEnvelope(
        task_id="t-r11-positive",
        literal_request="generate a bounded independent hypothesis",
        subject_refs=("subject:1",),
        constraints=("bounded",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=TaskSpecProbe(),
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
    assert {
        proposition.proposition_id: proposition.content
        for proposition in episode.snapshot().current_propositions
    }["h-task-spec"] == (
        "generate a bounded independent hypothesis|subject:1|bounded"
    )
