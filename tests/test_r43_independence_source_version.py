from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.receipts import (
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class Verifier:
    def __init__(self, node_id, target_id, proposition_id):
        self.node_id = node_id
        self.target_id = target_id
        self.proposition_id = proposition_id
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    self.proposition_id,
                    episode_id,
                    PropositionKind.TEST_RESULT,
                    "passed",
                    source_refs=(self.target_id,),
                    producer_execution_id=view.execution_id,
                ),
            ),
            verification_status=VerificationStatus.PASSED,
            verification_target_ids=(self.target_id,),
        )


def _metadata(label, consumed):
    return IndependenceMetadata(
        executor_id=f"executor-{label}",
        model_id=f"model-{label}",
        provider_id=f"provider-{label}",
        prompt_lineage=f"prompt-{label}",
        context_lineage=f"context-{label}",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=consumed,
        independence_basis_refs=(f"policy:{label}",),
    )


def _policy(label, metadata):
    return IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref=f"policy:{label}",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=(f"review:{label}",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=metadata.consumed_evidence_refs,
        ),
    ))


def _node(label, target_id, source_ref, source_version):
    metadata = _metadata(label, (target_id, source_ref))
    executor = Verifier(f"verifier-{label}", target_id, f"t{label}")
    node = RunnerNode(
        NodeDescriptor(
            f"verifier-{label}",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            independence_required=True,
            verification_target_ids=(target_id,),
        ),
        executor,
        VisibilityPolicy(allow_ids=(target_id,)),
        metadata,
        _policy(label, metadata),
    )
    evidence = Proposition(
        target_id,
        "e1",
        PropositionKind.EVIDENCE,
        f"evidence {label}",
        source_refs=(source_ref,),
        source_versions=(source_version,),
    )
    return node, executor, evidence


def test_independence_rejects_distinct_evidence_refs_with_same_source_version():
    left, left_executor, left_evidence = _node(
        "a", "ev-a", "src:a", "source@v1"
    )
    right, right_executor, right_evidence = _node(
        "b", "ev-b", "src:b", "source@v1"
    )

    episode = Episode("e1")
    episode.add_proposition(left_evidence)
    episode.add_proposition(right_evidence)

    outcome = EpisodeRunner((left, right), budget_limit=2).run(
        episode,
        task_id="t-r43",
    )

    assert left_executor.calls == 1
    assert right_executor.calls == 0
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "independence:verifier-b" in outcome.receipt.unresolved
    assert tuple(record.independence_demonstrated for record in outcome.trace.records) == (
        True,
        False,
    )
    assert "tb" not in {
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    }


def test_independence_allows_distinct_evidence_with_distinct_source_versions():
    left, left_executor, left_evidence = _node(
        "a", "ev-a", "src:a", "source-a@v1"
    )
    right, right_executor, right_evidence = _node(
        "b", "ev-b", "src:b", "source-b@v1"
    )

    episode = Episode("e1")
    episode.add_proposition(left_evidence)
    episode.add_proposition(right_evidence)

    outcome = EpisodeRunner((left, right), budget_limit=2).run(
        episode,
        task_id="t-r43",
    )

    assert outcome.receipt.failures == ()
    assert not outcome.receipt.unresolved
    assert left_executor.calls == 1
    assert right_executor.calls == 1
    assert tuple(record.independence_demonstrated for record in outcome.trace.records) == (
        True,
        True,
    )
