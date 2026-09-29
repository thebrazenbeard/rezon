import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.provenance import canonical_episode_snapshot_digest
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy, build_execution_view


def _p(pid: str, kind: PropositionKind, content: str | None = None, *, source_refs=(), producer=None):
    return Proposition(
        pid,
        "e1",
        kind,
        content or pid,
        source_refs=tuple(source_refs),
        producer_execution_id=producer,
    )


def _relation(rid: str, relation_type: str = "supports", *, producer=None):
    return Hyperrelation(
        rid,
        "e1",
        relation_type,
        (Participant("p1", "source"), Participant("p2", "target")),
        producer_execution_id=producer,
    )


def test_relation_id_blinding_survives_visible_participants():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    ep.add_proposition(_p("p2", PropositionKind.CLAIM))
    ep.add_relation(_relation("r1"))

    view = build_execution_view(
        "x1",
        ep.snapshot(),
        VisibilityPolicy(blind_ids=("r1",)),
    )

    assert {p.proposition_id for p in view.propositions} == {"p1", "p2"}
    assert view.relations == ()
    assert view.blinded_relation_ids == ("r1",)


def test_relation_id_allowlist_suppresses_unlisted_relation():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    ep.add_proposition(_p("p2", PropositionKind.CLAIM))
    ep.add_relation(_relation("r1"))

    hidden = build_execution_view(
        "x1",
        ep.snapshot(),
        VisibilityPolicy(allow_ids=("p1", "p2")),
    )
    visible = build_execution_view(
        "x2",
        ep.snapshot(),
        VisibilityPolicy(allow_ids=("p1", "p2", "r1")),
    )

    assert hidden.relations == ()
    assert hidden.blinded_relation_ids == ("r1",)
    assert tuple(r.relation_id for r in visible.relations) == ("r1",)


def test_relation_emission_requires_explicit_descriptor_capability():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    ep.add_proposition(_p("p2", PropositionKind.CLAIM))
    result = ExecutionResult(
        execution_id="x1",
        node_id="relator",
        emitted_relations=(_relation("r1", "contradicts", producer="x1"),),
    )

    with pytest.raises(AdmissionError):
        admit_execution_result(
            ep,
            NodeDescriptor("relator", ()),
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
                ep.snapshot()
            ),
            expected_execution_id="x1",
            allowed_source_refs=("p1", "p2"),
        )


def test_relation_emission_accepts_only_declared_relation_type():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    ep.add_proposition(_p("p2", PropositionKind.CLAIM))
    result = ExecutionResult(
        execution_id="x1",
        node_id="relator",
        emitted_relations=(_relation("r1", "supports", producer="x1"),),
    )
    descriptor = NodeDescriptor("relator", (), permitted_relation_types=("supports",))

    admit_execution_result(
        ep,
        descriptor,
        result,
        expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
            ep.snapshot()
        ),
        expected_execution_id="x1",
        allowed_source_refs=("p1", "p2"),
    )

    assert tuple(r.relation_id for r in ep.snapshot().current_relations) == ("r1",)


def test_worker_cannot_launder_unconsumed_source_into_canonical_or_receipt_provenance():
    class FabricatingWorker:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            emitted = Proposition(
                "h-fake",
                episode_id,
                PropositionKind.HYPOTHESIS,
                "fabricated provenance",
                source_refs=("repo:fake@v9",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(emitted,),
                source_refs=("repo:fake@v9",),
                source_versions=("repo:fake@v9",),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=FabricatingWorker(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-provenance-fabrication")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "repo:fake@v9" not in outcome.receipt.source_versions
    assert "h-fake" not in {p.proposition_id for p in ep.snapshot().current_propositions}
    record = outcome.trace.records[0]
    assert record.source_versions == ()
    assert record.reported_source_versions == ("repo:fake@v9",)


def test_retracting_support_source_invalidates_derived_propositions_transitively():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("h1", PropositionKind.HYPOTHESIS, source_refs=("o1",)))
    ep.add_proposition(_p("c1", PropositionKind.CLAIM, source_refs=("h1",)))

    ep.retract_proposition("o1", "superseded")
    snapshot = ep.snapshot()

    assert {p.proposition_id for p in snapshot.current_propositions} == set()
    assert {p.proposition_id for p in snapshot.all_propositions} == {"o1", "h1", "c1"}
    invalidated = {
        event.target_id
        for event in snapshot.events
        if event.event_type == "proposition_invalidated"
    }
    assert invalidated == {"h1", "c1"}


def test_inconclusive_test_result_cannot_satisfy_mandatory_verification():
    class InconclusiveVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            result = Proposition(
                "t-inconclusive",
                episode_id,
                PropositionKind.TEST_RESULT,
                "could not determine",
                source_refs=("o1",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(result,),
                verification_status=VerificationStatus.INCONCLUSIVE,
                verification_target_ids=("o1",),
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
        executor=InconclusiveVerifier(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-inconclusive")

    assert FailureState.INSUFFICIENT_EVIDENCE in outcome.receipt.failures
    assert any(item.startswith("verification:") for item in outcome.receipt.unresolved)


def test_passed_mandatory_verification_is_explicit_and_target_bound():
    class PassingVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            result = Proposition(
                "t-passed",
                episode_id,
                PropositionKind.TEST_RESULT,
                "verified",
                source_refs=("o1",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(result,),
                verification_status=VerificationStatus.PASSED,
                verification_target_ids=("o1",),
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
        executor=PassingVerifier(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-passed")

    assert outcome.receipt.failures == ()
    assert not any(item.startswith("verification:") for item in outcome.receipt.unresolved)
    assert "t-passed" in {p.proposition_id for p in ep.snapshot().current_propositions}


def test_mandatory_verification_target_must_be_visible_and_cited_by_test_result():
    class MisboundVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            result = Proposition(
                "t-misbound",
                episode_id,
                PropositionKind.TEST_RESULT,
                "verified something else",
                source_refs=("o1",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(result,),
                verification_status=VerificationStatus.PASSED,
                verification_target_ids=("missing-target",),
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
        executor=MisboundVerifier(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-misbound")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert any(item.startswith("verification:") for item in outcome.receipt.unresolved)
    assert "t-misbound" not in {p.proposition_id for p in ep.snapshot().current_propositions}


def test_runner_explicitly_marks_current_claims_as_undispositioned():
    ep = Episode("e1")
    ep.add_proposition(_p("c1", PropositionKind.CLAIM, "candidate claim"))

    outcome = EpisodeRunner((), budget_limit=0).run(ep, task_id="t-claim-disposition")

    assert outcome.receipt.accepted_claim_ids == ()
    assert outcome.receipt.rejected_claim_ids == ()
    assert outcome.receipt.claim_disposition_complete is False
    assert "claim_disposition:c1" in outcome.receipt.unresolved
