from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


_CURRENT_EPISODE = None


class AttributeMutatingFalsifier:
    node_id = "falsifier"

    def __init__(self, target=None):
        self.target_hypothesis_id = target

    def __getattribute__(self, name):
        if name == "target_hypothesis_id":
            episode = globals()["_CURRENT_EPISODE"]
            if episode is not None and "attribute-side" not in {
                proposition.proposition_id
                for proposition in episode.snapshot().current_propositions
            }:
                episode.add_proposition(
                    Proposition(
                        "attribute-side",
                        "e1",
                        PropositionKind.OBSERVATION,
                        "target attribute side effect",
                    )
                )
        return object.__getattribute__(self, name)

    def execute(self, view, episode_id):
        return ExecutionResult(view.execution_id, self.node_id)


class ConstructorMutatingFalsifier:
    node_id = "falsifier"
    target_hypothesis_id = None

    def __init__(self, target=None):
        if target is not None:
            episode = globals()["_CURRENT_EPISODE"]
            episode.add_proposition(
                Proposition(
                    "constructor-side",
                    "e1",
                    PropositionKind.OBSERVATION,
                    "target constructor side effect",
                )
            )
        self.target_hypothesis_id = target

    def execute(self, view, episode_id):
        return ExecutionResult(view.execution_id, self.node_id)


def _run(executor):
    global _CURRENT_EPISODE

    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            "h1",
            "e1",
            PropositionKind.HYPOTHESIS,
            "candidate",
            confidence=0.95,
        )
    )
    before = episode.snapshot()
    _CURRENT_EPISODE = episode

    node = RunnerNode(
        NodeDescriptor(
            "falsifier",
            (PropositionKind.TEST_RESULT,),
        ),
        executor,
        VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r40",
    )
    _CURRENT_EPISODE = None
    return episode, before, outcome


def _assert_contained(episode, before, outcome):
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "executor_episode_mutation:t-r40:exec:1:falsifier" in (
        outcome.receipt.unresolved
    )
    assert episode.snapshot() == before


def test_target_attribute_probe_mutation_is_rolled_back():
    _assert_contained(
        *_run(AttributeMutatingFalsifier())
    )


def test_target_constructor_mutation_is_rolled_back():
    _assert_contained(
        *_run(ConstructorMutatingFalsifier())
    )
