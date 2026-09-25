from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _metadata() -> IndependenceMetadata:
    return IndependenceMetadata(
        executor_id="executor-b",
        model_id="model-b",
        provider_id="provider-b",
        prompt_lineage="prompt-b",
        context_lineage="context-b",
        saw_other_answer=False,
        common_evidence_refs=(),
        independence_basis_refs=("policy:independent-b",),
    )


def _legacy_policy(metadata: IndependenceMetadata) -> IndependenceVerificationPolicy:
    return IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref=metadata.independence_basis_refs[0],
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:independence-b",),
        ),
    ))


def _bound_policy(metadata: IndependenceMetadata) -> IndependenceVerificationPolicy:
    return IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref=metadata.independence_basis_refs[0],
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:independence-b",),
            saw_other_answer=metadata.saw_other_answer,
            common_evidence_refs=metadata.common_evidence_refs,
            consumed_evidence_refs=metadata.consumed_evidence_refs,
        ),
    ))


def test_external_policy_cannot_verify_unattested_negative_independence_claims():
    metadata = _metadata()
    policy = _legacy_policy(metadata)

    assert policy.verify(metadata) is False


def test_scheduled_independence_worker_cannot_read_peer_answer_relation():
    class RelationReader:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            leaked = next(
                relation
                for relation in view.relations
                if relation.relation_id == "peer-answer:H1"
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(
                    Proposition(
                        "derived-from-peer-relation",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        f"copied {leaked.relation_id}",
                        source_refs=(leaked.relation_id,),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    episode.add_proposition(
        Proposition("input-a", "e1", PropositionKind.OBSERVATION, "premise A")
    )
    episode.add_proposition(
        Proposition("input-b", "e1", PropositionKind.OBSERVATION, "premise B")
    )
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
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=RelationReader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=_bound_policy(metadata),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode, task_id="t-r6-relation-blind"
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "derived-from-peer-relation" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_external_policy_accepts_exact_negative_and_evidence_attestation():
    metadata = IndependenceMetadata(
        executor_id="executor-attested",
        model_id="model-attested",
        provider_id="provider-attested",
        prompt_lineage="prompt-attested",
        context_lineage="context-attested",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=("evidence:a",),
        independence_basis_refs=("policy:attested",),
    )
    assert _bound_policy(metadata).verify(metadata) is True


def test_pairwise_independence_rejects_shared_attested_consumed_evidence():
    left = IndependenceMetadata(
        executor_id="executor-left",
        model_id="model-left",
        provider_id="provider-left",
        prompt_lineage="prompt-left",
        context_lineage="context-left",
        saw_other_answer=False,
        consumed_evidence_refs=("evidence:shared",),
        independence_basis_refs=("policy:left",),
    )
    right = IndependenceMetadata(
        executor_id="executor-right",
        model_id="model-right",
        provider_id="provider-right",
        prompt_lineage="prompt-right",
        context_lineage="context-right",
        saw_other_answer=False,
        consumed_evidence_refs=("evidence:shared",),
        independence_basis_refs=("policy:right",),
    )

    assert _bound_policy(left).verify(left)
    assert _bound_policy(right).verify(right)
    assert left.demonstrably_independent_from(right) is False


def test_external_policy_rejects_mismatched_consumed_evidence_attestation():
    metadata = IndependenceMetadata(
        executor_id="executor-mismatch",
        model_id="model-mismatch",
        provider_id="provider-mismatch",
        prompt_lineage="prompt-mismatch",
        context_lineage="context-mismatch",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=("evidence:actual",),
        independence_basis_refs=("policy:mismatch",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:mismatch",
            executor_id="executor-mismatch",
            model_id="model-mismatch",
            provider_id="provider-mismatch",
            prompt_lineage="prompt-mismatch",
            context_lineage="context-mismatch",
            verification_refs=("review:mismatch",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=("evidence:different",),
        ),
    ))

    assert policy.verify(metadata) is False


def test_explicit_source_version_cannot_be_laundered_from_worker_output():
    class VersionLaunderer:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            emitted = Proposition(
                "h-version-launder",
                episode_id,
                PropositionKind.HYPOTHESIS,
                "candidate",
                source_refs=("o1",),
                source_versions=("repo:fake@v9",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(emitted,),
                source_versions=("repo:fake@v9",),
            )

    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            "o1",
            "e1",
            PropositionKind.OBSERVATION,
            "input",
            source_versions=("repo:policy@v1",),
        )
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor=VersionLaunderer(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode, task_id="t-version-launder"
    )

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "repo:fake@v9" not in outcome.receipt.source_versions
    assert "h-version-launder" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }
