from rezon.receipts import IndependenceMetadata


def _meta(*, executor, model, provider, prompt, context, evidence=()):
    return IndependenceMetadata(
        executor_id=executor,
        model_id=model,
        provider_id=provider,
        prompt_lineage=prompt,
        context_lineage=context,
        saw_other_answer=False,
        common_evidence_refs=tuple(evidence),
        independence_basis_refs=("policy:independent-generation",),
    )


def test_pairwise_independence_rejects_same_executor_with_otherwise_distinct_lineage():
    a = _meta(executor="shared", model="m-a", provider="p-a", prompt="q-a", context="c-a")
    b = _meta(executor="shared", model="m-b", provider="p-b", prompt="q-b", context="c-b")
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_same_model_across_different_providers():
    a = _meta(executor="e-a", model="shared", provider="p-a", prompt="q-a", context="c-a")
    b = _meta(executor="e-b", model="shared", provider="p-b", prompt="q-b", context="c-b")
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_same_provider_across_different_models():
    a = _meta(executor="e-a", model="m-a", provider="shared", prompt="q-a", context="c-a")
    b = _meta(executor="e-b", model="m-b", provider="shared", prompt="q-b", context="c-b")
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_shared_prompt_lineage():
    a = _meta(executor="e-a", model="m-a", provider="p-a", prompt="shared", context="c-a")
    b = _meta(executor="e-b", model="m-b", provider="p-b", prompt="shared", context="c-b")
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_shared_context_lineage():
    a = _meta(executor="e-a", model="m-a", provider="p-a", prompt="q-a", context="shared")
    b = _meta(executor="e-b", model="m-b", provider="p-b", prompt="q-b", context="shared")
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_rejects_declared_common_evidence():
    a = _meta(executor="e-a", model="m-a", provider="p-a", prompt="q-a", context="c-a", evidence=("src:shared",))
    b = _meta(executor="e-b", model="m-b", provider="p-b", prompt="q-b", context="c-b", evidence=("src:shared",))
    assert not a.demonstrably_independent_from(b)


def test_pairwise_independence_accepts_fully_distinct_complete_lineage():
    a = _meta(executor="e-a", model="m-a", provider="p-a", prompt="q-a", context="c-a")
    b = _meta(executor="e-b", model="m-b", provider="p-b", prompt="q-b", context="c-b")
    assert a.is_demonstrably_independent
    assert b.is_demonstrably_independent
    assert a.demonstrably_independent_from(b)
