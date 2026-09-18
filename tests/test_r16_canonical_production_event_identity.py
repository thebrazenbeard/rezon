from types import SimpleNamespace

import rezon.runner as runner_module
from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class RetryThenProduce:
    def __init__(self):
        self.count = 0

    def execute(self, view, episode_id):
        self.count += 1
        if self.count == 1:
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
            )
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id="h-r16-retry",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content="produced on retry",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


class FixedOutput:
    def __init__(self, content: str):
        self.content = content

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id="h-r16-fixed",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content=self.content,
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _node(executor):
    metadata = IndependenceMetadata(
        executor_id="exec-r16",
        model_id="model-r16",
        provider_id="provider-r16",
        prompt_lineage="prompt-r16",
        context_lineage="context-r16",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r16-production-event",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r16-production-event",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r16-production-event",),
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
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )


def _envelope():
    return TaskEnvelope(
        task_id="task-r16",
        literal_request="same task",
    )


def test_no_output_attempt_has_no_durable_producer_identity_then_retry_does(monkeypatch):
    ids = iter(("a" * 32, "b" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    episode = Episode("episode-r16-retry")
    envelope = _envelope()
    runner = EpisodeRunner(
        (_node(RetryThenProduce()),),
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

    first_record = first.trace.records[0]
    second_record = second.trace.records[0]

    assert first_snapshot.version == 0
    assert first_record.execution_id != second_record.execution_id
    assert first_record.canonical_episode_snapshot_digest == second_record.canonical_episode_snapshot_digest

    assert first_record.canonical_output_digest is None
    assert first_record.canonical_producer_execution_id is None

    assert second_record.canonical_output_digest is not None
    assert second_record.canonical_producer_execution_id is not None

    proposition = second_snapshot.current_propositions[0]
    assert proposition.producer_execution_id == second_record.canonical_producer_execution_id


def test_same_input_and_same_output_replay_reproduces_production_identity(monkeypatch):
    ids = iter(("c" * 32, "d" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    def run_once():
        episode = Episode("episode-r16-same")
        envelope = _envelope()
        outcome = EpisodeRunner(
            (_node(FixedOutput("same output")),),
            budget_limit=1,
        ).run(
            episode,
            task_id=envelope.task_id,
            task_envelope=envelope,
        )
        return episode.snapshot(), outcome

    snapshot_a, outcome_a = run_once()
    snapshot_b, outcome_b = run_once()
    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert record_a.execution_id != record_b.execution_id
    assert record_a.canonical_episode_snapshot_digest == record_b.canonical_episode_snapshot_digest
    assert record_a.canonical_output_digest == record_b.canonical_output_digest
    assert record_a.canonical_producer_execution_id == record_b.canonical_producer_execution_id
    assert snapshot_a == snapshot_b


def test_same_input_but_different_output_gets_distinct_production_identity(monkeypatch):
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex="e" * 32),
    )

    def run_once(content):
        episode = Episode("episode-r16-different")
        envelope = _envelope()
        outcome = EpisodeRunner(
            (_node(FixedOutput(content)),),
            budget_limit=1,
        ).run(
            episode,
            task_id=envelope.task_id,
            task_envelope=envelope,
        )
        return outcome

    outcome_a = run_once("output A")
    outcome_b = run_once("output B")
    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert record_a.canonical_episode_snapshot_digest == record_b.canonical_episode_snapshot_digest
    assert record_a.canonical_output_digest != record_b.canonical_output_digest
    assert record_a.canonical_producer_execution_id != record_b.canonical_producer_execution_id


class FixedRelationOutput:
    def __init__(self, role: str):
        self.role = role

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_relations=(
                Hyperrelation(
                    relation_id="r-r16-fixed",
                    episode_id=episode_id,
                    relation_type="supports",
                    participants=(
                        Participant(ref_id="o-r16", role=self.role),
                    ),
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _relation_node(executor):
    base = _node(executor)
    return RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            accepted_input_kinds=(PropositionKind.OBSERVATION,),
            independence_required=True,
            permitted_relation_types=("supports",),
        ),
        executor=executor,
        visibility=base.visibility,
        independence=base.independence,
        independence_policy=base.independence_policy,
    )


def _run_relation(role: str):
    episode = Episode("episode-r16-relation")
    episode.add_proposition(
        Proposition(
            proposition_id="o-r16",
            episode_id=episode.episode_id,
            kind=PropositionKind.OBSERVATION,
            content="shared observation",
        )
    )
    envelope = _envelope()
    outcome = EpisodeRunner(
        (_relation_node(FixedRelationOutput(role)),),
        budget_limit=1,
    ).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )
    return episode.snapshot(), outcome


def test_relation_output_uses_same_deterministic_production_identity_contract(monkeypatch):
    ids = iter(("f" * 32, "1" * 32))
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex=next(ids)),
    )

    snapshot_a, outcome_a = _run_relation("supporter")
    snapshot_b, outcome_b = _run_relation("supporter")

    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert outcome_a.receipt.failures == ()
    assert outcome_b.receipt.failures == ()
    assert record_a.execution_id != record_b.execution_id
    assert record_a.canonical_output_digest == record_b.canonical_output_digest
    assert record_a.canonical_producer_execution_id == record_b.canonical_producer_execution_id
    assert snapshot_a == snapshot_b

    relation = snapshot_a.current_relations[0]
    assert relation.producer_execution_id == record_a.canonical_producer_execution_id


def test_relation_semantic_difference_changes_output_and_producer_digest(monkeypatch):
    monkeypatch.setattr(
        runner_module,
        "uuid4",
        lambda: SimpleNamespace(hex="2" * 32),
    )

    _, outcome_a = _run_relation("supporter")
    _, outcome_b = _run_relation("context")

    record_a = outcome_a.trace.records[0]
    record_b = outcome_b.trace.records[0]

    assert outcome_a.receipt.failures == ()
    assert outcome_b.receipt.failures == ()
    assert record_a.canonical_episode_snapshot_digest == record_b.canonical_episode_snapshot_digest
    assert record_a.canonical_output_digest != record_b.canonical_output_digest
    assert record_a.canonical_producer_execution_id != record_b.canonical_producer_execution_id
