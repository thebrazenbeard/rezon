# Rezon Kernel V0 R17 Task-Bound Production Identity

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R17 is the bounded successor to failed R16 exact subject `f1dd71fb32afd8dc0a3391caa3661dab39ae3131`.

R16 successfully moved durable producer derivation into admission and bound producer identity to canonical input-state plus canonical output. A fresh hostile probe then showed that two different executor-visible TaskSpecifications could still collapse to one durable producer ID when state and output matched. R17 restores task specification as an explicit causal input while preserving admission ownership of provenance.

## Exact ancestry

- failed R16 review head: `f1dd71fb32afd8dc0a3391caa3661dab39ae3131`
- failed R16 tree: `fe73a6a4d73de2c00b74f86e8e5f9344604ebee4`
- R17 branch: `work/rezon-kernel-v0-r17-task-bound-production-identity`
- R17 RED: `da69c0386855653ffa704cd2d87b18699adf79a7`
- executable repair: `b82503294341738b4b0dc7df352f31bd482c3bbc`
- executable tree: `e6673bac9f38612a279ceb6efccd03f06fe3656c`
- CI-enablement head: `359da34aa588726c6e237187b54571bd9c8ec4bd`

## R16 failure — cross-task producer collision

Fresh exact-R16 hostile execution used:

- same episode ID;
- same empty canonical Episode state;
- same node/executor lineage;
- different literal requests, therefore different executor-visible TaskSpecification digests;
- deterministic identical durable proposition output.

Observed:

- task-specification digests differed;
- canonical input-state digests matched;
- canonical output digests matched;
- canonical producer IDs were identical;
- both executions succeeded.

Task digests:

- A: `aef4481f9b9d85ac26bad6e2d5717bc6db62653517bf8ee4d7e14c8d0d92378e`
- B: `33fbe4cec1e548f34ae297ab2267107098f2fc25ebc269b270b49ee7f630f505`

Shared R16 producer:

`canonical:exec:echo_hypothesis:716ccd9444e8f322c37eafd1c6cb2cac0ca80731fe5570d49539b081b5ddaabe`

TaskSpecification is executor-visible causal input. Different tasks must not silently share a durable production-event identity merely because state and output match.

## Frozen RED

R17 froze the failure before production repair:

- test: `tests/test_r17_task_bound_production_identity.py`
- exact test-only head: `da69c0386855653ffa704cd2d87b18699adf79a7`
- targeted result: **1 failed / 1 passed**

The failing case required different TaskSpecifications to produce different durable producer IDs.

The passing control already established that the same task + same state + same output must remain deterministic across different opaque attempt UUIDs.

## R17 repair

R17 preserves admission ownership of durable producer identity.

The runner passes the structured executor-visible `TaskSpecification` object to admission.

Admission computes:

`task_specification_digest = task_specification.digest`

internally rather than accepting a raw caller-selected digest or canonical producer ID.

Canonical producer identity now derives from:

- validated node ID;
- exact canonical pre-admission EpisodeSnapshot digest;
- internally computed TaskSpecification digest, or explicit `no-task-spec`;
- canonical output digest.

Format remains:

`canonical:exec:<node_id>:<sha256(...)>`

The opaque actual attempt identity remains independent and UUID-backed.

## AdmissionReceipt

AdmissionReceipt now additionally returns:

`task_specification_digest`

alongside:

- canonical episode snapshot digest;
- canonical output digest;
- canonical producer execution ID.

This allows the mutation boundary's exact task binding to be read back rather than inferred.

## Trust boundary

Direct admission callers may omit TaskSpecification. Such calls are explicitly bound as:

`no-task-spec`

If a direct trusted local caller supplies a TaskSpecification, admission computes the digest from the structured object itself.

R17 does not claim cryptographic authenticity for that local object or protection against a malicious trusted process. It prevents reintroducing a raw caller-selected producer identity/digest shortcut.

## Qualification

Focused R15-R17/admission provenance controls after repair:

- **14/14 PASS**

Full local suite before push:

- **140/140 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact executable repair `b82503294341738b4b0dc7df352f31bd482c3bbc` under CPython 3.12:

- pytest: **140/140 PASS**
- compileall PASS
- diff-check PASS

Hosted CI-enablement head `359da34aa588726c6e237187b54571bd9c8ec4bd`:

- run `35408994021`
- overall: **SUCCESS**

## Preserved R16 controls

R17 retains:

- admission-owned durable producer derivation;
- exact opaque attempt provenance validation before canonical rewrite;
- stale-state / TOCTOU rejection;
- deterministic canonical EpisodeSnapshot digest;
- canonical output digest with random attempt producer IDs stripped;
- proposition and relation output coverage;
- no-output attempt -> no durable producer identity;
- failed result -> no durable producer identity or mutation;
- preflight/exception -> no durable producer identity;
- direct caller cannot choose canonical producer identity;
- same task/state/output replay determinism;
- different state changes producer identity;
- different output changes producer identity;
- different task now also changes producer identity.

## Explicit non-claims

R17 does not establish:

- fresh independent hostile PASS on the final R17 subject;
- cryptographic executor/model/provider identity;
- cryptographic authenticity of TaskSpecification;
- semantic truth of state/output/task content;
- cross-language canonicalization outside current Python 3.12 V0;
- SHA-256 collision impossibility;
- protection against a malicious trusted Python process;
- merge authority;
- deployment, installation, activation, runtime effect, training, provider/model mutation, or learned-routing qualification;
- reasoning superiority.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
