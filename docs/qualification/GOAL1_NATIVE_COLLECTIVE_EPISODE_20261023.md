# Actual Rezon Collective V1 episode — four-host Goal 1 calibration

**Status as of 2026-10-23: THREE physical host first-round answers committed to native Rezon CollectiveStore; fourth host (Mister Malaphor) PENDING. NOT a completed four-host dialogue, peer-review round, synthesis, autonomous cognitive network or AGI qualification.**

This is a distinct **native Collective V1** episode, not the earlier source-only blind packet test on this PR. We use the existing merged `src/rezon/collective.py` and `collective_http.py` at Rezon `main@72e9ec97e39eb0f0cfed0e62c5252f027b25ecb9`. It does **not** require a new collective reasoning framework.

## Exact episode

- **Episode:** `collective-5aa0f89c3d674a46b7935b3ea47dc0f1`
- **Authoritative native Rezon SQLite WAL store:** VN2 isolated research directory `/home/patrick/vera-review-sandbox/experiments/rezon-four-host-goal1-20261023/state/episode.sqlite3` (not a canonical/production memory store)
- **Required worker IDs:** `vera-lappy`, `vera-vn1`, `vera-vn2`, `malaphor`
- **Prompt SHA-256:** `dbb150199d567b4bc8358f2581742f563210f419b59e3af70c4768d6243e0927` — the same bytes were supplied to all three real model workers
- **Native episode snapshot digest after three answers:** `57882421d32fa49d9d053e4903751177ca89c3e48652cd3ef67d5891270e92d2`
- **Exact literal first-round prompt:**

> Rezon collective FIRST ROUND. You are one independent worker; other worker answers are unavailable. Same topic for all participants: What minimum observation would distinguish feedback-caused learning in QualifiedVeraRuntime from prompt conditioning, retrieval, or memorization across a cold restart? Propose one falsifiable minimum observation, the strongest confound, and one decisive experiment. Do not claim tests were run or invent numeric thresholds. Keep answer under 160 words.

## Actual host-generated contributions

All three fresh first-round inferences were launched in one concurrent orchestration turn. Each model responded without peer plaintext. The resulting raw answers were durably stored on their own machines, imported through the **primary-operated Executor relay** (not a separately authenticated cross-host Rezon connection), and then submitted to **one actual `rezon.collective.CollectiveStore`** instance on VN2. The native contribution IDs and SHA-256 hashes below were verified against imported content.

| Native Rezon contribution | Host/model | SHA-256 of exact stored answer | Status |
| --- | --- | --- | --- |
| `answer:vera-lappy` | Lappy / local Ollama `qwen3:4b-instruct` | `1428b5a0332508efbc3e7c660740e03f10bccd360d4cd68951c9e00ba0162515` | Committed |
| `answer:vera-vn1` | VERA-NODE-1 / local Ollama `qwen3:1.7b` | `58200404d87639cbe6978ed9b14a3270bb178bc6797b9727136ddbf435b9eaa0` | Committed |
| `answer:vera-vn2` | VN2 / local llama.cpp Granite 3.3 2B GGUF | `cd0a00ee65dbc6c65726200cf93d25a39b42d41be5f1c6e976336a02d6c3b1d6` | Committed |
| `answer:malaphor` | MT-262029 / independently operated model/process | **Pending** | Not submitted |

Their first-round answers deliberately remain unrevealed to the other workers. Output hashes prove ordinary content consistency, not worker/process/model-weight identity or independent trust.

## Native Rezon protocol verification

Fresh separate VN2 process reopened persisted SQLite: `len(snapshot.answers)=3`, `missing_agents=("malaphor",)`, `snapshot.complete=False`, `len(snapshot.reviews)=0`, `len(snapshot.syntheses)=0`.

A temporary loopback native `rezon.collective_http.make_server` HTTP gateway against **this exact persisted episode** returned:
- authenticated `malaphor` `GET /v1/episodes/<episode_id>`: HTTP **200** with common topic;
- authenticated `vera-lappy` `GET /v1/episodes/<episode_id>/state`: HTTP **409**, enforcing peer-answer embargo before round completion;
- admin `GET /v1/episodes/<episode_id>/state`: HTTP **200**, three answers, Malaphor outstanding.

The loopback test server was shut down immediately. **No external authenticated tunnel, remote worker HTTP service, production deployment, independent verifier, or long-running background coordinator is currently established.** The actual cross-host content import was orchestrated through Executor, and admin-side identity values were assigned by the primary, so this is not a cryptographically independently authenticated four-host session.

## Specific instructions for Mister Malaphor's own execution chat

1. Verify your own available host/process/model on MT-262029; do not claim local model if your reasoning ran only in ChatGPT cloud.
2. Independently invoke the **exact literal prompt above** without any other worker's answer. Make one completed inference, no fabricated process receipts or automatic replay on ambiguous timeout.
3. Preserve raw output on your own device, calculate SHA-256 of UTF-8 text, and publish an event-local **MALAPHOR_REZON_FIRST_ANSWER** checkpoint to the conversation of this PR #109 (or Vera Mono Issue #85), including episode ID, actual host, method/model, exact answer text, answer SHA-256, prompt SHA-256, source/model provenance and one explicit potential falsifier. No private evaluator holdout truth is involved in this public coordination topic.
4. This event currently has **three already-frozen submitted answers**. Once your answer is posted and checked, Vera will import it under `agent_id=malaphor`, verify Rezon `snapshot.complete=True`, expose first-round contributions to all workers, and launch Rezon targeted peer critiques with actual host model calls. Your role may additionally propose a specific adverse test against another host's exact answer.
5. If your host is inaccessible or your model cannot be invoked, report precise UNKNOWN/BLOCKED; DO NOT fabricate a fourth contribution.

## Hostile review

> A single primary-controlled relay can make three independent physical model calls but still author or edit their Rezon database submissions. The loopback gateway has not established remote host identity or direct reciprocal dialogue.

**Accepted.** We have real three-host model generation + one native persisted Rezon episode, not a qualified four-host live network. To demonstrate genuine four-way shared cognition: Malaphor independently contributes; native store opens peer review after all four; all four hosts *consume other answers and produce targeted revisions/critiques*; one integrator produces a source-attributed non-authoritative synthesis; fresh-process readback and accurate transport provenance remain mandatory.

Security: Rezon `main` still carries an untrusted VS Code folder-open task and disguised executable; security Draft/HOLD PR #106 is separate. This event fetched ONLY named source Python files by exact immutable Git blob hashes into isolated directories and never launched editor workspace tasks or obfuscated assets. No repo main merge, installation/cutover, credential/trust/provider or canonical-memory modifications.
