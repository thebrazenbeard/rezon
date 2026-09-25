import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest
from rezon.receipts import IndependenceMetadata
from rezon.visibility import VisibilityPolicy, build_execution_view


def _p(pid, kind, content=None, producer=None):
    return Proposition(pid, "e1", kind, content or pid, producer_execution_id=producer)


def test_episode_retraction_preserves_history_and_removes_current_visibility():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.HYPOTHESIS))
    ep.retract_proposition("p1", "disproved")
    snap = ep.snapshot()
    assert "p1" not in {p.proposition_id for p in snap.current_propositions}
    assert "p1" in {p.proposition_id for p in snap.all_propositions}
    assert [e.event_type for e in snap.events] == ["proposition_added", "proposition_retracted"]


def test_duplicate_id_with_different_content_is_rejected():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM, "a"))
    with pytest.raises(EpisodeInvariantError):
        ep.add_proposition(_p("p1", PropositionKind.CLAIM, "b"))


def test_visibility_can_blind_hypotheses_and_records_withheld_ids():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("ev1", PropositionKind.EVIDENCE))
    ep.add_proposition(_p("h1", PropositionKind.HYPOTHESIS))
    view = build_execution_view(
        "x1",
        ep.snapshot(),
        VisibilityPolicy(blind_kinds=(PropositionKind.HYPOTHESIS,)),
        IndependenceMetadata(
            executor_id="independent-generator",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="fresh-prompt",
            context_lineage="view:x1",
            saw_other_answer=False,
            independence_basis_refs=("policy:blind-hypotheses",),
        ),
    )
    assert {p.proposition_id for p in view.propositions} == {"o1", "ev1"}
    assert view.blinded_proposition_ids == ("h1",)
    assert view.independence.is_demonstrably_independent


def test_output_admission_rejects_stronger_kind_than_descriptor_allows():
    ep = Episode("e1")
    descriptor = NodeDescriptor(
        node_id="generator",
        permitted_output_kinds=(PropositionKind.HYPOTHESIS,),
    )
    result = ExecutionResult(
        execution_id="x1",
        node_id="generator",
        emitted_propositions=(_p("evidence-launder", PropositionKind.EVIDENCE, producer="x1"),),
    )
    with pytest.raises(AdmissionError):
        admit_execution_result(
            ep,
            descriptor,
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(ep.snapshot()),
        )
    assert not ep.snapshot().current_propositions


def test_admitted_duplicate_hypotheses_remain_hypotheses():
    ep = Episode("e1")
    descriptor = NodeDescriptor("generator", (PropositionKind.HYPOTHESIS,))
    r1 = ExecutionResult("x1", "generator", (_p("h1", PropositionKind.HYPOTHESIS, "same", "x1"),))
    r2 = ExecutionResult("x2", "generator", (_p("h2", PropositionKind.HYPOTHESIS, "same", "x2"),))
    admit_execution_result(
        ep,
        descriptor,
        r1,
        expected_episode_snapshot_digest=canonical_episode_snapshot_digest(ep.snapshot()),
    )
    admit_execution_result(
        ep,
        descriptor,
        r2,
        expected_episode_snapshot_digest=canonical_episode_snapshot_digest(ep.snapshot()),
    )
    assert [p.kind for p in ep.snapshot().current_propositions] == [
        PropositionKind.HYPOTHESIS,
        PropositionKind.HYPOTHESIS,
    ]


def test_relation_participants_must_reference_existing_episode_objects():
    ep = Episode("e1")
    ep.add_proposition(_p("p1", PropositionKind.CLAIM))
    bad = Hyperrelation("r1", "e1", "supports", (Participant("missing", "premise"), Participant("p1", "claim")))
    with pytest.raises(EpisodeInvariantError):
        ep.add_relation(bad)


def test_execution_admission_is_atomic_when_late_relation_is_invalid():
    ep = Episode("e1")
    descriptor = NodeDescriptor("generator", (PropositionKind.HYPOTHESIS,))
    good = _p("h-new", PropositionKind.HYPOTHESIS, "new", "x1")
    bad_relation = Hyperrelation(
        "r-bad", "e1", "supports", (Participant("h-new", "claim"), Participant("missing", "source")),
        producer_execution_id="x1",
    )
    result = ExecutionResult("x1", "generator", (good,), (bad_relation,))
    with pytest.raises(AdmissionError):
        admit_execution_result(
            ep,
            descriptor,
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(ep.snapshot()),
        )
    assert ep.snapshot().current_propositions == ()
    assert ep.snapshot().current_relations == ()
