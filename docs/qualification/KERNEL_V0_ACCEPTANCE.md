# Rezon Kernel V0 Acceptance

Status: R4 SOURCE / BUILD / TEST CANDIDATE — R3 INDEPENDENT REVIEW FAILURES REPAIRED / FRESH INDEPENDENT R4 REVIEW PENDING

This record binds executable qualification evidence for the provider-independent Rezon Kernel V0 R4 candidate. It does not self-award independent hostile qualification and does not establish reasoning superiority, production deployment, installation, model training, provider activation, or downstream behavioral effect.

## Exact executable payload

- repository: `thebrazenbeard/rezon`
- repair branch: `work/rezon-kernel-v0-r4-mune`
- executable payload commit: `2f50287f4c8fad5fefb99e5ed73d91e8ad2063dc`
- executable payload tree: `3d729ecc7a558fa030d2d350a3cd82bc5ad3fa6d`
- predecessor R3 documentation head: `4f5319e42fdf2718a62a4f62a96294e4350f88d7`
- predecessor R3 executable payload: `bc3321346234c1127a86aaeddae03da2db463dc8`
- research base: `rezon/hcae-semantic-reapplication-v1@0cf560ce4a573230b94db2982dbec074dd3b1b20`

## Independent review history

R1/R2 independent failures remain preserved as exact-subject history. Masa returned `HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED` on R1 and `CHANGES_REQUESTED / HOSTILE_R2_FAIL` on R2. Mune returned `CHANGES_REQUESTED / R2_EXECUTABLE_SEMANTIC_BLOCKERS / NO_MUNE_FULL_SUITE_PASS` plus supplemental producer-provenance and retrieval-content/scope findings. Those cases remain part of the permanent regression surface.

Mune then rereviewed exact R3 and returned:

`CHANGES_REQUESTED / R3_KERNEL_V0_SEMANTIC_BLOCKERS / HOSTED_67_PASS_NOT_SUFFICIENT`

His R3 findings were:

- relation ID allow/blind controls were not enforced on relations;
- descriptors did not constrain emitted relation types;
- worker-reported source/provenance metadata could be treated as trusted provenance;
- derived propositions could remain current after canonical support was retracted;
- mandatory verification lacked explicit machine-readable target-bound success semantics;
- result-receipt claim disposition was broader than the implementation actually supported.

The hosted R3 67-test PASS remains valid source/build/test evidence for that exact subject, but Mune's independent semantic verdict remains `CHANGES_REQUESTED` for R3.

## R4 controls

R4 adds or strengthens:

- relation IDs now obey `VisibilityPolicy.allow_ids` and `blind_ids` in addition to dependency visibility;
- `NodeDescriptor.permitted_relation_types` explicitly gates worker relation emission;
- governed admission rejects emitted proposition/relation provenance that is not present in the worker's governed execution view;
- trace provenance separates trusted consumed `source_refs/source_versions` from worker-reported `reported_source_refs/reported_source_versions`;
- final receipt source versions derive from consumed governed inputs, not worker self-report;
- canonical object IDs in proposition/relation `source_refs` act as currentness dependencies; retracting support recursively invalidates dependent current propositions/relations while preserving history;
- newly added canonical state cannot cite an already inactive canonical source;
- mandatory-verification descriptors must declare explicit `verification_target_ids`;
- verification results carry `VerificationStatus` (`PASSED`, `FAILED`, `INCONCLUSIVE`) plus explicit target IDs;
- a mandatory verifier passes only when it reports `PASSED`, targets exactly the descriptor-declared objects, those targets are visible, and an admitted `TEST_RESULT` cites them;
- no-op, failed, inconclusive, hidden-target, or target-switching verification remains unresolved/fails closed;
- `ResultReceipt.claim_disposition_complete` explicitly narrows claim-disposition semantics; current claims that have not been dispositioned are emitted as `claim_disposition:<id>` unresolved items rather than being silently implied accepted/rejected.

## TDD / adversarial evidence

Mune's R3 findings were first frozen as ten R4 regression cases. The initial hosted run installed and compiled successfully and then failed at collection because the new machine-readable verification contract did not yet exist, establishing RED before production repair.

After the first R4 repair pass, the combined suite reached **76 passed / 1 failed**. The single failure was an older R3 positive fixture that still expected a worker's self-reported source/version to become trusted provenance. That fixture was updated to assert the stronger consumed-vs-reported boundary; production trust rules were not relaxed. The suite then reached **77 passed**.

A subsequent One-side hostile source review found two additional seams before freeze:

1. a new derived proposition could cite a canonical source that had already been retracted;
2. a mandatory verifier could select a different visible verification target than the requirement intended.

Both were added as tests before repair. Exact pre-repair head `b8433da23a16c9f9ddd90e08d6318769172fb7d7` reproduced **2 failed / 77 passed**. R4 then rejects inactive canonical support at insertion and binds mandatory verification targets at the descriptor/runtime boundary. Older positive verifier fixtures were updated to explicitly name their intended targets rather than weakening that requirement.

## Hosted qualification sequence

The exact executable payload `2f50287f4c8fad5fefb99e5ed73d91e8ad2063dc` was checked by branch-local GitHub Actions on Ubuntu 24.04.5 / CPython 3.12.14:

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
79 passed in 0.15s
```

Editable install: PASS. Compile: PASS. Full pytest suite: PASS. `git diff --check`: PASS.

The 79-test surface includes original Kernel V0 cases, Masa R1/R2 hostile artifacts, Mune R2/R3 regressions, supplemental provenance/content/scope cases, and additional R4 adversarial self-review cases.

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
- Kernel V0 has no live external-effect executor; effect receipts become mandatory before effectful adapters are qualified.
- one-shot node completion remains a Kernel V0 limit; frontier reruns, starvation handling, retries/cooldowns, and guard-band behavior belong to later dynamic scheduler qualification.

Fresh exact-head Mune and Masa R4 rereview is required before R4 is promoted into the P0 integration subject or any predecessor PR is advanced.
