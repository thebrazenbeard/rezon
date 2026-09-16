# Rezon Kernel V0 Acceptance

Status: R4 SOURCE / BUILD / TEST CANDIDATE — R3 + SUPPLEMENTAL INDEPENDENT REVIEW FAILURES REPAIRED / FRESH INDEPENDENT R4 REVIEW PENDING

This record binds executable qualification evidence for the provider-independent Rezon Kernel V0 R4 candidate. It does not self-award independent hostile qualification and does not establish reasoning superiority, production deployment, installation, model training, provider activation, or downstream behavioral effect.

## Exact executable payload

- repository: `thebrazenbeard/rezon`
- repair branch: `work/rezon-kernel-v0-r4-mune`
- executable payload commit: `90952cd4af2b1d1aefa90565a993c7f8221b39df`
- executable payload tree: `b2ec15c34f45d00d77c9b66edb6e3296d613c0d9`
- predecessor R3 documentation head: `4f5319e42fdf2718a62a4f62a96294e4350f88d7`
- predecessor R3 executable payload: `bc3321346234c1127a86aaeddae03da2db463dc8`
- research base: `rezon/hcae-semantic-reapplication-v1@0cf560ce4a573230b94db2982dbec074dd3b1b20`

## Independent review history

R1/R2 independent failures remain preserved as exact-subject history. Masa returned `HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED` on R1 and `CHANGES_REQUESTED / HOSTILE_R2_FAIL` on R2. Mune returned `CHANGES_REQUESTED / R2_EXECUTABLE_SEMANTIC_BLOCKERS / NO_MUNE_FULL_SUITE_PASS` plus supplemental producer-provenance and retrieval-content/scope findings. Those cases remain part of the permanent regression surface.

Mune rereviewed exact R3 and returned:

`CHANGES_REQUESTED / R3_KERNEL_V0_SEMANTIC_BLOCKERS / HOSTED_67_PASS_NOT_SUFFICIENT`

The primary R3 findings covered relation visibility, relation-output capability, provenance trust separation, derived-state currentness, target-bound verification, and honest claim-disposition semantics.

Mune then appended `mune-0019` without rewriting the prior verdict and added two source-proven blockers:

- bare `ResultReceipt` construction could self-certify lifecycle/effect states above `PLAN` without governed transition evidence;
- independence candidate blindness covered visible `HYPOTHESIS` only, allowing answer-bearing `CLAIM` or `DECISION` propositions to remain visible.

The hosted R3 67-test PASS remains valid source/build/test evidence for that exact subject, but Mune's independent semantic verdict remains `CHANGES_REQUESTED` for R3.

## R4 controls

R4 adds or strengthens:

- relation IDs obey `VisibilityPolicy.allow_ids` and `blind_ids` in addition to dependency visibility;
- `NodeDescriptor.permitted_relation_types` explicitly gates worker relation emission;
- governed admission rejects emitted proposition/relation provenance not present in the worker's governed execution view;
- trace provenance separates trusted consumed `source_refs/source_versions` from worker-reported `reported_source_refs/reported_source_versions`;
- final receipt source versions derive from consumed governed inputs, not worker self-report;
- canonical object IDs in proposition/relation `source_refs` act as currentness dependencies; retracting support recursively invalidates dependent current propositions/relations while preserving history;
- newly added canonical state cannot cite an already inactive canonical source;
- mandatory-verification descriptors declare exact `verification_target_ids`;
- verification results carry `VerificationStatus` (`PASSED`, `FAILED`, `INCONCLUSIVE`) plus explicit target IDs;
- mandatory verification passes only when status is `PASSED`, result targets exactly equal descriptor-declared targets, those targets are visible, and an admitted `TEST_RESULT` cites them;
- no-op, failed, inconclusive, hidden-target, or target-switching verification remains unresolved/fails closed;
- `ResultReceipt.claim_disposition_complete` narrows claim-disposition semantics; undispositioned current claims remain explicit unresolved items;
- ordinary `ResultReceipt` is now intentionally non-promotional and may report `EffectState.PLAN` only; lifecycle/effect promotion requires a separately governed transition artifact;
- independence-required descriptors define an explicit answer-bearing blindness class, defaulting to `HYPOTHESIS`, `CLAIM`, and `DECISION`, plus optional exact protected proposition IDs; visible protected candidates fail the independence gate before execution.

## TDD / adversarial evidence

Mune's primary R3 findings were first frozen as R4 regressions before production repair. After the first repair pass, the combined suite reached **76 passed / 1 failed**. The remaining failure was an obsolete R3 positive fixture that treated worker self-reported source/version data as trusted provenance. The fixture was updated to assert the stronger consumed-vs-reported boundary; production trust rules were not relaxed. The suite then reached **77 passed**.

A One-side hostile review then added two more RED cases before repair: insertion from already inactive canonical support and verifier target switching. Exact pre-repair head `b8433da23a16c9f9ddd90e08d6318769172fb7d7` reproduced **2 failed / 77 passed**. Those controls were repaired and old positive verifier fixtures were updated to declare their intended targets.

Mune's supplemental `mune-0019` findings were discovered after the first R4 review request had already been sent. The prior R4 review subject was therefore treated as stale. Five new negative cases were added before repair: bare `INSTALLED`, `ACTIVE`, and `EFFECT_OBSERVED` receipts plus visible peer `CLAIM` and `DECISION` under an otherwise valid independence policy. Exact RED head `d6bb16c71a09a3038ebdbbbec8d4bf9bdd459515` reproduced **5 failed / 79 passed**. R4 then made `ResultReceipt` PLAN-only and generalized the independence blindness contract. The older positive receipt fixture was narrowed to PLAN rather than weakening the lifecycle control.

## Hosted qualification sequence

The exact executable payload `90952cd4af2b1d1aefa90565a993c7f8221b39df` was checked by branch-local GitHub Actions on Ubuntu 24.04.5 / CPython 3.12.14:

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
84 passed in 0.15s
```

Editable install: PASS. Compile: PASS. Full pytest suite: PASS. `git diff --check`: PASS.

The 84-test surface includes original Kernel V0 cases, Masa R1/R2 hostile artifacts, Mune R2/R3 and supplemental regression surfaces, provenance/content/scope cases, and additional R4 adversarial self-review cases.

## Explicit limits / non-claims

This evidence establishes only that the exact R4 executable payload satisfies the currently encoded Kernel V0 contracts and hostile/regression cases in the recorded hosted environment.

It does **not** establish:

- independent Mune R4 PASS;
- independent Masa R4 PASS;
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

Fresh exact-head Mune and Masa R4 rereview is required before R4 is promoted into the P0 integration subject or any predecessor PR is advanced.
