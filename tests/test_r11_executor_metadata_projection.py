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


def test_strong_independence_hides_task_derived_execution_id_and_audit_metadata():
    class MetadataProbe:
        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        "h-r11-metadata-leak",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        (
                            f"{view.execution_id}|"
                            f"{view.independence.prompt_lineage}|"
                            f"{view.independence.context_lineage}"
                        ),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    metadata = IndependenceMetadata(
        executor_id="exec-r11-hostile",
        model_id="model-r11-hostile",
        provider_id="provider-r11-hostile",
        prompt_lineage="peer-answer:H5",
        context_lineage="peer-answer:H6",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r11-metadata",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r11-metadata",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r11-metadata",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    envelope = TaskEnvelope(
        task_id="peer-answer:H4",
        literal_request="generate independent hypothesis",
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=MetadataProbe(),
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
    admitted = {
        proposition.proposition_id: proposition.content
        for proposition in episode.snapshot().current_propositions
    }
    leaked = admitted["h-r11-metadata-leak"]
    assert "peer-answer:H4" not in leaked
    assert "peer-answer:H5" not in leaked
    assert "peer-answer:H6" not in leaked
