# Rezon Benchmark V1 Layer 1 Reference Evidence R2

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / REPLAY_OBSERVED / INDEPENDENT_QUALIFICATION_PENDING`

This R2 record supersedes the R1 reference evidence for current Benchmark V1 qualification while preserving the original R1 artifact as historical evidence. It records deterministic recorded-output replay only. It does not qualify live model/provider reasoning, deployment, installation, activation, runtime effect, or general reasoning superiority.

## Exact executable subject

- repository: `thebrazenbeard/rezon`
- branch: `rezon/benchmark-v1-r2-fairness`
- executable/reference head: `8cf571358703bf79e2a430d18b3f6d707b2e9327`
- executable/reference tree: `276c203c54da887595a1851a72d82e2478fb1ed3`
- R1 review ancestor: `3674fdb2374232ca1d23e3887e7f787ee237049e`
- benchmark design base: `work/rezon-benchmark-v1@19dd3a1d1933152e85ef52d86f764256e2790e52`
- fixture version: `benchmark-v1.0`
- adverse fixture: `tests/fixtures/benchmark_v1.json`
- adverse fixture SHA-256: `a6244ff59da30bb2f6571b1e5abf89f2121d158af5a84d4b090891c7dc4039c4`
- clean-control supplement: `tests/fixtures/benchmark_v1_clean_controls.json`
- clean-control supplement SHA-256: `2bd93ec82fb9c8bd281c4d3e19d7708fa325f6f5494a7b8ca132873d62481925`
- composite fixture-manifest SHA-256: `9a6d277f80d3bea4552aad745cb6204538ecf0b150590bc5965dcaa73498087c`
- composite strategy-input digest: `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`
- replay seed: `20260916`

The original 14-case adverse fixture is byte-for-byte unchanged from R1. R2 adds clean controls as a separate file rather than rewriting historical adverse evidence.

## Why R2 exists

R1 had three fairness/accounting defects discovered during Task 9 self-hostile review:

1. the corpus contained 12 non-answer cases but only 2 answer cases, making an always-abstain policy superficially competitive on disposition accuracy;
2. missing wall-clock measurements were aggregated as `0.0`, creating false precision;
3. accepting evidence that failed admission did not increment the benchmark's unsupported-acceptance metric.

R2 froze these defects as failing tests before repair. Exact RED head `b093b43f899dad50eae6942f84d941e4281ce1f9` reproduced **5 failed / 94 passed**: one population-balance failure and four metric/cost-accounting failures.

## R2 repairs

- The original adverse fixture remains unchanged.
- Ten neutral clean-answer controls were added in a separate supplement, producing a 24-case composite population with **12 ANSWER / 12 non-ANSWER** gold dispositions.
- `wall_clock_seconds` is now `null` unless every evaluated case supplies a measurement; partial or absent timing data is not treated as zero.
- Pairwise wall-clock deltas remain `null` when either side is unmeasured.
- `ADMISSION_INTEGRITY` acceptance contributes to `unsupported_acceptance`.
- The runner emits each fixture file and SHA-256 plus a deterministic composite manifest digest.

An always-ABSTAIN strategy would now be disposition-correct on 10/24 cases (41.67%): it gets the ten ABSTAIN cases right, misses the two FAIL_CLOSED cases, and false-abstains on all twelve ANSWER controls. This is below both simple baselines and the guarded strategy.

## Hosted reproduction

GitHub Actions freshly checked out exact executable head `8cf571358703bf79e2a430d18b3f6d707b2e9327` on Ubuntu 24.04.5 with CPython 3.12.14 and ran:

```text
python -m pip install --upgrade pip
python -m pip install pytest
python -m pip install -e .
python -m compileall -q src scripts
pytest -q
python scripts/run_benchmark_v1.py \
  tests/fixtures/benchmark_v1.json \
  tests/fixtures/benchmark_v1_clean_controls.json \
  --seed 20260916 \
  --code-version "$GITHUB_SHA"
