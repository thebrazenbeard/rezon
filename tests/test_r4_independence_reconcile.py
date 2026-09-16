from rezon.receipts import IndependenceMetadata


def _meta(*, executor: str, model: str, provider: str, prompt: str, context: str) -> IndependenceMetadata:
    return IndependenceMetadata(
        executor_id=executor,
        model_id=model,
        provider_id=provider,
        prompt_lineage=prompt,
        context_lineage=context,
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-generation",),
    )


def test_pairwise_independence_rejects_reused_executor_with_changed_metadata():
    a = _meta(executor="shared", model="m1", provider="p1", prompt="pa", context="ca")
    b = _meta(executor="shared", model="m2", provider="p2", prompt="pb", context="cb")
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_same_model_across_different_providers():
    a = _meta(executor="a", model="shared-model", provider="p1", prompt="pa", context="ca")
    b = _meta(executor="b", model="shared-model", provider="p2", prompt="pb", context="cb")
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_same_provider_across_different_models():
    a = _meta(executor="a", model="m1", provider="shared-provider", prompt="pa", context="ca")
    b = _meta(executor="b", model="m2", provider="shared-provider", prompt="pb", context="cb")
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)
