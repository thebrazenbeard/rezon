from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class PostTransactionResult:
    execution_id = "t-r38:exec:1:echo_hypothesis"
    node_id = "echo_hypothesis"
    emitted_relations = ()
    failures = ()
    source_refs = ()
    source_versions = ()
    verification_status = None
    verification_target_ids = ()

    def __init__(self, episode):
        self.episode = episode
        self.mutated = False

    @property
    def emitted_propositions(self):
        if not self.mutated:
            self.mutated = True
            self.episode.add_proposition(
                Proposition(
                    "posttx",
                    "e1",
                    PropositionKind.OBSERVATION,
                    "mutated while runner inspected result",
                )
            )
        return ()


class ResultSubclass(ExecutionResult):
    def __getattribute__(self, name):
        if name == "source_refs":
            episode = object.__getattribute__(self, "_episode")
            if "subclass-posttx" not in {
                proposition.proposition_id
                for proposition in episode.snapshot().current_propositions
            }:
                episode.add_proposition(
                    Proposition(
                        "subclass-posttx",
                        "e1",
                        PropositionKind.OBSERVATION,
                        "subclass side effect",
                    )
                )
        return super().__getattribute__(name)


class Executor:
    node_id = "echo_hypothesis"

    def __init__(self, factory):
        self.factory = factory

    def execute(self, view, episode_id):
        return self.factory(view)


def _runner(executor):
    return EpisodeRunner(
        (
            RunnerNode(
                NodeDescriptor(
                    "echo_hypothesis",
                    (PropositionKind.HYPOTHESIS,),
                ),
                executor,
                VisibilityPolicy(),
            ),
        ),
        budget_limit=1,
    )


def test_duck_result_cannot_mutate_episode_during_post_execution_field_reads():
    episode = Episode("e1")
    before = episode.snapshot()

    outcome = _runner(
        Executor(lambda _view: PostTransactionResult(episode))
    ).run(episode, task_id="t-r38")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "execution_result:invalid_contract:t-r38:exec:1:echo_hypothesis" in (
        outcome.receipt.unresolved
    )
    assert episode.snapshot() == before


def test_execution_result_subclass_cannot_run_getattribute_side_effects_after_tx():
    episode = Episode("e1")
    before = episode.snapshot()

    def build(view):
        result = ResultSubclass(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
        )
        object.__setattr__(result, "_episode", episode)
        return result

    outcome = _runner(Executor(build)).run(episode, task_id="t-r38")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert episode.snapshot() == before


def test_exact_result_still_executes_normally():
    episode = Episode("e1")

    def build(view):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    "h1",
                    "e1",
                    PropositionKind.HYPOTHESIS,
                    "ordinary result",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )

    outcome = _runner(Executor(build)).run(episode, task_id="t-r38")

    assert outcome.receipt.failures == ()
    assert "h1" in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
