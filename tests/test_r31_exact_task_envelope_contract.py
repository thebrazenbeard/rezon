import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.envelopes import TaskEnvelope, TaskSpecification
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest
from rezon.receipts import (
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


SECRET = "peer-answer:H1=compressor"


class SmugglingEnvelope(TaskEnvelope):
    def to_task_specification(self):
        return TaskSpecification(
            literal_request=f"independent task; hidden auxiliary context: {SECRET}"
        )


class EvilStr(str):
    def __new__(cls, value, target):
        obj = str.__new__(cls, value)
        obj.target = target
        return obj

    def __eq__(self, other):
        return str(other) == self.target

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.target)

    def __reduce_ex__(self, protocol):
        return (EvilStr, (str(self), self.target))


class Reader:
    node_id = "echo_hypothesis"

    def __init__(self):
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(
            view.execution_id,
            self.node_id,
            (
                Proposition(
                    "smuggled",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    view.task_specification.literal_request,
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _independence():
    metadata = IndependenceMetadata(
        executor_id="exec",
        model_id="model",
        provider_id="provider",
        prompt_lineage="prompt",
        context_lineage="context",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r31",),
    )
    evidence = IndependenceVerificationEvidence(
        basis_ref="policy:r31",
        executor_id="exec",
        model_id="model",
        provider_id="provider",
        prompt_lineage="prompt",
        context_lineage="context",
        verification_refs=("review:r31",),
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
    )
    return metadata, IndependenceVerificationPolicy((evidence,))


def _runner(envelope):
    metadata, policy = _independence()
    reader = Reader()
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        reader,
        VisibilityPolicy(),
        metadata,
        policy,
    )
    episode = Episode("e1")
    outcome = EpisodeRunner((node,), 1).run(
        episode,
        task_id="t-r31",
        task_envelope=envelope,
    )
    return reader, episode, outcome


def test_task_envelope_subclass_cannot_smuggle_auxiliary_context_into_independent_task_spec():
    envelope = SmugglingEnvelope(
        task_id="t-r31",
        literal_request="generate independently",
        context_refs=(),
    )
    reader, episode, outcome = _runner(envelope)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert reader.calls == 0
    assert "smuggled" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_custom_task_id_cannot_match_runner_task_id_via_custom_equality():
    envelope = TaskEnvelope(
        task_id=EvilStr("forged-task", "t-r31"),
        literal_request="generate independently",
    )
    reader, episode, outcome = _runner(envelope)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert reader.calls == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("subject_refs", ["subject:1"]),
        ("constraints", ["bounded"]),
        ("available_authority", []),
        ("context_refs", []),
    ],
)
def test_task_envelope_collection_fields_must_be_exact_tuples(field, value):
    kwargs = dict(
        task_id="t-r31",
        literal_request="generate independently",
        subject_refs=(),
        constraints=(),
        available_authority=(),
        context_refs=(),
    )
    kwargs[field] = value
    envelope = TaskEnvelope(**kwargs)
    reader, episode, outcome = _runner(envelope)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert reader.calls == 0


def test_task_envelope_resource_budget_bool_is_rejected():
    envelope = TaskEnvelope(
        task_id="t-r31",
        literal_request="generate independently",
        resource_budget=True,
    )
    reader, episode, outcome = _runner(envelope)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert reader.calls == 0


def test_exact_task_specification_fields_are_required_at_direct_admission():
    episode = Episode("e-spec")
    result = ExecutionResult(
        execution_id="attempt",
        node_id="generator",
        emitted_propositions=(
            Proposition(
                "h1",
                "e-spec",
                PropositionKind.HYPOTHESIS,
                "candidate",
                producer_execution_id="attempt",
            ),
        ),
    )
    malformed = TaskSpecification(
        literal_request=EvilStr("forged-request", "real-request"),
        subject_refs=["subject:1"],
    )
    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            NodeDescriptor("generator", (PropositionKind.HYPOTHESIS,)),
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
                episode.snapshot()
            ),
            expected_execution_id="attempt",
            task_specification=malformed,
        )

