from rezon.episode import Episode, EpisodeSnapshot
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class CanonicalMutator:
    node_id = "echo_hypothesis"

    def __init__(self, episode):
        self.episode = episode
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        Episode.add_proposition(
            self.episode,
            Proposition(
                "side",
                "e1",
                PropositionKind.OBSERVATION,
                "direct canonical mutation hidden by instance-shadowed snapshot",
            ),
        )
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "returned",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "ordinary returned candidate",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def test_exact_episode_instance_cannot_shadow_snapshot_to_defeat_rollback():
    episode = Episode("e1")
    fake = EpisodeSnapshot(
        episode_id="e1",
        version=0,
        current_propositions=(),
        all_propositions=(),
        current_relations=(),
        all_relations=(),
        events=(),
    )
    episode.snapshot = lambda: fake

    executor = CanonicalMutator(episode)
    node = RunnerNode(
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor,
        VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r38",
    )

    assert executor.calls == 1
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert any(
        item.startswith("executor_episode_mutation:")
        for item in outcome.receipt.unresolved
    )
    assert Episode.snapshot(episode) == fake
