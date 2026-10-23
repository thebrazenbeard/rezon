# Rezon

Rezon is an executable multi-faceted reasoning project: a place to study, formalize, test, and eventually run heterogeneous reasoning as a coordinated system rather than treating one model invocation as the whole reasoning process.

The project deliberately separates four things that are often collapsed together:

1. **Reasoning methods** — deduction, induction, abduction, causality, counterfactuals, planning, analogy, probabilistic inference, semantic reasoning, adversarial challenge, and more.
2. **Reasoning topology** — how several reasoning processes cooperate, oppose, verify, retrieve, route, and integrate.
3. **State and identity** — what subject is being reasoned about, what changed, what persisted, and what evidence supports continuity.
4. **Execution** — provider/model adapters, worker routing, receipts, provenance, resource constraints, and runtime behavior.

Rezon's V0 reasoning kernel is executable. The optional V1 collective layer
provides a bounded, local implementation of concurrent multi-model reasoning;
the wider distributed topology below remains a roadmap, not a deployed system.

## Core direction

A working Rezon system should eventually support a flow like:

```text
TaskEnvelope
  -> Decomposer / Planner
  -> Heterogeneous Reasoning Nodes
  -> Opposition / Falsification Lane
  -> Retrieval + Semantic / Provenance Verification
  -> Integrator
  -> ResultReceipt
```

Cross-cutting state substrates:

```text
Persistent Subject / Identity Track
Multi-View State Graph / Hypergraph
Evidence + Provenance Ledger
```

A stronger model is never automatically an authority source. A reasoning node may be more capable, more expensive, or more specialized without being entitled to promote identity, consent, facts, deployment state, or governance claims.

## Documents

- `docs/FOUNDATION.md` — project principles and scope
- `docs/REASONING_TAXONOMY.md` — reasoning families worth modeling
- `docs/HUMAN_AI_REASONING_SYNTHESIS.md` — transferable human/AI reasoning mechanisms
- `docs/IDENTITY_TRACKING.md` — persistent identity under discontinuous observations
- `docs/MULTIVIEW_HYPERGRAPH_STATE.md` — many-to-many, multi-view state representation
- `docs/HIERARCHICAL_DISTRIBUTED_REASONING.md` — slow/fast and heterogeneous worker topology
- `docs/ADVERSARIAL_COLLABORATION.md` — literal-proposition hostile review method
- `docs/RETRIEVAL_CONTEXT.md` — reasoning-based retrieval and context selection
- `docs/SEMANTIC_PROVENANCE.md` — knowledge graphs, ontologies, provenance, repair
- `docs/WORKER_ROUTING_ULTRA.md` — optional high-reasoning worker routing
- `docs/EVALUATION_AND_FALSIFICATION.md` — how Rezon should try to prove itself wrong
- `docs/SOURCE_TRANSFER_MATRIX.md` — source-by-source transfer analysis
- `docs/EXECUTABLE_FRAMEWORK_DIRECTION.md` — runnable system direction
- `docs/VERA_ADOPTION_CANDIDATES.md` — mechanisms that may be promoted into Vera later
- [`docs/COLLECTIVE_RUNTIME_V1.md`](docs/COLLECTIVE_RUNTIME_V1.md) — model config, agent API, security boundaries, and verification

## Run locally

Python 3.12+ is required. From a clone:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e . pytest
.venv/bin/python -m pytest -q
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`.

For concurrent model reasoning, configure two or more OpenAI-compatible or
Anthropic endpoints and a synthesis model using the [collective runtime guide](docs/COLLECTIVE_RUNTIME_V1.md).
The CLI runs independent first answers **in parallel**, then concurrent peer
critique, then a synthesis bound to the exact saved input state:

```bash
.venv/bin/python -m rezon.collective_cli run \
  --db ./rezon-episodes.sqlite3 --prompt "Compare these explanations" \
  --models-config ./models.json --integrator-config ./integrator.json
```

Separately running agents can instead submit answers and reviews to the
authenticated, **loopback-only** HTTP gateway. Configuration and routes are in
the guide. Neither mode verifies a model's factual accuracy, claims authority,
or supplies production-ready distributed consensus.

## Current status

Kernel V0 and the opt-in collective V1 are executable and covered by automated
tests, including two independently authenticated HTTP workers, separate-process
durability, simulated provider protocols, peer critique, and stale-result
rejection. The backend is one SQLite authority, not a distributed-consensus
system. No live model-provider deployment, remote installation, Vera adoption,
or measured reasoning improvement has been established by these source tests.
