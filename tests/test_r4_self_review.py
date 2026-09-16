import pytest

from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _p(pid: str, kind: PropositionKind, *, source_refs=()):
    return Proposition(pid, "e1", kind, pid, source_refs=tuple(source_refs))


def test_new_derived_proposition_cannot_depend_on_retracted_canonical_source():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.retract_proposition("o1", "superseded")

    with pytest.raises(EpisodeInvariantError):
        ep.add_proposition(_p("h1", PropositionKind.HYPOTHESIS, source_refs=("o1",)))


def test_mandatory_verifier_cannot_choose_a_different_visible_target():
    class TargetSwitchingVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            result = Proposition(
                "t1",
                episode_id,
                PropositionKind.TEST_RESULT,
                "verified o2 instead",
                source_refs=("o2",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(result,),
                verification_status=VerificationStatus.PASSED,
                verification_target_ids=("o2",),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("o2", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("o1",),
        ),
        executor=TargetSwitchingVerifier(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-target-switch")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert any(item.startswith("verification:") for item in outcome.receipt.unresolved)
    assert "t1" not in {p.proposition_id for p in ep.snapshot().current_propositions}
