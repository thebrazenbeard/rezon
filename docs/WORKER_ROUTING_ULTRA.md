# Worker Routing and Ultra

## Principle

A more capable or more expensive worker should be treated as a specialized computational resource, not as an authority source and not as the architecture itself.

Rezon should therefore support runtime-discovered worker capabilities and route tasks according to task semantics, resource constraints, and expected information gain.

## Ultra / Work discovery status

A Vera/Work experiment observed a GPT-5.6 Sol Max configuration and an execution trace reporting that an internal GPT-5.6 Sol Ultra worker had been instantiated. The important limitation is that no stable, transferable invocation descriptor was recovered before Work quota exhaustion.

Therefore the current defensible claim is:

> Work can apparently internally delegate to an Ultra worker under some conditions.

Not:

> ordinary Sol chats have a supported reusable Ultra connector.

Rezon must not depend on an unverified internal provider mechanism.

## Routing abstraction

```text
WorkerDescriptor {
  worker_id
  operator_types[]
  provider
  model
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

The `authority_ceiling` is explicit because capability must not be confused with permission.

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
- privacy constraints;
- reproducibility requirements;
- whether a deterministic worker can solve the task more reliably than an LLM.

## Dynamic routing pattern

The `lucasdinnouti/custom-reverse-proxy` project is useful as a structural analogy. Its ML proxy predicts latency for several processors and forwards the request to the selected backend.

Source: https://github.com/lucasdinnouti/custom-reverse-proxy

Rezon can generalize the pattern:

```text
reasoning request
   -> classify operator + constraints
   -> score eligible workers
   -> reserve resource / capability lease
   -> invoke selected worker
   -> verify response envelope
   -> settle resource receipt
```

The routing model should never select a worker that is ineligible under hard privacy, authority, tool, or subject constraints even if it is faster.

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

## Ultra as optional opposition lane

If a stable Ultra callable is eventually discovered, a particularly valuable use is independent hostile review:

```text
Sol coordinator -> candidate
Ultra opposition worker -> strongest falsification attempt
Verifier -> check evidence and proposition fidelity
Sol coordinator -> integrate
```

Ultra does not decide by rank. It supplies a high-cost independent reasoning product that still passes through evidence and governance checks.
