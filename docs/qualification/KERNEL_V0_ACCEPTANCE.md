# Rezon Kernel V0 Acceptance

Status: SOURCE / BUILD / TEST ACCEPTANCE CANDIDATE ? HOSTILE R1 REPAIRED / R2 REREVIEW PENDING

This record binds executable qualification evidence for the provider-independent Rezon Kernel V0 R2 candidate. It does not establish reasoning superiority, production deployment, installation into another system, model training, provider activation, or downstream behavioral qualification.

## Exact executable payload

- repository: `thebrazenbeard/rezon`
- branch: `work/rezon-kernel-v0-p0`
- executable payload commit: `6675a91935e5bc98ca57a5fa48413e772ac980be`
- executable payload tree: `3f2e50daa9babb79dc824e6eb1a1bf41aea66f71`
- predecessor research head: `rezon/hcae-semantic-reapplication-v1@0cf560ce4a573230b94db2982dbec074dd3b1b20`

## Independent hostile history

Masa independently reviewed prior integration head `2500e717895eae123fa4438aa827e63c53fd39eb` and returned `HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED`.

His frozen hostile branch `masa/rezon-p0-hostile-kernel-review-v2@4d9e8875da618ab12af2253fbeca532d15292368` added nine hostile cases. Those nine cases reproduced locally against `2500e717...` as **9 failed / 0 passed**.

R2 repairs address all seven blocking findings:

- independence cannot rely on arbitrary self-asserted basis references; independence-required execution fails closed and pairwise correlation checks are available;
- runner-issued execution identity is bound through admission;
- worker/model output cannot self-promote to `EVIDENCE` merely through descriptor permission;
- retrieval evidence requires a separate external admission policy bound to exact source/version;
- contradictory/impossible `ResultReceipt` states are rejected;
- worker exceptions produce typed `ATTEMPTED_UNKNOWN` receipts/traces rather than escaping the governed run;
- retracting a proposition invalidates dependent current relations while preserving history.

Three additional Masa material gaps were also hardened:

- `TaskEnvelope` can be bound to runtime execution, authority checks, resource budget, trace, and result receipt through its deterministic digest;
- admission failures are reflected consistently in both final receipt and execution trace, with unadmitted emitted IDs omitted from admitted output;
- executor-visible views no longer reveal blinded proposition/relation IDs, while audit traces retain them.

The remaining one-shot node-completion behavior is intentionally retained as a Kernel V0 limit. Dynamic frontier reruns/starvation handling belong to later scheduler qualification and are not claimed here.

## Reproduction environment

- Windows host
- Python `3.12.10`
- isolated fresh clone of the remote branch
- branch-local virtual environment
- `pytest` installed into that environment
- package installed editable from the fresh clone

## Qualification sequence

```text
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install pytest
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m compileall -q src
.venv\Scripts\python.exe -m pytest -q
git diff --check
git status --short
```

Observed on a fresh remote clone of executable payload `6675a91935e5bc98ca57a5fa48413e772ac980be`:

```text
46 passed in 0.18s
```

`compileall` completed successfully, `git diff --check` returned clean, and the qualification checkout had no tracked working-tree changes.

The 46-test suite includes the exact nine-case Masa hostile artifact plus additional regression coverage for pairwise independence, task-envelope/authority binding, executor-side blinding, and receipt/trace agreement.

## Qualification boundary

This establishes only that the exact R2 executable payload satisfies the currently encoded Kernel V0 contracts and the imported Masa R1 hostile cases under the recorded environment.

It does **not** establish:

- independent hostile R2 PASS ? fresh Masa rereview is still required;
- Mune reproducibility/qualification PASS ? pending;
- reasoning superiority over single-pass or fixed-multipass baselines;
- live LLM/tool executor correctness;
- HCAE/HyPER/hyperbolic routing effectiveness;
- production persistence, provider integration, deployment, installation, activation, or downstream behavioral effect.
