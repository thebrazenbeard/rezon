from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class SpyEmitter:
    node_id = "verifier"

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h-r31",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "should never execute through descriptor substitution",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


class SwitchingNodeSequence:
    """Expose a strict node to iteration and a weaker same-ID node to indexing."""

    def __init__(self, strict_node: RunnerNode, weak_node: RunnerNode) -> None:
        self.strict_node = strict_node
        self.weak_node = weak_node

    def __iter__(self):
        return iter((self.strict_node,))

    def __getitem__(self, index):
        if index != 0:
            raise IndexError(index)
        return self.weak_node


def test_scheduler_descriptor_cannot_be_swapped_before_execution() -> None:
    executor = SpyEmitter()
    strict = RunnerNode(
        NodeDescriptor(
            "verifier",
            (PropositionKind.HYPOTHESIS,),
            mandatory_verification=True,
            verification_target_ids=("target",),
        ),
        executor,
        VisibilityPolicy(),
    )
    weak = RunnerNode(
        NodeDescriptor(
            "verifier",
            (PropositionKind.HYPOTHESIS,),
            mandatory_verification=False,
        ),
        executor,
        VisibilityPolicy(),
    )

    nodes = SwitchingNodeSequence(strict, weak)

    try:
        runner = EpisodeRunner(nodes, budget_limit=1)
    except ValueError:
        assert executor.calls == 0
        return

    episode = Episode("e1")
    outcome = runner.run(episode, task_id="t-r31")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert executor.calls == 0
    assert "h-r31" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
