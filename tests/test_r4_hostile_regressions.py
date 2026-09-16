import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    EffectState,
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
    ResultReceipt,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy, build_execution_view


def _p(pid, kind, content=None, *, source_refs=(), producer=None):
    return Proposition(
        proposition_id=pid,
        episode_id="e1",
        kind=kind,
        content=content or pid,
        source_refs=tuple(source_refs),
        producer_execution_id=producer,
    )


def _policy(metadata: IndependenceMetadata) -> IndependenceVerificationPolicy:
    return IndependenceVerificationPolicy((IndependenceVerificationEvidence(
        basis_ref=metadata.independence_basis_refs[0],
        executor_id=metadata.executor_id,
        model_id=metadata.model_id,
        provider_id=metadata.provider_id,
        prompt_lineage=metadata.prompt_lineage,
        context_lineage=metadata.context_lineage,
        verification_refs=("receipt:independence-verified",),
    ),))


def test_relation_id_blinding_is_enforced_in_execution_view():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM))
    ep.add_proposition(_p("b", PropositionKind.CLAIM))
    ep.add_relation(Hyperrelation(
        "r-secret",
        "e1",
        "supports",
        (Participant("a", "source"), Participant("b", "target")),
    ))

    view = build_execution_view(
        "exec-1",
        ep.snapshot(),
        VisibilityPolicy(blind_ids=("r-secret",)),
    )

    assert "r-secret" not in {relation.relation_id for relation in view.relations}
    assert "r-secret" in view.blinded_relation_ids


def test_relation_id_allowlist_does_not_leak_extra_relations():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM))
    ep.add_proposition(_p("b", PropositionKind.CLAIM))
    ep.add_relation(Hyperrelation(
        "r-allowed",
        "e1",
        "supports",
        (Participant("a", "source"), Participant("b", "target")),
    ))
    ep.add_relation(Hyperrelation(
        "r-extra",
        "e1",
        "contradicts",
        (Participant("a", "left"), Participant("b", "right")),
    ))

    view = build_execution_view(
        "exec-1",
        ep.snapshot(),
        VisibilityPolicy(allow_ids=("a", "b", "r-allowed")),
    )

    assert tuple(relation.relation_id for relation in view.relations) == ("r-allowed",)
    assert "r-extra" in view.blinded_relation_ids


def test_node_without_relation_capability_cannot_emit_relation():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM))
    ep.add_proposition(_p("b", PropositionKind.CLAIM))
    descriptor = NodeDescriptor("relator", (PropositionKind.HYPOTHESIS,))
    result = ExecutionResult(
        execution_id="exec-1",
        node_id="relator",
        emitted_relations=(Hyperrelation(
            "r1",
            "e1",
            "supports",
            (Participant("a", "source"), Participant("b", "target")),
            producer_execution_id="exec-1",
        ),),
    )

    with pytest.raises(AdmissionError):
        admit_execution_result(ep, descriptor, result, expected_execution_id="exec-1")
    assert ep.snapshot().current_relations == ()


def test_declared_relation_capability_allows_exact_relation_type():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM))
    ep.add_proposition(_p("b", PropositionKind.CLAIM))
    descriptor = NodeDescriptor(
        "relator",
        (),
        permitted_relation_types=("supports",),
    )
    result = ExecutionResult(
        execution_id="exec-1",
        node_id="relator",
        emitted_relations=(Hyperrelation(
            "r1",
            "e1",
            "supports",
            (Participant("a", "source"), Participant("b", "target")),
            producer_execution_id="exec-1",
        ),),
    )

    admit_execution_result(ep, descriptor, result, expected_execution_id="exec-1")
    assert tuple(r.relation_id for r in ep.snapshot().current_relations) == ("r1",)


