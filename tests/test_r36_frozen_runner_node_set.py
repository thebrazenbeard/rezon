import pytest

from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class MutatingVerifier:
    node_id = "verifier-a"

    def __init__(self, mutation):
        self.runner = None
        self.mutation = mutation
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        self.mutation(self.runner)
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "ta",
                    episode_id,
                    PropositionKind.TEST_RESULT,
                    "verifier a passed",
                    source_refs=("o1",),
                    producer_execution_id=view.execution_id,
                ),
            ),
            verification_status=VerificationStatus.PASSED,
            verification_target_ids=("o1",),
        )


class SpyVerifier:
    node_id = "verifier-b"

    def __init__(self):
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "tb",
                    episode_id,
                    PropositionKind.TEST_RESULT,
                    "verifier b passed",
                    source_refs=("o1",),
                    producer_execution_id=view.execution_id,
                ),
            ),
            verification_status=VerificationStatus.PASSED,
            verification_target_ids=("o1",),
        )


def _run_with_mutation(mutation):
    first = MutatingVerifier(mutation)
    second = SpyVerifier()
    nodes = (
        RunnerNode(
            NodeDescriptor(
                "verifier-a",
                (PropositionKind.TEST_RESULT,),
                mandatory_verification=True,
                verification_target_ids=("o1",),
            ),
            first,
            VisibilityPolicy(),
        ),
        RunnerNode(
            NodeDescriptor(
                "verifier-b",
                (PropositionKind.TEST_RESULT,),
                mandatory_verification=True,
                verification_target_ids=("o1",),
            ),
            second,
            VisibilityPolicy(),
        ),
    )
    runner = EpisodeRunner(nodes, budget_limit=2)
    first.runner = runner

    episode = Episode("e1")
    episode.add_proposition(
        Proposition("o1", "e1", PropositionKind.OBSERVATION, "input")
    )

    outcome = runner.run(episode, task_id="t-r36")
    return first, second, episode, outcome


@pytest.mark.parametrize(
    "mutation",
    [
        lambda runner: setattr(runner, "nodes", (runner.nodes[0],)),
        lambda runner: setattr(runner, "nodes", ()),
        lambda runner: setattr(
            runner,
            "nodes",
            (
                runner.nodes[0],
                RunnerNode(
                    NodeDescriptor(
                        "echo_hypothesis",
                        (PropositionKind.HYPOTHESIS,),
                    ),
                    None,
                    VisibilityPolicy(),
                ),
            ),
        ),
    ],
)
def test_executor_cannot_mutate_preflighted_node_set_to_skip_mandatory_verifier(
    mutation,
):
    first, second, episode, outcome = _run_with_mutation(mutation)

    assert first.calls == 1
    assert second.calls == 1
    assert outcome.receipt.failures == ()
    assert not outcome.receipt.unresolved
    assert {"ta", "tb"}.issubset(
        {
            proposition.proposition_id
            for proposition in episode.snapshot().current_propositions
        }
    )
    assert tuple(record.node_id for record in outcome.trace.records) == (
        "verifier-a",
        "verifier-b",
    )
