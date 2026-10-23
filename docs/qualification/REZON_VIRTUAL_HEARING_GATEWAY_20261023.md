# Rezon virtual collective hearing API — 2026-10-23

**Status: research source, not an installed or activated cross-host network.** Rezon's existing Collective V1 stores one authoritative episode and gates peer-answer visibility. This addition lets *separately running token-enrolled HTTP clients* conduct a T'Kal-in-ket hearing inside that same episode through `collective_http.make_server`. It does not introduce a second broker, consensus database, model scheduler or external effects.

## Four-worker virtual network

The administrator creates one episode with four worker IDs through `POST /v1/episodes`. Each participant submits a first answer using its own bearer token. Prior to all four answers, worker `GET /v1/episodes/{id}/state` returns HTTP 409, hiding peer plaintext. After completion, workers can read state and submit target-specific reviews through the existing API.

An optional hearing can then be opened against the **exact current** CollectiveStore snapshot digest. Four distinct workers play roles: one proposer and three lens reviewers (`purist_logic`, `pragmatism`, `bridge`). The entire hearing is durably stored in tables of the **same** SQLite WAL database. Each lens must challenge before a verdict. Any partial or unresolved challenge blocks determination. New collective contributions stale an existing hearing.

## Additional HTTP routes

All under `/v1/episodes/{id}`:

| Request | Role | Body / response |
| --- | --- | --- |
| `POST /tkal` | admin | Exact `expected_digest, proposer, lenses, hypothesis, falsifier`. Creates hearing, returns view (201) |
| `GET /tkal` | enrolled participant or admin | Returns hearing and challenges (200); worker cannot bypass unfinished first round |
| `POST /tkal/challenges` | lens worker | `challenge_id, target, question`; reviewer ID is derived from the bearer token (201) |
| `POST /tkal/defenses` | challenged worker | `challenge_id, response, evidence_ref`; defender ID comes from token (201) |
| `POST /tkal/resolutions` | admin chair | `challenge_id, disposition, rationale`; dispositions ANSWERED/CONCEDED/WAIVED/PARTLY_ANSWERED/UNRESOLVED (201) |
| `POST /tkal/verdict` | admin chair | `verdict, rationale`; SUSTAIN/REFINE/WITHDRAW only after each lens has challenged and all objections were resolved (201) |

The existing HTTP gateway rejects invalid bearer tokens (401), wrong-role actions (403), malformed requests (400), incomplete, stale or closed hearings (409). Body fields may not supply `reviewer` or `defender`; those identities must derive from the worker token. A document `evidence_ref` is only a claim and is **not** an authenticated proof of source truth.

The **protocol chair is an administrative role**, not a fifth reasoning model; administrative determination has no external execution authority. Source `TkalVirtualNetwork.HearingView.to_dict()` explicitly returns `authority: NONE` and `independence_verified: false`.

## Network reachability boundary

`make_server` still deliberately binds to `127.0.0.1` only and the token environment remains opt-in. A client on another physical machine requires an independently authorized, authenticated private tunnel or TLS proxy terminating locally, unique per-worker token enrollment, access controls and end-to-end verification. **None was deployed or altered by this research PR.** Do not expose `0.0.0.0`, publish tokens in repository files, describe Executor-mediated packet transfer as direct device-to-device ingress, or represent four localhost subprocesses as four physical hosts.

The system supports *shared virtual workspace semantics*: enrolled agents can join the same fixed episode, exchange reasoned claims, cross-examine a hypothesis, defend, concede, and retain reviewed state with explicit dissent. It is not always-on distributed consensus, secure multi-machine attestation, proof of model learning or an AGI runtime.

## Verification and held boundary

At isolated Rezon PR #109 head `591c67c7eec311296591c1fa83e8474137ddfea0`:
- New test `tests/test_tkal_collective_http.py` Git blob `5eff8566829756f080dcb567dbba25b22567bc7d`.
- Baseline test **RED** against current merged-branch Rezon Collective HTTP: hearing `POST /tkal` returned 404; test asserted 201.
- `src/rezon/collective_http.py` Git blob `d4097840a53c8fb7f81eb691b164c56a0e16b9ff`: minimal authenticated routing to pre-existing `src/rezon/tkal_network.py` (Git blob `12ca23c044a11e30e522e3c2cbabcfc6348d38e4`).
- **GREEN** on physical VN2/Linux Python 3.12 and Lappy/Windows Python 3.12: four actual local subprocess HTTP clients complete challenge/defense/three-lens hearing; native SQLite reopening, auth and incorrect-role/replay/closed-state negatives; Lappy additionally passed preexisting `test_four_worker_collective_http.py` separate-process test.
- Exact-head GitHub Rezon kernel and Benchmark V1 workflows both terminal SUCCESS for the code commit. If this document adds a later commit, inspect *that new exact head* CI separately.

> **HOSTILE REVIEW (accepted):** A localhost gateway exercised by four separate processes is not a genuine four-physical-device virtual network. The source now exposes the correct role-bound hearing API, but independent remote ingress, credentials, operational scheduling and source-attested model execution remain separate qualification gates. **No active multi-host networking should be claimed.**

Source lineage is Rezon Collective V1 already merged on main. This original opt-in hearing adapter is informed by published T'Kal-in-ket protocol concepts, without importing code from its presently unlicensed repository. Rezon's suspicious workspace autorun file remains a separate SECURITY/HOLD concern; tests loaded only exact Python source into isolated temporary directories, never the VS Code checkout/startup task.
