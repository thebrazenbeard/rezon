# Rezon Benchmark V1 Layer 1 Reference Evidence R4

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / REPLAY_OBSERVED / INDEPENDENT_QUALIFICATION_PENDING`

R4 is a narrow provenance/currentness hardening delta over R3. It preserves the R2 balanced corpus, R3 ambiguity repair, evaluator gold, baseline strategy behavior, replay metrics, and all prior non-claims. It does not qualify live model/provider reasoning, deployment, installation, activation, runtime effect, or general reasoning superiority.

## Exact subject

- repository: `thebrazenbeard/rezon`
- branch: `rezon/benchmark-v1-r4-unknown-currentness`
- R3 review ancestor: `95870b738b2faa8cbe7f14e7a9d2957f19f513bd`
- R3 review tree: `081dbd2fed4c4a1804e81f3eb3adc94a2fb7d24a`
- R4 RED head: `9533d2470e028ceac6d6a157dc65f2e55c53c51d`
- R4 RED tree: `48456bc59570f92f22e6379542160aab277ceb4e`
- R4 executable/GREEN head: `dd29350f9396cf8a7b10cba0485eca4cf617577b`
- R4 executable/GREEN tree: `bf0c6b5173073bcf3bf780ddab22b6278df9026d`
- Mune inspected R4 documentation head: `8f21876098dc4a2f56d55418e4d1f4f2fab0b28e`
- StrategyInput structural RED head: `61c955e11339ad9e7e33f74546bf6c32d707981c`
- StrategyInput structural GREEN head: `fb5281f26a6bd9abab63ae92b6c1a44c39aa2265`
- adverse fixture SHA-256: `a6244ff59da30bb2f6571b1e5abf89f2121d158af5a84d4b090891c7dc4039c4`
- clean-control SHA-256: `2bd93ec82fb9c8bd281c4d3e19d7708fa325f6f5494a7b8ca132873d62481925`
- composite fixture-manifest SHA-256: `9a6d277f80d3bea4552aad745cb6204538ecf0b150590bc5965dcaa73498087c`
- composite strategy-input digest: `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`

## Defect

`ReplaySource.is_current` is explicitly tri-state: `True`, `False`, or unknown (`None`). R3's `provenance_currentness` guard rejected only sources whose currentness was explicitly `False`. A candidate answering a current-value question from an admitted cited source with `is_current=None` was therefore treated as eligible and could be returned as an answer.

That behavior was inconsistent with Rezon's provenance/currentness boundary. Unknown currentness is not evidence of currentness, and the analogous admission guard already requires explicit `ADMITTED` rather than treating an unknown admission value as admitted.

## Frozen RED evidence

R4 added one test before production repair. The frozen case contains:

- an admitted cited source;
- `is_current=None`;
- a candidate answer of `30`;
- literal and solved request: `What is the current approved timeout?`.

Required behavior:

1. with all guards enabled, the candidate must be rejected and the strategy must `ABSTAIN` with `PROVENANCE_CURRENTNESS` detected;
2. with only `provenance_currentness` ablated, the same frozen payload may answer `30`.

Hosted GitHub Actions on exact RED head `9533d247...` produced:

- install: PASS
- compile: PASS
- pytest: **1 failed / 101 passed**

The sole failure was the new currentness test. Full governance incorrectly returned `ANSWER` with `30`; no unrelated test failed.

## Repair

Only the cited-source currentness predicate in `rezon_guarded` changed.

Previous behavior rejected a known cited source only when:

```text
is_current is False
```

R4 requires explicit currentness for a known cited source:

```text
is_current is True
```

Operationally, the guard now rejects when a referenced known source has `is_current is not True`.

This does not make the currentness guard responsible for missing source IDs; missing references remain the `admission_integrity` guard's responsibility. It also does not require every answer to cite a source: the replay contract does not yet have a typed support-requirement model capable of distinguishing source-grounded claims from valid calculations, tests, formal derivations, or other support classes.

## Public StrategyInput structural hardening

Mune's bounded hostile review of exact head `8f21876098dc4a2f56d55418e4d1f4f2fab0b28e` found that direct callers could construct `StrategyInput` with duplicate source IDs. `rezon_guarded()` then built a dict with:

```text
{source.source_id: source for source in strategy_input.sources}
```

so duplicate source identity collapsed last-wins. The same two source objects could therefore produce different guarded outcomes solely from ordering.

This did not falsify the frozen 24-case benchmark metrics because `ReplayCase.validate()` already rejects duplicate source IDs before `to_strategy_input()`. It did show that the public governed `StrategyInput` boundary was not fail-closed.

### Frozen RED evidence

A direct-boundary regression was frozen before repair.

- initial source-collision RED head: `47517691ee0fb32c03d081a53984b168ebc723f8`;
- expanded structural RED head: `61c955e11339ad9e7e33f74546bf6c32d707981c`;
- CPython 3.12.10 targeted result: **3 failed / 0 passed**.

The three failures covered:

1. duplicate source IDs in both source orders;
2. duplicate candidate IDs;
3. a missing `primary_candidate_id` target.

### Repair

`StrategyInput.validate()` now enforces the non-gold structural invariants needed by the guarded public surface:

- required strategy identity/request fields are non-empty;
- every candidate and source validates itself;
- candidate IDs are unique;
- `primary_candidate_id` names an existing candidate;
- source IDs are unique.

`rezon_guarded()` invokes this validation before building the source map. Invalid direct inputs now raise `ReplayValidationError` before governance/integration logic can observe last-wins collisions.

The baseline strategies were intentionally left unchanged; this repair is scoped to the governed public path that Mune identified.

### GREEN evidence and benchmark preservation

Exact executable head `fb5281f26a6bd9abab63ae92b6c1a44c39aa2265` was checked under CPython 3.12.10:

- targeted structural regressions: **3 passed**;
- `python -m compileall -q src scripts`: PASS;
- full pytest: **105 passed / 0 failed**;
- balanced 24-case reference benchmark: PASS;
- `git diff --check`: PASS;
- tracked/staged diffs: clean.

The frozen benchmark evidence remained unchanged:

- strategy-input digest: `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`;
- `rezon_guarded`: 21/24 disposition-correct;
- 2 false accepts;
- 174 operations;
- 9/15 evaluator-required violation labels detected.

Therefore the public-boundary repair hardens direct governed input without improving or rewriting the frozen benchmark result.

## Exact GREEN reproduction

GitHub Actions freshly checked out exact executable head `dd29350f9396cf8a7b10cba0485eca4cf617577b` on Ubuntu 24.04.5 / CPython 3.12.14 and passed:

- editable install: PASS
- `python -m compileall -q src scripts`: PASS
- pytest: **102 passed / 0 failed**
- balanced 24-case reference replay: PASS
- `git diff --check`: PASS

The frozen 24-case fixture files, composite manifest, strategy-input digest, and replay metric vector were unchanged. In particular, `rezon_guarded` remains:

- 21/24 disposition-correct;
- 12/12 answer-correct when it answers on gold-answer cases;
- 2 false accepts;
- 0 false abstains;
- 0 false rejects;
- 0 unsupported acceptances under the current evaluator mapping;
- 0 accepted provenance/currentness violations in the frozen corpus;
- 9/15 evaluator-required violation labels detected;
- 174 deterministic operations;
- wall-clock unmeasured (`null`).

The unchanged vector matters: R4 closes a previously unrepresented semantic path without modifying adverse fixtures, clean controls, evaluator gold, or labels to improve the benchmark result.

## Scope and non-claims

R4 supports only the narrow observation that an admitted cited source with unknown currentness can no longer satisfy the guarded replay currentness check merely because it is not explicitly stale.

It does **not** prove:

- general reasoning superiority;
- complete provenance semantics;
- that every answer requires a source reference;
- that the replay contract has a complete typed support model;
- live provider/model quality;
- justified production cost;
- deployment, installation, activation, runtime effect, or behavioral qualification.

Known Layer 1 limitations remain, including:

- contradiction omission can still false-accept;
- malformed receipt can still false-accept;
- mandatory-verification unavailability currently yields guarded `ABSTAIN` where evaluator gold is `FAIL_CLOSED`;
- the replay contract has no typed support-requirement field capable of distinguishing source support from calculation/test/proof/tool-receipt support;
- candidate-order permutation is not yet a first-class corpus-wide experiment even though R3 directly covers the discovered tie defect;
- failure visibility remains conservative and does not yet model optional-peer vs mandatory-verifier role semantics.

## Remaining gate

R4 remains `INDEPENDENT_QUALIFICATION_PENDING`. Independent hostile review must verify the exact current documentation head/tree once frozen, both RED-to-GREEN transitions, the explicit-True currentness rule, direct `StrategyInput` structural fail-closed behavior, guard-ablation isolation, unchanged frozen replay evidence, and whether another unknown/missing provenance state can still be silently promoted.
