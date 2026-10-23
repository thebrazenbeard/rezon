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

For a local Ollama installation, point each OpenAI-compatible model at
`http://127.0.0.1:11434/v1`, with its `api_key_env` set to an environment
variable containing any nonempty loopback-only placeholder. Supported optional
per-model controls include `timeout_seconds`, `max_tokens`, and
`reasoning_effort` (where supported by the local model/endpoint). See the
[VN1 Ollama qualification note](docs/VN1_OLLAMA_2026-10-23.md) for a
reproducible, two-model smoke test and its limitations.

Separately running agents can instead submit answers and reviews to the
authenticated, **loopback-only** HTTP gateway. Configuration and routes are in
the guide. Neither mode verifies a model's factual accuracy, claims authority,
or supplies production-ready distributed consensus.

## T'Kal-in-ket hearing (opt-in)

Use the existing authenticated loopback-only Collective V1 gateway with the
explicit `--tkal` flag:

```bash
python -m rezon.collective_cli serve --db ./private-collective.sqlite3 --tkal
```

This adds durable three-lens challenge, defense, resolution, REFINE and
SUSTAIN inquiry over a four-worker Collective episode. Three distinct
cross-peer exchanges are required for SUSTAIN; self-targeted initial reviews,
waived challenges or proposer-only replies do not qualify. Without `--tkal`,
the hearing routes are absent. Details: [Virtual hearing guide](docs/TKAL_VIRTUAL_NETWORK_V1.md) and [gateway qualification](docs/qualification/REZON_VIRTUAL_HEARING_GATEWAY_20261023.md).

The gate verifies attributed records and digest consistency, NOT independent
physical host identity, trustworthiness of model outputs, or factual truth.
No remote TLS ingress or four-machine persistent service is installed. The
real four-source episode was primary-relayed into a single persisted Rezon
store, not a qualified direct four-device mesh.

The repository's hidden VS Code folder-open execution was removed from
source in security PR #106. This does not prove that previously exposed
machines are uncompromised. See [source triage](docs/security/WORKSPACE_AUTORUN_TRIAGE_20261023.md).

## Private worker execution (one-shot)

The [private worker client](docs/PRIVATE_WORKER_CLIENT_V1.md) runs a **single**
`status`, `answer`, or `review` action against the existing authenticated
Collective API. An authorized operator must separately provision each worker's
`REZON_WORKER_TOKEN`; the client cannot extract or distribute secrets, weaken
SSH host-key validation, or grant itself a model identity.

```sh
python -m rezon.worker_client status --gateway https://vn2.tail86ea75.ts.net \
  --episode collective-REPLACE_WITH_ID
```

For `answer` and `review`, configure a localhost OpenAI-compatible model and
its separate API-key environment variable. External gateways require HTTPS
and certificate validation; bearer redirects are refused. Accepted receipts
are **unattested**, and ambiguous network writes are marked
`OUTCOME_UNKNOWN`, never automatically retried. This does **not** qualify a
four-machine inference episode or permanently connected worker mesh.

## Current status

Kernel V0 and the opt-in collective V1 are executable and covered by automated
tests, including two independently authenticated HTTP workers, separate-process
durability, simulated provider protocols, peer critique, and stale-result
rejection. The backend is one SQLite authority, not a distributed-consensus
system. No live model-provider deployment, remote installation, Vera adoption,
or measured reasoning improvement has been established by these source tests.
