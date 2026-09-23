import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.envelopes import TaskSpecification
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


class FakeTaskSpecification:
    def __init__(self, digest: str):
        self.digest = digest


class EvilTaskSpecification(TaskSpecification):
    @property
    def digest(self) -> str:
        return "f" * 64


def _episode_and_result():
    episode = Episode("r23-task-spec")
    attempt_id = "attempt-r23"
    result = ExecutionResult(
        execution_id=attempt_id,
        node_id="generator",
        emitted_propositions=(
            Proposition(
                proposition_id="h-r23",
                episode_id=episode.episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="same output",
                producer_execution_id=attempt_id,
            ),
        ),
    )
    return episode, attempt_id, result


def _admit(task_specification):
    episode, attempt_id, result = _episode_and_result()
    digest = canonical_episode_snapshot_digest(episode.snapshot())
    receipt = admit_execution_result(
        episode,
        NodeDescriptor(
            "generator",
            (PropositionKind.HYPOTHESIS,),
        ),
        result,
        expected_episode_snapshot_digest=digest,
        expected_execution_id=attempt_id,
        task_specification=task_specification,
    )
    return episode, receipt


def test_duck_typed_task_digest_cannot_control_canonical_producer():
    with pytest.raises(AdmissionError, match="exact TaskSpecification"):
        _admit(FakeTaskSpecification("a" * 64))


def test_task_specification_subclass_cannot_override_digest_semantics():
    with pytest.raises(AdmissionError, match="exact TaskSpecification"):
        _admit(EvilTaskSpecification(literal_request="same request"))


def test_exact_task_specification_remains_supported():
    specification = TaskSpecification(
        literal_request="same request",
        subject_refs=("subject:1",),
        constraints=("constraint:1",),
    )
    episode, receipt = _admit(specification)

    assert receipt.task_specification_digest == specification.digest
    assert receipt.canonical_producer_execution_id is not None
    assert tuple(
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    ) == ("h-r23",)


def test_explicit_no_task_specification_path_remains_supported():
    episode, receipt = _admit(None)

    assert receipt.task_specification_digest is None
    assert receipt.canonical_producer_execution_id is not None
    assert tuple(
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    ) == ("h-r23",)
