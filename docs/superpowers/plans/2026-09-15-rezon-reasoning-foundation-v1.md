# Rezon Reasoning Foundation V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an executable Rezon V1 that compiles typed multi-view reasoning cases into canonical hypergraph state, performs deterministic reasoning operations, records receipts, and evaluates an HCAE-derived learned representation against frozen baselines.

**Architecture:** Python 3.11 package with an immutable typed domain model, canonical JSON serialization, deterministic multi-view hypergraph compiler, explicit operator layer, and receipt system. The learned experiment is isolated behind a narrow interface and consumes compiled snapshots; it never owns provenance, authority, policy, or currentness.

**Tech Stack:** Python 3.11, standard library dataclasses/enum/hashlib/json, NumPy, SciPy, pytest; PyTorch for the learned experimental encoder only.

**Spec:** `docs/superpowers/specs/2026-09-15-rezon-reasoning-foundation-v1-design.md`

## Global Constraints

- Learned and heuristic relations may not silently become explicit or deterministic-derived relations.
- Exact identity, provenance, authority, policy, currentness, and protected effects remain deterministic concerns.
- Every deterministic snapshot has canonical bytes and a SHA-256 state digest.
- Every state transition records input-state identity, operation identity, source refs, and output identity.
- Learned outputs record model digest, training-corpus digest, and input-state digest.
- The first evaluation corpus is synthetic and frozen before comparing model architectures.
- Third-party research repositories are design evidence only unless a separate dependency decision is made.

---

## File map

```text
pyproject.toml
src/rezon/__init__.py
src/rezon/model.py          # enums and immutable reasoning objects
src/rezon/canonical.py      # canonical serialization and snapshot digest
src/rezon/hypergraph.py     # view-separated incidence representation and G construction
src/rezon/compiler.py       # deterministic ReasoningCase -> CompiledCase pipeline
src/rezon/operators.py      # exact/currentness/contradiction/neighborhood operators
src/rezon/receipts.py       # operation and learned-output receipts
src/rezon/learned.py        # narrow HCAE-derived experimental interface

tests/test_model.py
tests/test_canonical.py
tests/test_hypergraph.py
tests/test_compiler.py
tests/test_operators.py
tests/test_receipts.py
tests/test_learned.py

tests/fixtures/cases/
  complete_qualified.json
  missing_provenance.json
  stale_semantic_match.json
  authority_conflict.json
  legitimate_supersession.json
  unresolved_contradiction.json
  structural_analogy_a.json
  structural_analogy_b.json
```

---

### Task 1: Typed domain model and canonical snapshot identity

**Files:**
- Create: `pyproject.toml`
- Create: `src/rezon/__init__.py`
- Create: `src/rezon/model.py`
- Create: `src/rezon/canonical.py`
- Create: `tests/test_model.py`
- Create: `tests/test_canonical.py`

**Interfaces:**
- Produces: `NodeKind`, `ViewKind`, `ConstructionClass`, `ReasoningNode`, `ReasoningHyperedge`, `ReasoningCase`.
- Produces: `canonical_case_bytes(case: ReasoningCase) -> bytes`.
- Produces: `case_digest(case: ReasoningCase) -> str`.

- [ ] **Step 1: Create package metadata and test dependencies**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[project]
name = "rezon"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "numpy>=2.0",
  "scipy>=1.14",
]

