from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class ForgedTaskId:
    def __eq__(self, other):
        return other == "t-governed"

    def __ne__(self, other):
        return not self.__eq__(other)

    def __format__(self, spec):
        return "t-governed"

    def __str__(self):
        return "t-governed"


class EvilTaskStr(str):
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

    def __format__(self, spec):
        return self.target


class SpyGenerator:
    node_id = "echo_hypothesis"

    def __init__(self):
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "ran",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "ran under forged task identity",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _runner():
    spy = SpyGenerator()
    node = RunnerNode(
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        spy,
        VisibilityPolicy(),
    )
    return EpisodeRunner((node,), budget_limit=1), spy


def _assert_rejected(task_id, envelope=None):
    runner, spy = _runner()
    episode = Episode("e1")
    outcome = runner.run(
        episode,
        task_id,
        task_envelope=envelope,
    )
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert spy.calls == 0
    assert "ran" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_duck_task_id_cannot_equal_exact_envelope_task_id_and_execute():
    _assert_rejected(
        ForgedTaskId(),
        TaskEnvelope(
            task_id="t-governed",
            literal_request="governed task",
        ),
    )


def test_str_subclass_task_id_cannot_equal_exact_envelope_task_id_and_execute():
    _assert_rejected(
        EvilTaskStr("forged", "t-governed"),
        TaskEnvelope(
            task_id="t-governed",
            literal_request="governed task",
        ),
    )


def test_non_string_task_id_is_rejected_without_envelope():
    _assert_rejected(ForgedTaskId())


def test_empty_exact_task_id_is_rejected_before_execution():
    _assert_rejected("")
