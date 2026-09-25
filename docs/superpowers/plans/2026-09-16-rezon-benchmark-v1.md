# Rezon Benchmark V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Layer 1 of the Rezon benchmark program: a deterministic recorded-output replay benchmark comparing single-pass, fixed-multipass, and Rezon-governed integration on identical frozen reasoning material with structural gold-label isolation.

**Architecture:** Keep Kernel source untouched. Add an evaluator-owned `ReplayCase`, a separate gold-free `StrategyInput`, deterministic replay strategies, semantic/cost metrics, named guard ablations, permutation controls, and a reference runner. The implementation remains isolated on `work/rezon-benchmark-v1`; live matched-budget trials and learned-routing experiments are later layers and are not implemented here.

**Tech Stack:** Python 3.12+, standard library, pytest.

**Spec:** `docs/superpowers/specs/2026-09-16-rezon-benchmark-v1-design.md`

## Global Constraints

- No live LLM/provider/tool calls in Benchmark V1.
- Kernel source files must not be modified by this plan.
- All strategies receive the same `StrategyInput` for a case.
- Gold disposition, gold answer, expected evaluator-only violations, and evaluator state must be absent from `StrategyInput`.
- Disposition is exactly `ANSWER`, `ABSTAIN`, or `FAIL_CLOSED`.
- Do not collapse semantic and cost metrics into one score.
- Advisory confidence/entropy/geometry/path signals never establish truth, evidence, identity, authority, or currentness.
- Preserve PR #8 and PR #10 unchanged; benchmark work stays on `work/rezon-benchmark-v1`.
- Layer 1 replay evidence must not be generalized into live end-to-end reasoning superiority.

---

### Task 1: Replay contracts with structural gold isolation

**Files:**
- Create: `src/rezon/replay.py`
- Test: `tests/test_replay_contracts.py`

**Interfaces:**
- Produces: `Disposition`, `ReplaySource`, `ReplayCandidate`, `StrategyInput`, `ReplayCase`, `ReplayStrategyOutcome`, `ReplayValidationError`, `load_replay_cases(path)`.
- `ReplayCase.to_strategy_input() -> StrategyInput` is the only supported evaluator-to-strategy projection.
- Consumes: standard-library `dataclasses`, `enum`, `json`, `pathlib` only.

- [ ] **Step 1: Write failing contract tests**

```python
import dataclasses
import pytest

from rezon.replay import (
    Disposition,
    ReplayCandidate,
    ReplayCase,
    ReplaySource,
    ReplayValidationError,
)


def test_answer_case_requires_gold_answer():
    case = ReplayCase(
        case_id="case-a",
        fixture_version="benchmark-v1.0",
        fixture_provenance="fixture:test",
        literal_request="Is A true?",
        primary_candidate_id="cand-a",
        gold_disposition=Disposition.ANSWER,
        gold_answer=None,
        expected_violations=(),
        candidates=(),
        sources=(),
    )
    with pytest.raises(ReplayValidationError):
        case.validate()


def test_strategy_input_structurally_excludes_gold_and_expected_labels():
    candidate = ReplayCandidate(
        candidate_id="cand-a",
        worker_id="worker-a",
        execution_id="exec-a",
        answer="A",
        model_id="model-a",
        provider_id="provider-a",
    )
    case = ReplayCase(
        case_id="case-a",
        fixture_version="benchmark-v1.0",
        fixture_provenance="fixture:test",
        literal_request="Is A true?",
        primary_candidate_id="cand-a",
        gold_disposition=Disposition.ANSWER,
        gold_answer="A",
        expected_violations=("PROVENANCE_CURRENTNESS",),
        candidates=(candidate,),
        sources=(),
    )
    projected = case.to_strategy_input()
    field_names = {field.name for field in dataclasses.fields(projected)}
    assert "gold_disposition" not in field_names
    assert "gold_answer" not in field_names
    assert "expected_violations" not in field_names
    assert projected.primary_candidate_id == "cand-a"
```

Also test duplicate case/candidate/source IDs, missing primary candidate, missing literal request, invalid disposition/answer combinations, fixture version/provenance requirements, and structurally valid suspicious candidate claims remaining loadable for strategy testing.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_contracts.py -q`
Expected: import/module failure because `rezon.replay` does not exist.

- [ ] **Step 3: Implement minimal frozen contracts and loader**

Use frozen dataclasses. `ReplaySource` must expose explicit source identity/version/locator/admission/currentness/origin fields. `ReplayCandidate` must expose candidate/worker/execution IDs, answer, source/evidence refs, model/provider/prompt/context lineage, candidate exposure/common-evidence metadata, failures, receipt/effect/authority claims, and optional advisory signals.

`ReplayCase.to_strategy_input()` must copy only strategy-visible fields. Never pass `self` through or keep an evaluator back-reference.

Use `ReplayStrategyOutcome` rather than defining a second generic `StrategyOutcome` that conflicts with `src/rezon/benchmark.py`.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_contracts.py -q && pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay.py tests/test_replay_contracts.py
git commit -m "feat: add gold-isolated replay contracts"
```

