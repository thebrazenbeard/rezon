from rezon.episode import Episode, EpisodeSnapshot
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class CanonicalMutator:
    node_id = "echo_hypothesis"

    def __init__(self, episode):
        self.episode = episode
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        Episode.add_proposition(
            self.episode,
            Proposition(
                "side",
                "e1",
                PropositionKind.OBSERVATION,
                "direct canonical mutation hidden by instance-shadowed snapshot",
            ),
        )
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "returned",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "ordinary returned candidate",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def test_exact_episode_instance_cannot_shadow_snapshot_to_defeat_rollback():
    episode = Episode("e1")
    fake = EpisodeSnapshot(
        episode_id="e1",
        version=0,
        current_propositions=(),
        all_propositions=(),
        current_relations=(),
        all_relations=(),
        events=(),
    )
    episode.snapshot = lambda: fake

    executor = CanonicalMutator(episode)
    node = RunnerNode(
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor,
        VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r38",
    )

    assert executor.calls == 1
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert any(
        item.startswith("executor_episode_mutation:")
        for item in outcome.receipt.unresolved
    )
    assert Episode.snapshot(episode) == fake


def test_direct_admission_cannot_be_neutered_by_shadowed_add_proposition():
    from rezon.admission import admit_execution_result
    from rezon.provenance import canonical_episode_snapshot_digest

    episode = Episode("e2")
    episode.add_proposition = lambda proposition: None
    before = Episode.snapshot(episode)
    descriptor = NodeDescriptor(
        "echo_hypothesis",
        (PropositionKind.HYPOTHESIS,),
    )
    result = ExecutionResult(
        execution_id="attempt-1",
        node_id="echo_hypothesis",
        emitted_propositions=(
            Proposition(
                "admitted",
                "e2",
                PropositionKind.HYPOTHESIS,
                "must become canonical despite instance shadow",
                producer_execution_id="attempt-1",
            ),
        ),
    )

    admit_execution_result(
        episode,
        descriptor,
        result,
        expected_execution_id="attempt-1",
        expected_episode_snapshot_digest=canonical_episode_snapshot_digest(before),
    )

    assert "admitted" in {
        proposition.proposition_id
        for proposition in Episode.snapshot(episode).current_propositions
    }


def test_retrieval_admission_cannot_be_neutered_by_shadowed_add_proposition():
    from rezon.receipts import AdmissionStatus, RetrievalReceipt
    from rezon.retrieval import (
        RetrievalAdmissionEvidence,
        RetrievalAdmissionPolicy,
        admit_retrieval_as_evidence,
        digest_retrieved_content,
    )

    content = "verified retrieval content"
    episode = Episode("e3")
    episode.add_proposition = lambda proposition: None
    receipt = RetrievalReceipt(
        retrieval_id="ret-r38",
        query="query",
        source_id="repo:source",
        source_version="abc123",
        method="exact_ref",
        returned_refs=("source.md#1",),
        admission_status=AdmissionStatus.ADMITTED,
    )
    evidence = RetrievalAdmissionEvidence(
        source_id="repo:source",
        source_version="abc123",
        admission_authority_ref="review:admission",
        verification_refs=("receipt:verified",),
        currentness_ref="receipt:current",
        authoritative_scope="scope/current",
        content_digest=digest_retrieved_content(content),
        locator_refs=("source.md#1",),
    )

    admitted = admit_retrieval_as_evidence(
        episode,
        receipt,
        "ev-r38",
        content,
        policy=RetrievalAdmissionPolicy((evidence,)),
        required_scope="scope/current",
    )

    assert admitted.proposition_id == "ev-r38"
    assert "ev-r38" in {
        proposition.proposition_id
        for proposition in Episode.snapshot(episode).current_propositions
    }
