import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.executors import ContradictionScannerExecutor
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest
from rezon.receipts import FailureState, IndependenceMetadata
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _p(pid: str, kind: PropositionKind, content: str | None = None) -> Proposition:
    return Proposition(pid, "e1", kind, content or pid)


def test_add_relation_rejects_retracted_proposition_dependency():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    ep.add_proposition(_p("p2", PropositionKind.CLAIM))
    ep.retract_proposition("p1", "superseded")
    relation = Hyperrelation(
        "r1",
        "e1",
        "supports",
        (Participant("p1", "source"), Participant("p2", "target")),
    )
    with pytest.raises(EpisodeInvariantError):
        ep.add_relation(relation)


def test_add_relation_rejects_invalidated_relation_dependency_transitively():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    ep.add_proposition(_p("p2", PropositionKind.CLAIM))
    ep.add_relation(
        Hyperrelation(
            "r1",
            "e1",
            "supports",
            (Participant("p1", "source"), Participant("p2", "target")),
        )
    )
    ep.retract_proposition("p1", "superseded")
    with pytest.raises(EpisodeInvariantError):
        ep.add_relation(
            Hyperrelation(
                "r2",
                "e1",
                "supports",
                (Participant("r1", "source"), Participant("p2", "target")),
            )
        )


def test_admission_rejects_relation_to_inactive_dependency():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    ep.add_proposition(_p("p2", PropositionKind.CLAIM))
    ep.retract_proposition("p1", "superseded")
    descriptor = NodeDescriptor("relator", ())
    result = ExecutionResult(
        execution_id="x1",
        node_id="relator",
        emitted_relations=(
            Hyperrelation(
                "r1",
                "e1",
                "supports",
                (Participant("p1", "source"), Participant("p2", "target")),
                producer_execution_id="x1",
            ),
        ),
    )
    with pytest.raises(AdmissionError):
        admit_execution_result(
            ep,
            descriptor,
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(ep.snapshot()),
            expected_execution_id="x1",
        )


def test_scheduled_contradiction_cannot_disappear_behind_visibility():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM, "A"))
    ep.add_proposition(_p("b", PropositionKind.CLAIM, "not A"))
    ep.add_relation(
        Hyperrelation(
            "r1",
            "e1",
            "contradicts",
            (Participant("a", "left"), Participant("b", "right")),
        )
    )
    node = RunnerNode(
        descriptor=NodeDescriptor("contradiction_scanner", (PropositionKind.TEST_RESULT,)),
        executor=ContradictionScannerExecutor(),
        visibility=VisibilityPolicy(blind_ids=("a",)),
    )
    outcome = EpisodeRunner((node,), budget_limit=2).run(ep, task_id="t-visibility")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert outcome.receipt.unresolved


def test_independence_is_not_demonstrated_with_unknown_model_or_provider():
    metadata = IndependenceMetadata(
        executor_id="worker-a",
        prompt_lineage="fresh-prompt",
        context_lineage="fresh-context",
        saw_other_answer=False,
        independence_basis_refs=("policy:blind-hypotheses",),
    )
    assert metadata.is_demonstrably_independent is False


def test_independence_claim_fails_when_prior_hypothesis_is_visible():
    class IndependentGenerator:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            emitted = Proposition(
                "h-new",
                episode_id,
                PropositionKind.HYPOTHESIS,
                "new guess",
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(emitted,),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION, "machine stopped"))
    ep.add_proposition(_p("h-old", PropositionKind.HYPOTHESIS, "old guess"))
    metadata = IndependenceMetadata(
        executor_id="worker-a",
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="fresh-prompt",
        context_lineage="fresh-context",
        saw_other_answer=False,
        independence_basis_refs=("policy:blind-hypotheses",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=IndependentGenerator(),
        visibility=VisibilityPolicy(),
        independence=metadata,
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-independent")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-new" not in {p.proposition_id for p in ep.snapshot().current_propositions}


def test_independence_required_is_candidate_blind_for_any_trusted_policy_basis():
    class IndependentGenerator:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            emitted = Proposition(
                "h-new-generic",
                episode_id,
                PropositionKind.HYPOTHESIS,
                "new guess",
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(emitted,),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("h-old", PropositionKind.HYPOTHESIS, "candidate answer"))
    metadata = IndependenceMetadata(
        executor_id="worker-a",
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="fresh-prompt",
        context_lineage="fresh-context",
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-generation",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=IndependentGenerator(),
        visibility=VisibilityPolicy(),
        independence=metadata,
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-generic-independent")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h-new-generic" not in {p.proposition_id for p in ep.snapshot().current_propositions}


def test_mandatory_verifier_noop_is_not_clean_completion():
    class NoopVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            return ExecutionResult(execution_id=view.execution_id, node_id=self.node_id)

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("o1",),
        ),
        executor=NoopVerifier(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-verify")
    assert FailureState.INSUFFICIENT_EVIDENCE in outcome.receipt.failures
    assert outcome.receipt.unresolved


def test_failed_mandatory_verifier_remains_unresolved():
    class FailingVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                failures=(FailureState.INSUFFICIENT_EVIDENCE,),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("o1",),
        ),
        executor=FailingVerifier(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-failed-verify")
    assert FailureState.INSUFFICIENT_EVIDENCE in outcome.receipt.failures
    assert any(item.startswith("verification:") for item in outcome.receipt.unresolved)


def test_accepted_input_kinds_are_enforced_before_execution():
    class ObservationVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            result = Proposition(
                "t1",
                episode_id,
                PropositionKind.TEST_RESULT,
                "checked",
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(result,),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("h1", PropositionKind.HYPOTHESIS, "candidate"))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            accepted_input_kinds=(PropositionKind.OBSERVATION,),
            mandatory_verification=True,
            verification_target_ids=("h1",),
        ),
        executor=ObservationVerifier(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-input")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "t1" not in {p.proposition_id for p in ep.snapshot().current_propositions}


def test_trace_and_receipt_separate_consumed_from_worker_reported_provenance():
    class SourcedGenerator:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            emitted = Proposition(
                "h1",
                episode_id,
                PropositionKind.HYPOTHESIS,
                "candidate",
                source_refs=("o1",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(emitted,),
                source_refs=("repo:reported@v9",),
                source_versions=("repo:reported@v9",),
            )

    ep = Episode("e1")
    ep.add_proposition(Proposition(
        "o1",
        "e1",
        PropositionKind.OBSERVATION,
        "observed",
        source_refs=("repo:policy@abc123",),
        source_versions=("repo:policy@abc123",),
    ))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=SourcedGenerator(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-provenance")
    record = outcome.trace.records[0]
    assert record.source_refs == ("repo:policy@abc123",)
    assert record.reported_source_refs == ("repo:reported@v9",)
    assert record.reported_source_versions == ("repo:reported@v9",)
    assert record.duration_seconds >= 0
    assert outcome.receipt.source_versions == ("repo:policy@abc123",)
