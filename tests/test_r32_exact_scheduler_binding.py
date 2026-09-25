from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.scheduler import (
    DeterministicScheduler,
    ScheduleAction,
    ScheduleDecision,
)
from rezon.visibility import VisibilityPolicy


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
                    "generated",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "bypassed mandatory verifier",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


class SkipVerifierScheduler:
    def __init__(self):
        self.calls = 0

    def next(self, snapshot, nodes, completed_node_ids, budget):
        self.calls += 1
        if self.calls == 1:
            return ScheduleDecision(
                ScheduleAction.EXECUTE,
                node_id="echo_hypothesis",
                reason="skip-mandatory-verifier",
                node_index=1,
            )
        return ScheduleDecision(ScheduleAction.TERMINATE, reason="done")


class SkipVerifierSubclass(DeterministicScheduler):
    def __init__(self):
        self.calls = 0

    def next(self, snapshot, nodes, completed_node_ids, budget):
        self.calls += 1
        if self.calls == 1:
            return ScheduleDecision(
                ScheduleAction.EXECUTE,
                node_id="echo_hypothesis",
                reason="skip-mandatory-verifier",
                node_index=1,
            )
        return ScheduleDecision(ScheduleAction.TERMINATE, reason="done")


def _runner_and_generator():
    generator = SpyGenerator()
    nodes = (
        RunnerNode(
            NodeDescriptor(
                "verifier",
                (PropositionKind.TEST_RESULT,),
                mandatory_verification=True,
                verification_target_ids=("target",),
            ),
            None,
            VisibilityPolicy(),
        ),
        RunnerNode(
            NodeDescriptor(
                "echo_hypothesis",
                (PropositionKind.HYPOTHESIS,),
            ),
            generator,
            VisibilityPolicy(),
        ),
    )
    return EpisodeRunner(nodes, budget_limit=2), generator


def _assert_scheduler_mutation_cannot_skip_mandatory_verifier(scheduler):
    runner, generator = _runner_and_generator()
    runner.scheduler = scheduler
    episode = Episode("e1")

    outcome = runner.run(episode, task_id="t-r32")

    assert generator.calls == 0
    assert FailureState.UNAVAILABLE in outcome.receipt.failures
    assert "generated" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_duck_scheduler_cannot_replace_governed_scheduler():
    _assert_scheduler_mutation_cannot_skip_mandatory_verifier(
        SkipVerifierScheduler()
    )


def test_scheduler_subclass_cannot_override_governed_scheduling():
    _assert_scheduler_mutation_cannot_skip_mandatory_verifier(
        SkipVerifierSubclass()
    )


def test_exact_scheduler_instance_cannot_shadow_next_method():
    scheduler = DeterministicScheduler()
    malicious = SkipVerifierScheduler()
    scheduler.next = malicious.next
    _assert_scheduler_mutation_cannot_skip_mandatory_verifier(scheduler)
