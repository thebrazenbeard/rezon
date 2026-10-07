# Reasoning Surface Evidence — 2026-10-07

## Purpose

This note records a controlled black-box comparison of three ChatGPT reasoning surfaces using the same user task:

```text
Stress test this repo: https://github.com/thebrazenbeard/portal
```

The purpose was not to recover hidden chain-of-thought or infer undocumented provider internals. The purpose was to observe externally visible orchestration behavior, compare resulting work products, and derive constraints for Rezon worker routing.

## Experimental surfaces

1. **Desktop Chat — GPT-5.6 Sol High reasoning**
2. **ChatGPT Desktop Work — Ultra reasoning**
3. **Firefox cloud Work — Max reasoning**

The Desktop Chat and Desktop Work runs used the same WorkLaptop and the same installed ChatGPT/Codex runtime generation. Firefox Max ran concurrently for part of the Desktop Ultra window.

Instrumentation on WorkLaptop included:

- Tattler V0005, exact CI artifact, Windows IP Helper transport observations at 250 ms polling;
- a companion Codex process/network tracer that recorded process births, MXC command lines, connection transitions, and user-declared phase markers.

The Tattler evidence ceiling matters: port-derived TLS/HTTPS labels are heuristic, encrypted payloads were not decrypted, and application semantic events exist only when an application or adapter reports them.

## Timing and local orchestration observations

### High reasoning Chat

Controlled window:

- start: `2026-10-07T12:38:06.1331014Z`
- end: `2026-10-07T13:00:45.3042022Z`
- elapsed: approximately 22 minutes 39 seconds

The companion tracer observed during that window:

- **0** `codex.exe --__codex-windows-mxc` launches;
- **0** fs-helper launches;
- **2** new established Codex TLS connections, both to `104.18.32.47:443`.

The newer Tattler recorded ChatGPT/Codex transport activity, but no application-level semantic events were reported.

### Desktop Work Ultra

Controlled window:

- start: `2026-10-07T13:06:29.4952049Z`
- end: `2026-10-07T13:27:09.9895098Z`
- elapsed: approximately 20 minutes 40 seconds

Using the same companion tracer and comparable event definitions, the Ultra window produced:

- **59** MXC launches;
- **0** fs-helper launches;
- **73** new established Codex TLS connections;
- endpoint distribution: **45** to `104.18.32.47:443`, **28** to `172.64.155.209:443`.

The newer Tattler, which samples and journals connection transitions differently, recorded a larger number of Codex outbound established-open events. That count is not directly comparable to the companion tracer's open count and must not be substituted for it in the High-vs-Ultra comparison.

The defensible local conclusion is:

> the large MXC/process and Codex connection fanout is associated with the Desktop Work execution path in this runtime, not merely with having the newer Desktop runtime installed.

This does **not** establish that each process or socket corresponds to an independent reasoning agent.

### Firefox cloud Work Max

The Firefox cloud Work Max run began shortly before the marker at `2026-10-07T13:15:28.7909687Z` and ended at `2026-10-07T13:37:17.6413079Z`.

Because the actual cloud execution occurs remotely, local Tattler evidence can attribute browser-side connections to Firefox but cannot count or identify server-side workers, agent fanout, or hidden model topology. The start marker is also slightly late, so a small interval around startup is intentionally treated as ambiguous.

## Work-product comparison

### Desktop Work Ultra output

Ultra tested Portal revision:

`fd55ae74db582294e5c2eba9349831e6f1404ca3`

Its report classified the repository as failing orchestration reliability. The existing suite produced 752 passes and one failure, where that failure was a documentation/test mismatch rather than one of the runtime defects found by added stress probes.

Two high-priority control failures were directly reproduced:

1. finally held queued work could still cross an execution boundary after capacity was freed;
2. an in-flight continuation could overwrite a newer acknowledged STOP and admit work.

The Ultra run also reported scheduling underfill, cross-lineage ambiguous replay, slow-cognition control starvation, a Desktop error-callback `NameError`, Unicode launcher failure, completed-cognition capability mismatch, and several lower-level durability/numeric edge cases.

### Firefox Work Max output

Max began from the same initial Portal revision and finished on:

`7d00d8bf3b48c0676b2278359838ee563c66c67f`

Its final-head baseline passed all 753 repository tests. The report states that the intervening final-head change affected `PORTAL.md` and its architectural contract test, with no changes under `portal/` or `runner/`.

Max reproduced seven failure classes. Three directly affected execution control:

1. finally held queued work remained executable;
2. same-attempt races could invoke the driver twice under an identical deterministic attempt ID;
3. an in-flight continuation could overwrite a newer STOP.

Additional findings included bounded-pump starvation, invalid heartbeat timestamps appearing healthy, capability-insensitive cognition replay, and infinite route TTL acceptance.

## Cross-surface convergence

The most important result is not that one surface found more findings than another. It is that two different Work reasoning settings independently converged on the same central control failures:

- **final hold must close the execution boundary**;
- **STOP/generation state must remain current across admission and commit**;
- **idempotent attempt-marker replay must not itself become execution ownership**.

This kind of convergence is useful evidence, but Rezon must still record shared context, shared code, prompt lineage, and possible common-model/provider ancestry. Two labels do not prove epistemic independence.

## What this experiment does not prove

It does not prove:

- hidden chain-of-thought content;
- the number of cloud agents used by Max;
- that an MXC child equals one independent model worker;
- that opening more sockets increases reasoning quality;
- that a client can promote a High chat into Ultra or Max by changing local transport behavior;
- that model entitlement or reasoning tier can be modified through routing flags, connection replay, credentials, or process manipulation;
- that the three runs are a perfect identical-head benchmark.

## Rezon design consequences

### 1. Surface and reasoning tier are runtime capability metadata

Rezon should represent a selected product surface and reasoning tier as observed/capability metadata on a worker descriptor and execution receipt. It must not infer tier from socket count, process count, or latency.

### 2. More connections are an observation, not a capability grant

The Ultra process/socket fanout is useful diagnostic evidence about the Work path. It is not an invocation API and not a mechanism for upgrading High.

### 3. Escalation should be explicit delegation

A High-reasoning coordinator can potentially gain access to stronger specialist work by delegating a bounded task to an authorized Work Ultra or Work Max surface and receiving a result artifact back. That is delegation, not mutation of the High session's model.

### 4. Exact-subject binding is mandatory

Every cross-surface comparison or escalation should bind:

- repository and exact head;
- literal task;
- context manifest;
- selected surface and reasoning tier;
- tool/environment constraints;
- start/end timestamps;
- artifact hashes or stable locators where possible;
- authority ceiling;
- independence/contamination metadata.

### 5. Reasoning-quality evaluation must include orchestration

A reasoning surface can differ not only in final prose quality but in execution topology, adversarial breadth, test strategy, artifact production, retries, and verification depth. Rezon benchmarks should therefore evaluate the whole receipt, not only the final answer.

## Current evidence ceiling

This is black-box behavioral evidence from one machine, one task family, and one runtime generation. It is strong enough to improve Rezon's routing and evaluation abstractions, but not enough to freeze provider-specific architecture or claim universal behavior.
