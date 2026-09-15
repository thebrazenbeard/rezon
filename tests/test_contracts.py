import pytest

from rezon.envelopes import TaskEnvelope
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind, SupportKind
from rezon.receipts import (
    AdmissionStatus,
    EffectState,
    FailureState,
    IndependenceMetadata,
    ResultReceipt,
    RetrievalReceipt,
)
from rezon.subjects import SubjectBinding, SubjectBindingError


def test_task_envelope_preserves_literal_request_without_decomposition():
    env = TaskEnvelope(
        task_id="t1",
        literal_request="Use X to solve Y exactly as stated",
        subject_refs=("subject:1",),
        constraints=("no-network",),
        context_refs=("src:a",),
        available_authority=("read",),
        resource_budget=4,
    )
    assert env.literal_request == "Use X to solve Y exactly as stated"
    assert env.subject_refs == ("subject:1",)
    assert not hasattr(env, "inferred_goal")


def test_epistemic_types_do_not_collapse():
    p = Proposition("p1", "e1", PropositionKind.HYPOTHESIS, "maybe", confidence=0.9)
    assert p.kind is PropositionKind.HYPOTHESIS
    assert SupportKind.MODEL_JUDGMENT is not SupportKind.DIRECT_OBSERVATION
    assert PropositionKind.HYPOTHESIS is not PropositionKind.EVIDENCE


def test_hyperrelation_supports_many_role_bearing_participants():
    relation = Hyperrelation(
        relation_id="r1",
        episode_id="e1",
        relation_type="jointly_supports",
        participants=(
            Participant("p1", "premise"),
            Participant("p2", "premise"),
            Participant("p3", "conclusion"),
        ),
    )
    assert len(relation.participants) == 3
    with pytest.raises(ValueError):
        Hyperrelation("r2", "e1", "empty", ())


def test_failure_and_effect_states_are_explicit_and_distinct():
    assert FailureState.ATTEMPTED_UNKNOWN.value == "attempted_unknown"
    assert EffectState.SOURCE_VERIFIED.value == "source_verified"
    assert EffectState.SOURCE_VERIFIED is not EffectState.INSTALLED
    assert EffectState.INSTALLED is not EffectState.QUALIFIED


def test_retrieval_receipt_does_not_imply_admission():
    receipt = RetrievalReceipt(
        retrieval_id="ret1",
        query="current policy",
        source_id="repo:policy",
        source_version="abc123",
        method="exact_ref",
        returned_refs=("policy.md#L10",),
        admission_status=AdmissionStatus.RETRIEVED_ONLY,
    )
    assert receipt.admission_status is AdmissionStatus.RETRIEVED_ONLY
    assert receipt.source_version == "abc123"


def test_unknown_independence_is_not_independent():
    meta = IndependenceMetadata()
    assert meta.is_demonstrably_independent is False
    correlated = IndependenceMetadata(
        executor_id="x",
        model_id="same-model",
        provider_id="same-provider",
        prompt_lineage="prompt-a",
        context_lineage="context-a",
        saw_other_answer=True,
        common_evidence_refs=("src:1",),
    )
    assert correlated.is_demonstrably_independent is False


def test_subject_binding_requires_association_evidence():
    with pytest.raises(SubjectBindingError):
        SubjectBinding(subject_id="s1", observation_refs=("obs1",))
    binding = SubjectBinding(
        subject_id="s1",
        observation_refs=("obs1",),
        association_evidence_refs=("receipt:association",),
        advisory_similarity_refs=("embedding:nearest",),
    )
    assert binding.association_evidence_refs == ("receipt:association",)


def test_result_receipt_keeps_unresolved_failures_and_effect_state_visible():
    receipt = ResultReceipt(
        task_id="t1",
        episode_version="v7",
        accepted_claim_ids=("p1",),
        rejected_claim_ids=("p2",),
        unresolved=("conflict:r4",),
        failures=(FailureState.INSUFFICIENT_EVIDENCE,),
        effect_state=EffectState.SOURCE_VERIFIED,
        source_versions=("repo@abc",),
        execution_ids=("exec1",),
    )
    assert receipt.unresolved
    assert receipt.failures == (FailureState.INSUFFICIENT_EVIDENCE,)
    assert receipt.effect_state is EffectState.SOURCE_VERIFIED


def test_result_receipt_requires_exact_task_and_episode_subject():
    with pytest.raises(ValueError):
        ResultReceipt(task_id="", episode_version="e1@1")
    with pytest.raises(ValueError):
        ResultReceipt(task_id="t1", episode_version="")


def test_pairwise_independence_rejects_shared_model_provider_lineage():
    a = IndependenceMetadata(
        executor_id="a",
        model_id="m1",
        provider_id="p1",
        prompt_lineage="prompt-a",
        context_lineage="context-a",
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-generation",),
    )
    b = IndependenceMetadata(
        executor_id="b",
        model_id="m1",
        provider_id="p1",
        prompt_lineage="prompt-b",
        context_lineage="context-b",
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-generation",),
    )
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)
