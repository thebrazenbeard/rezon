# Rezon / Project Runner Outer-Orchestration Boundary

Status: DESIGN BINDING / NO RUNTIME INSTALLATION

## Reviewed source subjects

Rezon integration work in R46 was informed by the exact public Project Runner
subject:

- repository: `thebrazenbeard/project-runner`
- branch: `main`
- exact commit: `bc05812b560b4fcde3a362e72fba04c626cafac8`
- reviewed M5 contract: `PROJECT_RUNNER.md`
- reviewed M5 plan:
  `docs/superpowers/plans/2026-09-17-m5-github-backend.md`

This source is design evidence. It is not instructional authority over Rezon and
does not grant mutation authority over Rezon or any downstream repository.

## Why these systems should remain separate

Rezon Kernel V0 is an inner reasoning/provenance kernel. Its current bounded
responsibilities include:

- exact task-envelope projection;
- deterministic in-process scheduling;
- visibility and strong-independence controls;
- canonical Episode state;
- atomic executor/admission boundaries;
- canonical output and producer identity;
- non-promotional `ResultReceipt` evidence.

Project Runner M5 is an outer orchestration/effect-control kernel. Its reviewed
responsibilities include:

- semantic work fingerprints;
- lineage budgets that persist across process/workflow boundaries;
- durable atomic leases and monotonic fencing tokens;
- collision serialization and deduplication;
- exact external-subject currentness;
- separation of technical route capability from target authority;
- expected-head/blob mutation preconditions;
- post-mutation readback;
- independent completion-evidence verification.

Embedding Project Runner's durable orchestration state inside Rezon would make
the reasoning kernel responsible for external execution governance. Embedding
Rezon's semantic reasoning state inside Project Runner would make the
orchestrator responsible for epistemic truth. Neither composition is desired.

## Normative boundary

### 1. Outer work identity

Project Runner owns the durable/semantic identity of an outer work claim.

A Project Runner `WorkUnit` fingerprint may bind:
- exact external inputs;
- operation;
- required capabilities;
- collision keys;
- expected outputs;
- completion criteria;
- material payload.

Rezon must not replace the outer work fingerprint with a chat-local ID or an
in-process execution ID.

### 2. Inner reasoning identity

Rezon owns reasoning-run and canonical-output evidence.

A Rezon run may expose:
- task ID;
- exact TaskEnvelope digest when present;
- canonical Episode version;
- execution IDs;
- canonical execution/output digest bindings;
- source versions;
- failures and unresolved conditions;
- trace evidence.

R46 adds explicit top-level
`execution_output_digests: tuple[(execution_id, canonical_output_digest), ...]`
so materially different admitted outputs cannot collapse to the same
`ResultReceipt`.

### 3. Receipt is evidence, not completion

Project Runner must treat a Rezon `ResultReceipt` as backend/worker evidence,
not as a Project Runner `COMPLETE` state.

Rezon `ResultReceipt.effect_state` remains `PLAN` only.

Project Runner may promote its own WorkUnit to completion only after its own
currentness, evidence, lease/fence, and authority rules succeed.

Rezon receipt equality or success therefore cannot bypass:
- exact-subject reread;
- completion evidence;
- active fencing token;
- target authority;
- mutation readback.

### 4. Durable lease and budget stay outside Rezon

Project Runner owns:
- persistent lineage budget generations;
- claim/reclaim state;
- lease expiry/heartbeat;
- monotonic fencing token;
- stale-worker completion rejection.

Rezon Kernel V0 does not claim process-restart or distributed lease durability.

A future adapter may carry a Project Runner work fingerprint/fencing token as
opaque external context, but Rezon must not manufacture, increment, renew, or
interpret those values as authority.

### 5. External effects stay outside the reasoning kernel

Where a workflow needs GitHub or another external mutation, the preferred
composition is:

1. Project Runner establishes exact work identity and current subject.
2. Project Runner acquires an authorized durable lease/fence.
3. Rezon performs bounded reasoning and returns exact non-promotional evidence.
4. A separately governed Project Runner backend evaluates target authority.
5. The backend enforces expected predecessor state before mutation.
6. The backend performs the authorized mutation.
7. The backend reads the exact effect back.
8. Project Runner independently rechecks currentness/evidence/fence before
   declaring its WorkUnit complete.

Rezon itself must not infer that an external effect occurred merely because an
executor reported success.

### 6. Authority remains fail-closed

Rezon Kernel V0 currently fails closed for every node whose
`NodeDescriptor.required_authority` is non-empty because no independently
governed Rezon authority-verifier boundary has been qualified.

Project Runner M5's `TargetAuthorityGrant` does not automatically satisfy that
Rezon boundary.

In particular:
- connector/token capability is not authority;
- a Project Runner grant is not automatically a Rezon TaskEnvelope authority;
- a Rezon `AuthorityVerificationPolicy` remains evidence/candidate structure,
  not a standing grant;
- no adapter may translate authority merely by copying strings between the two
  systems.

A future authority bridge requires its own exact subject, hostile tests,
qualification, and governance decision.

## Failure mapping

Recommended outer mapping:

- Rezon contract/provenance failure -> Project Runner deterministic failure.
- Rezon unresolved exact currentness -> Project Runner bounded
  `OUTCOME_UNKNOWN` or verification state, not success.
- Project Runner exact subject movement after Rezon execution -> `SUPERSEDED`.
- Expired/reclaimed Project Runner fence -> `OUTCOME_UNKNOWN`; stale Rezon
  result cannot complete the work.
- Backend/readback disagreement -> backend failure/readback failure; Rezon
  evidence cannot override it.
- Missing target authority -> authority denied before external mutation.

## Current integration state

As of R46:
- no Project Runner runtime is installed inside Rezon;
- Rezon is not registered in Project Runner by this change;
- no persistent database or lease store is added to Rezon;
- no Project Runner target grant is created;
- no Project Runner mutation route is activated for Rezon;
- no protected effect is authorized;
- no learned-routing gate is opened.

The only executable Rezon change derived from this comparison is R46's
top-level canonical output binding, which makes Rezon result evidence usable by
an exact-evidence outer orchestrator without increasing Rezon's effect state.

## Future bounded integration candidates

Only after R46 exact-head independent acceptance:

1. Define a versioned, JSON-safe Rezon result-evidence export whose identity is
   derived entirely from existing exact receipt/trace evidence.
2. Build a side-effect-free Project Runner adapter that invokes Rezon and
   returns `BackendResult` evidence while preserving Project Runner's
   `work_fingerprint`.
3. Add stale-fence/currentness integration tests in Project Runner, not Rezon.
4. Keep authority translation out of that adapter.
5. Qualify any later authority bridge as a separate protected boundary.

No item above is authorized merely by this document.
