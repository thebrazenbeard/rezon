# Rezon Virtual Inquiry Network V1 — source-level, opt-in

**Scope:** four reasoning participants on one Rezon collective topic, then a bounded T'Kal-in-ket-style adversarial hearing. **Status:** source implemented and locally tested. This is a transport-overlay feature, not a deployed cross-machine network, automatic inference daemon, consensus truth system, or approval authority.

## Architecture

The canonical four-worker data plane is existing `rezon.collective.CollectiveStore` (SQLite WAL, persistent append-only first answers and peer reviews). The same store backs `TkalVirtualNetwork`, which adds durable case, attributed challenge/defense and disposition records; the hearing source does not copy or import the unlicensed external `thebrazenbeard/t-kal-in-ket` code. The public protocol concepts were consulted at `t-kal-in-ket/main@b62abc2447919cca6b29a52c4656db584b5471d8` and overlap with longstanding three-peer deliberation patterns.

`make_server(...,tkal_network=TkalVirtualNetwork(store))` opts into HTTP routes on the existing **127.0.0.1-only** authenticated collective gateway. `make_server` still rejects nonloopback host. It does not create remote ingress, provision credentials, approve a tunnel, or connect other physical hosts. Authenticated private TLS proxy/tunnel configuration and independent host identity/provenance remain explicit separate operator-governed work.

The protocol reference has since merged stronger source guards into `t-kal-in-ket/main@e3dff0561b68810af8d40a1295739afaa763fc2b` through separately owned PRs #4 and #3. This Rezon implementation remains an original separate codebase: no library or unlicensed upstream source is imported.

To enable the virtual hearing interface explicitly, run `python -m rezon.collective_cli serve --db <private-state-file> --tkal` with the **existing** Rezon collective gateway's operator-managed environment credentials. With no `--tkal`, the hearing API is absent. The listener remains `127.0.0.1`; any remote agent connection requires separately authorized, authenticated, private TLS transport, and a bearer token is not an independent hardware identity witness.

No source-level role/token identifies an independent physical model execution. Expose only `independence_verified:false`, `authority:NONE`. Rezon worker reviews remain claims; a `SUSTAIN` result records completed peer exchange, not correctness or deployment permission.

## One episode / four workers

1. Admin creates an existing `/v1/episodes` with four uniquely enrolled agents. Each submits first answer using their distinct worker credential. Peer state remains withheld while initial answers are missing; the existing Rezon first-answer barrier applies.
2. Each peer submits a targeted, attributable review to `/reviews`. A new hearing may open only after all four first answers are present and each of three peer lenses has actually submitted a review. Use a **frozen exact current CollectiveSnapshot.digest**.
3. Admin `POST /v1/episodes/{episode_id}/tkal` with exactly `expected_digest,proposer,lenses,hypothesis,falsifier`. The proposer + three lens assignments must be four distinct enrolled worker identities. The hearing freezes the input snapshot digest.
4. Lens-assigned worker `POST .../tkal/challenges` with `challenge_id,target,question` (one outstanding challenge). Target worker `POST .../tkal/defenses` with `challenge_id,response,evidence_ref`. Admin `POST .../tkal/resolutions` with `challenge_id,disposition,rationale`. A partial/unresolved challenge remains outstanding, may receive an attributable continuation, and cannot silently be replaced by a new challenge. Continuation preserves the earlier response text and references within bounded fields; this is **not** a cryptographic append-only event history.
5. Admin `POST .../tkal/determination` with `verdict,rationale` where verdict is SUSTAIN or REFINE. A SUSTAIN requires all three lens reviewers to ask directed cross-peer questions, plus attributed replies from all three distinct peer lenses; three WAIVED questions or three proposer-only replies do **not** pass. REFINE allows a reasoned weaker disposition only after all lens questions and without an unresolved challenge. Proposer alone `POST .../tkal/withdrawals` with `reason`.
6. `GET .../tkal` gives the durable hearing. Reopened processes observe the same challenges and status. Changed collective answers/reviews make the hearing `stale:true` and prohibit further mutation. Create a new versioned episode for changed claims.

Admin credentials cannot be used to impersonate worker answers/defenses in these routes; worker bearer tokens identify enrolled *claims*, not authenticated hosts. HTTP access controls explicitly refuse invalid/unauthenticated requests. An external nonlocal client needs an independently authorized private authenticated transport to reach localhost safely.

## Security and tests

- Rezon CollectiveStore transaction use is preserved, and the new hearing shares its DB handle.
- Strong existing bearer validation and hidden first-round answers continue. HTTP server never binds to `0.0.0.0`.
- Four-agent roster collision, false reviewer, challenge replay, multiple simultaneous challenges, stale state, missing defenses, invalid waiver, attempted admin withdrawal, and all-three directed SUSTAIN tests passed on physical Lappy Windows and VN2 Linux (14 focused tests each at head `4191f62a119526dc665de2940eaec468d854c9c3`). A subsequent 15th test used **four separate authenticated Python client processes on Lappy**, with parallel initial answers/reviews and cross-peer challenges via the one real loopback HTTP gateway; 15/15 passed on Lappy. A matching VN2 subprocess test command was blocked by host safety controls, **not** rerun around the block; GitHub Linux CI at that exact source head was SUCCESS.
- The source tests use synthetic worker text, not independent host inference. The real mediated Rezon four-source episode in PR #109 is a distinct provenance artifact (three local models and one separate Malaphor GPT-6 cloud account). It is not evidence that this API was installed on those four hosts.
- Independent review from `COORDINATION_TKIK` is recorded in `t-kal-in-ket/issues/2` and Bus Issue #388. Concurrent tkik PRs #3 and #4 alter their own `tkik/core.py`; this Rezon feature does **not** merge, overwrite, or import those sources.

## Qualification ceiling

The chair is not an independent truth oracle. Self-declared model/runtime source IDs and consistent SHA-256 JSON snapshots do not attest the host. Local HTTP tokens do not establish who controlled remote execution. This candidate can safely merge as an opt-in **source interface** after CI and review, but no claim of deployed physical mesh or live independent host capture is warranted. No production activation, credential changes, private TLS tunnel, automatic agent daemon, provider mutation or canonical-memory write is included.

> **HOSTILE REVIEW (accepted):** A chair initially could WAIVE all three questions and incorrectly SUSTAIN a claim, or satisfy all three lenses with only proposer responses. Negative tests reproduced both at exact source head `f6100be9a0ab587bfa3514398ce49d1f05c76afe` (2 failures out of 11), and the revised gate rejects them. The external project’s PR #4 likewise requires substantive cross-peer examination. Model critiques from real Qwen3/Gemma/Granite hosts were inspected against actual code, and unsupported model assertions were not adopted.
