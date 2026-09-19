import pytest

from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class TaskIdSubclass(str):
    pass


class TruthyTaskId:
    def __bool__(self):
        return True

    def __str__(self):
        return "forged-task-id"


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
                    "ran-r34",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "ran under invalid task identity",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _runner(spy):
    return EpisodeRunner(
        (
            RunnerNode(
                NodeDescriptor(
                    "echo_hypothesis",
                    (PropositionKind.HYPOTHESIS,),
                ),
                spy,
                VisibilityPolicy(),
            ),
        ),
        budget_limit=1,
    )


@pytest.mark.parametrize(
    "task_id",
    (
        "",
        TaskIdSubclass("subclass-task"),
        TruthyTaskId(),
    ),
)
def test_invalid_runner_task_id_fails_before_executor_or_state_mutation(task_id):
    spy = SpyGenerator()
    runner = _runner(spy)
    episode = Episode("e1")

    with pytest.raises(ValueError, match="task_id"):
        runner.run(episode, task_id=task_id)

    assert spy.calls == 0
    assert "ran-r34" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
