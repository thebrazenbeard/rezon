# Rezon Benchmark V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic recorded-output replay benchmark that compares single-pass, fixed-multipass, and Rezon-governed integration on identical frozen reasoning material.

**Architecture:** Keep the existing Kernel V0 untouched. Add a replay schema, strategy layer, semantic metrics, and experimental controls as a separate evaluation subsystem. Fixtures contain candidate outputs and provenance/lineage metadata; strategies receive identical cases and return typed dispositions/traces; reports preserve semantic and cost metrics separately.

**Tech Stack:** Python 3.12+, standard library, pytest.

**Spec:** `docs/superpowers/specs/2026-09-16-rezon-benchmark-v1-design.md`

## Global Constraints

- No live LLM/provider calls in Benchmark V1.
- All strategies receive the same replay payload for a case.
- Gold labels are never passed to strategies.
- Disposition is one of `ANSWER`, `ABSTAIN`, `FAIL_CLOSED`.
- Do not collapse semantic and cost metrics into one score.
- Advisory confidence/entropy/geometry/path signals never establish truth, evidence, identity, authority, or currentness.
- Preserve PR #8 / Kernel R2 unchanged; benchmark work stays on `work/rezon-benchmark-v1`.

---

### Task 1: Replay case and outcome contracts

**Files:**
- Create: `src/rezon/replay.py`
- Test: `tests/test_replay_contracts.py`

**Interfaces:**
- Produces: `Disposition`, `ReplayCandidate`, `ReplayCase`, `StrategyOutcome`, `ReplayValidationError`, `load_replay_cases(path)`.
- Consumes: standard-library `dataclasses`, `enum`, `json`, `pathlib` only.

- [ ] **Step 1: Write failing contract tests**

```python
from rezon.replay import Disposition, ReplayCase, ReplayCandidate, ReplayValidationError


def test_gold_disposition_requires_answer_only_for_answer_cases():
    case = ReplayCase(case_id="c1", literal_request="A?", gold_disposition=Disposition.ANSWER, gold_answer=None)
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_candidate_identity_and_lineage_are_explicit():
    c = ReplayCandidate(candidate_id="cand1", execution_id="x1", answer="A", model_id="m", provider_id="p")
    assert c.execution_id == "x1"
```

Also test duplicate case/candidate IDs, missing literal request, invalid source-version/currentness combinations, and fixture version/provenance requirements.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_contracts.py -q`
Expected: import/module failure because `rezon.replay` does not exist.

- [ ] **Step 3: Implement minimal frozen contracts and loader**

`ReplayCase` must carry case identity, literal request, gold disposition/answer, candidates, source records, expected violations, fixture version and provenance. `ReplayCandidate` must carry worker/execution identity, answer, accepted evidence/source refs, lineage/exposure/common-evidence metadata, failures, authority/effect claims, and advisory signals.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_contracts.py -q && pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay.py tests/test_replay_contracts.py
git commit -m "feat: add benchmark replay contracts"
```

### Task 2: Strategy interface and baseline integrators

**Files:**
- Create: `src/rezon/replay_strategies.py`
- Test: `tests/test_replay_strategies.py`

**Interfaces:**
- Consumes: `ReplayCase`, `ReplayCandidate`, `StrategyOutcome`, `Disposition` from Task 1.
- Produces: `single_pass(case)`, `fixed_multipass(case)`, `rezon_guarded(case)`.

- [ ] **Step 1: Write RED tests with identical candidate payloads**

Cases must prove:
- `single_pass` selects the designated primary candidate without hidden evidence;
- `fixed_multipass` applies a deterministic majority/first-valid rule and does not inspect gold labels;
- `rezon_guarded` rejects stale/unadmitted evidence, correlated consensus, hidden failures, proposition substitution, and unsupported authority/effect promotion;
- clean controls return the same correct answer across all strategies;
- insufficient evidence yields `ABSTAIN` or `FAIL_CLOSED`, not invented certainty.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_strategies.py -q`
Expected: missing strategy module/functions.

- [ ] **Step 3: Implement minimal deterministic strategies**

`rezon_guarded` must use only metadata already present in the replay case; it must not call Kernel executors, models, tools, or gold labels. Its trace must list consulted candidate/source IDs, violations detected, and rejection reasons.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_strategies.py -q && pytest -q`

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay_strategies.py tests/test_replay_strategies.py
git commit -m "feat: add replay comparison strategies"
```

### Task 3: Semantic metrics and pairwise report

**Files:**
- Create: `src/rezon/replay_metrics.py`
- Test: `tests/test_replay_metrics.py`

**Interfaces:**
- Consumes: replay cases and strategy outcomes.
- Produces: `StrategyMetrics`, `PairwiseDelta`, `evaluate_strategy(cases, strategy)`, `compare_reports(a, b)`.

- [ ] **Step 1: Write RED tests**

Assert separate accounting for:
- disposition accuracy;
- answer accuracy conditional on `ANSWER`;
- false accepts;
- false rejects/abstains;
- unsupported acceptance;
- provenance/currentness violations accepted;
- correlated-consensus laundering accepted;
- hidden-failure acceptance;
- authority/effect-promotion errors;
- violation-detection recall;
- operation count and wall-clock time.

A strategy that always abstains must not equal a strategy that answers clean cases correctly.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_metrics.py -q`

