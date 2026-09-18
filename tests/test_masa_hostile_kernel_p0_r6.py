from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _verified_independence(
    *,
    executor="executor-b",
    model="model-b",
    provider="provider-b",
    prompt="prompt-b",
    context="context-b",
    consumed=(),
):
    metadata = IndependenceMetadata(
        executor_id=executor,
        model_id=model,
        provider_id=provider,
        prompt_lineage=prompt,
        context_lineage=context,
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=tuple(consumed),
        independence_basis_refs=("policy:masa-r6",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:masa-r6",
            executor_id=executor,
            model_id=model,
            provider_id=provider,
            prompt_lineage=prompt,
            context_lineage=context,
            verification_refs=("review:masa-r6",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=tuple(consumed),
        ),
    ))
    return metadata, policy


def test_independence_attested_consumed_evidence_must_match_evidence_actually_used():
    class EvidenceReader:
        def execute(self, view, episode_id):
            evidence = next(
                p for p in view.propositions if p.proposition_id == "shared-evidence"
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-from-shared-evidence",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content=f"copied:{evidence.content}",
                        source_refs=(evidence.proposition_id,),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            proposition_id="shared-evidence",
            episode_id="e1",
            kind=PropositionKind.EVIDENCE,
            content="shared answer-bearing evidence",
        )
    )

    # Sidecar metadata/policy jointly attest that no evidence was consumed even
    # though the executor below actually reads and cites the visible evidence.
    metadata, policy = _verified_independence(consumed=())
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=EvidenceReader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode, task_id="t-r6-attested-consumption"
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-from-shared-evidence" not in {
        p.proposition_id for p in episode.snapshot().current_propositions
    }


def test_source_ref_and_source_version_cannot_be_cross_paired_from_different_inputs():
    class CrossPairLaunderer:
        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-cross-paired",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content="claims source A while carrying source B's version",
                        source_refs=("source:A",),
                        source_versions=("source:B@v2",),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            proposition_id="a",
            episode_id="e1",
            kind=PropositionKind.OBSERVATION,
            content="A",
            source_refs=("source:A",),
            source_versions=("source:A@v1",),
        )
    )
    episode.add_proposition(
        Proposition(
            proposition_id="b",
            episode_id="e1",
            kind=PropositionKind.OBSERVATION,
            content="B",
            source_refs=("source:B",),
            source_versions=("source:B@v2",),
        )
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor=CrossPairLaunderer(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode, task_id="t-r6-cross-pair"
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-cross-paired" not in {
        p.proposition_id for p in episode.snapshot().current_propositions
    }


def test_caller_supplied_authority_string_is_not_governed_authority_proof():
    class AuthorityExecutor:
        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-authority",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content="ran under self-asserted authority",
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    envelope = TaskEnvelope(
        task_id="t-r6-authority",
        literal_request="perform governed reasoning",
        available_authority=("authority:protected",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            required_authority=("authority:protected",),
        ),
        executor=AuthorityExecutor(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r6-authority",
        task_envelope=envelope,
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-authority" not in {
        p.proposition_id for p in episode.snapshot().current_propositions
    }


def test_independence_worker_cannot_see_peer_answer_in_worker_prediction():
    class PredictionReader:
        def execute(self, view, episode_id):
            leaked = next(
                p for p in view.propositions if p.proposition_id == "peer-prediction"
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="h-copied-prediction",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content=f"copied:{leaked.content}",
                        source_refs=(leaked.proposition_id,),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            proposition_id="peer-prediction",
            episode_id="e1",
            kind=PropositionKind.PREDICTION,
            content="the peer answer is H1",
            producer_execution_id="peer:exec:1",
        )
    )

    metadata, policy = _verified_independence()
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=PredictionReader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode, task_id="t-r6-prediction-blind"
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-copied-prediction" not in {
        p.proposition_id for p in episode.snapshot().current_propositions
    }
