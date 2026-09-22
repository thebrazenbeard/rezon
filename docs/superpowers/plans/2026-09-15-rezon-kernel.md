# Rezon Kernel V0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal executable Rezon kernel that preserves epistemic semantics while routing constrained reasoning-node executions over explicit episode state.

**Architecture:** Python library with typed immutable-ish records, append-oriented episode mutation, explicit visibility/blinding, deterministic routing, pluggable executor protocol, and structured traces. External LLMs, graph databases, and the HCAE experiment stay behind later adapters.

**Tech Stack:** Python 3.12+, standard library, pytest.

**Spec:** `docs/superpowers/specs/2026-09-15-rezon-kernel-design.md`

## Global Constraints

- Evidence, inference/hypothesis, assumption, observation, test result, and decision remain semantically distinct.
- Repetition does not promote a hypothesis to evidence.
- Execution visibility and blindings are explicit and testable.
- Scheduler routing cannot mutate truth/support state.
- No private chain-of-thought storage requirement.
- Kernel has no mandatory network, database, model-provider, or TensorFlow dependency.

---

### Task 1: Epistemic domain records

**Files:**
- Create: `pyproject.toml`
- Create: `src/rezon/__init__.py`
- Create: `src/rezon/epistemics.py`
- Test: `tests/test_epistemics.py`

**Interfaces:**
- Produces: `PropositionKind`, `SupportKind`, `Proposition`, `Participant`, `Hyperrelation`, `Support`.

- [ ] **Step 1: Write failing tests** asserting proposition kinds remain explicit, `SupportKind.MODEL_JUDGMENT` differs from `DIRECT_OBSERVATION`, and a hyperrelation can contain three or more role-bearing participants.
- [ ] **Step 2: Run** `pytest tests/test_epistemics.py -v` and verify failure because the package/types do not exist.
- [ ] **Step 3: Implement** enums and frozen dataclasses. Use string-valued enums and tuples for referenced IDs. Reject an empty hyperrelation participant list in `__post_init__`.
- [ ] **Step 4: Run** `pytest tests/test_epistemics.py -v` and require PASS.
- [ ] **Step 5: Commit** with `feat: add epistemic domain model`.

Expected core signatures:

```python
class PropositionKind(str, Enum):
    OBSERVATION = "observation"
    EVIDENCE = "evidence"
    CLAIM = "claim"
    HYPOTHESIS = "hypothesis"
    ASSUMPTION = "assumption"
    QUESTION = "question"
    PREDICTION = "prediction"
    TEST = "test"
    TEST_RESULT = "test_result"
    DECISION = "decision"

@dataclass(frozen=True)
class Proposition:
    proposition_id: str
    episode_id: str
    kind: PropositionKind
    content: str
    source_refs: tuple[str, ...] = ()
    producer_execution_id: str | None = None
    confidence: float | None = None
```

---

### Task 2: Append-oriented episode state

**Files:**
- Create: `src/rezon/episode.py`
- Test: `tests/test_episode.py`

**Interfaces:**
- Consumes: Task 1 records.
- Produces: `Episode`, `EpisodeEvent`, `EpisodeSnapshot`, `EpisodeInvariantError`.

- [ ] **Step 1: Write failing tests** that add a hypothesis twice from different executions and confirm both remain hypotheses; retract a proposition and confirm the original is still present in history; reject duplicate proposition IDs with conflicting content.
- [ ] **Step 2: Run** `pytest tests/test_episode.py -v` and require the expected import/behavior failures.
- [ ] **Step 3: Implement** an append-only event list plus indexes for current propositions and relations. Retraction marks current status through a new event; it does not delete the historical record.
- [ ] **Step 4: Run** `pytest tests/test_episode.py -v` and require PASS.
- [ ] **Step 5: Commit** with `feat: add append-oriented episode state`.

Core API:

```python
class Episode:
    def add_proposition(self, proposition: Proposition) -> None: ...
    def add_relation(self, relation: Hyperrelation) -> None: ...
    def retract_proposition(self, proposition_id: str, reason: str) -> None: ...
    def snapshot(self) -> EpisodeSnapshot: ...
```

---

### Task 3: Node and visibility contracts

**Files:**
- Create: `src/rezon/nodes.py`
- Create: `src/rezon/visibility.py`
- Test: `tests/test_visibility.py`

**Interfaces:**
- Consumes: `EpisodeSnapshot`, proposition/relation types.
- Produces: `NodeDescriptor`, `ExecutionRequest`, `ExecutionView`, `ExecutionResult`, `VisibilityPolicy`, `build_execution_view()`.

- [ ] **Step 1: Write failing tests** proving an independent hypothesis generator can be blinded to existing `HYPOTHESIS` propositions while still seeing `OBSERVATION` and `EVIDENCE`; confirm the view records which IDs were withheld.
- [ ] **Step 2: Run** `pytest tests/test_visibility.py -v` and verify failure.
- [ ] **Step 3: Implement** explicit allow-kind, allow-ID, and blind-kind rules. `build_execution_view()` returns copied tuples of visible records plus `blinded_proposition_ids` and `blinded_relation_ids` metadata.
- [ ] **Step 4: Run** the focused test and require PASS.
- [ ] **Step 5: Commit** with `feat: add node execution and blinding contracts`.

