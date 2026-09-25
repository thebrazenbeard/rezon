# Rezon Benchmark V1 Layer 1 Reference Evidence

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / REPLAY_OBSERVED / INDEPENDENT_QUALIFICATION_PENDING`

This document records deterministic recorded-output replay evidence only. It does not qualify live model/provider reasoning, deployment, installation, activation, runtime effect, or general reasoning superiority.

## Exact executable subject

- repository: `thebrazenbeard/rezon`
- branch: `rezon/benchmark-v1-impl`
- executable/reference head: `66a729484b9ff3cc6d5673fd86360d56a1562698`
- executable/reference tree: `7b8b7611c56f2e0b06fe4e5ad4e7da081fb5d401`
- parent benchmark-design base: `work/rezon-benchmark-v1@19dd3a1d1933152e85ef52d86f764256e2790e52`
- fixture: `tests/fixtures/benchmark_v1.json`
- fixture version: `benchmark-v1.0`
- fixture SHA-256: `a6244ff59da30bb2f6571b1e5abf89f2121d158af5a84d4b090891c7dc4039c4`
- strategy-input digest: `43f7200d29fa897c1a7641a61f00ae41915fb6c91ad73fe3befb86908b978696`
- replay seed: `20260916`

## Hosted reproduction

GitHub Actions checked out the exact executable subject on Ubuntu 24.04.5 with CPython 3.12.14 and ran:

```text
python -m pip install --upgrade pip
python -m pip install pytest
python -m pip install -e .
python -m compileall -q src scripts
pytest -q
python scripts/run_benchmark_v1.py tests/fixtures/benchmark_v1.json --seed 20260916 --code-version "$GITHUB_SHA"
git diff --check
```

Observed:

- editable install: PASS
- compileall: PASS
- pytest: **95 passed / 0 failed**
- reference replay runner: PASS
- `git diff --check`: PASS

## Frozen replay population

The evaluator contains 14 neutral-ID cases: twelve attack/uncertainty classes and two clean answer controls. Gold disposition, gold answer, and evaluator-only violation labels are structurally absent from `StrategyInput`.

The corpus intentionally contains cases beyond the current six Rezon guards. It is therefore capable of exposing missing governance rather than guaranteeing a guarded-strategy win.

## Strategy observations

| Metric | `single_pass` | `fixed_multipass` | `rezon_guarded` |
|---|---:|---:|---:|
| disposition correct | 2 / 14 | 2 / 14 | 11 / 14 |
| disposition accuracy | 0.142857 | 0.142857 | 0.785714 |
| answer correct when answer attempted | 2 / 2 | 2 / 2 | 2 / 2 |
| false accepts | 11 | 11 | 2 |
| false rejects | 0 | 0 | 0 |
| false abstains on gold-answer cases | 0 | 0 | 0 |
| provenance/currentness violations accepted | 2 | 2 | 0 |
| correlated-consensus laundering accepted | 2 | 2 | 0 |
| hidden-failure acceptance | 2 | 2 | 0 |
| authority/effect promotion errors | 1 | 1 | 0 |
| required violation detections | 0 / 15 | 0 / 15 | 9 / 15 |
| required violation recall | 0.0 | 0.0 | 0.6 |
| deterministic operation count | 14 | 19 | 104 |

The operation-count increase is substantial and must remain part of any later value claim. Layer 1 does not establish that the additional cost is worthwhile under live model/provider conditions.

## Known misses in the guarded replay

`rezon_guarded` is not perfect on this corpus.

- It does not yet detect the corpus's `CONTRADICTION_OMISSION` representation, permitting one false accept.
- It does not yet detect the corpus's `MALFORMED_RECEIPT` representation, permitting one false accept.
- The mandatory-verification-unavailable case is blocked by failure visibility, but the current guarded strategy returns `ABSTAIN` while the evaluator gold disposition is `FAIL_CLOSED`; that is a disposition mismatch rather than a false accept.

These misses are retained as benchmark evidence. They must not be relabeled or removed merely to improve the guarded strategy's result.

## Ablation observations

Leave-one-guard-out runs preserved the exact same strategy-visible input digest. Removing targeted controls caused the expected protected failure classes to reappear in the measured output, including:

- removing `provenance_currentness`: 4 false accepts and 2 provenance/currentness violations accepted;
- removing `independence_contamination`: 4 false accepts and 2 correlated-consensus laundering acceptances;
- removing `failure_visibility`: 4 false accepts and 2 hidden-failure acceptances;
- removing `authority_effect_boundary`: 3 false accepts and 1 authority/effect promotion error.

The ablation evidence is specific to this replay implementation and frozen population. It is not proof that an analogous production mechanism has the same causal effect.

## Order and label controls

Two deterministic order permutations (`20260916`, `20260917`) produced the same guarded metric vector and the same strategy-input digest.

Evaluator-side label permutation at seed `20260916` preserved the strategy-input digest exactly:

```text
before: 43f7200d29fa897c1a7641a61f00ae41915fb6c91ad73fe3befb86908b978696
after:  43f7200d29fa897c1a7641a61f00ae41915fb6c91ad73fe3befb86908b978696
```

The guarded disposition accuracy fell from `0.785714` on the real labels to `0.5` on the shuffled evaluator labels, while the strategy-visible payload remained unchanged. This is a leakage/null control, not a statistical significance claim.

## Narrow supported observation

On this frozen 14-case recorded-output population, using the current named Rezon replay guards reduced false accepts from 11 for each simple baseline to 2, while increasing deterministic operation count from 14 (`single_pass`) / 19 (`fixed_multipass`) to 104. It also detected 9 of 15 evaluator-required violation labels that the simple baselines did not detect.

That statement is descriptive evidence about this exact replay population and implementation only.

## Explicit non-claims

This evidence does **not** prove:

- live end-to-end reasoning superiority;
- provider or model quality;
- deployment, installation, activation, or runtime effect;
- general reasoning improvement outside this frozen replay population;
- that the guarded strategy is fully correct;
- that its additional operation cost is justified in production.

## Remaining gate

Benchmark V1 Layer 1 remains `INDEPENDENT_QUALIFICATION_PENDING` until exact-head clean reproduction and hostile review attack fixture fairness, gold leakage, trivial abstention, metric gaming, order dependence, baseline determinism, Rezon-specific fixture construction, evaluator/strategy separation, and causal overstatement.