[project.optional-dependencies]
learned = ["torch>=2.4"]
test = ["pytest>=8.3"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing model invariants**

Create `tests/test_model.py` with tests proving that invalid learned/explicit coercion and duplicate member IDs fail:

```python
import pytest
from rezon.model import (
    ConstructionClass,
    ReasoningHyperedge,
    ViewKind,
)


def test_hyperedge_rejects_duplicate_members():
    with pytest.raises(ValueError, match="duplicate member"):
        ReasoningHyperedge(
            hyperedge_id="H1",
            view=ViewKind.PROVENANCE,
            relation_type="SOURCE_BUNDLE",
            members=("N1", "N1"),
            construction_class=ConstructionClass.EXPLICIT,
            source_provenance=("source:fixture",),
        )


def test_learned_edge_remains_learned():
    edge = ReasoningHyperedge(
        hyperedge_id="H2",
        view=ViewKind.SEMANTIC,
        relation_type="SEMANTIC_NEIGHBORHOOD",
        members=("N1", "N2"),
        construction_class=ConstructionClass.LEARNED,
        source_provenance=("model:m1",),
    )
    assert edge.construction_class is ConstructionClass.LEARNED
```

- [ ] **Step 3: Run model tests and verify failure**

Run:

```bash
pytest tests/test_model.py -v
```

Expected: collection/import failure because `rezon.model` does not exist.

- [ ] **Step 4: Implement immutable model types**

Implement `src/rezon/model.py` using frozen dataclasses and string enums. The minimum constructor signatures are:

```python
@dataclass(frozen=True)
class ReasoningNode:
    node_id: str
    kind: NodeKind
    canonical_label: str
    source_provenance: tuple[str, ...]
    inline_payload: object | None = None
    payload_ref: str | None = None
    created_at: str | None = None
    valid_time: tuple[str | None, str | None] | None = None
    confidence_class: str = "UNSPECIFIED"


@dataclass(frozen=True)
class ReasoningHyperedge:
    hyperedge_id: str
    view: ViewKind
    relation_type: str
    members: tuple[str, ...]
    construction_class: ConstructionClass
    source_provenance: tuple[str, ...]
    valid_time: tuple[str | None, str | None] | None = None
    weight: float = 1.0
    uncertainty: float = 0.0


@dataclass(frozen=True)
class ReasoningCase:
    case_id: str
    subject_type: str
    subject_key: str
    created_at: str
    source_set_digest: str
    schema_version: str
    nodes: tuple[ReasoningNode, ...]
    hyperedges: tuple[ReasoningHyperedge, ...]
```

Validation must reject blank IDs, duplicate node IDs, duplicate hyperedge IDs, duplicate members within an edge, edges referencing missing nodes, uncertainty outside `[0, 1]`, and deterministic node/edge objects with empty provenance where provenance is required.

- [ ] **Step 5: Run model tests and verify pass**

Run:

```bash
pytest tests/test_model.py -v
```

Expected: PASS.

- [ ] **Step 6: Write canonicalization tests**

Create `tests/test_canonical.py`:

```python
from rezon.canonical import canonical_case_bytes, case_digest
from tests.helpers import build_case


def test_digest_is_independent_of_input_order():
    a = build_case(reverse=False)
    b = build_case(reverse=True)
    assert canonical_case_bytes(a) == canonical_case_bytes(b)
    assert case_digest(a) == case_digest(b)


def test_digest_changes_when_semantics_change():
    a = build_case(max_value=5)
    b = build_case(max_value=6)
    assert case_digest(a) != case_digest(b)
```

- [ ] **Step 7: Run canonical tests and verify failure**

Run:

```bash
pytest tests/test_canonical.py -v
```

Expected: FAIL because canonicalization is not implemented.

- [ ] **Step 8: Implement canonical bytes and digest**

Implement stable JSON with UTF-8, sorted object keys, normalized node ordering by `node_id`, hyperedge ordering by `hyperedge_id`, member ordering for unordered hyperedges, compact separators, and explicit schema version. Hash only those canonical bytes:

```python
def case_digest(case: ReasoningCase) -> str:
    return hashlib.sha256(canonical_case_bytes(case)).hexdigest()
```

- [ ] **Step 9: Run Task 1 tests**

Run:

```bash
pytest tests/test_model.py tests/test_canonical.py -v
```

Expected: PASS.

- [ ] **Step 10: Commit Task 1**

```bash
git add pyproject.toml src/rezon tests/test_model.py tests/test_canonical.py tests/helpers.py
git commit -m "feat: add typed Rezon reasoning state"
```

---

### Task 2: Deterministic multi-view hypergraph compiler

**Files:**
- Create: `src/rezon/hypergraph.py`
- Create: `src/rezon/compiler.py`
- Create: `tests/test_hypergraph.py`
- Create: `tests/test_compiler.py`

**Interfaces:**
- Consumes: `ReasoningCase`, `ViewKind`.
- Produces: `CompiledView(view, node_ids, hyperedge_ids, H, weights, G)`.
- Produces: `CompiledCase(case_digest, node_index, views)`.
- Produces: `compile_case(case: ReasoningCase) -> CompiledCase`.

- [ ] **Step 1: Write hypergraph matrix tests**

Create a three-node/two-hyperedge fixture and assert exact incidence membership:

```python
def test_incidence_matrix_preserves_higher_order_membership():
    compiled = compile_case(build_three_node_case())
    view = compiled.views[ViewKind.PROVENANCE]
    assert view.H.shape == (3, 2)
    assert view.H[view.node_index["N1"], view.hyperedge_index["H1"]] == 1.0
    assert view.H[view.node_index["N3"], view.hyperedge_index["H1"]] == 1.0
```

Also assert that `G` is symmetric within tolerance and finite.

- [ ] **Step 2: Run hypergraph tests and verify failure**

```bash
pytest tests/test_hypergraph.py -v
```

Expected: FAIL because compiler/hypergraph modules are absent.

- [ ] **Step 3: Implement `build_propagation_matrix`**

Use the HCAE-derived normalization:

```python
def build_propagation_matrix(H: np.ndarray, weights: np.ndarray) -> np.ndarray:
    dv = H @ weights
    de = H.sum(axis=0)
    if np.any(dv <= 0) or np.any(de <= 0):
        raise ValueError("hypergraph contains zero-degree vertex or edge")
    dv_inv_sqrt = np.diag(np.power(dv, -0.5))
    de_inv = np.diag(np.power(de, -1.0))
    W = np.diag(weights)
    return dv_inv_sqrt @ H @ W @ de_inv @ H.T @ dv_inv_sqrt
```

Do not use KNN in the deterministic compiler.

- [ ] **Step 4: Implement view-separated compilation**

`compile_case` must group hyperedges by `ViewKind`, build stable node/hyperedge indexes, emit one incidence matrix per view, and preserve construction class/provenance metadata alongside matrices.

- [ ] **Step 5: Add fail-closed compiler tests**

Test unsupported/empty views, zero-degree construction errors, and deterministic source state whose edge provenance is missing.

- [ ] **Step 6: Run Task 2 tests**

```bash
pytest tests/test_hypergraph.py tests/test_compiler.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 2**

```bash
git add src/rezon/hypergraph.py src/rezon/compiler.py tests/test_hypergraph.py tests/test_compiler.py
git commit -m "feat: compile typed multi-view hypergraphs"
```

---

### Task 3: Deterministic operators, contradiction semantics, and receipts

**Files:**
- Create: `src/rezon/operators.py`
- Create: `src/rezon/receipts.py`
- Create: `tests/test_operators.py`
- Create: `tests/test_receipts.py`
- Create: the seven JSON fixtures under `tests/fixtures/cases/`

**Interfaces:**
- Produces: `ContradictionClass`.
- Produces: `classify_claim_relation(...) -> ContradictionClass`.
- Produces: `exact_lookup(case, predicate) -> tuple[str, ...]`.
- Produces: `hypergraph_neighborhood(compiled, node_id, views) -> NeighborhoodResult`.
- Produces: `OperationReceipt` and `receipt_digest(receipt) -> str`.

- [ ] **Step 1: Freeze the synthetic fixtures before operator implementation**

Each fixture must have a human-readable `expected` block outside the compiled state describing the expected classification. At minimum:

```json
{
  "fixture_id": "legitimate_supersession",
  "expected": {
    "claim_relation": "SUPERSESSION",
    "current_claim": "N4"
  },
  "case": { "...": "ReasoningCase JSON" }
}
```

Record a SHA-256 manifest for the fixture directory in `tests/fixtures/cases/MANIFEST.sha256` before implementing learned evaluation.

- [ ] **Step 2: Write contradiction/currentness tests**

Tests must distinguish:

```text
CONTRADICTION_CONFIRMED
SUPERSESSION
PARALLEL_SCOPE
UNRESOLVED_SCOPE
ALTERNATIVE_HYPOTHESES
NO_CONFLICT
```

The stale-semantic fixture must return `SUPERSESSION`, never `CONTRADICTION_CONFIRMED`.

- [ ] **Step 3: Run operator tests and verify failure**

```bash
pytest tests/test_operators.py -v
```

Expected: FAIL because operator module is absent.

- [ ] **Step 4: Implement explicit scope-aware classification**

The function must compare subject, predicate, valid time, source snapshot/branch, authority class, and modality. Unknown required scope yields `UNRESOLVED_SCOPE` rather than guessing.

- [ ] **Step 5: Write receipt tests**

Create tests proving receipt digest changes when input-state digest, operator version, source refs, or output changes, and remains stable under source-ref input ordering if source refs are defined as an unordered set.

- [ ] **Step 6: Implement receipts**

Minimum type:

```python
@dataclass(frozen=True)
class OperationReceipt:
    receipt_id: str
    input_state_digest: str
    operation: str
    operator_version: str
    parameters_digest: str
    source_refs: tuple[str, ...]
    created_at: str
    actor: str
    output_state_digest: str | None = None
    output_ref: str | None = None
```

Reject receipts that define neither output identity nor output reference.

- [ ] **Step 7: Run deterministic suite**

```bash
pytest tests/test_model.py tests/test_canonical.py tests/test_hypergraph.py tests/test_compiler.py tests/test_operators.py tests/test_receipts.py -v
```

Expected: PASS.

- [ ] **Step 8: Commit Task 3**

```bash
git add src/rezon/operators.py src/rezon/receipts.py tests/test_operators.py tests/test_receipts.py tests/fixtures/cases
git commit -m "feat: add scoped deterministic reasoning operators"
```

---

### Task 4: HCAE-derived learned baseline and structural retrieval evaluation

**Files:**
- Create: `src/rezon/learned.py`
- Create: `tests/test_learned.py`
- Create: `experiments/hcae_v1.py`
- Create: `experiments/evaluate_v1.py`
- Create: `docs/results/REZON_HCAE_V1_EVALUATION.md`

**Interfaces:**
- Consumes: `CompiledCase`.
- Produces: `LearnedReceipt` with model/corpus/input digests.
- Produces: `encode_case(compiled: CompiledCase, model: MultiViewHyperEncoder) -> np.ndarray`.
- Produces: comparable metrics for all frozen baselines.

- [ ] **Step 1: Write the learned-layer provenance tests first**

Before model quality, prove that outputs without identity fail:

```python
def test_learned_output_requires_model_corpus_and_input_digests():
    with pytest.raises(ValueError):
        LearnedReceipt(
            model_digest="",
            training_corpus_digest="abc",
            input_state_digest="def",
            output_type="CASE_EMBEDDING",
            output_digest="123",
        )
```

- [ ] **Step 2: Run learned tests and verify failure**

```bash
pytest tests/test_learned.py -v
```

Expected: FAIL because learned module is absent.

- [ ] **Step 3: Implement minimal view-aware encoder**

Use one projection per view and a deterministic sorted view order. Initial block:

```python
class MultiViewHyperEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, views: tuple[str, ...]):
        super().__init__()
        self.views = views
        self.project = nn.ModuleDict({v: nn.Linear(input_dim, hidden_dim) for v in views})
        self.fuse = nn.Linear(hidden_dim * len(views), output_dim)

    def forward(self, x_by_view: dict[str, Tensor], g_by_view: dict[str, Tensor]) -> Tensor:
        encoded = []
        for view in self.views:
            x = self.project[view](x_by_view[view])
            encoded.append(g_by_view[view] @ x)
        return self.fuse(torch.cat(encoded, dim=-1))
