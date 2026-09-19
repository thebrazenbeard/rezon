from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class EpisodeSubclass(Episode):
    pass


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
                    "executor ran before exact Episode admission",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def test_non_exact_episode_is_rejected_before_executor_invocation():
    spy = SpyGenerator()
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        spy,
        VisibilityPolicy(),
    )
    episode = EpisodeSubclass("e1")

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r34",
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert spy.calls == 0
    assert "runner:invalid_episode_contract" in outcome.receipt.unresolved
    assert "ran" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
