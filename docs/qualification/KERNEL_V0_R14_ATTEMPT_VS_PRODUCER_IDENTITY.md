# Rezon Kernel V0 R14 Attempt / Canonical Producer Identity Split

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R14 is the bounded successor to failed R13 exact subject `9ff7d5c025fec8a69b22640394e03fbbe3304409`.

R13 correctly made strong-independent execution attempts opaque and unique with UUID4, but it stored that random attempt ID directly in canonical proposition/relation provenance. That made otherwise identical deterministic runs produce different canonical episode snapshots, conflicting with the Kernel V0 design statement that canonical episode state is explicit and deterministic.

## Exact ancestry

- failed R13 review head: `9ff7d5c025fec8a69b22640394e03fbbe3304409`
- failed R13 tree: `3218bbe5a58424c495f65f100a856744897f15f4`
- R14 branch: `work/rezon-kernel-v0-r14-attempt-vs-producer-identity`
- R14 RED: `48894d5be8d3694dc9817d5afcfa2f022ce9f106`
- executable GREEN: `c24fa63817be21cfd7ad0ce96658cca6253e0b15`
- executable GREEN tree: `52ef5683dce9bcc3432b9af100802b020bf6bdcc`
- CI-enablement head: `ee367bee10a52eb168860418fab622631424e4d4`

## R13 failure — random attempt identity contaminated canonical state

Fresh exact-R13 determinism probe used:

- two fresh Episodes with the same episode ID;
- the same TaskEnvelope;
- the same strong-independent node and policy;
- a deterministic executor emitting the same proposition ID/kind/content/source state.

Only R13's UUID-backed worker execution attempt ID differed.

Observed:

- `EXEC_IDS_EQUAL=False`
- `SNAPSHOTS_EQUAL=False`
- `EVENTS_EQUAL=True`
- `SEMANTIC_FIELDS_EQUAL=True`

The only canonical proposition difference was `producer_execution_id`, which carried the random worker attempt UUID.

That contradicts the Kernel V0 design requirement:

`The canonical episode state is explicit and deterministic.`

## Frozen RED

R14 froze the identity split before production repair:

- test: `tests/test_r14_attempt_vs_producer_identity.py`
- exact test-only head: `48894d5be8d3694dc9817d5afcfa2f022ce9f106`
- targeted result: **2 failed / 0 passed**

RED requirements:

1. two fresh deterministic runs may have different opaque attempt IDs but must produce equal canonical EpisodeSnapshot objects;
2. canonical producer identity must be trace-visible and separate from attempt identity;
3. repeated actual executions in one episode must still receive distinct canonical producer identities.

## R14 identity model

R14 explicitly separates two identities.

### 1. Attempt execution identity

Worker/executor-facing identity remains the R13 UUID-backed token:

`independent:exec:<node_id>:<uuid4-hex>`

Properties:

- unique per actual strong-independent execution attempt;
- opaque;
- not derived from task ID;
- not derived from canonical episode event count;
- not derived from execution ordinal;
- not the TaskSpecification digest;
- used to validate ExecutionResult identity;
- worker-emitted proposition/relation producer IDs must exactly equal this attempt ID before admission.

### 2. Canonical producer execution identity

Durable canonical provenance is now runner-derived deterministically from:

- node ID;
- exact pre-execution canonical episode version;
- exact allowed TaskSpecification digest (or explicit no-task-spec marker).

The canonical ID is:

`canonical:exec:<node_id>:<sha256(node_id || episode_version || task_spec_digest)>`

This identity is never used as the worker-facing execution request ID.

It is computed from canonical/audit-side state and therefore may incorporate canonical history without leaking that history to the strong-independent executor.

## Admission boundary

R14 does NOT trust a worker-provided canonical producer ID.

Admission proceeds in two stages:

1. validate the worker result and every emitted proposition/relation against the exact runner-issued opaque attempt ID;
2. only after all existing identity/source/output-kind checks pass, create admitted copies whose `producer_execution_id` is rewritten to the deterministic canonical producer ID.

Therefore:
- forged attempt identity still fails;
- forged proposition/relation producer attempt identity still fails;
- worker cannot directly choose durable canonical producer provenance;
- canonical state no longer inherits UUID randomness.

## Trace binding

`TraceRecord` now records both:

- `execution_id` — opaque actual attempt identity;
- `canonical_producer_execution_id` — deterministic durable producer provenance identity.

Normal, exception, and preflight trace paths bind the canonical producer identity calculated from the exact audit-side input state.

This makes the attempt-to-canonical mapping inspectable without exposing canonical-history information to the worker.

## R13 predecessor regression update

The R13 uniqueness test now preserves the intended semantics:

- separate actual strong-independent executions must have distinct opaque attempt IDs;
- their canonical producer IDs must also be distinct when the canonical pre-execution episode versions differ;
- canonical proposition producer provenance must equal the trace's canonical producer ID, not the attempt UUID.

## Determinism result

R14 targeted controls prove:

- fresh deterministic runs with different attempt UUIDs produce equal canonical EpisodeSnapshot objects;
- repeated executions in one episode receive distinct canonical producer IDs because the canonical pre-execution episode version changes;
- attempt IDs remain distinct and opaque.

## Exact executable qualification

Fresh clean checkout of exact executable head `c24fa63817be21cfd7ad0ce96658cca6253e0b15` under CPython 3.12:

- pytest: **126 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS

Focused R12-R14 identity/isolation controls before push:

- **8/8 PASS**

Additional inherited hostile identity checks:

- forged runner execution identity / provenance: PASS
- exact producer execution provenance enforcement: PASS

## Hosted qualification

R14 was added to the existing `Rezon kernel tests` workflow without changing its commands.

Hosted GitHub Actions on CI-enablement head `ee367bee10a52eb168860418fab622631424e4d4`:

- run: `35404488301`
- install: PASS
- compile: PASS
- test: PASS
- diff-check: PASS
- overall: **success**

## Preserved R9-R13 controls

R14 retains:

- context_refs fail closed for strong independence;
- full TaskEnvelope absent from strong-independent executor;
- TaskSpecification-only task content;
- task ID / authority / privacy / budget / context structurally absent from executor task spec;
- executor-facing independence metadata empty;
- complete independence attestation runner/audit-side;
- executor episode-version marker remains `independent@0`;
- canonical episode version stays audit-side;
- opaque unique attempt UUID per actual strong-independent attempt;
- prior-history leakage tests pass with controlled UUID source;
- worker cannot self-select durable canonical producer identity.

## Explicit trust boundaries / non-claims

R14 does not establish:

- independent hostile PASS on the final R14 subject;
- cryptographic executor/model/provider identity;
- cryptographic authentication of canonical producer IDs;
- a globally unique canonical producer ID across unrelated repositories/systems;
- semantic proof that TaskSpecification content itself is non-adversarial;
- protection against a malicious trusted orchestrator choosing false canonical episode state;
- merge authority;
- deployment, installation, activation, runtime effect, provider/model mutation, or learned-routing qualification;
- reasoning superiority.

The canonical producer ID is deterministic provenance, not authorization, truth, or evidence.

The opaque attempt UUID is execution-instance identity, not durable epistemic truth.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
