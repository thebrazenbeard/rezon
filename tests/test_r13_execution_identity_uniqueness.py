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


class CountingGenerator:
    def __init__(self):
        self.count = 0

    def execute(self, view, episode_id):
        self.count += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id=f"h-r13-{self.count}",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content=f"candidate-{self.count}",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _independence():
    metadata = IndependenceMetadata(
        executor_id="exec-r13",
        model_id="model-r13",
        provider_id="provider-r13",
        prompt_lineage="prompt-r13",
        context_lineage="context-r13",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r13-opaque-execution",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r13-opaque-execution",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r13-opaque-execution",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    return metadata, policy


def test_distinct_strong_independent_runs_get_distinct_opaque_execution_ids():
    metadata, policy = _independence()
    executor = CountingGenerator()
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=executor,
        visibility=VisibilityPolicy(blind_kinds=(PropositionKind.HYPOTHESIS,)),
        independence=metadata,
        independence_policy=policy,
    )
    runner = EpisodeRunner((node,), budget_limit=1)
    episode = Episode("opaque-r13")
    envelope = TaskEnvelope(
        task_id="peer-answer:must-not-appear",
        literal_request="generate an independent hypothesis",
    )

    first = runner.run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )
    second = runner.run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    assert first.receipt.failures == ()
    assert second.receipt.failures == ()
    first_id = first.trace.records[0].execution_id
    second_id = second.trace.records[0].execution_id

    assert first_id != second_id
    assert first_id.startswith("independent:exec:echo_hypothesis:")
    assert second_id.startswith("independent:exec:echo_hypothesis:")
    for execution_id in (first_id, second_id):
        assert envelope.task_id not in execution_id
        assert "opaque-r13@" not in execution_id

    current = {
        proposition.proposition_id: proposition.producer_execution_id
        for proposition in episode.snapshot().current_propositions
    }
    assert current["h-r13-1"] == first_id
    assert current["h-r13-2"] == second_id


def test_strong_independent_execution_id_is_not_task_spec_digest_reuse():
    metadata, policy = _independence()
    executor = CountingGenerator()
    envelope = TaskEnvelope(
        task_id="t-r13-digest",
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
        executor=executor,
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )
    episode = Episode("opaque-r13-digest")

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    execution_id = outcome.trace.records[0].execution_id
    task_spec_digest = envelope.to_task_specification().digest
    assert execution_id != f"independent:exec:echo_hypothesis:{task_spec_digest}"
