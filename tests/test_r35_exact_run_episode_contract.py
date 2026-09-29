from contextlib import contextmanager

from rezon.episode import Episode, EpisodeSnapshot
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class EpisodeSubclass(Episode):
    pass


class DeceptiveEpisode(Episode):
    def snapshot(self):
        return EpisodeSnapshot(
            episode_id=self.episode_id,
            version=0,
            current_propositions=(),
            all_propositions=(),
            current_relations=(),
            all_relations=(),
            events=(),
        )


class DuckEpisode:
    episode_id = "e1"

    @contextmanager
    def atomic_mutation(self):
        yield

    def snapshot(self):
        return EpisodeSnapshot(
            episode_id="e1",
            version=0,
            current_propositions=(),
            all_propositions=(),
            current_relations=(),
            all_relations=(),
            events=(),
        )


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
                    "ran under non-exact episode",
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


def _assert_preflight_rejected(episode):
    runner, spy = _runner()
    outcome = runner.run(episode, task_id="t-r35")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "runner:invalid_episode_contract" in outcome.receipt.unresolved
    assert spy.calls == 0


def test_episode_subclass_is_rejected_before_executor_invocation():
    _assert_preflight_rejected(EpisodeSubclass("e1"))


def test_deceptive_episode_snapshot_cannot_change_scheduler_semantics_before_rejection():
    episode = DeceptiveEpisode("e1")
    Episode.add_proposition(
        episode,
        Proposition(
            "existing",
            "e1",
            PropositionKind.HYPOTHESIS,
            "already present",
        ),
    )
    _assert_preflight_rejected(episode)
    assert tuple(
        proposition.proposition_id
        for proposition in Episode.snapshot(episode).current_propositions
    ) == ("existing",)


def test_duck_episode_is_rejected_before_executor_invocation():
    _assert_preflight_rejected(DuckEpisode())
