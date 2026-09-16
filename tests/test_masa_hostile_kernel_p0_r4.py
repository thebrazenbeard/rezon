import pytest

from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.executors import EchoHypothesisExecutor
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.receipts import EffectState, ResultReceipt
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _p(pid, kind, content=None, source_refs=()):
    return Proposition(pid, "e1", kind, content or pid, source_refs=tuple(source_refs))


def test_duplicate_node_ids_cannot_bypass_mandatory_verification_descriptor():
    class BypassExecutor:
        node_id = "verifier"

        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(
                    Proposition(
                        "bypass-hypothesis",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        "verification never actually ran",
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("target", PropositionKind.CLAIM, "claim under verification"))

    mandatory = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("target",),
        ),
        executor=None,
        visibility=VisibilityPolicy(),
    )
    shadow = RunnerNode(
        descriptor=NodeDescriptor("verifier", (PropositionKind.HYPOTHESIS,)),
        executor=BypassExecutor(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((mandatory, shadow), budget_limit=2).run(ep, task_id="t-dup")

    assert outcome.receipt.failures
    assert "bypass-hypothesis" not in {
        p.proposition_id for p in ep.snapshot().current_propositions
    }


def test_email_like_source_ref_is_not_misclassified_as_source_version():
    ep = Episode("e1")
    ep.add_proposition(
        _p(
            "o1",
            PropositionKind.OBSERVATION,
            "input",
            source_refs=("analyst@example.com",),
        )
    )
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=EchoHypothesisExecutor(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-source-version")

    assert "analyst@example.com" not in outcome.receipt.source_versions


def test_result_receipt_rejects_claim_disposition_complete_with_unresolved_claim_disposition():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t1",
            episode_version="e1@1",
            unresolved=("claim_disposition:c1",),
            claim_disposition_complete=True,
            effect_state=EffectState.PLAN,
        )


def test_result_receipt_cannot_assert_accepted_claims_without_governed_disposition_evidence():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t1",
            episode_version="e1@1",
            accepted_claim_ids=("c1",),
            claim_disposition_complete=True,
            effect_state=EffectState.PLAN,
        )
