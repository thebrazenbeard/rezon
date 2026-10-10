import pytest

from rezon.receipts import IndependenceMetadata, IndependenceVerificationEvidence, IndependenceVerificationPolicy


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
    # Untrusted evidence is constructible so its forged claims can be inspected,
    # but it cannot qualify even properly formed independent metadata.
    valid = _metadata("policy:independent-review-42")
    forged = IndependenceVerificationEvidence(
        basis_ref="policy:",
        executor_id=valid.executor_id,
        model_id=valid.model_id,
        provider_id=valid.provider_id,
        prompt_lineage=valid.prompt_lineage,
        context_lineage=valid.context_lineage,
        verification_refs=("v-1",),
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
    )
    assert IndependenceVerificationPolicy((forged,)).verify(valid) is False
