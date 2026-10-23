# Rezon collective runtime V1 (optional prototype)

Status: **source implemented and locally testable; not installed or deployed**.

This opt-in layer provides two complementary ways to combine independent agents:

1. A loopback HTTP gateway where separately running, token-enrolled agents can
   concurrently read a task and submit immutable first-round answers, then read
   peer outputs and challenge specific answers.
2. A local fan-out/critique/fan-in runner that calls multiple configured
   language-model endpoints concurrently, persists separate initial claims,
   sends each model the other answers for an adversarial review round, and
   invokes one configured integrator against the contributions and critiques.

Both paths use a single SQLite WAL episode database with transactional writes,
idempotent repeat submission, collision rejection, and snapshot-digest-bound
syntheses. New database files are created owner-only (0600 on POSIX; protect
database directories and pre-existing files through operating-system access
controls). The database can be reopened by another process. The gateway never
authorizes external effects. The existing Rezon V0 `EpisodeRunner` remains
untouched: external claims project into `PropositionKind.CLAIM`, peer challenges
into explicit `challenges` relations, and synthesis into `HYPOTHESIS`.
Historic syntheses are retained but flagged `is_current: false` in the HTTP
snapshot whenever newer contributions change the input digest; only current
syntheses project as hypotheses in the active Episode view.

## Local model fan-out

Install from the repository with Python 3.12 or later, then supply a config file
containing endpoint identities and **environment variable names**, not keys:

```json
{
  "models": [
    {
      "agent_id": "model_a",
      "provider": "openai_compatible",
      "model": "configured-model-name",
      "base_url": "https://example-model-provider.invalid/v1",
      "api_key_env": "MODEL_A_KEY"
    },
    {
      "agent_id": "model_b",
      "provider": "anthropic",
      "model": "configured-anthropic-model",
      "base_url": "https://api.anthropic.com/v1",
      "api_key_env": "MODEL_B_KEY"
    }
  ]
}
```

Integrator config is a single model object with the same fields. Export
`MODEL_A_KEY`, `MODEL_B_KEY`, and the integrator's key in your private process
environment. Then run:

```bash
python -m rezon.collective_cli run --db ./rezon-episodes.sqlite3 \
  --prompt "Evaluate this proposition and its evidence" \
  --models-config ./models.json --integrator-config ./integrator.json
```

OpenAI-compatible endpoints include local servers supporting the chat-completion
wire protocol. API compatibility and provider model IDs must be independently
checked for a specific deployment. HTTPS is required for non-loopback HTTP
connections unless a config explicitly enables `allow_insecure_http: true`
(for a separately secured LAN setup); that option risks credential exposure.
The CLI does not synthesize a supposedly completed review round if any
enrolled reviewer fails. It prints the durable episode ID and per-model
outcomes for recovery; reruns of already-submitted answers/reviews are
idempotent only if their text matches exactly.

## HTTP gateway for independently running agents

Set `REZON_COLLECTIVE_ADMIN_TOKEN` to a unique random secret of at least 16
characters and `REZON_COLLECTIVE_WORKER_TOKENS_JSON` to a JSON object mapping
enrolled agent IDs to **distinct** random secrets, each at least 16 characters.
Use printable ASCII secrets without whitespace (for example URL-safe random
tokens); the service rejects control characters and duplicate credentials.
Do not put the secrets in committed files. Run:

```bash
python -m rezon.collective_cli serve --db ./rezon-episodes.sqlite3 --port 8765 \
  --integrator-config ./integrator.json
```

The listener binds to `127.0.0.1` only. Use an authenticated private TLS
reverse proxy or trusted private tunnel to reach it from another host. This
prototype has **not** been qualified as an Internet-facing service.
It has no admission rate limiting or production-grade ingress hardening. Do
not expose the loopback port publicly or treat a TLS proxy alone as a complete
security review.

All authenticated requests use `Authorization: Bearer <token>` and JSON bodies.

| Request | Role | Purpose |
| --- | --- | --- |
| `POST /v1/episodes` `{ "prompt":"...", "agents":["a","b"] }` | admin | Create a fixed participant roster |
| `GET /v1/episodes/{id}` | participant/admin | Read task (no peer answers) |
| `POST /v1/episodes/{id}/answers` `{ "content":"...", "source_refs":[] }` | participant | Submit one immutable independent answer |
| `GET /v1/episodes/{id}/state` | admin; participant after all first answers | Read durable contributions |
| `POST /v1/episodes/{id}/reviews` `{ "content":"...", "target_ids":["answer:b"] }` | participant after first round | Challenge existing answer IDs |
| `POST /v1/episodes/{id}/synthesize` `{}` | admin | Invoke configured integrator and persist digest-bound result |

Agent identity is derived from the configured bearer token, never accepted
from a client-supplied actor name. No universal automatic agent enrollment,
provider credentials, or background job runner is included.

## Boundaries and residual gaps

- **Not consensus truth:** model outputs and `source_refs` are unverified
  assertions. Synthesis is model judgment, not a formally verified answer.
- **Not a replacement for Blotter or the communication bus:** Blotter remains
  an activity ledger; coordination and outer work leases belong to other
  explicitly governed systems.
- **Not distributed consensus:** the database is one authoritative SQLite
  server-side file, accessed by multiple threads/processes through a gateway.
  There is no replicated database, durable distributed worker lease, failover,
  or autonomous scheduling across machines.
- **Not deployed:** no live provider credentials, endpoint registration,
  service installation, remote connectivity, or end-to-end model-quality
  benchmark has been verified. The provider tests use local HTTP simulators.
- **No authority translation:** outputs cannot mutate repositories or remote
  resources. A Project Runner adapter may later consume non-promotional
  receipts, but this layer does not create grants or claim completion.

Verification commands:

```bash
PYTHONPATH=src python -m pytest -q tests/test_collective_runtime.py \
  tests/test_provider_adapters.py tests/test_collective_http.py
PYTHONPATH=src python -m pytest -q
```
