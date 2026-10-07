# Reasoning Escalation Bridge

## Goal

Rezon should support a coordinator that remains on one reasoning surface while delegating bounded specialist work to a different, explicitly authorized reasoning surface.

The motivating case is:

```text
High Chat coordinator
    |
    v
Rezon escalation request
    |
    +--> Work Ultra specialist
    |
    +--> Work Max independent reviewer
    |
    v
verified artifacts / receipts
    |
    v
High Chat integrator
```

This does not convert High into Ultra or Max. It gives the coordinator access to separate higher-cost reasoning products through supported callable surfaces.

## Non-goals

The bridge must not:

- spoof product entitlements;
- forge model/reasoning flags;
- replay credentials to impersonate another surface;
- infer a reasoning tier from process or network fanout;
- treat more sockets as more intelligence;
- bypass provider quotas or governance;
- promote a specialist's answer directly into operational authority.

## EscalationRequest

A minimal request should carry:

```text
EscalationRequest {
  request_id
  parent_task_id
  literal_task
  subject_refs[]
  exact_subject_versions[]
  context_manifest[]
  requested_operator_types[]
  requested_reasoning_class?
  preferred_surfaces[]?
  required_tools[]
  independence_requirement
  privacy_scope
  resource_budget
  authority_ceiling
  deadline?
}
```

`requested_reasoning_class` is a requirement such as `HIGH_COST_HOSTILE_REVIEW`, not a fabricated provider entitlement. An adapter may map that requirement only onto surfaces the runtime can actually discover and invoke.

## WorkerObservation

A runtime-discovered worker should expose observed facts separately from inferred capability:

```text
WorkerObservation {
  worker_id
  provider
  product_surface
  model_label?
  reasoning_label?
  callable_surface
  tool_capabilities[]
  availability
  observed_runtime_version?
  observed_process_topology?
  observed_transport_summary?
  evidence_class
  observed_at
  expires_at?
}
```

Process/socket topology is diagnostic metadata. It does not establish model identity or reasoning authority.

## Escalation lifecycle

```text
REQUESTED
  -> ELIGIBILITY_CHECKED
  -> RESOURCE_RESERVED
  -> DISPATCH_BOUND
  -> RUNNING
  -> COMPLETED | FAILED | ATTEMPTED_UNKNOWN
  -> RESULT_VERIFIED
  -> INTEGRATED | REJECTED | UNRESOLVED
  -> SETTLED
```

A STOP/HOLD that becomes current before a new effect boundary must prevent further execution. Rezon should explicitly test this lifecycle against the control failures reproduced in the 2026-10-07 Portal study.

## Dispatch binding

Before invocation, bind a dispatch to:

- exact task text or canonical digest;
- exact repository/file/source versions;
- worker/surface observation;
- tool and environment requirements;
- context manifest;
- resource reservation;
- authority ceiling;
- attempt identity.

Changing any semantic input that matters to correctness should require a new dispatch identity or an explicit supersession record.

## Return artifact

A specialist should return a structured result rather than only prose:

```text
EscalationResult {
  request_id
  dispatch_id
  worker_observation_ref
  started_at
  completed_at
  artifacts[]
  claims[]
  evidence_refs[]
  tests_or_checks[]
  unresolved[]
  failure_state?
  execution_receipt
}
```

## Independence

For independent review, record whether two specialists share:

- provider;
- model family;
- product surface;
- prompt lineage;
- context package;
- retrieved sources;
- prior candidate answer;
- tool outputs;
- execution environment.

Different labels are not sufficient proof of independence.

## Routing policy

The first router should be conservative and inspectable.

Examples:

- deterministic parsing/calculation -> deterministic worker;
- ordinary synthesis -> coordinator/current worker;
- broad repository exploration or parallel adversarial testing -> Work-style specialist when available;
- difficult hostile review -> high-cost specialist;
- safety-critical or high-impact conclusion -> independent specialist review plus verifier;
- unavailable specialist -> remain explicit `UNAVAILABLE` or continue under a downgraded plan with a receipt stating the loss of capability.

## Verification before integration

The coordinator must not accept a specialist result merely because it came from a higher reasoning tier.

Verification can include:

- exact-head/source-currentness checks;
- artifact hash validation;
- rerunning deterministic tests;
- proposition-fidelity review;
- contradictory evidence search;
- cross-specialist comparison;
- authority/effect-state checks.

## Empirical basis

The 2026-10-07 same-prompt study found that Desktop Work Ultra had substantial local MXC and Codex connection fanout while Desktop High did not, and that Ultra and Max independently converged on central Portal control defects.

The correct architectural transfer is therefore:

> use stronger reasoning surfaces as explicit specialist workers with receipts and verification.

Not:

> reproduce their local connection pattern to upgrade another chat.