---

### Task 4: Output admission and deterministic executors

**Files:**
- Create: `src/rezon/executors.py`
- Create: `src/rezon/admission.py`
- Test: `tests/test_execution.py`

**Interfaces:**
- Consumes: node descriptors, execution views, episode.
- Produces: `Executor` protocol, `EchoHypothesisExecutor`, `ContradictionScannerExecutor`, `FalsifierExecutor`, `admit_execution_result()`.

- [ ] **Step 1: Write failing tests** where a node descriptor permits only `HYPOTHESIS` but a malicious test executor emits `EVIDENCE`; admission must reject it. Add a test that two identical emitted hypotheses from separate executions remain hypotheses.
- [ ] **Step 2: Run** `pytest tests/test_execution.py -v` and verify failure.
- [ ] **Step 3: Implement** the executor protocol and output-kind admission validation. Implement the three deterministic executors described in the spec.
- [ ] **Step 4: Run** the focused test and require PASS.
- [ ] **Step 5: Commit** with `feat: enforce reasoning-node output contracts`.

---

### Task 5: Deterministic scheduler and budgets

**Files:**
- Create: `src/rezon/scheduler.py`
- Test: `tests/test_scheduler.py`

**Interfaces:**
- Consumes: episode snapshot, registered descriptors, completed execution metadata.
- Produces: `Budget`, `ScheduleDecision`, `DeterministicScheduler.next()`.

- [ ] **Step 1: Write failing tests** for the priority order: mandatory verifier first; unresolved contradiction second; independent hypothesis generation when no hypothesis exists; falsifier for unsupported high-confidence hypothesis; explicit terminal decision at budget exhaustion.
- [ ] **Step 2: Run** `pytest tests/test_scheduler.py -v` and verify failure.
- [ ] **Step 3: Implement** deterministic rules with no learned state. Ensure `next()` is pure with respect to epistemic state.
- [ ] **Step 4: Run** the focused test and require PASS.
- [ ] **Step 5: Commit** with `feat: add deterministic reasoning scheduler`.

---

### Task 6: Episode runner and trace serialization

**Files:**
- Create: `src/rezon/runner.py`
- Create: `src/rezon/trace.py`
- Test: `tests/test_trace.py`

**Interfaces:**
- Consumes: scheduler, executor registry, visibility policy, episode.
- Produces: `EpisodeRunner.run()`, JSON-serializable trace records.

- [ ] **Step 1: Write a failing end-to-end test** that starts from one observation, generates a blinded hypothesis, runs a falsifier, terminates under budget, and serializes a trace containing execution ID, node ID, visible IDs, blinded IDs, outputs, timing, and terminal reason.
- [ ] **Step 2: Run** `pytest tests/test_trace.py -v` and verify failure.
- [ ] **Step 3: Implement** the minimal synchronous runner. Do not add concurrency in V0.
- [ ] **Step 4: Run** `pytest tests/test_trace.py -v` and require PASS.
- [ ] **Step 5: Run** `pytest -q` and require all tests PASS.
- [ ] **Step 6: Commit** with `feat: add traced Rezon episode runner`.

---

### Task 7: Baseline benchmark harness

**Files:**
- Create: `src/rezon/benchmark.py`
- Create: `tests/fixtures/cases.json`
- Test: `tests/test_benchmark.py`

**Interfaces:**
- Consumes: callable case runners and gold-labeled fixture cases.
- Produces: per-case and aggregate metrics for correctness, unsupported claims, execution count, and duration.

- [ ] **Step 1: Write failing tests** with two synthetic cases: one where the baseline and Rezon are both correct, and one where an explicit falsification lets Rezon reject an unsupported answer that the simple baseline accepts.
- [ ] **Step 2: Run** `pytest tests/test_benchmark.py -v` and verify failure.
- [ ] **Step 3: Implement** a provider-neutral benchmark API and JSON result serialization.
- [ ] **Step 4: Run** focused tests then `pytest -q`; require PASS.
- [ ] **Step 5: Commit** with `feat: add baseline comparison harness`.

---

### Task 8: Freeze the first executable kernel subject

**Files:**
- Modify: `README.md`
- Create: `docs/qualification/KERNEL_V0_ACCEPTANCE.md`

**Interfaces:**
- Consumes: exact tested commit and test output.
- Produces: a reproducible acceptance record; does not claim behavioral superiority.

- [ ] **Step 1: Document** exact Python version, dependency install command, exact test command, and invariants covered.
- [ ] **Step 2: From a clean checkout of the exact candidate commit, run** `python -m pytest -q`.
- [ ] **Step 3: Record** exact commit SHA and test result in the acceptance document.
- [ ] **Step 4: Confirm** README status says kernel source/test acceptance only; do not call reasoning quality verified.
- [ ] **Step 5: Commit** with `docs: bind Rezon kernel v0 acceptance`.

## Next plan after kernel acceptance

Create a separate implementation plan for the HCAE-inspired Episode Hyperconnectome Encoder using `docs/research/HCAE_EPISODE_HYPERCONNECTOME.md` as the research basis. That plan must include a no-HCAE control, view-ablation tests, modern dependency choices, and predeclared promotion metrics before any learned structural signal is allowed to influence production routing.