### Task 2: Strategy interface and deterministic baseline integrators

**Files:**
- Create: `src/rezon/replay_strategies.py`
- Test: `tests/test_replay_strategies.py`

**Interfaces:**
- Consumes: `StrategyInput`, `ReplayCandidate`, `ReplayStrategyOutcome`, `Disposition` from Task 1.
- Produces: `single_pass(strategy_input)`, `fixed_multipass(strategy_input)`.

- [ ] **Step 1: Write RED tests for exact baseline behavior**

```python
from rezon.replay import Disposition
from rezon.replay_strategies import fixed_multipass, single_pass


def test_single_pass_selects_exact_primary_candidate(strategy_input_factory):
    inp = strategy_input_factory(
        primary="cand-2",
        answers=("wrong", "right", "wrong"),
    )
    outcome = single_pass(inp)
    assert outcome.disposition is Disposition.ANSWER
    assert outcome.answer == "right"
    assert outcome.accepted_candidate_ids == ("cand-2",)


def test_fixed_multipass_tie_breaks_by_candidate_order(strategy_input_factory):
    inp = strategy_input_factory(
        primary="cand-3",
        answers=("A", "B", "B", "A"),
    )
    outcome = fixed_multipass(inp)
    assert outcome.answer == "A"
```

Also prove:
- explicit failed/no-answer candidates are ineligible for the fixed baseline;
- no eligible candidate yields `FAIL_CLOSED`;
- normalized exact answer matching is deterministic;
- neither baseline receives/uses provenance, currentness, independence, gold, or expected-violation data to improve its decision.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_strategies.py -q`
Expected: missing strategy module/functions.

- [ ] **Step 3: Implement the two simple baselines**

`single_pass` selects `primary_candidate_id` exactly.

`fixed_multipass`:
1. removes only candidates with explicit execution failure or `answer is None`;
2. counts normalized exact answer strings;
3. selects the unique highest count;
4. resolves ties using earliest eligible fixture candidate order;
5. returns `FAIL_CLOSED` if no eligible candidate exists.

Trace consulted candidate IDs and deterministic reason. Do not inspect governance metadata for baseline selection.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_strategies.py -q && pytest -q`

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay_strategies.py tests/test_replay_strategies.py
git commit -m "feat: add deterministic replay baselines"
```

### Task 3: Named Rezon guard configuration and guarded integrator

**Files:**
- Modify: `src/rezon/replay_strategies.py`
- Test: `tests/test_rezon_guarded_replay.py`

**Interfaces:**
- Produces: `GuardName`, `GuardConfig`, `ALL_GUARDS`, `rezon_guarded(strategy_input, guards=ALL_GUARDS)`.
- Required guard names: `proposition_fidelity`, `provenance_currentness`, `admission_integrity`, `independence_contamination`, `failure_visibility`, `authority_effect_boundary`.

- [ ] **Step 1: Write RED tests for each guard independently**

For each guard, create a structurally valid strategy input that is clean except for the target semantic defect. Assert full guards reject/abstain/fail closed as specified, then disable only that guard and assert the corresponding bad candidate can pass while unrelated guards remain active.

Also test:
- a clean control answers correctly with all guards enabled;
- insufficient evidence does not invent certainty;
- proposition substitution compares candidate solved/literal semantics present in the replay payload rather than using fixture labels;
- correlated consensus uses lineage/exposure/common-evidence metadata, not worker count;
- advisory confidence/path/geometry/model prestige cannot establish evidence or authority.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_rezon_guarded_replay.py -q`

- [ ] **Step 3: Implement minimal guard pipeline**

Each named guard returns explicit detected violation/rejection data. `rezon_guarded` composes enabled guards in fixed order and returns a `ReplayStrategyOutcome` with accepted/rejected candidate IDs, detected violations, unresolved state and a trace of consulted metadata.

The integrator may inspect only `StrategyInput`; it must not import evaluator functions, fixture gold fields, Kernel executors, providers or tools.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_rezon_guarded_replay.py -q && pytest -q`

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay_strategies.py tests/test_rezon_guarded_replay.py
git commit -m "feat: add named guarded replay integrator"
```

### Task 4: Semantic metrics and pairwise report

**Files:**
- Create: `src/rezon/replay_metrics.py`
- Test: `tests/test_replay_metrics.py`

**Interfaces:**
- Consumes: evaluator-owned `ReplayCase`, strategy callable accepting only `StrategyInput`, and `ReplayStrategyOutcome`.
- Produces: `StrategyMetrics`, `PairwiseDelta`, `evaluate_strategy(cases, strategy)`, `compare_reports(a, b)`.