```

This is a deliberately small experimental baseline, not a claim of optimal HCAE reproduction.

- [ ] **Step 4: Add reconstruction objective**

For each view, decode expected node-hyperedge membership from node embeddings and report per-view reconstruction loss. Keep per-view losses separate in addition to an aggregate.

- [ ] **Step 5: Implement frozen baselines**

`experiments/evaluate_v1.py` must evaluate the same manifest-bound fixtures with:

1. semantic-only vector retrieval,
2. flattened feature vector,
3. pairwise graph projection,
4. deterministic typed-hypergraph query,
5. HCAE-derived multi-view embedding.

- [ ] **Step 6: Add cross-view ablation**

Run the learned model with each view removed once. Record the delta for stale/current discrimination, structural analogy retrieval, and missing-relation detection.

- [ ] **Step 7: Generate a result document from machine-readable metrics**

`docs/results/REZON_HCAE_V1_EVALUATION.md` must include:

```text
fixture manifest digest
source commit
model code digest
random seeds
Python/PyTorch/NumPy versions
training corpus digest
per-baseline metrics
per-view ablation metrics
known limitations
```

Do not label the model qualified merely because it beats one baseline.

- [ ] **Step 8: Run full suite**

```bash
pytest -v
```

Expected: PASS.

- [ ] **Step 9: Run deterministic repeatability check**

Run canonical/compiler tests twice in separate processes and compare emitted snapshot digests. Expected: exact match.

- [ ] **Step 10: Run learned evaluation twice with fixed seeds**

Record whether metrics and output digests are exact or tolerance-stable. Do not promise bitwise determinism across unconstrained BLAS/CUDA/runtime environments.

- [ ] **Step 11: Commit Task 4**

```bash
git add src/rezon/learned.py tests/test_learned.py experiments docs/results
git commit -m "feat: add HCAE-derived reasoning experiment"
```

---

### Task 5: Final integration verification and source-bound review packet

**Files:**
- Modify: `README.md`
- Create: `docs/qualification/REZON_V1_SOURCE_REVIEW_PACKET.md`

**Interfaces:**
- Consumes all previous tasks.
- Produces an exact-head review packet. It does not merge or deploy.

- [ ] **Step 1: Run all tests from a clean checkout of the exact candidate commit**

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test,learned]'
pytest -v
```

