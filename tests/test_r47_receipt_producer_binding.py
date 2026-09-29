from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class SameOutputExecutor:
    node_id = "echo_hypothesis"

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h1",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "same-output",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _run(input_content):
    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            "o1",
            "e1",
            PropositionKind.OBSERVATION,
            input_content,
        )
    )
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        SameOutputExecutor(),
        VisibilityPolicy(),
    )
    return EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r47",
    )


def test_result_receipt_binds_canonical_producer_identity():
    left = _run("input-alpha")
    right = _run("input-beta")

    assert (
        left.trace.records[0].canonical_output_digest
        == right.trace.records[0].canonical_output_digest
    )
    assert (
        left.trace.records[0].canonical_episode_snapshot_digest
        != right.trace.records[0].canonical_episode_snapshot_digest
    )
    assert (
        left.trace.records[0].canonical_producer_execution_id
        != right.trace.records[0].canonical_producer_execution_id
    )

    assert left.receipt != right.receipt
    assert left.receipt.execution_producer_ids == (
        (
            left.trace.records[0].execution_id,
            left.trace.records[0].canonical_producer_execution_id,
        ),
    )
    assert right.receipt.execution_producer_ids == (
        (
            right.trace.records[0].execution_id,
            right.trace.records[0].canonical_producer_execution_id,
        ),
    )


def test_result_receipt_producer_binding_is_deterministic():
    first = _run("same-input")
    second = _run("same-input")

    assert first.receipt == second.receipt
    assert first.receipt.execution_producer_ids
