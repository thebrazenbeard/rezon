import pytest

from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import EffectState, FailureState, ResultReceipt
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def test_failed_execution_result_cannot_mutate_canonical_episode_state():
    class FailedExecutor:
        def execute(self, view, episode_id):
            hypothesis = Proposition(
                "h-failed",
                episode_id,
                PropositionKind.HYPOTHESIS,
                "must not become canonical",
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                view.execution_id,
                "echo_hypothesis",
                emitted_propositions=(hypothesis,),
                failures=(FailureState.CONTRACT_VIOLATION,),
            )

    episode = Episode("e1")
    episode.add_proposition(Proposition("o1", "e1", PropositionKind.OBSERVATION, "input"))
    node = RunnerNode(
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        FailedExecutor(),
        VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), 1).run(episode, "t-failed")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-failed" not in {p.proposition_id for p in episode.snapshot().current_propositions}
    assert outcome.trace.records[0].emitted_proposition_ids == ()


def test_result_receipt_and_trace_expose_source_versions_consumed_by_execution():
    class Verifier:
        def execute(self, view, episode_id):
            return ExecutionResult(
                view.execution_id,
                "verifier",
                verification_satisfied=True,
            )

    episode = Episode("e1")
    episode.add_proposition(Proposition(
        "ev1",
        "e1",
        PropositionKind.EVIDENCE,
        "versioned evidence",
        source_versions=("repo:policy@v2",),
    ))
    node = RunnerNode(
        NodeDescriptor("verifier", (PropositionKind.TEST_RESULT,), mandatory_verification=True),
        Verifier(),
        VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), 1).run(episode, "t-source")

    assert outcome.trace.records[0].source_versions == ("repo:policy@v2",)
    assert outcome.receipt.source_versions == ("repo:policy@v2",)


def test_bare_result_receipt_cannot_self_promote_to_qualified():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t-qualified",
            episode_version="e1@1",
            effect_state=EffectState.QUALIFIED,
        )
