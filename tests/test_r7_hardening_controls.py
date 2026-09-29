from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _policy(metadata: IndependenceMetadata) -> IndependenceVerificationPolicy:
    return IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref=metadata.independence_basis_refs[0],
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r7-positive",),
            saw_other_answer=False,
            common_evidence_refs=metadata.common_evidence_refs,
            consumed_evidence_refs=metadata.consumed_evidence_refs,
        ),
    ))


def test_independence_with_exact_visible_evidence_attestation_can_run():
    class Reader:
        def execute(self, view, episode_id):
            evidence = next(p for p in view.propositions if p.proposition_id == "ev1")
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        "h1",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        f"derived:{evidence.content}",
                        source_refs=("ev1",),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    episode.add_proposition(
        Proposition("ev1", "e1", PropositionKind.EVIDENCE, "independent evidence")
    )
    metadata = IndependenceMetadata(
        executor_id="executor-r7",
        model_id="model-r7",
        provider_id="provider-r7",
        prompt_lineage="prompt-r7",
        context_lineage="context-r7",
        saw_other_answer=False,
        consumed_evidence_refs=("ev1",),
        independence_basis_refs=("policy:r7-positive",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=Reader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=_policy(metadata),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(episode, task_id="t-r7-pos")
    assert outcome.receipt.failures == ()
    assert "h1" in {p.proposition_id for p in episode.snapshot().current_propositions}


def test_matching_source_ref_version_pair_from_same_input_is_admitted():
    class PairPreserver:
        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="echo_hypothesis",
                emitted_propositions=(
                    Proposition(
                        "h-pair",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        "preserved pair",
                        source_refs=("source:A",),
                        source_versions=("source:A@v1",),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            "a",
            "e1",
            PropositionKind.OBSERVATION,
            "A",
            source_refs=("source:A",),
            source_versions=("source:A@v1",),
        )
    )
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=PairPreserver(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(episode, task_id="t-r7-pair")
    assert outcome.receipt.failures == ()
    assert "h-pair" in {
        p.proposition_id for p in episode.snapshot().current_propositions
    }
