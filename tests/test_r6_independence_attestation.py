from rezon.receipts import (
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)


def _metadata(*, basis: str = "policy:a") -> IndependenceMetadata:
    return IndependenceMetadata(
        executor_id="executor-a",
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="prompt-a",
        context_lineage="context-a",
        saw_other_answer=False,
        common_evidence_refs=(),
        independence_basis_refs=(basis,),
    )


def test_independence_policy_binds_negative_answer_exposure_attestation():
    metadata = _metadata()
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:a",
            executor_id="executor-a",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
            verification_refs=("review:a",),
            saw_other_answer=True,
            consumed_evidence_refs=(),
        ),
    ))

    assert not policy.verify(metadata)


def test_independence_policy_exposes_attested_consumed_evidence_for_pairwise_checking():
    metadata = _metadata()
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:a",
            executor_id="executor-a",
            model_id="model-a",
            provider_id="provider-a",
            prompt_lineage="prompt-a",
            context_lineage="context-a",
            verification_refs=("review:a",),
            saw_other_answer=False,
            consumed_evidence_refs=("source:shared",),
        ),
    ))

    evidence = policy.evidence_for(metadata)

    assert evidence is not None
    assert evidence.saw_other_answer is False
    assert evidence.consumed_evidence_refs == ("source:shared",)