- [ ] **Step 1: Write RED metric tests**

Assert separate accounting for:
- disposition accuracy;
- answer accuracy conditional on gold `ANSWER` and strategy `ANSWER`;
- false accepts;
- false rejects;
- false abstains;
- unsupported acceptance;
- provenance/currentness violations accepted;
- correlated-consensus laundering accepted;
- hidden-failure acceptance;
- authority/effect-promotion errors;
- required violation-detection recall;
- operation count and wall-clock time.

Add an explicit reject-everything control:

```python
def test_always_abstain_is_penalized_on_clean_answer_cases(clean_answer_cases):
    metrics = evaluate_strategy(clean_answer_cases, always_abstain)
    assert metrics.false_abstains == len(clean_answer_cases)
    assert metrics.disposition_correct == 0
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_metrics.py -q`

- [ ] **Step 3: Implement evaluator-side projection and typed metrics**

`evaluate_strategy` must call `case.to_strategy_input()` before invoking a strategy. Pairwise deltas preserve every metric independently. Do not compute a weighted or prestige score.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_metrics.py -q && pytest -q`

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay_metrics.py tests/test_replay_metrics.py
git commit -m "feat: add replay semantic metrics"
```

### Task 5: Frozen Benchmark V1 replay corpus

**Files:**
- Create: `tests/fixtures/benchmark_v1.json`
- Create: `tests/test_benchmark_v1_fixtures.py`

**Interfaces:**
- Consumes: Task 1 loader/validation.
- Produces: deterministic corpus with fixture version/provenance and neutral IDs.

- [ ] **Step 1: Write fixture-validation tests before the fixture**

Require at least one case for every spec class: proposition substitution, stale source, rollback, duplicate evidence, correlated consensus, retrieved-unadmitted evidence, advisory-signal authority, omitted contradiction, partial worker failure, mandatory verifier unavailable, malformed semantic receipt, insufficient evidence, and clean control.

Require both `ANSWER` and non-answer gold dispositions and multiple clean `ANSWER` controls so reject-everything cannot look competitive.

Assert `StrategyInput` generated from every loaded case contains no gold/expected-label fields.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_benchmark_v1_fixtures.py -q`
Expected: fixture missing.

- [ ] **Step 3: Create deterministic fixture corpus**

Every case uses neutral IDs that do not encode the expected result. Candidate payloads must be plausible inputs to all three strategies. Set exact fixture version `benchmark-v1.0` and provenance note.

Do not encode attack class into candidate IDs, source IDs, candidate order, or primary-candidate naming.

- [ ] **Step 4: Run GREEN plus all three strategies over corpus**

Run: `pytest tests/test_benchmark_v1_fixtures.py tests/test_replay_strategies.py tests/test_rezon_guarded_replay.py -q`

- [ ] **Step 5: Commit**

```text
git add tests/fixtures/benchmark_v1.json tests/test_benchmark_v1_fixtures.py
git commit -m "test: add frozen benchmark v1 replay corpus"
```

### Task 6: Ablation, order-permutation and evaluator-side null controls

**Files:**
- Create: `src/rezon/replay_experiments.py`
- Test: `tests/test_replay_experiments.py`

**Interfaces:**
- Consumes: replay cases, strategies, metrics, `GuardConfig`.
- Produces: `run_order_permutations`, `run_guard_ablation`, `run_label_permutation_control`.

- [ ] **Step 1: Write RED tests**

Tests must prove:
- deterministic strategy metrics are invariant to case order;
- leave-one-guard-out changes only guard configuration, not fixture payload/gold;
- the corresponding protected case becomes vulnerable when its guard is removed;
- label permutation changes evaluator labels only and leaves serialized `StrategyInput` digests identical;
- label permutation destroys an apparent perfect semantic result rather than preserving impossible performance;
- experiment seeds/permutation IDs are emitted.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_replay_experiments.py -q`

- [ ] **Step 3: Implement deterministic controls**

Use `random.Random(seed)` only; no numpy dependency. Compute a canonical serialization/digest of every projected `StrategyInput` before and after label permutation and assert equality inside the experiment helper.

