# Rezon four-worker virtual network — observed Tailscale transport (2026-10-23)

**Status: existing private overlay VERIFIED; Rezon shared gateway ingress NOT ACTIVATED.**
This is bounded qualification and an activation proposal, not a deployment authorization or another backend.

## Physical topology verified via Executor, read-only

All three primary machines were reachable and reported `Tailscale BackendState=Running`.

| Actual device | Identity observed | Peer reachability |
| --- | --- | --- |
| Lappy / Windows | `Lappy` | Tailscale ping to `vn2` succeeded (9 ms) |
| VN1 / Windows | `vn1` | Tailscale ping to `Lappy` succeeded (9 ms) |
| VN2 / Linux | `vn2` | Tailscale ping to `vn1` succeeded (1 ms) |

Each reported the others online, and an additional existing peer `TheSimsVault`. None reported an `MT-262029` peer. Tailscale's apparent peer list is not evidence that Mister Malaphor's separate ChatGPT account is remotely enrolled. The previous four-source Rezon reasoning session used his separate cloud account, with host-mediated receipt import; it did not use a fourth local LLM.

**Current listeners/config:** VN1 and VN2 have no Tailscale Serve web/tcp route observed at the check; Lappy has preexisting Serve targets on unrelated local ports but **none to Rezon 8765**. On Lappy, TCP 8765 is owned by `workbridge-mcp`, and `GET /healthz` did not yield Rezon. Do not rebind, overwrite or route this port as Rezon. Rezon Collective V1 gateway `make_server` explicitly binds `127.0.0.1` only and was *not* activated during these probes.

## Smallest viable virtual Rezon network (activation still needs exact authority)

1. **Keep one authoritative Rezon collective runtime and one T'Kal source lineage** (avoid competing PR #109 / #111 definitions of the same `tkal_network.py` and `collective_http.py`). First repair the common self-review quorum issue, and resolve the unresolved source security Draft #106.
2. Select **VN2** as the authoritative opt-in Rezon SQLite WAL episode host, with a dedicated isolated state directory, and start Rezon's existing authenticated **loopback** Collective V1 HTTP gateway on a free VN2-local port after checking port conflicts.
3. Publish *only that loopback service* via an approved **Tailscale Serve private HTTPS route** restricted by tailnet ACL and service authorization. Do **not** use Tailscale Funnel, `0.0.0.0` listener, public ingress, insecure HTTP or bypass existing host firewall/trust policy. This changes network ingress/trust and requires Patrick's explicit authorization for VN2 and the exact route.
4. Generate four **distinct per-worker** Rezon bearer secrets plus separate admin secret via governed host-local secret provisioning. Keep secrets out of PRs, Issues, Blotter, logs and prompts. Credential/trust mutation also requires explicit authority. Define expiry/revocation and ensure the handler never grants repo or arbitrary tool effects.
5. Run **physical-client** attestation: Lappy, VN1 and VN2 independently contact the private route, authenticate with different worker identities, submit sealed first answers on the SAME native Rezon `CollectiveStore` episode, then unlock peer answers, submit targeted critiques, defenses and T'Kal hearing actions. Record exact host, source, model, input hashes, response, role, transport and persistence; no counterfeit device role claims.
6. Bring Mister Malaphor through his independently authorized account/device using the *same private authenticated route* **only if that endpoint and client are confirmed reachable**. Until then, leave his worker pending and never submit an answer on his behalf. ChatGPT API sessions are not persistent background agents merely because enrolled in Rezon.
7. Query server-side snapshot from another process, verify four independent first answers, reciprocal critiques, hearing resolution/synthesis and one current non-decision hypothesis. Stop or leave running only according to authorized service lifecycle. A four-host test without physically separate client evidence remains unqualified.

## Security and qualification ceiling

- Rezon main `72e9ec97e39eb0f0cfed0e62c5252f027b25ecb9` contains previously reported hidden editor-autostart executable references. Source security containment is in Draft/HOLD #106. We did **not** open its VS Code workspace, execute the hidden payload, install anything or change Tailscale routes.
- Existing Rezon `collective_http.py` includes an authenticated role-bound loopback gateway, but has no autonomous remote worker scheduler or independently authenticated model-output witness. The existing four-worker hearing tests on #109 use separate *localhost processes*, not physical remote devices.
- The completed native episode `collective-5aa0f89c3d674a46b7935b3ea47dc0f1` was independently reread with 4 answers, 4 real peer-targeted reviews and one current `HYPOTHESIS`, via primary-mediated inputs. It is valuable evidence of **multi-source discourse**, not of an always-on mesh, genuine learning or consensus truth.

> **HOSTILE REVIEW (accepted):** A private Tailscale tunnel does not itself prove model independence, each source's identity, or reasoning quality. The protocol needs meaningful distinct physical client receipts and peer-targeted challenges; a self-review must not satisfy a peer quorum. Existing backend and overlay are preferable to another competing virtualization layer.

No main merge, deployment, network/credential/trust/provider change or canonical-memory mutation performed by this qualification.
