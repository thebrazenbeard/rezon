# Portable Assurance Layer

## Position

Rezon should not compete with general agent orchestration frameworks for handoffs,
tool calling, sessions, workflow hosting, or provider-specific model loops.

Its strongest current asset is narrower: a provider-independent epistemic kernel
that can make reasoning runs inspectable and fail closed when provenance,
currentness, independence, failure reporting, or authority boundaries do not bind.

## V1 integration surface

A Rezon run can be exported as deterministic rezon.run-evidence.v1 JSON.
The portable verifier validates that artifact without rerunning the reasoning job.

    rezon verify-evidence run-evidence.json

Verification covers:

- canonical body digest integrity;
- exact receipt-to-trace execution coverage;
- source-version ordered binding;
- trace-failure visibility in the receipt;
- output-digest binding;
- canonical producer identity recomputation;
- task-envelope digest consistency;
- the non-promotional PLAN ceiling.

A valid artifact proves internal structural consistency of that Rezon evidence
artifact. It does not prove semantic truth, source authenticity outside the
recorded bindings, external authority, deployment state, or reasoning superiority.

## Integration direction

External runtimes should remain responsible for orchestration and execution.
Adapters can translate their completed runs into governed Rezon inputs, then retain
Rezon run evidence as an audit artifact alongside native traces.

High-value adapter targets include agent SDK traces, workflow runtimes, MCP tool
activity, and A2A task exchanges. Each adapter must preserve source identity,
version/currentness, executor lineage, tool/effect receipts, and authority data
rather than flattening them into generic text.

## Next executable frontier

1. Define an adapter protocol for external execution events.
2. Implement one dependency-optional reference adapter.
3. Add cross-runtime fixture tests proving that correlated workers, stale evidence,
   concealed failures, and authority laundering remain detectable.
4. Benchmark the assurance layer against simpler trace-only acceptance baselines.
