from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class EvilBudget:
    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __ge__(self, other):
        return False


class IntBudgetSubclass(int):
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
                    "ran despite governed zero budget",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _node(spy):
    return RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        spy,
        VisibilityPolicy(),
    )


def _assert_zero_envelope_budget_cannot_be_overridden(runner):
    spy = runner.nodes[0].executor
    envelope = TaskEnvelope(
        task_id="t-r33",
        literal_request="do not spend resources",
        resource_budget=0,
    )
    episode = Episode("e1")

    outcome = runner.run(
        episode,
        task_id="t-r33",
        task_envelope=envelope,
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert spy.calls == 0
    assert "ran" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_duck_runner_budget_cannot_override_exact_zero_envelope_budget():
    spy = SpyGenerator()
    runner = EpisodeRunner((_node(spy),), budget_limit=EvilBudget())
    _assert_zero_envelope_budget_cannot_be_overridden(runner)


def test_mutated_runner_budget_cannot_override_exact_zero_envelope_budget():
    spy = SpyGenerator()
    runner = EpisodeRunner((_node(spy),), budget_limit=0)
    runner.budget_limit = EvilBudget()
    _assert_zero_envelope_budget_cannot_be_overridden(runner)


def test_integer_subclass_runner_budget_is_not_an_exact_budget_contract():
    spy = SpyGenerator()
    runner = EpisodeRunner((_node(spy),), budget_limit=IntBudgetSubclass(1))
    episode = Episode("e1")

    outcome = runner.run(episode, task_id="t-r33-no-envelope")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert spy.calls == 0
    assert "ran" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
