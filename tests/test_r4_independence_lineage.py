from rezon.receipts import IndependenceMetadata


def _meta(*, executor, model, provider, prompt, context):
    return IndependenceMetadata(
        executor_id=executor,
        model_id=model,
        provider_id=provider,
        prompt_lineage=prompt,
        context_lineage=context,
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-generation",),
    )


def test_pairwise_independence_rejects_same_model_across_different_providers():
    a = _meta(
        executor="a",
        model="shared-model",
        provider="provider-a",
        prompt="prompt-a",
        context="context-a",
    )
    b = _meta(
        executor="b",
        model="shared-model",
        provider="provider-b",
        prompt="prompt-b",
        context="context-b",
    )

    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_same_provider_across_different_models():
    a = _meta(
        executor="a",
        model="model-a",
        provider="shared-provider",
        prompt="prompt-a",
        context="context-a",
    )
    b = _meta(
        executor="b",
        model="model-b",
        provider="shared-provider",
        prompt="prompt-b",
        context="context-b",
    )

    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)
