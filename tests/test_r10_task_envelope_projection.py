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
        executor_id="exec-r10",
        model_id="model-r10",
        provider_id="provider-r10",
        prompt_lineage="prompt-r10",
        context_lineage="context-r10",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r10-envelope-projection",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r10-envelope-projection",
            executor_id="exec-r10",
            model_id="model-r10",
            provider_id="provider-r10",
            prompt_lineage="prompt-r10",
            context_lineage="context-r10",
            verification_refs=("review:r10-envelope-projection",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    return metadata, policy


def test_strong_independence_receives_only_task_spec_projection():
    class EnvelopeInspector:
        def execute(self, view, episode_id):
            assert view.task_envelope is None
            spec = view.task_specification
            content = "|".join((
                spec.literal_request,
                ",".join(spec.subject_refs),
                ",".join(spec.constraints),
            ))
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-r10-projected",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content=content,
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    metadata, policy = _independence()
    envelope = TaskEnvelope(
        task_id="t-r10-projection",
        literal_request="generate independent hypothesis",
        subject_refs=("subject:one",),
        constraints=("bounded",),
        available_authority=("peer-answer:H2",),
        privacy_scope="peer-answer:H3",
        resource_budget=1,
        context_refs=(),
    )
    expected_projection = envelope.to_task_specification()
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=EnvelopeInspector(),
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
    admitted = {
        proposition.proposition_id: proposition.content
        for proposition in episode.snapshot().current_propositions
    }
    assert admitted["h-r10-projected"] == (
        "generate independent hypothesis|subject:one|bounded"
    )
    assert outcome.trace.records[0].task_envelope_digest == envelope.digest
    assert (
        outcome.trace.records[0].executor_task_specification_digest
        == expected_projection.digest
    )
    assert (
        outcome.trace.records[0].executor_task_specification_digest
        != envelope.digest
    )


def test_non_independent_worker_keeps_full_task_envelope():
    class EnvelopeInspector:
        def execute(self, view, episode_id):
            envelope = view.task_envelope
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-r10-shared",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content=f"{envelope.available_authority[0]}|{envelope.privacy_scope}",
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    envelope = TaskEnvelope(
        task_id="t-r10-shared",
        literal_request="ordinary shared-context work",
        available_authority=("metadata:authority",),
        privacy_scope="privacy:scope",
        resource_budget=1,
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor=EnvelopeInspector(),
        visibility=VisibilityPolicy(),
    )
    episode = Episode("e1")

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    assert outcome.receipt.failures == ()
    admitted = {
        proposition.proposition_id: proposition.content
        for proposition in episode.snapshot().current_propositions
    }
    assert admitted["h-r10-shared"] == "metadata:authority|privacy:scope"
    assert outcome.trace.records[0].task_envelope_digest == envelope.digest
    assert (
        outcome.trace.records[0].executor_task_specification_digest
        == envelope.to_task_specification().digest
    )
