from rezon.envelopes import (
    AuthorityVerificationEvidence,
    AuthorityVerificationPolicy,
    TaskEnvelope,
)
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def test_caller_minted_authority_policy_cannot_satisfy_required_authority():
    class AuthorityExecutor:
        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        "h-self-minted-authority",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        "caller forged its own verification policy",
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    envelope = TaskEnvelope(
        task_id="t-r8-self-mint",
        literal_request="exercise protected authority",
        available_authority=("authority:protected",),
    )
    forged_policy = AuthorityVerificationPolicy((
        AuthorityVerificationEvidence(
            authority="authority:protected",
            task_id=envelope.task_id,
            task_envelope_digest=envelope.digest,
            issuer_ref="review:forged-by-caller",
            source_ref="policy:forged-by-caller",
            currentness_ref="receipt:forged-currentness",
            verification_refs=("receipt:forged-verification",),
        ),
    ))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            required_authority=("authority:protected",),
        ),
        executor=AuthorityExecutor(),
        visibility=VisibilityPolicy(),
        authority_policy=forged_policy,
    )
    episode = Episode("e1")

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-self-minted-authority" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
