# Rezon Kernel V0 Acceptance

Status: R3 SOURCE / BUILD / TEST CANDIDATE — R1/R2 REVIEW FAILURES REPAIRED / FRESH INDEPENDENT R3 REVIEW PENDING

This record binds executable qualification evidence for the provider-independent Rezon Kernel V0 R3 candidate. It does not self-award independent hostile qualification and does not establish reasoning superiority, production deployment, installation, model training, provider activation, or downstream behavioral effect.

## Exact executable payload

- repository: `thebrazenbeard/rezon`
- repair branch: `work/rezon-kernel-v0-r3-mune`
- executable payload commit: `974ccc4809e4ada629f835b4a2b0e21e5100e37b`
- executable payload tree: `00402fbc0e93b934d11afa4b5e899e0bde85e4d9`
- predecessor R2 documentation head: `8383acc9dcffbb545f79ddbbd6d03146966aa9db`
- predecessor R2 executable payload: `6675a91935e5bc98ca57a5fa48413e772ac980be`
- research base: `rezon/hcae-semantic-reapplication-v1@0cf560ce4a573230b94db2982dbec074dd3b1b20`

## Independent review history

Masa independently reviewed the earlier R1 subject and returned `HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED`. His frozen nine-case hostile artifact reproduced against that subject as **9 failed / 0 passed**. R2 repaired those seven blocking defects plus three material gaps, and the imported Masa suite became green.

Mune then independently inspected exact R2 and returned `CHANGES_REQUESTED / R2_EXECUTABLE_SEMANTIC_BLOCKERS / NO_MUNE_FULL_SUITE_PASS`. His findings were:

- current relations could be recreated from retracted/invalidated dependencies;
- scheduler-selected contradictions could disappear behind executor visibility and cleanly terminate;
- strong independence was not sufficiently bound to model/provider identity and actual candidate exposure;
- mandatory verification had no success postcondition;
- `accepted_input_kinds` was not enforced;
- trace/result provenance did not yet preserve the designed timing and source-version detail.

Mune could not independently clone/run the full R2 suite because of his transport environment, so his report was source/control-flow qualification rather than a reproduced full-suite PASS/FAIL.

## R3 controls

R3 adds or strengthens these controls:

- current relations may depend only on active propositions/relations; invalidated relation IDs cannot silently reactivate;
- governed result admission applies the same currentness rule, including staged relation dependencies;
- scheduler decisions bind an exact contradiction/falsification target, and the runner fails closed if the scheduled target is absent from the execution view;
- strong independence requires known executor/model/provider/prompt/context lineage, trusted basis evidence, no declared answer exposure/common evidence, pairwise separation where applicable, and candidate-blind execution views;
- `accepted_input_kinds` is enforced before execution;
- mandatory verification must yield an admitted `TEST_RESULT`; no-op or failed verification remains typed and unresolved;
- execution trace records timing, source references, exact reported source versions, visible/blinded inputs, failures, and task-envelope binding;
- result receipts aggregate exact reported source versions and execution IDs;
- Masa's pre-execution independence rejection semantics are preserved: if a worker is rejected before execution, no execution trace is fabricated.

The remaining one-shot node-completion behavior is intentionally retained as a Kernel V0 limit. Dynamic frontier reruns/starvation handling belong to later scheduler qualification and are not claimed here.

## TDD evidence

The R3 regression gate was introduced before production repairs on exact R2 source. Hosted GitHub Actions successfully installed and compiled the package, then pytest failed **9 cases / 46 passed**, matching the nine Mune-derived regression cases. This established RED independently of local-machine availability.

After the first repair pass, the full hosted suite reached **55 passed**. A subsequent adversarial self-review found two additional seams:

- a differently named trusted `policy:*` basis could still claim independence while seeing a prior hypothesis;
- a mandatory verifier that returned a typed failure did not necessarily leave a `verification:*` unresolved marker.

Those two cases were added before the second production repair and reproduced as **2 failed / 55 passed**.

## Hosted qualification sequence

The exact executable payload `974ccc4809e4ada629f835b4a2b0e21e5100e37b` was checked by the branch-local GitHub Actions workflow on Ubuntu 24.04 / CPython 3.12.14:

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
57 passed in 0.16s
```

Install: PASS. Compile: PASS. Full pytest suite: PASS. `git diff --check`: PASS.

The 57-test suite includes the frozen Masa hostile artifact, Mune-derived R3 regressions, and additional self-review regressions for policy-name-independent candidate blinding and failed mandatory-verification unresolved state.

## Qualification boundary

This evidence establishes only that the exact R3 executable payload satisfies the currently encoded Kernel V0 contracts and hostile/regression cases in the hosted environment above.

It does **not** establish:

- fresh independent Masa R3 hostile PASS;
- fresh independent Mune R3 verification PASS;
- reasoning superiority over single-pass or fixed-multipass baselines;
- live LLM/tool executor correctness;
- HCAE/HyPER/hyperbolic routing effectiveness;
- dynamic scheduler rerun/starvation qualification;
- production persistence, provider integration, deployment, installation, activation, or downstream behavioral effect.

Fresh exact-head Mune and Masa rereview is required before this repair is promoted into the P0 integration subject.
