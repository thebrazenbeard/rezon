# Rezon Kernel V0 Acceptance

Status: R3 SOURCE / BUILD / TEST CANDIDATE — R1/R2 INDEPENDENT FAILURES REPAIRED / FRESH INDEPENDENT R3 REVIEW PENDING

This record binds executable qualification evidence for the provider-independent Rezon Kernel V0 R3 candidate. It does not self-award independent hostile qualification and does not establish reasoning superiority, production deployment, installation, model training, provider activation, or downstream behavioral effect.

## Exact executable payload

- repository: `thebrazenbeard/rezon`
- repair branch: `work/rezon-kernel-v0-r3-mune`
- executable payload commit: `2cf746779a5f755d4e7fe57df1c811baeb2ef764`
- executable payload tree: `a2418976a2666fb8254a087eb0dd3590d74ef3f6`
- predecessor R2 documentation head: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- predecessor R2 executable payload: `6675a91935e5bc98ca57a5fa48413e772ac980be`
- research base: `rezon/hcae-semantic-reapplication-v1@0cf560ce4a573230b94db2982dbec074dd3b1b20`

## Independent review history

Masa independently reviewed R1 and returned `HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED`. His frozen nine-case R1 hostile artifact reproduced against that subject as **9 failed / 0 passed**. R2 repaired those blocking defects and imported the R1 artifact as a permanent regression surface.

Mune independently inspected exact R2 and returned `CHANGES_REQUESTED / R2_EXECUTABLE_SEMANTIC_BLOCKERS / NO_MUNE_FULL_SUITE_PASS`. His source/control-flow findings identified currentness resurrection, scheduler/view mismatch, weak independence binding, mandatory-verifier no-op completion, unenforced input kinds, and incomplete execution provenance. Mune could not independently clone/run R2 in his chat transport, so his disposition was not a full-suite execution result.

Masa independently rereviewed exact R2 and returned `CHANGES_REQUESTED / HOSTILE_R2_FAIL`. His fresh R2 artifact `masa/rezon-p0-hostile-r2-v1@82dc308030acb3f6b4b58c2b2c1cabf5ebb2b0fc` added nine new hostile cases covering retrieval-content substitution, stale relation recreation, failed-result mutation, actual-view independence, unknown-provider correlation, missing producer provenance, dead input-kind metadata, bare qualification promotion, and consumed-source-version omission.

Masa could not independently execute his R2 artifact in that chat runtime, so his R2 disposition was source-proven rather than a numerical independent test run.

## R3 controls

R3 adds or strengthens these controls:

- current relations may depend only on active propositions/relations; invalidated relation IDs cannot silently reactivate;
- governed result admission applies the same currentness rule, including staged relation dependencies;
- failed `ExecutionResult` objects cannot mutate canonical episode state;
- execution-emitted propositions and relations must bind exactly to the runner-issued producer execution ID;
- scheduler decisions bind exact contradiction/falsification targets, and the runner fails closed if a scheduled target is absent from the execution view;
- node `accepted_input_kinds` is enforced before execution;
- mandatory verification must yield an admitted `TEST_RESULT`; no-op or failed verification remains typed and unresolved;
- strong independence requires complete executor/model/provider/prompt/context lineage, governed-form basis references, a separate external `IndependenceVerificationPolicy` bound to that exact lineage, pairwise separation where applicable, and an actually candidate-blind execution view;
- incomplete independence claims are rejected before execution without manufacturing an execution trace; complete claims rejected because verification/view checks fail leave an auditable pre-execution denial trace;
- retrieval admission binds exact source/version, exact locator set, and SHA-256 of the promoted content through external admission evidence; a source/version admission cannot attest arbitrary replacement text;
- `ResultReceipt` is prohibited from self-issuing `QUALIFIED`; qualification requires a separate governed qualification artifact;
- execution trace records timing, consumed/result source references, exact source versions, visible/blinded inputs, failures, and TaskEnvelope binding;
- final result receipts aggregate exact versioned source references actually exposed to/used by execution views as well as versions reported by execution results;
- TaskEnvelope task identity/resource budget/declared authority remains bound into runtime/trace/receipt surfaces;
- executor-visible views do not expose blinded IDs while audit traces retain them.

## TDD / hostile evidence

The first Mune-derived R3 regression gate was introduced before production repair. Hosted GitHub Actions installed and compiled successfully, then pytest failed **9 cases / 46 passed**. After the first repair pass, the suite reached **55 passed**.

A subsequent self-review added two new regressions before repair: generic-policy candidate blindness and failed mandatory-verification unresolved state. They reproduced as **2 failed / 55 passed** before becoming green.

After importing Masa's exact R2 hostile artifact unchanged, the then-current R3 source reproduced **6 failed / 60 passed**. The six failures were:

- retrieval content was not bound to admission evidence;
- failed execution results could still mutate canonical state;
- actual-view independence rejection needed an auditable pre-execution denial distinction;
- worker output could omit producer execution attribution;
- bare `ResultReceipt(effect_state=QUALIFIED)` remained constructible;
- final receipt omitted versioned source refs consumed from the execution view.

Those controls were repaired. The external-independence-policy hardening initially exposed three expected regression-fixture incompatibilities; the self-asserted independence case remained invalid, while two positive fixtures were updated to provide independently verified lineage rather than weakening the runtime rule.

## Hosted qualification sequence

The exact executable payload `2cf746779a5f755d4e7fe57df1c811baeb2ef764` was checked by the branch-local GitHub Actions workflow on Ubuntu 24.04 / CPython 3.12.14:

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
66 passed in 0.19s
```

Install: PASS. Compile: PASS. Full pytest suite: PASS. `git diff --check`: PASS.

The 66-test suite contains the original Kernel V0 tests, Masa R1 hostile artifact, Masa R2 hostile artifact, Mune-derived R3 regressions, and additional One-side adversarial regressions.

## Explicit limits / non-claims

This evidence establishes only that the exact R3 executable payload satisfies the currently encoded Kernel V0 contracts and hostile/regression cases in the recorded hosted environment.

It does **not** establish:

- fresh independent Masa R3 hostile PASS;
- fresh independent Mune R3 verification PASS;
- reasoning superiority over single-pass or fixed-multipass baselines;
- live LLM/tool executor correctness;
- HCAE/HyPER/hyperbolic routing effectiveness;
- dynamic scheduler rerun/starvation qualification;
- production persistence, provider integration, deployment, installation, activation, or downstream behavioral effect.

Additional trust boundaries remain deliberately unclaimed:

- `TaskEnvelope.available_authority` is still a declared string capability surface, not sufficient authorization for future protected external effects. Live write/provider/tool adapters require issuer/scope/currentness-bound authority evidence before this field may authorize them.
- `IndependenceVerificationPolicy` is an explicit trusted dependency boundary; Kernel V0 verifies exact lineage against the supplied policy but does not cryptographically establish the policy issuer. A governed higher layer must construct that policy from real verification evidence.
- the trace has no live tool-effect receipt fields because Kernel V0 has no live external-effect executor. Such fields become mandatory before effectful adapters are qualified.
- one-shot node completion is retained as a Kernel V0 limit; progress/frontier reruns, starvation, retries/cooldowns, and guard-band behavior belong to later dynamic scheduler qualification.

Fresh exact-head Mune and Masa R3 rereview is required before R3 is promoted into the P0 integration subject or PR #8 is advanced.
