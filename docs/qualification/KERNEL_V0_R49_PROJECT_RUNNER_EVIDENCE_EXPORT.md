# Rezon Kernel V0 R49 Project Runner Evidence Export

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R49 is the bounded successor to current Rezon R48 integration subject
`e5af543b6306ee41c88b9b5419ca6653f787be24`.

R49 adds a side-effect-free interoperability surface for outer orchestrators
such as Project Runner. It does not install Project Runner, register Rezon
there, grant authority, or perform external effects.

## Motivation

The reviewed Project Runner M5/M6 model treats backend/worker output as evidence
that still requires outer exact-subject currentness, lease/fence validity,
target authority, and independent completion verification.

R47/R48 already provide top-level Rezon receipt bindings for:
- execution -> canonical output digest;
- execution -> canonical producer execution ID.

R49 makes those bounded results transportable as deterministic JSON-safe
evidence without requiring a Project Runner adapter to reach into Python trace
objects.

## Frozen RED

Regression file:
`tests/test_r49_project_runner_evidence_export.py`

Exact RED:
`d1c864b5f9ea50f24e48df6f56c9dfd6fa152ea3`

On exact R48 the test module fails at collection because no
`rezon.interop` evidence surface exists.

## Implementation

Implementation:
`8715a1924548e61d9b84ef617f3fe5115676ddc7`

CI-enablement head:
`f31e3a928993c243a6a541814cccbff677bf674c`

R49 adds:
- schema ID `rezon.run-evidence.v1`;
- `export_run_evidence(outcome)`;
- `RunEvidenceError`;
- deterministic SHA-256 `evidence_digest` over the canonical JSON body.

The export contains:
- stable receipt fields;
- stable trace execution fields;
- canonical snapshot/output/producer identities;
- source/ref/version evidence;
- failure states;
- no duration/timing field.

It remains JSON-safe and deterministic for the same concrete reasoning event.

## Self-validation boundary

Before export, R49 requires exact:
- `RunOutcome`;
- `ResultReceipt`;
- `ExecutionTrace`;
- `TraceRecord` values.

It then requires:
1. receipt execution IDs exactly equal trace execution IDs in order;
2. receipt execution/output bindings exactly equal the trace-derived bindings;
3. receipt execution/producer bindings exactly equal the trace-derived bindings;
4. each trace task-envelope digest equals the receipt task-envelope digest;
5. each present canonical producer ID recomputes from:
   - node ID;
   - canonical Episode snapshot digest;
   - executor task-specification digest / no-task-spec marker;
   - canonical output digest.

Forged receipt output bindings, forged producer bindings, and missing receipt
execution coverage are rejected before evidence emission.

## Non-promotional boundary

The export accepts `ResultReceipt.effect_state == PLAN` only.

It performs:
- no filesystem I/O;
- no network I/O;
- no database work;
- no leases/fencing;
- no target-authority translation;
- no mutation/readback;
- no lifecycle/effect promotion.

Project Runner or any other consumer must continue to apply its own currentness,
authority, fencing, readback, and completion rules.

## Important trust ceiling

R49 provides deterministic structural evidence and receipt/trace consistency.

It is **not** a cryptographic signature or independent attestation.

A caller able to manually construct an entire internally consistent exact
`RunOutcome` can still construct internally consistent exportable evidence.
R49 does not authenticate the origin of Python objects or independently
recompute canonical output digests from external output payloads that are not
contained in `RunOutcome`.

Therefore the export is suitable as backend/worker evidence, not standing
completion truth or authority.

## Qualification

Fresh detached-checkout qualification at
`f31e3a928993c243a6a541814cccbff677bf674c`:
- R49 regressions: **6/6 PASS**;
- focused R16-R49 controls: **142/142 PASS**;
- recent R40-R49 slice: **27/27 PASS**;
- full suite: **271/271 PASS**;
- compileall: PASS;
- git diff --check: PASS.

Hosted GitHub Actions:
- run `35474286246`;
- exact head `f31e3a928993c243a6a541814cccbff677bf674c`;
- job `105980730198`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Source relationship

R49 is based on exact current R48:
`e5af543b6306ee41c88b9b5419ca6653f787be24`

R48 already composes:
- R47 receipt -> canonical producer identity binding; and
- non-empty canonical/nested producer execution identities.

R49 does not replace or reinterpret those controls.

## Remaining gates

1. Requalify the exact documentation head locally and hosted.
2. Run accepted Benchmark R4 local-only no-commit composition.
3. Obtain fresh exact-head independent hostile rereview.
4. Keep Issue #5 learned-routing CLOSED.
5. Do not merge or install without Patrick's explicit authority.