Expected: PASS.

- [ ] **Step 2: Run the frozen experiment**

```bash
python experiments/evaluate_v1.py --manifest tests/fixtures/cases/MANIFEST.sha256
```

Expected: metrics artifact produced only if manifest digest matches.

- [ ] **Step 3: Inspect authority-boundary tests explicitly**

Confirm tests cover:

- semantic similarity cannot create `EXPLICIT` authority,
- learned missing-relation suggestions cannot mutate deterministic state without an explicit transition,
- stale/current classification is scope-aware,
- unknown scope fails closed,
- learned outputs always bind model/corpus/input digests.

- [ ] **Step 4: Write exact-head source review packet**

Record candidate commit, tree, test commands/results, fixture manifest digest, model/corpus/runtime identity, known limitations, and status labels separately:

```text
SOURCE
BUILD
TEST
EXPERIMENT
RUNTIME
BEHAVIORAL_QUALIFICATION
```

`SOURCE_REVIEW = PASS` must not imply merge, runtime installation, or behavioral qualification.

- [ ] **Step 5: Commit the review packet**

```bash
git add README.md docs/qualification/REZON_V1_SOURCE_REVIEW_PACKET.md
git commit -m "docs: add Rezon V1 source review packet"
```

- [ ] **Step 6: Request independent review of the exact head**

The review request must identify the exact commit and explicitly challenge:

1. authority laundering from learned relations,
2. contradiction/currentness scope errors,
3. hyperedge/view semantic leakage,
4. false determinism claims,
5. fixture contamination or post-result mutation.

No merge or deployment is part of this plan without separate authority.

---

## Plan self-review

Spec coverage:

- typed reasoning objects: Task 1,
- deterministic canonical identity: Task 1,
- multi-view hypergraph compilation: Task 2,
- HCAE-derived propagation: Tasks 2 and 4,
- scoped contradiction/currentness: Task 3,
- provenance/receipts: Task 3,
- learned/deterministic boundary: Tasks 1, 3, 4, 5,
- frozen synthetic proof: Tasks 3 and 4,
- baseline comparison and ablation: Task 4,
- exact-head verification: Task 5.

No implementation task in this plan requires importing code from the surveyed third-party repositories.