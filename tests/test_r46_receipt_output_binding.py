from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class ContentExecutor:
    node_id = "echo_hypothesis"

    def __init__(self, content):
        self.content = content

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h1",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    self.content,
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _run(content):
    episode = Episode("e1")
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        ContentExecutor(content),
        VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r46",
    )
    return outcome


def test_result_receipt_binds_distinct_canonical_outputs():
    left = _run("alpha")
    right = _run("beta")

    assert left.trace.records[0].canonical_output_digest
    assert right.trace.records[0].canonical_output_digest
    assert (
        left.trace.records[0].canonical_output_digest
        != right.trace.records[0].canonical_output_digest
    )

    assert left.receipt != right.receipt
    assert left.receipt.execution_output_digests == (
        (
            left.trace.records[0].execution_id,
            left.trace.records[0].canonical_output_digest,
        ),
    )
    assert right.receipt.execution_output_digests == (
        (
            right.trace.records[0].execution_id,
            right.trace.records[0].canonical_output_digest,
        ),
    )


def test_result_receipt_output_binding_is_deterministic_for_same_output():
    first = _run("same")
    second = _run("same")

    assert first.receipt == second.receipt
    assert first.receipt.execution_output_digests
