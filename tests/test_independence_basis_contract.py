from rezon.receipts import IndependenceMetadata, IndependenceVerificationEvidence


def _metadata(basis):
    return IndependenceMetadata(
        executor_id="different-host",
        model_id="independent-model",
        provider_id="separate-provider",
        prompt_lineage="different-prompt",
        context_lineage="different-context",
        saw_other_answer=False,
        independence_basis_refs=(basis,),
    )


def test_namespace_prefix_without_identity_is_not_independence_evidence():
    assert _metadata("policy:").is_demonstrably_independent is False


def test_complete_namespace_ref_can_be_checked_by_policy():
    assert _metadata("policy:independent-review-42").is_demonstrably_independent is True


def test_verification_evidence_rejects_empty_governed_reference():
    evidence = IndependenceVerificationEvidence(
        basis_ref="policy:",
        executor_id="host2", model_id="m2", provider_id="p2",
        prompt_lineage="prompt2", context_lineage="context2",
        verification_refs=("v-1",),
    )
    # Constructor must fail rather than expose a vacuous independent basis.
    assert evidence.basis_ref != "policy:"
