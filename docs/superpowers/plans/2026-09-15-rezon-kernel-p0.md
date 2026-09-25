# Rezon Kernel V0 P0 Implementation Plan

> **For agentic workers:** Execute task-by-task with test-first discipline; preserve exact-subject evidence and independent hostile review.

**Goal:** Build and qualify the smallest provider-independent Rezon kernel that preserves epistemic semantics, contamination boundaries, provenance, typed failure/effect state, and falsifiable baseline comparison.

**Architecture:** A Python 3.12+ library. Canonical episode state is append-oriented and explicit; workers receive bounded `ExecutionView`s; outputs pass admission before entering state; scheduling is deterministic first; receipts expose sources, independence, failures, and effects. Learned geometry and confidence signals remain outside Kernel V0 authority.

**Tech Stack:** Python 3.12+, standard library, pytest.

**Spec:** `docs/superpowers/specs/2026-09-15-rezon-kernel-design.md`

## Global Constraints
- Never promote hypothesis/model judgment/consensus/confidence into evidence.
- Subject continuity needs association evidence; similarity is advisory.
- Retrieval is not admission; every retrieval binds an exact source/version when known.
- Worker labels do not establish independence.
- Effect lifecycle states never collapse upward.
- No network/model/graph-database dependency in Kernel V0.

---

### Task 1: Core contracts
**Files:** create `pyproject.toml`, `src/rezon/{__init__,epistemics,envelopes,receipts,subjects}.py`; test `tests/test_contracts.py`.
- [ ] Write failing tests for typed proposition/support/hyperrelations, literal `TaskEnvelope`, `FailureState`, `EffectState`, `RetrievalReceipt`, `ResultReceipt`, subject binding, and independence metadata.
- [ ] Run focused tests and verify RED.
- [ ] Implement minimal frozen dataclasses/enums and validation.
- [ ] Run focused tests and require GREEN.

### Task 2: Episode, visibility, and admission
**Files:** create `src/rezon/{episode,nodes,visibility,admission}.py`; test `tests/test_episode_visibility_admission.py`.
- [ ] RED tests: append/retract preserves history; duplicate conflicting IDs fail; blind hypotheses while retaining observations/evidence; record withheld IDs; reject output kinds outside descriptor contract; reject unknown independence as proof of independence.
- [ ] Implement minimal behavior.
- [ ] Require focused GREEN.

### Task 3: Retrieval and deterministic operators
**Files:** create `src/rezon/{retrieval,executors}.py`; test `tests/test_retrieval_execution.py`.
- [ ] RED tests: retrieval receipt preserves source version and admission status; stale retrieval cannot become evidence by retrieval alone; deterministic hypothesis/contradiction/falsifier operators preserve kind and support refs.
- [ ] Implement minimal behavior.
- [ ] Require focused GREEN.

### Task 4: Scheduler, runner, trace, receipts
**Files:** create `src/rezon/{scheduler,runner,trace}.py`; test `tests/test_runner_scheduler.py`.
- [ ] RED tests: mandatory verification first; contradiction handling; independent generation; falsification; explicit resource exhaustion; mandatory worker failure remains visible; trace records visible/blinded inputs and independence; final receipt cannot imply a higher effect state.
- [ ] Implement deterministic synchronous runner.
- [ ] Require focused and full GREEN.

### Task 5: Hostile benchmark harness
**Files:** create `src/rezon/benchmark.py`, `tests/fixtures/hostile_cases.json`, `tests/test_hostile_benchmark.py`.
- [ ] RED cases for proposition substitution, stale/rollback source, duplicate-source laundering, correlated-worker consensus, learned/confidence authority laundering, malformed receipt, partial-worker failure, and budget exhaustion.
- [ ] Implement simple/fixed-multipass/dynamic-Rezon comparison API.
- [ ] Require all hostile cases detect their targeted broken behavior.

### Task 6: Exact-subject qualification
**Files:** create `docs/qualification/KERNEL_V0_ACCEPTANCE.md`; update `README.md` status only after evidence exists.
- [ ] From clean exact-head checkout run Python 3.12 `pytest -q` and `git diff --check`.
- [ ] Record commit/tree, environment, commands, counts, known limits, and what PASS does not prove.
- [ ] Obtain specialist hostile/regression findings and patch valid defects.
- [ ] Re-run exact-head qualification after every patch.
- [ ] Do not claim reasoning superiority until comparative benchmarks support it.
