from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState, IndependenceMetadata
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class SpyExecutor:
    node_id = "echo_hypothesis"

    def __init__(self):
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(view.execution_id, self.node_id)


class MutatingVisibility(VisibilityPolicy):
    def __getattribute__(self, name):
        if name == "allow_ids":
            episode = object.__getattribute__(self, "_episode")
            if "visibility-side" not in {
                proposition.proposition_id
                for proposition in episode.snapshot().current_propositions
            }:
                episode.add_proposition(
                    Proposition(
                        "visibility-side",
                        "e1",
                        PropositionKind.OBSERVATION,
                        "visibility side effect",
                    )
                )
        return super().__getattribute__(name)


class MutatingTuple(tuple):
    def __new__(cls, episode):
        obj = tuple.__new__(cls, ())
        obj.episode = episode
        return obj

    def __iter__(self):
        if "tuple-side" not in {
            proposition.proposition_id
            for proposition in self.episode.snapshot().current_propositions
        }:
            self.episode.add_proposition(
                Proposition(
                    "tuple-side",
                    "e1",
                    PropositionKind.OBSERVATION,
                    "container side effect",
                )
            )
        return super().__iter__()


class MutatingIndependence(IndependenceMetadata):
    def __bool__(self):
        episode = object.__getattribute__(self, "_episode")
        if "independence-side" not in {
            proposition.proposition_id
            for proposition in episode.snapshot().current_propositions
        }:
            episode.add_proposition(
                Proposition(
                    "independence-side",
                    "e1",
                    PropositionKind.OBSERVATION,
                    "independence truthiness side effect",
                )
            )
        return True


def _run(visibility, independence=IndependenceMetadata()):
    episode = Episode("e1")
    executor = SpyExecutor()

    if isinstance(visibility, MutatingVisibility):
        object.__setattr__(visibility, "_episode", episode)
    if isinstance(independence, MutatingIndependence):
        object.__setattr__(independence, "_episode", episode)

    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor,
        visibility,
        independence=independence,
    )

    before = episode.snapshot()
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r39",
    )
    return episode, before, executor, outcome


def _assert_preflight_rejected(episode, before, executor, outcome):
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "runner:invalid_node_contract" in outcome.receipt.unresolved
    assert executor.calls == 0
    assert episode.snapshot() == before


def test_visibility_subclass_cannot_mutate_episode_during_view_build():
    _assert_preflight_rejected(
        *_run(MutatingVisibility())
    )


def test_visibility_field_container_must_be_exact_before_iteration():
    episode = Episode("e1")
    visibility = VisibilityPolicy()
    object.__setattr__(visibility, "allow_ids", MutatingTuple(episode))
    executor = SpyExecutor()
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor,
        visibility,
    )
    before = episode.snapshot()

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r39",
    )

    _assert_preflight_rejected(episode, before, executor, outcome)


def test_independence_subclass_cannot_mutate_episode_from_truthiness():
    _assert_preflight_rejected(
        *_run(
            VisibilityPolicy(),
            MutatingIndependence(),
        )
    )
