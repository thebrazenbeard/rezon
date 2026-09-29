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
                    proposition_id="h-r15",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content="same output",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _node():
    metadata = IndependenceMetadata(
        executor_id="exec-r15",
        model_id="model-r15",
        provider_id="provider-r15",
        prompt_lineage="prompt-r15",
        context_lineage="context-r15",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r15-state-digest",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r15-state-digest",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r15-state-digest",),
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


def _run(initial_content: str):
    episode = Episode("same-r15-episode")
    episode.add_proposition(Proposition(
        proposition_id="o1",
        episode_id=episode.episode_id,
        kind=PropositionKind.OBSERVATION,
        content=initial_content,
    ))
    envelope = TaskEnvelope(
        task_id="task-r15",
        literal_request="same task",
    )
    outcome = EpisodeRunner((_node(),), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )
    return episode.snapshot(), outcome


def test_divergent_same_version_states_get_distinct_canonical_producer_ids(monkeypatch):
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex="a" * 32),
    )

    snapshot_a, outcome_a = _run("state A")
    snapshot_b, outcome_b = _run("state B")

    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert record_a.episode_version == record_b.episode_version == "same-r15-episode@1"
    assert snapshot_a.current_propositions[0].content != snapshot_b.current_propositions[0].content

    assert record_a.canonical_episode_snapshot_digest != record_b.canonical_episode_snapshot_digest
    assert record_a.canonical_producer_execution_id != record_b.canonical_producer_execution_id


def test_identical_canonical_states_reproduce_digest_and_producer_identity(monkeypatch):
    ids = iter(("b" * 32, "c" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    snapshot_a, outcome_a = _run("same state")
    snapshot_b, outcome_b = _run("same state")

    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert record_a.execution_id != record_b.execution_id
    assert record_a.canonical_episode_snapshot_digest == record_b.canonical_episode_snapshot_digest
    assert record_a.canonical_producer_execution_id == record_b.canonical_producer_execution_id
    assert snapshot_a == snapshot_b


class TwoStepOutput:
    def __init__(self):
        self.count = 0

    def execute(self, view, episode_id):
        self.count += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id=f"h-r15-step-{self.count}",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content=f"semantic-{self.count}",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _node_for(executor):
    metadata = IndependenceMetadata(
        executor_id="exec-r15-multi",
        model_id="model-r15-multi",
        provider_id="provider-r15-multi",
        prompt_lineage="prompt-r15-multi",
        context_lineage="context-r15-multi",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r15-multi",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r15-multi",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r15-multi",),
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
        executor=executor,
        visibility=VisibilityPolicy(blind_kinds=(PropositionKind.HYPOTHESIS,)),
        independence=metadata,
        independence_policy=policy,
    )


def test_multistep_replay_reproduces_canonical_digest_chain(monkeypatch):
    def run_sequence(uuid_values):
        values = iter(uuid_values)
        monkeypatch.setattr(
            runner_module,
            "uuid4",
            lambda: SimpleNamespace(hex=next(values)),
        )
        episode = Episode("multi-r15")
        envelope = TaskEnvelope(
            task_id="task-r15-multi",
            literal_request="same two-step task",
        )
        executor = TwoStepOutput()
        runner = EpisodeRunner(
            (_node_for(executor),),
            budget_limit=1,
        )

        first = runner.run(
            episode,
            task_id=envelope.task_id,
            task_envelope=envelope,
        )
        first_snapshot = episode.snapshot()
        second = runner.run(
            episode,
            task_id=envelope.task_id,
            task_envelope=envelope,
        )
        second_snapshot = episode.snapshot()
        return first_snapshot, second_snapshot, first, second

    a1, a2, a_first, a_second = run_sequence(("1" * 32, "2" * 32))
    b1, b2, b_first, b_second = run_sequence(("a" * 32, "b" * 32))

    assert a_first.trace.records[0].execution_id != b_first.trace.records[0].execution_id
    assert a_second.trace.records[0].execution_id != b_second.trace.records[0].execution_id

    assert a1 == b1
    assert a2 == b2

    assert (
        a_first.trace.records[0].canonical_episode_snapshot_digest
        == b_first.trace.records[0].canonical_episode_snapshot_digest
    )
    assert (
        a_second.trace.records[0].canonical_episode_snapshot_digest
        == b_second.trace.records[0].canonical_episode_snapshot_digest
    )
    assert (
        a_first.trace.records[0].canonical_producer_execution_id
        == b_first.trace.records[0].canonical_producer_execution_id
    )
    assert (
        a_second.trace.records[0].canonical_producer_execution_id
        == b_second.trace.records[0].canonical_producer_execution_id
    )

    assert a_first.receipt.failures == ()
    assert a_second.receipt.failures == ()
    assert b_first.receipt.failures == ()
    assert b_second.receipt.failures == ()
