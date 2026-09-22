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


class DeterministicGenerator:
    def __init__(self):
        self.count = 0

    def execute(self, view, episode_id):
        self.count += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id=f"h-{self.count}",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content=f"candidate-{self.count}",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _independence():
    metadata = IndependenceMetadata(
        executor_id="exec-r14",
        model_id="model-r14",
        provider_id="provider-r14",
        prompt_lineage="prompt-r14",
        context_lineage="context-r14",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r14",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r14",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r14",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    return metadata, policy


def _node(executor):
    metadata, policy = _independence()
    return RunnerNode(
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


def test_fresh_deterministic_runs_preserve_canonical_snapshot_identity(monkeypatch):
    ids = iter(("a" * 32, "b" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    def run_once():
        episode = Episode("episode-r14")
        envelope = TaskEnvelope(
            task_id="task-r14",
            literal_request="generate a deterministic hypothesis",
        )
        outcome = EpisodeRunner(
            (_node(DeterministicGenerator()),),
            budget_limit=1,
        ).run(
            episode,
            task_id=envelope.task_id,
            task_envelope=envelope,
        )
        return episode.snapshot(), outcome

    first_snapshot, first_outcome = run_once()
    second_snapshot, second_outcome = run_once()

    assert first_outcome.receipt.failures == ()
    assert second_outcome.receipt.failures == ()
    assert first_outcome.trace.records[0].execution_id != second_outcome.trace.records[0].execution_id

    # Attempt identity is intentionally unique, but canonical epistemic state
    # must remain reproducible for the same deterministic execution.
    assert first_snapshot == second_snapshot

    first_record = first_outcome.trace.records[0]
    second_record = second_outcome.trace.records[0]
    assert first_record.canonical_producer_execution_id == second_record.canonical_producer_execution_id
    assert first_record.canonical_producer_execution_id != first_record.execution_id
    assert second_record.canonical_producer_execution_id != second_record.execution_id

    proposition = first_snapshot.current_propositions[0]
    assert proposition.producer_execution_id == first_record.canonical_producer_execution_id


def test_repeated_executions_same_episode_get_distinct_canonical_producer_ids(monkeypatch):
    ids = iter(("c" * 32, "d" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    episode = Episode("episode-r14-repeat")
    envelope = TaskEnvelope(
        task_id="task-r14-repeat",
        literal_request="generate a deterministic hypothesis",
    )
    executor = DeterministicGenerator()
    runner = EpisodeRunner((_node(executor),), budget_limit=1)

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

    first_record = first.trace.records[0]
    second_record = second.trace.records[0]

    assert first_record.execution_id != second_record.execution_id
    assert first_record.canonical_producer_execution_id != second_record.canonical_producer_execution_id

    current = {
        proposition.proposition_id: proposition.producer_execution_id
        for proposition in episode.snapshot().current_propositions
    }
    assert current["h-1"] == first_record.canonical_producer_execution_id
    assert current["h-2"] == second_record.canonical_producer_execution_id