git diff --check
```

Observed:

- editable install: PASS
- compileall: PASS
- pytest: **99 passed / 0 failed**
- composite reference replay runner: PASS
- `git diff --check`: PASS

## R2 replay observations

| Metric | `single_pass` | `fixed_multipass` | `rezon_guarded` |
|---|---:|---:|---:|
| disposition correct | 12 / 24 | 12 / 24 | 21 / 24 |
| disposition accuracy | 0.500000 | 0.500000 | 0.875000 |
| answer correct when answer attempted | 12 / 12 | 12 / 12 | 12 / 12 |
| false accepts | 11 | 11 | 2 |
| false rejects | 0 | 0 | 0 |
| false abstains on gold-answer cases | 0 | 0 | 0 |
| unsupported acceptance | 1 | 1 | 0 |
| provenance/currentness violations accepted | 2 | 2 | 0 |
| correlated-consensus laundering accepted | 2 | 2 | 0 |
| hidden-failure acceptance | 2 | 2 | 0 |
| authority/effect-state promotion errors | 1 | 1 | 0 |
| required violation detections | 0 / 15 | 0 / 15 | 9 / 15 |
| required violation recall | 0.0 | 0.0 | 0.6 |
| deterministic operation count | 24 | 29 | 174 |
| wall-clock seconds | unmeasured | unmeasured | unmeasured |

The operation-count increase remains substantial and is now shown without inventing a wall-clock value. Layer 1 does not establish that the additional operations are worthwhile under live model/provider conditions.

## Known guarded misses retained

R2 intentionally does not repair the known R1 semantic misses merely to improve benchmark performance:

- `CONTRADICTION_OMISSION` remains a false accept;
- `MALFORMED_RECEIPT` remains a false accept;
- mandatory-verification unavailability is blocked, but the guarded result is `ABSTAIN` while evaluator gold is `FAIL_CLOSED`.

These remain open evidence for later mechanism work and hostile review.

## Ablation observations

All leave-one-guard-out runs used the same composite strategy-input digest `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`.

Notable removals:

- without `provenance_currentness`: 19/24 disposition-correct, 4 false accepts, 2 provenance/currentness violations accepted;
- without `admission_integrity`: 20/24 disposition-correct, 3 false accepts, 1 unsupported acceptance;
- without `independence_contamination`: 19/24 disposition-correct, 4 false accepts, 2 correlated-consensus laundering acceptances;
- without `failure_visibility`: 20/24 disposition-correct, 4 false accepts, 2 hidden-failure acceptances;
- without `authority_effect_boundary`: 20/24 disposition-correct, 3 false accepts, 1 authority/effect promotion error.

Ablation evidence remains specific to this frozen replay implementation and does not establish equivalent causal effects in production.

## Order and evaluator-label controls

Order permutations at seeds `20260916` and `20260917` preserved the guarded metric vector and exact strategy-input digest.

Evaluator-side label permutation at seed `20260916` preserved strategy-visible input exactly:

```text
before: 56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a
after:  56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a
```

Guarded disposition accuracy fell from `0.875` on the actual labels to `0.5` on shuffled evaluator labels. This is a leakage/null control, not a statistical-significance result.

## Narrow supported observation

On this frozen, balanced 24-case recorded-output population, the current named Rezon replay guards reduced false accepts from 11 for each simple baseline to 2 while increasing deterministic operation count from 24 (`single_pass`) / 29 (`fixed_multipass`) to 174. The guarded strategy detected 9 of 15 evaluator-required violation labels; the simple baselines detected none.

This is descriptive evidence about this exact replay population and implementation only.

## Explicit non-claims

R2 does **not** prove:

- live end-to-end reasoning superiority;
- provider or model quality;
- deployment, installation, activation, or runtime effect;
- general reasoning improvement outside this frozen replay population;
- that the guarded strategy is fully correct;
- that its additional operation cost is justified in production;
- a measured latency advantage or disadvantage, because wall-clock timing is not measured in Layer 1.

## Remaining gate

R2 remains `INDEPENDENT_QUALIFICATION_PENDING`. The R1 hostile-review subject is superseded for current qualification once the exact R2 documentation head is frozen and routed. Independent review must attack the R2 composite corpus, fairness, gold leakage, trivial rejection, metric gaming, baseline determinism, guarded bypasses, evaluator/strategy separation, composite-fixture provenance, operation-count semantics, and causal overstatement.
