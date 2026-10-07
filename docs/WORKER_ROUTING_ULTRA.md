# Worker Routing and Ultra

## Principle

A more capable or more expensive worker should be treated as a specialized computational resource, not as an authority source and not as the architecture itself.

Rezon should therefore support runtime-discovered worker capabilities and route tasks according to task semantics, resource constraints, expected information gain, and evidence about what callable surface actually exists.

## Current empirical status

Earlier Rezon notes recorded an experiment in which Work appeared to instantiate an Ultra worker internally but no stable transferable invocation descriptor was recovered. That historical observation remains useful, but the 2026-10-07 same-prompt comparison provides a stronger boundary.

The task was:

```text
Stress test this repo: https://github.com/thebrazenbeard/portal
```

Observed surfaces:

- Desktop Chat — GPT-5.6 Sol High reasoning
- ChatGPT Desktop Work — Ultra reasoning
- Firefox cloud Work — Max reasoning

On the same WorkLaptop and same Desktop runtime generation, the companion process/network tracer observed:

- High: 0 MXC launches and 2 new established Codex TLS connections during the controlled window;
- Desktop Work Ultra: 59 MXC launches and 73 new established Codex TLS connections during the controlled window.

That is strong evidence that the large local MXC/socket fanout belonged to the Desktop Work execution path in that runtime. It is **not** evidence that opening more connections creates Ultra reasoning, that each socket is an agent, or that a High chat can be promoted by imitating the transport pattern.

Firefox Work Max executed remotely. Local telemetry could observe browser-side traffic but could not count server-side workers or infer cloud model topology.

See `REASONING_SURFACE_EVIDENCE_20261007.md`.

## Defensible capability claim

The current defensible claim is:

> Distinct ChatGPT surfaces can expose materially different reasoning/orchestration behavior and work products, and Rezon can model them as separate worker capabilities when a supported callable surface is available.

Not:

> ordinary High chats have a reusable hidden Ultra connector.

And not:

> transport/process fanout is a mechanism for changing reasoning tier.

A user-selectable product surface may be observable and usable interactively while still lacking a stable programmatic adapter that Rezon can invoke. Rezon must preserve that distinction.

## Routing abstraction

```text
WorkerDescriptor {
  worker_id
  operator_types[]
  provider
  product_surface?
  model?
  reasoning_level?
  callable_surface
  tool_capabilities[]
  context_limit?
  expected_latency?
  cost_class?
  availability
  authority_ceiling
}
```

Observed runtime facts should be recorded separately:

```text
WorkerObservation {
  worker_id
  product_surface
  model_label?
  reasoning_label?
  observed_runtime_version?
  observed_process_topology?
  observed_transport_summary?
  evidence_class
  observed_at
  expires_at?
}
```

The `authority_ceiling` is explicit because capability must not be confused with permission. `WorkerObservation` is explicit because capability must not be inferred from incidental telemetry.

## Routing signals

A scheduler can consider:

- task/operator type;
- required tools;
- estimated difficulty;
- need for independence;
- latency target;
- cost budget;
- context size;
- provider availability;
- product surface availability;
- requested reasoning class;
- privacy constraints;
- reproducibility requirements;
- whether a deterministic worker can solve the task more reliably than an LLM;
- expected information gain from escalation.

Hard eligibility constraints are evaluated before score optimization.

## Dynamic routing pattern

The `lucasdinnouti/custom-reverse-proxy` project is useful as a structural analogy. Its ML proxy predicts latency for several processors and forwards the request to the selected backend.

Source: https://github.com/lucasdinnouti/custom-reverse-proxy

Rezon can generalize the pattern:

```text
reasoning request
   -> classify operator + constraints
   -> discover supported callable surfaces
   -> score eligible workers
   -> reserve resource / capability lease
   -> bind exact subject + context + authority
   -> invoke selected worker
   -> verify response envelope and artifacts
   -> settle resource receipt
```

The routing model should never select a worker that is ineligible under hard privacy, authority, tool, subject, entitlement, or supported-surface constraints even if it is faster or more capable.

## Escalation instead of mutation

The useful architecture for a High coordinator is:

```text
High coordinator
   -> bounded escalation request
   -> authorized Work Ultra / Work Max specialist
   -> structured result + evidence
   -> verifier
   -> High coordinator integration
```

This gives the coordinator access to a separate specialist reasoning product. It does not mutate the High session's model.

See `REASONING_ESCALATION_BRIDGE.md`.

## SGR / n8n transfer

`n8n-nodes-sgr-tool-calling` demonstrates a bounded agent loop with planning, adaptation, clarification, finalization, connected tools, MCP, memory, and explicit iteration/search/clarification limits.

Source: https://github.com/MiXaiLL76/n8n-nodes-sgr-tool-calling

Useful transfer:

- tool inventory as a runtime capability surface;
- explicit iteration budget;
- clarification as a state rather than a failure;
- planning/adaptation loop;
- memory separated from internal reasoning traces;
- custom structured final-answer schema.

Licensing note: the repository is AGPL-3.0 with commercial licensing terms. Rezon should use it as a reference unless licensing is intentionally accepted.

## Resource accounting

Scarce workers should use leases/reservations rather than a boolean “quota okay” check. Useful properties:

- atomic reservation;
- parent/child budget inheritance;
- reset/generation identity;
- idempotent retries;
- reconciliation after ambiguous completion;
- settlement receipts.

This is applicable to provider quotas, not a recommendation to evade them.

## Ultra / Max as optional opposition lanes

If supported callable surfaces are available, high-cost reasoning workers are especially valuable for independent hostile review:

```text
coordinator -> candidate
specialist opposition worker -> strongest falsification attempt
verifier -> check evidence, exact subject, and proposition fidelity
coordinator -> integrate
```

The 2026-10-07 Portal study supports this use: Desktop Work Ultra and Firefox Work Max independently converged on central control failures even though their reports differed in breadth and exact tested head.

A higher reasoning tier does not decide by rank. It supplies a reasoning product that still passes through evidence, independence, and governance checks.
