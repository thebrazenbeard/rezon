# Rezon Kernel V0 Acceptance

Status: R5 SOURCE / BUILD / TEST CANDIDATE — R4 PAIRWISE-INDEPENDENCE FAILURE REPAIRED / FRESH INDEPENDENT R5 REVIEW PENDING

This record binds executable qualification evidence for the provider-independent Rezon Kernel V0 R5 candidate. It does not self-award independent hostile qualification and does not establish reasoning superiority, production deployment, installation, model training, provider activation, or downstream behavioral effect.

## Exact executable payload

- repository: `thebrazenbeard/rezon`
- repair branch: `work/rezon-kernel-v0-r5-independence`
- executable payload commit: `d32cca38606e767813d9e0797681d1ab00e0b0b8`
- executable payload tree: `fbe4a4eca7251144306b4ba301fd7f3c9d9d9f8f`
- predecessor R4 documentation head: `e30b28e2485407c6fc6c44d538eb12247dba8b32`
- predecessor R4 executable payload: `90952cd4af2b1d1aefa90565a993c7f8221b39df`
- research base: `rezon/hcae-semantic-reapplication-v1@0cf560ce4a573230b94db2982dbec074dd3b1b20`

## Independent review history

R1/R2 independent failures remain preserved as exact-subject history. Masa returned `HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED` on R1 and `CHANGES_REQUESTED / HOSTILE_R2_FAIL` on R2. Mune returned `CHANGES_REQUESTED / R2_EXECUTABLE_SEMANTIC_BLOCKERS / NO_MUNE_FULL_SUITE_PASS` plus supplemental producer-provenance and retrieval-content/scope findings. Those cases remain part of the permanent regression surface.

Mune rereviewed exact R3 and returned:

`CHANGES_REQUESTED / R3_KERNEL_V0_SEMANTIC_BLOCKERS / HOSTED_67_PASS_NOT_SUFFICIENT`

The R3 findings covered relation visibility, relation-output capability, provenance trust separation, derived-state currentness, target-bound verification, honest claim-disposition semantics, lifecycle promotion, and answer-bearing contamination of independence-required execution. R4 repaired those surfaces and reached a hosted 84/84 source/build/test PASS.

Mune then rereviewed exact R4 head `e30b28e2485407c6fc6c44d538eb12247dba8b32` and independently confirmed the 84/84 hosted evidence while returning:

`CHANGES_REQUESTED / R4_PAIRWISE_INDEPENDENCE_REGRESSION / HOSTED_84_PASS_NOT_SUFFICIENT`

He found one HIGH blocker: `IndependenceMetadata.demonstrably_independent_from()` rejected only an identical `(model_id, provider_id)` pair, allowing two workers to count as pairwise independent when they shared an executor, shared a model across providers, or shared a provider across models. The runner used that method directly for pairwise independence.

Mune also identified sibling PR #11 as prior stronger source evidence. Its implementation independently rejects shared executor, model, provider, prompt lineage, context lineage, and declared common evidence. R5 restores that stricter invariant on top of the full current R4 repair surface rather than replacing R4 with the sibling branch.

## R5 control

For two workers to count as pairwise strongly independent, each must first satisfy the existing individual independence and external-policy gates, and the pair must additionally have no shared:

- executor ID;
- model ID;
- provider ID;
- prompt lineage;
- context lineage;
- declared common evidence.

The clean control requires all of those dimensions to remain distinct. This is intentionally conservative for Kernel V0: different providers do not make the same model independent, different models do not make the same provider independent, and changing prompts/models/providers does not make the same executor a new independent reasoning source.

All R4 controls remain carried forward unchanged, including relation visibility/capabilities, trusted-vs-reported provenance separation, derived-state invalidation, target-bound mandatory verification, PLAN-only `ResultReceipt`, answer-bearing candidate blindness, retrieval content/scope binding, and explicit unresolved claim disposition.

## TDD / adversarial evidence

R5 first froze seven pairwise-lineage cases before production repair:

- same executor, otherwise distinct lineage -> reject;
- same model / different provider -> reject;
- different model / same provider -> reject;
- shared prompt lineage -> reject;
- shared context lineage -> reject;
- shared declared evidence -> reject;
- all required dimensions distinct -> accept.

Exact RED head `289e89b8a2be526349aba893c09fa301f41011d4` installed and compiled successfully, then produced exactly:

```text
3 failed, 88 passed
```

The only failures were the three R4 bypasses identified by Mune: shared executor, shared model across providers, and shared provider across models. Existing prompt-lineage, context-lineage, evidence-overlap, and clean-control behavior remained green.

The production repair at exact executable payload `d32cca38606e767813d9e0797681d1ab00e0b0b8` is intentionally small: `demonstrably_independent_from()` now rejects shared executor ID, shared model ID, and shared provider ID separately before the already-existing prompt/context/evidence checks.

## Hosted qualification sequence

The exact executable payload `d32cca38606e767813d9e0797681d1ab00e0b0b8` was checked by GitHub Actions on Ubuntu 24.04.5 / CPython 3.12.14:

```text
python -m pip install --upgrade pip
python -m pip install pytest
python -m pip install -e .
python -m compileall -q src
pytest -q
git diff --check
```

Observed result:

```text
91 passed in 0.14s
```

Editable install: PASS. Compile: PASS. Full pytest suite: PASS. `git diff --check`: PASS.

The 91-test surface includes original Kernel V0 cases, Masa R1/R2 hostile artifacts, Mune R2/R3/R4 regression surfaces, supplemental provenance/content/scope and lifecycle/blinding cases, R4 self-review cases, and the seven R5 pairwise-lineage cases.

## Explicit limits / non-claims

This evidence establishes only that the exact R5 executable payload satisfies the currently encoded Kernel V0 contracts and hostile/regression cases in the recorded hosted environment.

It does **not** establish:

- independent Mune R5 PASS;
- independent Masa R5 PASS;
- reasoning superiority over single-pass, higher-effort, or fixed-multipass baselines;
- live LLM/tool executor correctness;
- HCAE/HyPER/hyperbolic routing effectiveness;
- production persistence, provider integration, deployment, installation, activation, or downstream behavioral effect;
- dynamic scheduler rerun/starvation qualification.

Additional trust boundaries remain deliberately unclaimed:

- `TaskEnvelope.available_authority` remains declared metadata and is not sufficient authorization for protected external effects. Live write/provider/tool adapters require governed issuer/scope/currentness-bound authority evidence.
- `IndependenceVerificationPolicy` remains a trusted dependency boundary; Kernel V0 verifies exact lineage against it but does not cryptographically establish its issuer.
- retrieval admission verifies supplied external policy/evidence structure but does not cryptographically establish its issuer.
- Kernel V0 has no live external-effect executor; lifecycle/effect transitions require separate governed artifacts before effectful adapters can be qualified.
- one-shot node completion remains a Kernel V0 limit; frontier reruns, starvation handling, retries/cooldowns, and guard-band behavior belong to later dynamic scheduler qualification.

Fresh exact-head Mune and Masa R5 rereview is required before R5 is promoted into the P0 integration subject or any predecessor PR is advanced.
