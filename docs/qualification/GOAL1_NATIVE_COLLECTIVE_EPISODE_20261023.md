# Actual Rezon Collective V1 episode — four-host Goal 1 calibration

**Updated status, 2026-10-23: FOUR independent account/model reasoning sources have committed first-round answers to one native Rezon CollectiveStore (THREE physical local-model hosts + ONE separately operated ChatGPT cloud account). THREE targeted peer reviews have been committed; Malaphor's review is still pending. The result is not four local-model hosts, a direct four-host network, a completed four-review round, verified autonomous learning, or AGI qualification.**

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
| `answer:malaphor` | Separate Mister Malaphor ChatGPT account (GPT-6 cloud); MT-262029 used only for record/hash verification | `a7916c57eb38a882668b91a64944c7eae17cbbbe15c4160f9230fa69d447d3ea` | Committed, **not a local MT-262029 model inference** |

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


## Verified four-source first-round completion and peer review (later checkpoint, 2026-10-23)

Mister Malaphor, independently operating a distinct ChatGPT conversation, contributed an actual **GPT-6 cloud** answer at [Rezon PR #109 comment 6370557977](https://github.com/thebrazenbeard/rezon/pull/109#issuecomment-6370557977). The text is 838 Unicode characters, exact answer-only UTF-8 SHA-256 `a7916c57eb38a882668b91a64944c7eae17cbbbe15c4160f9230fa69d447d3ea`; the prompt hash matches all three local workers. This is independent **account/conversation** provenance, NOT MT-262029 local-model execution. No independently governed external cross-host ingress/tunnel was installed. The primary verified the hash from the published literal answer before importing the fourth entry.

New native Rezon SQLite WAL readback: four answers, `missing_agents=[]`, `complete=True`, snapshot digest immediately after fourth answer `34ac621def6061f8bf854fc0b8144b88df2610281e3eeddf0a8a22b5fa1a1df5`. The built-in first-round peer visibility barrier now opens.

### Real targeted review calls

The primary sent a targeted, exact-answer critique prompt to each of three physical local models **after the first-answer barrier opened**. Each actual model output was saved on its own host, hashed, transferred under primary control and committed via native `CollectiveStore.submit_review` with target answer IDs.

| Reviewer / model | Target | Native review ID | SHA-256 | Caveat |
| --- | --- | --- | --- | --- |
| Lappy / Ollama Qwen3 4B | `answer:vera-vn1` | `review:vera-lappy` | `4090a94d4ac1755562fd8040568350ce71bb6018484d4719f60ce8199575ecb3` | Completed model output |
| VN1 / Ollama Qwen3 1.7B | `answer:vera-vn2` | `review:vera-vn1` | `e8d69092e2c3d493cfb1b91cf9493118232f7ac260ebd1308d06e53f41f42f8d` | Completed model output |
| VN2 / llama.cpp Granite 3.3 2B | `answer:malaphor` | `review:vera-vn2` | `dd50dc9d3f1926e3209727c68053c62725a0cbb2dedd4d7cfe5c3b684e63f1f6` | **TRUNCATED** at generation limit, recovered from a preserved successful llama.cpp console capture; initial parser failure retained, NOT silently retried |
| Mister Malaphor / separate ChatGPT account | `answer:vera-lappy` | Not yet present | Pending | Specific peer-review task posted at [PR #109 comment 6370656924](https://github.com/thebrazenbeard/rezon/pull/109#issuecomment-6370656924) |

**Source-data quality warning:** VN2's ORIGINAL first-round Granite submission included llama.cpp terminal banners, the prompt echo, and a truncated response. That original immutable answer remains unchanged and was a valid target for hostile critique. The VN2 review separately ended mid-sentence; both raw console and extracted review are preserved with this limitation. Neither is silently repaired into a complete generated answer.

Fresh distinct VN2 process reopened the authoritative store and verified `answers=4`, `reviews=3`, `syntheses=0`, `missing_agents=[]` with current native snapshot digest `d2554cdf2e6c823430f3736d95dc2aa12df821d96e3aa0602df0f3f23e0b36d6`. Native `project_episode` generated a typed V0 projection with 8 claims and 3 explicit challenge relations. A TEMPORARY loopback-only authenticated HTTP test for the actual episode returned **200** to Malaphor's enrolled agent view and the full four-answer/three-review snapshot; the test listener was then SHUT DOWN. No remote ingress or always-on service is claimed.

**Remaining required turn:** Malaphor must publish his independently generated targeted review of `answer:vera-lappy`. Only after verifying its provenance, exact text/digest, and native fourth review should a source-attributed, explicitly nonauthoritative synthesis be saved. Rezon is functioning as a native multi-source asynchronous collective store under active-turn relay, NOT a direct, continuously networked four-local-device autonomous cognition system. The four answers are independent sources, not four simultaneously running local models.


## Provisional four-source synthesis — native Rezon persistence (later 2026-10-23 checkpoint)

The same research-only Rezon episode **`collective-5aa0f89c3d674a46b7935b3ea47dc0f1`** now contains **4 immutable first-round answers, 3 targeted reviews, and 1 snapshot-bound provisional synthesis**. The Malaphor review of `answer:vera-lappy` has **not** been found in PR #109 comments and was **not** invented. His first answer has already been verified and committed; this does not require retransmission of his first answer.

After a new-process readback of the VN2 SQLite WAL at `/home/patrick/vera-review-sandbox/experiments/rezon-four-host-goal1-20261023/state/episode.sqlite3`, the verified facts were:

- Current Rezon input snapshot digest: `d2554cdf2e6c823430f3736d95dc2aa12df821d96e3aa0602df0f3f23e0b36d6`.
- Actual durable synthesis: `synthesis:d2554cdf2e6c823430f3736d95dc2aa12df821d96e3aa0602df0f3f23e0b36d6:vera-primary-provisional`.
- Exact synthesis-content SHA-256: `26c6f6dbddb033ccfbf53fb51d5d520d603144e6c3ae31e8d6917c29c0d5cbd2`.
- New native `CollectiveStore.snapshot` reopened in **another VN2 Python process**: answers=4, reviews=3, syntheses=1, complete=True, missing_agents=[]; all receipt digests match.
- Native `project_episode` produced a current **HYPOTHESIS** for this synthesis (9 current propositions and 3 challenge relations), not a decision or externally verified result. The stored synthesis is automatically historical/stale if another peer review changes the episode input digest.
- Source of synthesis: **Vera-primary author-integrator**, not Malaphor, not an extra independently invoked model, not an experiment result.

**Qualified interpretation:** Malaphor's separate-account answer offers a stronger randomized corrective-feedback-versus-sham-feedback cold-restart comparison than novelty-alone or restart-consistency arguments. Lappy's proposal insufficiently isolates feedback; VN1 lacks matched conditions; VN2's first reply includes llama.cpp prompt echo/banners and truncation. Three source-targeted reviews identify retrieval/state and task-complexity confounds. The absent fourth critique is material. The complete stored synthesis explicitly proposes matched randomized feedback/sham/frozen/retrieval-only comparisons, guarded revision identity, genuinely unseen blind held-outs, real cold restart, independent transport witness and negative-transfer controls. It does **not** claim those experiments ran.

**Hard limit:** FOUR independent reasoning sources provided first answers (three local models and Malaphor's distinct GPT-6 cloud account), with primary-mediated transport into a native Rezon SQLite episode, not four local models directly connected by private authenticated networking and not four complete reciprocal reviews. MT-262029 was for Malaphor's record/hash operations, not model inference. No production deployment, new network ingress, unsafe editor tasks, merge, or credential/trust/provider changes.

The remaining exact action is **one independent `review:malaphor` targeting `answer:vera-lappy`**, if that worker is still available. A later verified review makes this current synthesis stale and can be included in a new four-review synthesis. If the worker's session has ended, retain this accurate 4-answer/3-review synthesis rather than impersonating or forcing a fourth review.


## Final completed four-source review + digest-bound synthesis (verified 2026-10-23)

**This section supersedes prior PENDING-review checkpoints above; those remain historical provenance.** The research-only native VN2 CollectiveStore episode `collective-5aa0f89c3d674a46b7935b3ea47dc0f1` contains **4 immutable first-round answers, 4 source-targeted peer reviews, 2 historical syntheses, and exactly 1 CURRENT hypothesis projection**. No Rezon runtime source, production host or `main` was modified.

Independent Mister Malaphor explicitly posted the missing `review:malaphor` targeting `answer:vera-lappy` at [PR #109 comment 6372859766](https://github.com/thebrazenbeard/rezon/pull/109#issuecomment-6372859766). Its exact answer-text UTF-8 SHA-256 `dac15b9bbaac618f29be3359736ce62b3394084077bc827684756a9597c7a915` was independently recomputed on VN2 from the published review and matched before native `CollectiveStore.submit_review`. The review came from Malaphor's independently operated ChatGPT GPT-6 account; MT-262029 held the text/hash record, **not** local model inference. No fabricated review was substituted.

The fourth critique changed the native input digest from `d2554cdf2e6c823430f3736d95dc2aa12df821d96e3aa0602df0f3f23e0b36d6` to `d3271ee463744670c1f0c0a058d57b4ede4f40690d2262b13b7906665b2669f0`, automatically making the prior provisional synthesis stale. All eight contributors' raw text and exact SHA-256 were read from the authoritative native store and relayed to Lappy for an **actual local Qwen3 4B integrator inference**. That model's completed unverified draft is persisted under Lappy's isolated temp receipt `rezon_four_peer_integrator_result_20261023.json`, content SHA-256 `668061a242b759a5d6aa62ab6bb3f25e38b70f48d8f87ed14ed2ee323be046a0`; provider reported 2375 prompt and 279 completion tokens. Its claim that same-prompt nonreversion alone is sufficient evidence of feedback learning was **REJECTED** by the primary: feedback causation requires a matched sham/frozen contrast, not merely answer persistence.

The reviewed, explicit **Vera-primary-authored nonauthoritative synthesis**, correcting the model draft and attributing both all four initial claims and all four peer objections, was committed as native synthesis:
- ID: `synthesis:d3271ee463744670c1f0c0a058d57b4ede4f40690d2262b13b7906665b2669f0:vera-primary-reviewed`;
- exact stored UTF-8 SHA-256: `0a91045bdd61a4d60f8f0d2b9b5da5c3ac187bca32c20f1a337bfc782d5c945a`;
- isolated receipt text: VN2 `/home/patrick/vera-review-sandbox/experiments/rezon-four-host-goal1-20261023/state/reviewed_synthesis.txt`.

A **fresh separate VN2 process** reopened the SQLite WAL and asserted: all four agents' initial answers present; all four reviews present, `review:malaphor` targeting `answer:vera-lappy` with the cited hash; 4 native `challenges` relations; 2 historical syntheses; exactly one current `PropositionKind.HYPOTHESIS` equal to the reviewed synthesis ID; no current projection of the stale provisional synthesis. The exact input snapshot digest and synthesis digest were rehashed and matched.

**Result of the actual four-source reasoning:** propose independently controlled real-feedback-versus-sham and frozen/retrieval diagnostic arms, matched model/inference/tool budgets, genuinely unseen and evaluator-held heldouts, specific revision consumption receipts, cold restart, and reversal/negative-transfer tests. No such causality experiment ran. Lappy's novelty-alone, VN1's identical-prompt persistence, and the Lappy integrator's same-prompt repetition criterion cannot by themselves identify feedback-caused learning. VN2 Granite's first output contains console/prompt echo and truncation, and its critique truncates; those limitations are retained.

**Boundary:** This is a completed **four independent reasoning-source, four-review, native Rezon collective episode**, with three actual local models and one independent cloud-model account, orchestrated through a primary-controlled relay. It is **not** a directly authenticated four-machine peer network, four local inference hosts, always-on distributed cognition, consensus truth, a self-learning result, or production authorization. Security Draft/HOLD #106 remains unmerged; no editor-triggered script, credentials/trust/provider/deployment or direct-main mutation occurred.
