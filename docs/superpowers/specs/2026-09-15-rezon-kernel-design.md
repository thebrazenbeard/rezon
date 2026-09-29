# Rezon Kernel V0 Design

Status: DESIGN APPROVED IN CONVERSATION / IMPLEMENTATION NOT YET QUALIFIED

## Goal

Build the smallest executable Rezon kernel that can represent typed epistemic state, run constrained heterogeneous operators with selective context/blinding, preserve structured provenance and traces, and evaluate dynamic multi-node reasoning against simpler baselines.

## Scope

V0 includes:

- typed proposition and hyperrelation models;
- append-oriented episode state with correction/retraction events;
- reasoning-node descriptors and execution contracts;
- execution views that explicitly record visible and blinded state;
- a deterministic scheduler sufficient to test routing rules;
- several local deterministic operators for tests;
- an adapter boundary for future LLM/tool executors;
- structured execution traces;
- a benchmark harness for baseline comparisons.

The HCAE-inspired episode encoder is a separate experimental module that consumes the kernel's canonical state after the kernel contract exists. Its design is documented now, but it is not required to make the first kernel test suite pass.

## Architecture

The kernel is library-first. It does not require a daemon, database, UI, agent framework, or network service.

The canonical episode state is explicit and deterministic. Operators never receive the episode object directly; they receive an `ExecutionView` produced under a declared visibility policy. This keeps isolation testable.

The scheduler emits execution requests. Executors emit typed results. A result is admitted into episode state only through validation that preserves provenance and epistemic kind.

## Initial technology

- Python 3.12+
- standard-library `dataclasses`, `enum`, `typing`, `datetime`, `uuid`, and `json`
- `pytest` for tests
- no graph database or agent framework in V0

Research modules may add isolated dependencies later. The HCAE experiment should not force TensorFlow 1.x into the kernel.

## Package boundaries

```text
src/rezon/
  epistemics.py     # proposition/support/hyperrelation types
  episode.py        # append-oriented episode state and indexes
  nodes.py          # node descriptors, execution requests/results/views
  visibility.py     # context selection and blinding
  scheduler.py      # routing decisions under budgets
  executors.py      # executor protocol and deterministic test executors
  trace.py          # structured trace serialization

tests/
  test_epistemics.py
  test_episode.py
  test_visibility.py
  test_scheduler.py
  test_execution.py
  test_trace.py
```

## Required invariants

1. Hypothesis repetition never changes the proposition kind to evidence.
2. Confidence cannot be substituted for support type.
3. Corrections/retractions preserve earlier state and provenance.
4. An execution view contains only explicitly admitted proposition/relation IDs.
5. Blindings are inspectable in execution metadata.
6. Node output cannot invent a stronger epistemic kind than its descriptor permits.
7. Scheduler selection does not mutate epistemic truth/support state.
8. Budget exhaustion has an explicit terminal result.
9. Execution results preserve producer, input view, timing, and support references.
10. No test relies on private model chain-of-thought.

## Initial deterministic operators

V0 test executors should include:

- `EchoHypothesisExecutor`: emits a hypothesis from supplied observations; useful for proving kind preservation.
- `ContradictionScannerExecutor`: detects a direct `CONTRADICTS` relation in its visible view.
- `FalsifierExecutor`: given a target hypothesis and visible test results, emits a refutation only when an explicit contradictory result exists.

These are intentionally simple. Their purpose is to prove orchestration semantics before connecting expensive external intelligence.

## Scheduler V0

The first scheduler is deterministic and rule-based. Priority order:

1. satisfy mandatory verification requirements;
2. investigate unresolved explicit contradictions;
3. run an independent hypothesis generator when none exists;
4. run falsification against unsupported high-confidence hypotheses;
5. terminate when no rule applies or budget is exhausted.

Later schedulers may learn routing policies, but the deterministic baseline must remain available for comparison.

## Evaluation boundary

The first benchmark harness must be able to run the same case under:

- a simple single-executor baseline;
- fixed multi-pass execution;
- dynamic Rezon scheduler.

Metrics emitted by the harness must at least contain correctness (when gold labels exist), execution count, wall-clock duration, and unsupported-claim count. Cost/token accounting can be added when external model adapters are introduced.

## HCAE interface boundary

The kernel should expose enough canonical state for an experimental encoder to build compatible proposition-view matrices without changing kernel semantics.

Proposed future interface:

```python
class StructuralSignal(Protocol):
    def analyze(self, episode: EpisodeSnapshot) -> StructuralAnalysis: ...
```

The scheduler may consume `StructuralAnalysis`, but the canonical episode graph remains authoritative.

## Failure behavior

Unknown or unsupported state is represented explicitly. Executors fail closed on input-contract violations. The scheduler may skip a failed optional node, but mandatory verification failure must remain visible and prevent a falsely clean terminal status.
