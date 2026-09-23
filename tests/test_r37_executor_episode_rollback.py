from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class EpisodeMutator:
    node_id = "echo_hypothesis"

    def __init__(self, episode, mutation, *, raises=False):
        self.episode = episode
        self.mutation = mutation
        self.raises = raises
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        self.mutation(self.episode)
        if self.raises:
            raise RuntimeError("executor crash after direct canonical mutation")
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h-returned",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "ordinary returned candidate",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _run(mutation, *, raises=False, with_seed=True):
    episode = Episode("e1")
    if with_seed:
        episode.add_proposition(
            Proposition(
                "seed",
                "e1",
                PropositionKind.OBSERVATION,
                "seed",
            )
        )
    before = episode.snapshot()
    executor = EpisodeMutator(
        episode,
        mutation,
        raises=raises,
    )
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor,
        VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r37",
    )
    return episode, before, executor, outcome


def test_direct_proposition_addition_is_rolled_back_before_rejection():
    def mutate(episode):
        episode.add_proposition(
            Proposition(
                "side",
                "e1",
                PropositionKind.OBSERVATION,
                "direct side effect",
            )
        )

    episode, before, executor, outcome = _run(mutate)

    assert executor.calls == 1
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "executor_episode_mutation:t-r37:exec:1:echo_hypothesis" in (
        outcome.receipt.unresolved
    )
    assert episode.snapshot() == before


def test_direct_retraction_is_rolled_back_before_rejection():
    def mutate(episode):
        episode.retract_proposition("seed", "malicious executor retraction")

    episode, before, executor, outcome = _run(mutate)

    assert executor.calls == 1
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert episode.snapshot() == before


def test_direct_relation_addition_is_rolled_back_before_rejection():
    def mutate(episode):
        episode.add_relation(
            Hyperrelation(
                "side-rel",
                "e1",
                "supports",
                (Participant("seed", "source"),),
            )
        )

    episode, before, executor, outcome = _run(mutate)

    assert executor.calls == 1
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert episode.snapshot() == before


def test_executor_exception_rolls_back_direct_episode_mutation():
    def mutate(episode):
        episode.add_proposition(
            Proposition(
                "side-before-crash",
                "e1",
                PropositionKind.OBSERVATION,
                "must be rolled back",
            )
        )

    episode, before, executor, outcome = _run(mutate, raises=True)

    assert executor.calls == 1
    assert FailureState.ATTEMPTED_UNKNOWN in outcome.receipt.failures
    assert episode.snapshot() == before
