# Rezon Kernel V0 R11 Strong-Independent Task-Spec Boundary

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R11 is the bounded successor to the failed R10 executor-envelope projection. It replaces the reused full `TaskEnvelope` executor surface with a dedicated task-specification boundary and then closes two additional audit-metadata channels found by self-hostile testing before final review freeze.

## Exact ancestry

- repository: `thebrazenbeard/rezon`
- failed R10 subject: `bfcd54e197b06104481df576afb11f3559b6e55b`
- failed R10 tree: `7c9ef5e34ab5128441903f194b484f6d7d55d80d`
- R11 branch: `work/rezon-kernel-v0-r11-task-spec-boundary`
- R11 task-ID RED1: `7138eea794f3adac5591c9168dbb2394e2bf0244`
- R11 first executable repair: `4424837555c1c873ec141b43dd7a9ee08555885d`
- R11 executor-metadata RED2: `b47bb8715580c43c8553b39737f2ef3272c926e5`
- R11 executable GREEN: `c9e0b5941f8c64149d86ce861d96dc076b2d8326`
- executable GREEN tree: `e75ede61c2c3a3b910e88273c8760cb1e815b992`
- CI-enablement head: `e391f961be8e1ce60ffd1458e3f3c549d064f904`

## Why R10 failed

R10 removed authority/privacy/budget/context fields from the executor-facing TaskEnvelope, but it reused the TaskEnvelope type and preserved the original `task_id`.

A fresh exact-head self-hostile probe used:

`task_id="peer-answer:H4"`

The independent worker copied `view.task_envelope.task_id` into a hypothesis. R10 returned no failures, marked independence demonstrated, and admitted the leaked value.

Therefore R10's projection remained an answer-bearing runner-metadata channel.

## RED1 — original task ID remains visible

R11 froze the task-ID bypass before production repair:

- test: `tests/test_r11_task_spec_boundary.py`
- exact test-only head: `7138eea794f3adac5591c9168dbb2394e2bf0244`

Clean CPython 3.12 targeted result:

`1 failed / 1 passed`

The failure proved that a strong-independent worker could still observe the original task ID. The passing control proved that literal request, subject references, and constraints remained usable task content.

## R11 structural repair

R11 introduces `TaskSpecification` with only:

- `literal_request`
- `subject_refs`
- `constraints`

`TaskEnvelope.to_task_specification()` creates the exact task-defining projection.

`ExecutionView` now carries both audit-side fields:

- `task_envelope: TaskEnvelope | None`
- `task_specification: TaskSpecification | None`

For a strong `independence_required` executor:

- `view.task_envelope is None`;
- `view.task_specification` is present when a TaskEnvelope was supplied;
- the task specification has no `task_id`, `available_authority`, `privacy_scope`, `resource_budget`, or `context_refs` attributes.

For a non-independent executor, the full TaskEnvelope remains available.

The trace now binds:

- the exact original full TaskEnvelope digest; and
- the exact executor-visible TaskSpecification digest.

Preflight failures also bind the task-specification digest.

## RED2 — execution identity and independence attestation still leak

Self-hostile testing of the first R11 executable repair `44248375…` found two remaining audit channels:

1. strong-independent `view.execution_id` still used `<task_id>:exec:<n>:<node_id>`;
2. `view.independence` exposed audit-side executor/model/provider/prompt/context lineage to the worker.

The probe used:

- task ID `peer-answer:H4`;
- prompt lineage `peer-answer:H5`;
- context lineage `peer-answer:H6`.

R11 admitted a hypothesis containing all three while reporting `independence_demonstrated=True`.

That bypass was frozen at:

- test: `tests/test_r11_executor_metadata_projection.py`
- exact RED2 head: `b47bb8715580c43c8553b39737f2ef3272c926e5`
- targeted result: **1 failed / 0 passed**

## R11 second repair — executor metadata isolation

For strong independence:

- runner-issued execution IDs are now `independent:exec:<n>:<node_id>`, not derived from TaskEnvelope task ID;
- executor-facing `view.independence` is reset to empty `IndependenceMetadata()`;
- the full independence attestation and verification policy remain runner/audit-side and still control preflight;
- canonical admission still requires every emitted proposition/relation and ExecutionResult to bind to the exact runner-issued execution ID.

Non-independent execution retains the existing task-derived execution-ID behavior and full audit metadata semantics.

## Preserved R9/R10 controls

R11 retains and updates the predecessor tests so that:

- non-empty `context_refs` still fail closed for strong independence before worker execution;
- literal request / subject refs / constraints remain available through TaskSpecification;
- authority/privacy/budget are structurally absent from the strong-independent executor surface;
- non-independent workers retain the full TaskEnvelope;
- trace records both the full TaskEnvelope digest and task-specification digest.

## Exact executable qualification

Fresh clean clone of exact executable head `c9e0b5941f8c64149d86ce861d96dc076b2d8326` under CPython 3.12:

- pytest: **118 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS

Focused R9-R11 isolation controls before push:

- **7/7 PASS**

## Hosted qualification

R11 was added to the existing `Rezon kernel tests` push workflow without changing test commands.

Hosted GitHub Actions on CI-enablement head `e391f961be8e1ce60ffd1458e3f3c549d064f904`:

- run: `35393325145`
- event: push
- install: PASS
- compile: PASS
- test: PASS
- diff-check: PASS
- overall: **success**

## Explicit trust boundaries / non-claims

R11 does not establish:

- independent hostile PASS on the final R11 subject;
- a qualified shared-context/shared-read independence class;
- mechanical proof that `literal_request`, `subject_refs`, or `constraints` are free of answer-bearing or adversarial task content;
- semantic observation of an arbitrary executor's cognition;
- cryptographic model/provider/executor identity;
- a usable positive protected-authority path;
- merge authority;
- deployment, installation, activation, provider/model mutation, or runtime effect;
- learned-routing qualification;
- reasoning superiority.

R11 treats Kernel Episode identity/version as an internal opaque kernel identifier boundary. This qualification does not authorize encoding semantic task content into internal episode identifiers and does not claim a proof against arbitrary steganography in trusted identifiers.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh independent hostile rereview.

No merge is requested by this record.