- [ ] **Step 3: Implement typed metrics without aggregate prestige score**

Pairwise deltas must preserve each metric independently. Do not calculate a weighted total.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_metrics.py -q && pytest -q`

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay_metrics.py tests/test_replay_metrics.py
git commit -m "feat: add benchmark semantic metrics"
```

### Task 4: Frozen Benchmark V1 fixture corpus

**Files:**
- Create: `tests/fixtures/benchmark_v1.json`
- Create: `tests/test_benchmark_v1_fixtures.py`

**Interfaces:**
- Consumes: Task 1 loader/validation.
- Produces: deterministic corpus with version/provenance.

- [ ] **Step 1: Write fixture-validation tests before fixture**

Require at least one case for each spec class: proposition substitution, stale source, rollback, duplicate evidence, correlated consensus, retrieved-unadmitted evidence, advisory-signal authority, omitted contradiction, partial worker failure, mandatory verifier unavailable, malformed semantic outcome, insufficient evidence, and clean control.

Require both `ANSWER` and non-answer gold dispositions.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_benchmark_v1_fixtures.py -q`
Expected: fixture missing.

- [ ] **Step 3: Create deterministic fixture corpus**

Every case must use neutral IDs that do not encode expected result. Every candidate must be plausible under all compared strategy families. Include exact fixture version `benchmark-v1.0` and source/provenance note.

- [ ] **Step 4: Run GREEN plus strategy replay over corpus**

Run: `pytest tests/test_benchmark_v1_fixtures.py tests/test_replay_strategies.py -q`

- [ ] **Step 5: Commit**

```text
git add tests/fixtures/benchmark_v1.json tests/test_benchmark_v1_fixtures.py
git commit -m "test: add frozen benchmark v1 replay corpus"
```

### Task 5: Ablation, order-permutation, and null controls

**Files:**
- Create: `src/rezon/replay_experiments.py`
- Test: `tests/test_replay_experiments.py`

**Interfaces:**
- Consumes: replay cases, strategies, metrics.
- Produces: `run_order_permutations`, `run_guard_ablation`, `run_label_permutation_control`.

- [ ] **Step 1: Write RED tests**

Tests must prove:
- deterministic strategies are invariant to case order;
- disabling one Rezon safeguard can expose the fixture specifically protected by that safeguard;
- label permutation destroys apparent semantic advantage rather than preserving an impossible perfect result;
- experiment seeds and permutations are emitted in results.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_experiments.py -q`

- [ ] **Step 3: Implement deterministic experimental controls**

Use `random.Random(seed)` only; no numpy dependency. Guard ablation must toggle named controls, not mutate fixture gold labels.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_experiments.py -q && pytest -q`

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay_experiments.py tests/test_replay_experiments.py
git commit -m "feat: add benchmark ablation and permutation controls"
```

### Task 6: Reference runner and exact report artifact

**Files:**
- Create: `scripts/run_benchmark_v1.py`
- Create: `docs/qualification/BENCHMARK_V1_REFERENCE.md`
- Test: `tests/test_benchmark_v1_runner.py`

**Interfaces:**
- Consumes: frozen fixture corpus, three strategies, metrics, experiments.
- Produces: deterministic JSON report to stdout/file plus human-readable reference qualification document.

- [ ] **Step 1: Write RED runner test**

Invoke the script against `tests/fixtures/benchmark_v1.json`; assert report includes fixture version/digest, strategy names, independent metric vectors, pairwise deltas, experiment seeds, exact benchmark code version supplied by caller, and explicit `does_not_prove` statements.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_benchmark_v1_runner.py -q`

- [ ] **Step 3: Implement runner**

The runner must not describe a strategy as superior. It reports observed deltas only. Reference documentation may state whether a predetermined falsification condition was triggered, but not generalize beyond the fixture population.

- [ ] **Step 4: Run complete verification**

Run:

```text
python -m compileall -q src scripts
pytest -q
python scripts/run_benchmark_v1.py tests/fixtures/benchmark_v1.json --seed 20260916

git diff --check
```

- [ ] **Step 5: Record exact reference evidence and commit**

Record exact commit/tree, Python version, fixture digest/version, commands, per-strategy metric vectors, known limits, and what the replay does not prove.

```text
git add scripts/run_benchmark_v1.py docs/qualification/BENCHMARK_V1_REFERENCE.md tests/test_benchmark_v1_runner.py
git commit -m "feat: qualify Rezon benchmark v1 replay"
```

### Task 7: Independent hostile review gate

**Files:**
- Modify only if review identifies a defect.

- [ ] **Step 1: Freeze exact candidate and clean-clone reproduce**
- [ ] **Step 2: Send exact head/tree/fixture digest to Masa and Mune through the Bus**
- [ ] **Step 3: Require reviewers to attack fixture fairness, gold leakage, trivial abstention, metric gaming, order dependence, and Rezon-specific case construction**
- [ ] **Step 4: Repair valid findings test-first on a new exact head and rerun complete verification**
- [ ] **Step 5: Do not promote replay evidence into live-model reasoning qualification**
