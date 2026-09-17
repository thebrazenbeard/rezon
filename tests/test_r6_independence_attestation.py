from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _metadata(
    *,
    basis: str = "policy:a",
    executor: str = "executor-a",
    model: str = "model-a",
    provider: str = "provider-a",
    prompt: str = "prompt-a",
    context: str = "context-a",
) -> IndependenceMetadata:
    return IndependenceMetadata(
        executor_id=executor,
        model_id=model,
        provider_id=provider,
        prompt_lineage=prompt,
        context_lineage=context,
        saw_other_answer=False,
        common_evidence_refs=(),
        independence_basis_refs=(basis,),
    )


def _evidence(
    *,
    basis: str = "policy:a",
    executor: str = "executor-a",
    model: str = "model-a",
    provider: str = "provider-a",
    prompt: str = "prompt-a",
    context: str = "context-a",
    saw_other_answer: bool = False,
    consumed_evidence_refs: tuple[str, ...] = (),
) -> IndependenceVerificationEvidence:
    return IndependenceVerificationEvidence(
        basis_ref=basis,
        executor_id=executor,
        model_id=model,
        provider_id=provider,
        prompt_lineage=prompt,
        context_lineage=context,
        verification_refs=(f"review:{basis}",),
        saw_other_answer=saw_other_answer,
        consumed_evidence_refs=consumed_evidence_refs,
    )


def test_independence_policy_binds_negative_answer_exposure_attestation():
    metadata = _metadata()
    policy = IndependenceVerificationPolicy((
        _evidence(saw_other_answer=True),
    ))

    assert not policy.verify(metadata)


def test_independence_policy_exposes_attested_consumed_evidence_for_pairwise_checking():
    metadata = _metadata()
    policy = IndependenceVerificationPolicy((
        _evidence(consumed_evidence_refs=("source:shared",)),
    ))

    evidence = policy.evidence_for(metadata)

    assert evidence is not None
    assert evidence.saw_other_answer is False
    assert evidence.consumed_evidence_refs == ("source:shared",)


def test_pairwise_external_attestation_rejects_overlapping_consumed_evidence():
    metadata_a = _metadata()
    metadata_b = _metadata(
        basis="policy:b",
        executor="executor-b",
        model="model-b",
        provider="provider-b",
        prompt="prompt-b",
        context="context-b",
    )
    policy_a = IndependenceVerificationPolicy((
        _evidence(consumed_evidence_refs=("source:shared",)),
    ))
    policy_b = IndependenceVerificationPolicy((
        _evidence(
            basis="policy:b",
            executor="executor-b",
            model="model-b",
            provider="provider-b",
            prompt="prompt-b",
            context="context-b",
            consumed_evidence_refs=("source:shared",),
        ),
    ))

    assert not policy_a.attested_independent_from(
        metadata_a,
        policy_b,
        metadata_b,
    )


def test_independence_required_schedulable_worker_cannot_read_peer_answer_relation():
    class RelationReader:
        def execute(self, view, episode_id):
            leaked = next(r for r in view.relations if r.relation_id == "peer-answer:H1")
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        proposition_id="copied-peer-answer",
                        episode_id=episode_id,
                        kind=PropositionKind.HYPOTHESIS,
                        content=leaked.relation_id,
                        source_refs=(leaked.relation_id,),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    episode.add_proposition(Proposition("input-a", "e1", PropositionKind.OBSERVATION, "A"))
    episode.add_proposition(Proposition("input-b", "e1", PropositionKind.OBSERVATION, "B"))
    episode.add_relation(
        Hyperrelation(
            relation_id="peer-answer:H1",
            episode_id="e1",
            relation_type="peer_conclusion",
            participants=(
                Participant("input-a", "premise"),
                Participant("input-b", "premise"),
            ),
            producer_execution_id="peer:exec:1",
        )
    )
    metadata = _metadata()
    policy = IndependenceVerificationPolicy((_evidence(),))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=RelationReader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(episode, task_id="t-relation-r6")

    assert outcome.receipt.failures
    assert "copied-peer-answer" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
