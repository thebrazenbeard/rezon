# Rezon

**Rezon is an experimental, provider-independent reasoning kernel and collective-reasoning toolkit.** It lets applications structure a reasoning task, preserve evidence and source boundaries, compare distinct answers and objections, and produce attributable receipts. Its optional collective runtime can ask multiple configured model endpoints in parallel and integrate their responses.

Rezon is reusable outside any particular AI assistant or computer installation. It is **not** tensor/model parallelism, shared VRAM, an automatic cluster scheduler, or distributed consensus. The implemented collective uses a single SQLite episode store; multiple processes or privately connected hosts can participate through explicit, operator-controlled interfaces.

> **License:** Source-available proprietary software. The [LICENSE](LICENSE) permits limited private noncommercial evaluation, security review, interoperability assessment, education, and research; it does not grant general redistribution or commercial deployment rights. See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for separate commercial permissions.

## What is implemented

| Part | Reusable function | Important limit |
| --- | --- | --- |
| [V0 kernel](src/rezon/runner.py) | Typed reasoning episodes, node execution, task/identity boundaries, source-admission controls, receipts, and deterministic replay/benchmark support | No epistemic truth guarantee or authorization to execute effects |
| [Collective V1](src/rezon/collective.py) | Concurrent independent model responses, peer reviews, SQLite persistence, and input-digest-bound synthesis | One authoritative local store; not distributed consensus or shared neural inference |
| [Collective CLI](src/rezon/collective_cli.py) | Explicitly run an episode, serve an authenticated loopback gateway, import external reviewed findings, or synthesize an existing episode | The operator provisions providers, credentials, and trusted ingress |
| [Worker client](src/rezon/worker_client.py) | One-shot status, answer, and review participation with bounded replay and redirect handling | Neither the worker token nor response attests a physical host or authentic model |
| [T'Kal hearing](src/rezon/tkal_network.py) | Opt-in four-worker challenge, defense, and resolution over the collective gateway | A recorded REFINE/SUSTAIN decision is not independently verified truth |
| [Portable federation](src/rezon/federation.py) | Blind commitment/reveal and cross-peer objection records that can travel over an external transport | Digests detect ordinary substitution; they do not authenticate people, hosts, or chronology |
| [Isolated qualifier](src/rezon/qualify_isolated.py) | Local protocol exercise with temporary credentials, a SQLite fixture, and explicit qualification report | Most fixture contributions are synthetic; no remote installation or live worker independence is proven |

The larger multi-host topology, durable governance interfaces, metacognition, and reasoning-method taxonomy remain research directions. Start with [Foundation](docs/FOUNDATION.md), [Kernel contracts](docs/contracts/REASONING_NODE_V0.md), [Collective runtime](docs/COLLECTIVE_RUNTIME_V1.md), and [multi-node topology](docs/MULTINODE_TOPOLOGY.md) for the exact scope.

## Quick start: local and offline

Requires **Python 3.12+**. From a checkout, create an isolated environment and install the package and test runner:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e . pytest
.venv/bin/python -m pytest -q
```

On Windows use `.venv\Scripts\python.exe` instead of `.venv/bin/python`. The test suite exercises socket-based local gateways, so an environment that forbids loopback socket creation will need an appropriate isolated test runner. Tests do not contact production model providers by default.

To exercise the protocol **without any model API keys or external model calls**, choose a new, private output path:

```bash
.venv/bin/python -m rezon.qualify_isolated --output ./private-qualification
```

This creates a local SQLite fixture and a JSON report. The directory must not already exist. Keep it out of source control: it contains example episode content, even though the generated credentials are not persisted. A passing REFINE result proves that the isolated protocol gates ran, **not** real-world reasoning quality or independently authenticated workers.

## Opt-in collective reasoning across model endpoints

Prepare `models.json` with two or more independent agent identifiers and configured OpenAI-compatible or Anthropic endpoints. The following addresses and model identifiers are **placeholders**, not working services:

```json
{
  "models": [
    {
      "agent_id": "analyst_a",
      "provider": "openai_compatible",
      "model": "configured-model-a",
      "base_url": "https://model-a.example/v1",
      "api_key_env": "REZON_MODEL_A_KEY"
    },
    {
      "agent_id": "analyst_b",
      "provider": "openai_compatible",
      "model": "configured-model-b",
      "base_url": "https://model-b.example/v1",
      "api_key_env": "REZON_MODEL_B_KEY"
    }
  ]
}
```

Prepare `integrator.json` as a **single model specification**, rather than a `models` array:

```json
{
  "agent_id": "integrator",
  "provider": "openai_compatible",
  "model": "configured-integrator",
  "base_url": "https://synthesis.example/v1",
  "api_key_env": "REZON_INTEGRATOR_KEY"
}
```

Provision each key privately in its named environment variable and substitute genuine, validated endpoint addresses and model IDs. Then run:

```bash
.venv/bin/python -m rezon.collective_cli run \
  --db ./private-episodes.sqlite3 \
  --prompt "Compare two competing explanations for this observation" \
  --models-config ./models.json \
  --integrator-config ./integrator.json
```

The CLI asks the configured models for initial answers concurrently, then has them critique peers, and synthesizes the saved, digest-bound round. It returns an episode ID and per-worker outcomes; a failed or incomplete review does not silently become a qualified synthesis. Provider wire compatibility, model identity, independence, factual accuracy, and latency/performance are **not** established by supplying the configuration.

For a model server on the **same** machine, an OpenAI-compatible loopback base URL such as `http://127.0.0.1:11434/v1` may be used with the required `api_key_env` value (a nonempty local placeholder where the server does not require authentication). Remote HTTP is rejected by default; an explicit insecure-HTTP override exists but is **not** recommended for credentials on untrusted networks. Review the [provider and collective configuration guide](docs/COLLECTIVE_RUNTIME_V1.md) before enabling this path.

## Separate workers and private gateways

The optional authenticated gateway is bound to **127.0.0.1**. The operator provisions a distinct random admin credential and a different credential per enrolled worker; the service does not create, copy, or distribute those secrets. For example, after configuring the environment and selecting a private database path:

```bash
.venv/bin/python -m rezon.collective_cli serve --db ./private-episodes.sqlite3 --port 8765
```

Other hosts can reach this loopback service only through a separately governed private tunnel or authenticated HTTPS proxy. The [worker client](docs/PRIVATE_WORKER_CLIENT_V1.md) supports one-shot `status`, `answer`, and `review` operations. To check a previously authorized episode with an operator-provisioned `REZON_WORKER_TOKEN`:

```bash
.venv/bin/python -m rezon.worker_client status \
  --gateway https://gateway.example.com \
  --episode collective-REPLACE_WITH_REAL_ID
```

The example address and episode ID must be replaced. External gateways require verified HTTPS; bearer redirects are refused. No password should be placed in a README, command-line argument, committed config, or shared transcript. The [owner-local credential guide](docs/OWNER_LOCAL_CREDENTIAL_ENROLLMENT_V1.md) describes optional private enrollment through supported OS credential vaults, not remote enrollment performed by this project.

For gateway monitoring, `/healthz` reports process liveness. Authenticated `/readyz` additionally tests a bounded read of required SQLite schema; neither proves write permission, provider availability, worker quorum, or host identity. A [read-only probe](scripts/collective_gateway_probe.py) is available for a previously enrolled worker. The optional read-only state observer uses a separate nonce-bound HMAC protocol, not a general bearer authority; see [Collective V1](docs/COLLECTIVE_RUNTIME_V1.md) for its exact replay and disclosure limitations.

An explicit `--tkal` on `collective_cli serve` enables virtual hearing routes; without it those routes are absent. See the [T'Kal guide](docs/TKAL_VIRTUAL_NETWORK_V1.md) and [qualification notes](docs/qualification/REZON_VIRTUAL_HEARING_GATEWAY_20261023.md). An isolated or relayed four-source hearing is not a proven independent four-device network.

## Authority, evidence, and security

- **No authority transfer:** A model answer, provider adapter, source reference, worker credential, or successful review cannot grant identity, consent, tool permissions, deployment approval, or execution authority. A host must authenticate and authorize protected effects separately, with host-owned immutable identity/provider binding appropriate to its threat model.
- **No model-identity attestation:** Worker IDs and digests are recorded assertions. Separate strings or network connections do not prove physically independent machines, model providers, or minds.
- **No inference pooling:** Collective V1 performs *several model requests and synthesis*. It does not shard one model's layers, split its KV cache, pool GPU memory, or prove performance improvements over one model.
- **No consensus-truth claim:** The SQLite store supplies durable episode records and digest-bound currentness, not independent custody, proof of evidence, factual verification, or Byzantine consensus.
- **Secret and data custody:** Prompts, answers, critiques, and saved qualification artifacts can be sensitive. Use owner-controlled paths, restrictive OS permissions, configured provider privacy terms, TLS where applicable, and separately managed credential rotation. Do not expose the loopback gateway directly to the Internet.
- **Network ambiguity:** One-shot worker writes may be marked `OUTCOME_UNKNOWN`, not automatically replayed. Review receipts and server state before retrying. Some source-level checks are process-local or nonadversarial and must not be promoted into formal host security guarantees.

The repository includes [security notes for a previously removed editor-startup risk](docs/security/WORKSPACE_AUTORUN_TRIAGE_20261023.md). Removal of unsafe source content is not proof any previously exposed host is clean.

## Project status and validation

Kernel V0 and the optional collective V1 are implemented and covered by source tests. Against public `main` at `b25518b525b8d31c8e8730a3b4d23088d2c66cdc`, an isolated Python 3.12 environment passed **454 tests and 27 subtests**; the isolated no-model T'Kal qualifier returned `REFINE` with four fixture answers and `live_model_calls: 0`. This is local test evidence, not deployed-provider, physical-host, or independent security qualification.

More detailed research and interfaces:

- [Reasoning taxonomy](docs/REASONING_TAXONOMY.md) and [adversarial collaboration](docs/ADVERSARIAL_COLLABORATION.md)
- [State/effect semantics](docs/STATE_AND_EFFECT_SEMANTICS.md) and [identity tracking](docs/IDENTITY_TRACKING.md)
- [Retrieval/provenance](docs/SEMANTIC_PROVENANCE.md) and [evaluation/falsification](docs/EVALUATION_AND_FALSIFICATION.md)
- [Benchmark reference](docs/qualification/BENCHMARK_V1_REFERENCE.md) and [kernel acceptance notes](docs/qualification/KERNEL_V0_ACCEPTANCE.md)

