# Private Rezon worker client V1 — source-level only

The server already supports immutable first answers, peer reviews and a bounded T'Kal-in-ket hearing. This client adds **one explicit worker action per invocation**, without unattended polling, automatic enrollment, token issuance, host identity attestation, or a second state store.

Source-bound server: `thebrazenbeard/rezon@a13b7d5357ce5e2372eeda5fbe0551544a4c1dc4`. Authentication is by an existing Rezon per-agent bearer token. A separate authenticated private network (Tailscale Serve HTTPS, for example) transports requests to the localhost-only server. A host reachable over HTTPS is **not** itself a verified inference source.

## Requirements

Python 3.12+, this repository's Rezon package, a configured local OpenAI-compatible model (including Ollama) and an **individually provisioned** Rezon worker credential. Provision credentials by an explicitly authorized operator channel. Do not copy tokens into chats, command-line arguments, issue comments, Git files, or execution logs. The client **does not retrieve credentials from VN2, modify SSH authorized_keys, or weaken TLS**.

In each worker process, set `REZON_WORKER_TOKEN` from a local protected credential store. For Ollama's localhost OpenAI-compatible API set `REZON_MODEL_API_KEY` to a nonempty, localhost-only placeholder; do not use that placeholder for remote provider endpoints. The server uses a separate administrator credential to create episodes and open hearings; never give that token to a worker.

## Explicit actions

Use the actual episode ID from the server's authorized operator. This is a pattern, **not** a verified external-run receipt:

```sh
python -m rezon.worker_client status \
  --gateway https://vn2.tail86ea75.ts.net \
  --episode collective-REPLACE_WITH_ID

python -m rezon.worker_client answer \
  --gateway https://vn2.tail86ea75.ts.net \
  --episode collective-REPLACE_WITH_ID \
  --model lfm2.5-thinking:1.2b \
  --model-url http://127.0.0.1:11434/v1

# Only after the last initial answer is present:
python -m rezon.worker_client review \
  --gateway https://vn2.tail86ea75.ts.net \
  --episode collective-REPLACE_WITH_ID \
  --model lfm2.5-thinking:1.2b
```

Each invocation uses the token-bound identity the server returns, not a caller-supplied worker label. `answer` asks the local model to assess the original prompt before peer answers are available. `review` fetches the complete sealed first round, targets other participants' answers, then submits an adversarial critique. An incomplete first round yields a 409 conflict; no model invocation or fake review is created. The client does not automatically defend challenges or determine the case.

The client prints only bounded receipt metadata: episode ID, token-bound agent ID, input SHA-256, contribution ID and *self-declared* model name. It does not echo the bearer token, private model text or underlying prompt. An accepted submission is `ACCEPTED_UNATTESTED`, not proof of independent execution, hardware identity, scientific accuracy or permission for protected effects.

## Network and failure gates

- Only HTTPS gateways, or HTTP on a loopback host, are admitted. HTTPS certificate validation remains enabled.
- Redirects are never followed with bearer credentials. The client sends no token to a redirected destination.
- A read error reports a bounded failure. An ambiguous **POST transport failure** returns exit code 3 and `OUTCOME_UNKNOWN`; it never retries a possibly committed submission. The operator must check existing episode state before any manual replay.
- The gateway must accept the contribution ID matching the token-bound worker; otherwise the receipt is rejected.
- Content and response sizes are bounded. The local model configuration and HTTP API are not an independent provider/host attestation mechanism.
- No autonomous network exposure, per-host credential distribution, live four-machine hearing, deployment or model self-training is included.

## Qualification

```sh
python -m pytest -q tests/test_worker_client.py
python -m pytest -q
```

Tests cover local HTTP integration with a temporary SQLite store, credential and roster binding, no model call before review barriers, peer-target integrity, HTTPS-only off-host gateways, blocked token-bearing redirects, bounded error output, and post-dispatch outcome uncertainty. All test credentials and model outputs are synthetic. Real cross-device model execution and a genuine fourth model source require separate signed/logged host execution evidence and secure credential provisioning.
