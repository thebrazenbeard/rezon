from types import SimpleNamespace

import rezon.runner as runner_module
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


class SameOutput:
    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id="h-r17",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content="same durable output",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _node():
    metadata = IndependenceMetadata(
        executor_id="exec-r17",
        model_id="model-r17",
        provider_id="provider-r17",
        prompt_lineage="prompt-r17",
        context_lineage="context-r17",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r17-task-bound",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r17-task-bound",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r17-task-bound",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    return RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=SameOutput(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )


def _run(literal_request: str):
    episode = Episode("episode-r17")
    envelope = TaskEnvelope(
        task_id="task-r17",
        literal_request=literal_request,
    )
    outcome = EpisodeRunner(
        (_node(),),
        budget_limit=1,
    ).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )
    return episode.snapshot(), outcome


def test_different_task_specifications_change_durable_producer_identity(monkeypatch):
    ids = iter(("a" * 32, "b" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    snapshot_a, outcome_a = _run("Determine whether A is true")
    snapshot_b, outcome_b = _run("Determine whether B is true")
    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert outcome_a.receipt.failures == ()
    assert outcome_b.receipt.failures == ()
    assert record_a.execution_id != record_b.execution_id
    assert (
        record_a.executor_task_specification_digest
        != record_b.executor_task_specification_digest
    )
    assert (
        record_a.canonical_episode_snapshot_digest
        == record_b.canonical_episode_snapshot_digest
    )
    assert record_a.canonical_output_digest == record_b.canonical_output_digest
    assert (
        record_a.canonical_producer_execution_id
        != record_b.canonical_producer_execution_id
    )

    assert (
        snapshot_a.current_propositions[0].producer_execution_id
        == record_a.canonical_producer_execution_id
    )
    assert (
        snapshot_b.current_propositions[0].producer_execution_id
        == record_b.canonical_producer_execution_id
    )


def test_same_task_state_and_output_replay_keeps_same_producer_identity(monkeypatch):
    ids = iter(("c" * 32, "d" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    snapshot_a, outcome_a = _run("Determine whether A is true")
    snapshot_b, outcome_b = _run("Determine whether A is true")
    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert record_a.execution_id != record_b.execution_id
    assert (
        record_a.executor_task_specification_digest
        == record_b.executor_task_specification_digest
    )
    assert (
        record_a.canonical_episode_snapshot_digest
        == record_b.canonical_episode_snapshot_digest
    )
    assert record_a.canonical_output_digest == record_b.canonical_output_digest
    assert (
        record_a.canonical_producer_execution_id
        == record_b.canonical_producer_execution_id
    )
    assert snapshot_a == snapshot_b