Guard ablation toggles exactly one `GuardName` at a time.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_replay_experiments.py -q && pytest -q`

- [ ] **Step 5: Commit**

```text
git add src/rezon/replay_experiments.py tests/test_replay_experiments.py
git commit -m "feat: add replay ablation and permutation controls"
```

### Task 7: Legacy benchmark compatibility boundary

**Files:**
- Modify: `src/rezon/benchmark.py`
- Modify: `tests/test_hostile_benchmark.py`
- Test: `tests/test_benchmark_compatibility.py`

**Interfaces:**
- Existing `BenchmarkCase`, `StrategyOutcome`, `BenchmarkMetrics`, `run_benchmark` remain available for Kernel-era hostile tests.
- New replay code must not silently replace their semantics.

- [ ] **Step 1: Write compatibility tests**

Verify the current legacy hostile benchmark API still produces its existing counts and that `ReplayStrategyOutcome` is a distinct type.

- [ ] **Step 2: Run RED only if compatibility work is actually required**

Run: `pytest tests/test_hostile_benchmark.py tests/test_benchmark_compatibility.py -q`

- [ ] **Step 3: Make the smallest compatibility change**

Prefer no production change if coexistence already works. If shared helpers are needed, extract only behavior whose semantics are identical; do not alias replay outcomes onto the legacy generic outcome.

- [ ] **Step 4: Run GREEN and full suite**

Run: `pytest tests/test_hostile_benchmark.py tests/test_benchmark_compatibility.py -q && pytest -q`

- [ ] **Step 5: Commit only if files changed**

```text
git add src/rezon/benchmark.py tests/test_hostile_benchmark.py tests/test_benchmark_compatibility.py
git commit -m "test: preserve legacy benchmark compatibility"
```

### Task 8: Reference runner and exact replay report artifact

**Files:**
- Create: `scripts/run_benchmark_v1.py`
- Create: `docs/qualification/BENCHMARK_V1_REFERENCE.md`
- Test: `tests/test_benchmark_v1_runner.py`

**Interfaces:**
- Consumes: frozen fixture corpus, three strategies, metrics and experiments.
- Produces: deterministic JSON report plus human-readable reference qualification document.

- [ ] **Step 1: Write RED runner test**

Invoke the script against `tests/fixtures/benchmark_v1.json`; assert report includes:
- fixture version and SHA-256 digest;
- benchmark code version supplied by caller;
- strategy names;
- independent semantic/cost metric vectors;
- pairwise deltas;
- operation counts;
- guard-ablation results;
- permutation seeds/IDs;
- strategy-input digest evidence for label-shuffle isolation;
- exact `does_not_prove` statements.

- [ ] **Step 2: Run RED**

Run: `pytest tests/test_benchmark_v1_runner.py -q`

- [ ] **Step 3: Implement runner**

The runner reports observed metric vectors/deltas and whether predefined falsification conditions fired. It must not emit a generic "best strategy", "reasoning improvement", or weighted leaderboard.

- [ ] **Step 4: Run complete verification**

Run:

```text
python -m compileall -q src scripts
pytest -q
python scripts/run_benchmark_v1.py tests/fixtures/benchmark_v1.json --seed 20260916 --code-version <EXACT_COMMIT>
git diff --check
```

- [ ] **Step 5: Record exact reference evidence and commit**

Record exact commit/tree, Python version, fixture digest/version, commands, per-strategy metric vectors, known limits, and the narrow population-level claim the replay can support.

```text
git add scripts/run_benchmark_v1.py docs/qualification/BENCHMARK_V1_REFERENCE.md tests/test_benchmark_v1_runner.py
git commit -m "feat: qualify Rezon benchmark v1 replay"
```

### Task 9: Clean-checkout reproduction and independent hostile review gate

**Files:**
- Modify only if reproduction/review identifies a defect.

- [ ] **Step 1: Freeze exact candidate head/tree and fixture digest**
- [ ] **Step 2: Reproduce from a fresh checkout with Python 3.12+ using install, compile, full pytest, reference runner and `git diff --check`**
- [ ] **Step 3: Send exact head/tree/fixture digest/reference-report digest to Masa and Mune through the Bus**
- [ ] **Step 4: Require reviewers to attack fixture fairness, gold leakage, trivial abstention, metric gaming, order dependence, baseline determinism, Rezon-specific case construction, evaluator/strategy data separation and misleading causal attribution**
- [ ] **Step 5: Repair valid findings test-first on a new exact head and rerun complete verification**
- [ ] **Step 6: Do not promote Layer 1 replay evidence into Layer 2 live-model qualification**

## Plan self-review record

- Spec coverage: all Layer 1 acceptance requirements map to Tasks 1-9.
- Gold leakage: structurally prevented by `ReplayCase -> StrategyInput` projection and rechecked in fixtures/label permutation.
- Baseline ambiguity: primary selection, failure eligibility and tie-breaking are explicit.
- Type consistency: replay uses `ReplayStrategyOutcome`; legacy `benchmark.StrategyOutcome` remains a separate compatibility surface.
- Ablation causality: named guard toggles hold replay payload constant.
- Layer boundary: Layer 2 live matched-budget trials and Layer 3 learned routing are explicitly outside this plan.
- Integration boundary: this branch does not modify the R3 review subject or advance PR #8/#10.