def test_worker_reported_provenance_cannot_be_laundered_into_consumed_receipt_state():
    class ProvenanceLaunderer:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            emitted = Proposition(
                "h-fake",
                episode_id,
                PropositionKind.HYPOTHESIS,
                "candidate",
                source_refs=("repo:fake@v999",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(emitted,),
                source_refs=("repo:fake@v999",),
                source_versions=("repo:fake@v999",),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=ProvenanceLaunderer(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-prov")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "repo:fake@v999" not in outcome.receipt.source_versions
    assert "h-fake" not in {p.proposition_id for p in ep.snapshot().current_propositions}
    record = outcome.trace.records[0]
    assert record.source_versions == ()
    assert record.reported_source_versions == ("repo:fake@v999",)


def test_retracting_internal_source_invalidates_derived_proposition_transitively():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("h1", PropositionKind.HYPOTHESIS, source_refs=("o1",)))
    ep.add_proposition(_p("c1", PropositionKind.CLAIM, source_refs=("h1",)))

    ep.retract_proposition("o1", "superseded")

    current_ids = {p.proposition_id for p in ep.snapshot().current_propositions}
    assert "h1" not in current_ids
    assert "c1" not in current_ids
    invalidated = {
        event.target_id
        for event in ep.snapshot().events
        if event.event_type == "proposition_invalidated"
    }
    assert {"h1", "c1"}.issubset(invalidated)


def test_external_source_locator_is_not_mistaken_for_internal_dependency():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p(
        "h1",
        PropositionKind.HYPOTHESIS,
        source_refs=("repo:policy@abc123",),
    ))

    ep.retract_proposition("o1", "superseded")

    assert "h1" in {p.proposition_id for p in ep.snapshot().current_propositions}


class _Verifier:
    node_id = "verifier"

    def __init__(self, satisfied, targets):
        self.satisfied = satisfied
        self.targets = targets

    def execute(self, view, episode_id):
        result = Proposition(
            "t1",
            episode_id,
            PropositionKind.TEST_RESULT,
            "verification result",
            source_refs=("o1",),
            producer_execution_id=view.execution_id,
        )
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(result,),
            verification_satisfied=self.satisfied,
            verification_target_ids=tuple(self.targets),
        )


def test_negative_mandatory_verification_cannot_be_mistaken_for_success():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
        ),
        executor=_Verifier(False, ("o1",)),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-negative")

    assert FailureState.INSUFFICIENT_EVIDENCE in outcome.receipt.failures
    assert any(item.startswith("verification:") for item in outcome.receipt.unresolved)


def test_positive_mandatory_verification_requires_machine_readable_target_binding():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
        ),
        executor=_Verifier(True, ("o1",)),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-positive")

    assert outcome.receipt.failures == ()
    assert outcome.receipt.unresolved == ()


def test_mandatory_verification_rejects_nonvisible_target_binding():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
        ),
        executor=_Verifier(True, ("not-visible",)),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-target")

    assert FailureState.INSUFFICIENT_EVIDENCE in outcome.receipt.failures
    assert any(item.startswith("verification:") for item in outcome.receipt.unresolved)


@pytest.mark.parametrize(
    "state",
    [state for state in EffectState if state is not EffectState.PLAN],
)
def test_result_receipt_cannot_self_promote_any_lifecycle_state(state):
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t-effect",
            episode_version="e1@0",
            effect_state=state,
        )


@pytest.mark.parametrize("answer_kind", (PropositionKind.CLAIM, PropositionKind.DECISION))
def test_independence_fails_closed_when_answer_bearing_nonhypothesis_is_visible(answer_kind):
    class ShouldNotRun:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            raise AssertionError("answer-contaminated independent worker must not execute")

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("peer-answer", answer_kind, "peer conclusion"))
    metadata = IndependenceMetadata(
        executor_id="independent-worker",
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="prompt:fresh",
        context_lineage="context:fresh",
        saw_other_answer=False,
        independence_basis_refs=("policy:blind-peer-answers",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=ShouldNotRun(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=_policy(metadata),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-independent")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert outcome.trace.records
    assert outcome.trace.records[0].independence_demonstrated is False
