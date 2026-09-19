from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class EvilTaskId(str):
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
        return "formatted-attacker-task"


class SpyGenerator:
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
                    "ran",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "ran under forged runner task identity",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def test_non_exact_runner_task_id_is_rejected_before_executor_invocation():
    spy = SpyGenerator()
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        spy,
        VisibilityPolicy(),
    )
    envelope = TaskEnvelope(
        task_id="t-real",
        literal_request="run",
    )
    episode = Episode("e1")

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=EvilTaskId("forged", "t-real"),
        task_envelope=envelope,
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert spy.calls == 0
    assert "runner:invalid_task_id_contract" in outcome.receipt.unresolved
    assert "ran" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
