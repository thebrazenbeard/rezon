from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class DescriptorEscalator:
    node_id = "echo_hypothesis"

    def __init__(self):
        self.node = None
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        object.__setattr__(
            self.node,
            "descriptor",
            NodeDescriptor(
                "echo_hypothesis",
                (PropositionKind.CLAIM,),
            ),
        )
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "c1",
                    episode_id,
                    PropositionKind.CLAIM,
                    "not permitted by the preflighted descriptor",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


class Verifier:
    def __init__(self, node_id, proposition_id):
        self.node_id = node_id
        self.proposition_id = proposition_id
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    self.proposition_id,
                    episode_id,
                    PropositionKind.TEST_RESULT,
                    f"{self.node_id} passed",
                    source_refs=("o1",),
                    producer_execution_id=view.execution_id,
                ),
            ),
            verification_status=VerificationStatus.PASSED,
            verification_target_ids=("o1",),
        )


class MutatingVerifier(Verifier):
    def __init__(self, node_id, proposition_id, mutation):
        super().__init__(node_id, proposition_id)
        self.mutation = mutation

    def execute(self, view, episode_id):
        self.mutation()
        return super().execute(view, episode_id)


def _mandatory_node(node_id, executor):
    return RunnerNode(
        NodeDescriptor(
            node_id,
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("o1",),
        ),
        executor,
        VisibilityPolicy(),
    )


def test_executor_cannot_escalate_its_preflighted_output_permissions():
    executor = DescriptorEscalator()
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor,
        VisibilityPolicy(),
    )
    executor.node = node

    episode = Episode("e1")
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r41",
    )

    assert executor.calls == 1
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "c1" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_executor_cannot_remove_next_mandatory_verifier_by_descriptor_swap():
    second = Verifier("verifier-b", "tb")
    second_node = _mandatory_node("verifier-b", second)

    def mutate():
        object.__setattr__(
            second_node,
            "descriptor",
            NodeDescriptor(
                "verifier-b",
                (PropositionKind.TEST_RESULT,),
            ),
        )

    first = MutatingVerifier("verifier-a", "ta", mutate)
    first_node = _mandatory_node("verifier-a", first)

    episode = Episode("e1")
    episode.add_proposition(
        Proposition("o1", "e1", PropositionKind.OBSERVATION, "input")
    )

    outcome = EpisodeRunner(
        (first_node, second_node),
        budget_limit=2,
    ).run(episode, task_id="t-r41")

    assert outcome.receipt.failures == ()
    assert first.calls == 1
    assert second.calls == 1
    assert {"ta", "tb"}.issubset(
        {
            proposition.proposition_id
            for proposition in episode.snapshot().current_propositions
        }
    )


def test_executor_cannot_replace_next_preflighted_executor():
    original = Verifier("verifier-b", "tb")
    replacement = Verifier("verifier-b", "forged-b")
    second_node = _mandatory_node("verifier-b", original)

    def mutate():
        object.__setattr__(second_node, "executor", replacement)

    first = MutatingVerifier("verifier-a", "ta", mutate)
    first_node = _mandatory_node("verifier-a", first)

    episode = Episode("e1")
    episode.add_proposition(
        Proposition("o1", "e1", PropositionKind.OBSERVATION, "input")
    )

    outcome = EpisodeRunner(
        (first_node, second_node),
        budget_limit=2,
    ).run(episode, task_id="t-r41")

    assert outcome.receipt.failures == ()
    assert first.calls == 1
    assert original.calls == 1
    assert replacement.calls == 0
    ids = {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
    assert "tb" in ids
    assert "forged-b" not in ids
