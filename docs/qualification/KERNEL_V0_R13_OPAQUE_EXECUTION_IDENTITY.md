# Rezon Kernel V0 R13 Opaque Execution Identity

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R13 is the bounded successor to failed R12 exact subject `663e3aa5fbb4f8ca2751a2c792a100303070ec35`. R12 successfully removed dynamic history from strong-independent executor-visible episode-version and execution-ordinal metadata, but its deterministic execution-ID replacement collapsed distinct actual executions onto one provenance identity.

## Exact ancestry

- failed R12 review head: `663e3aa5fbb4f8ca2751a2c792a100303070ec35`
- failed R12 tree: `d0364b00cd3728717788b2159ab4e64ec4724db1`
- R13 branch: `work/rezon-kernel-v0-r13-opaque-execution-identity`
- execution-identity RED: `02bacee12a8e2c04519beb1be8ffe275234c1581`
- executable GREEN: `46e1999448a9431cc13634b360acdbaec6dfb4b4`
- executable GREEN tree: `43905771818e37a56a819b30d1ab74ad11a9fa87`
- CI-enablement head: `5337ea39cae6610e1bcf60413e706301f31cbbb1`

## R12 failure — deterministic provenance collision

R12 generated strong-independent execution IDs from static node identity plus allowed TaskSpecification digest.

A fresh exact-R12 hostile probe ran the same strong-independent node twice as two genuinely separate executions with:

- the same EpisodeRunner;
- the same task specification;
- the same episode;
- distinct emitted proposition IDs/content per run.

Observed on exact R12:

- first run failures: empty;
- second run failures: empty;
- first execution ID == second execution ID;
- exact repeated ID:
  `independent:exec:echo_hypothesis:79a0066b1b79ca99f42ad7273d22b4d244c1b89ca4bb167959398dc4bfbf47a0`;
- audit episode versions differed (`opaque-collision@0`, then `opaque-collision@1`);
- two distinct admitted propositions carried the same `producer_execution_id`.

Thus R12 removed history leakage by making identity a pure function of allowed task content, but that made separate executions indistinguishable in provenance.

## Frozen RED

R13 froze the collision before production repair:

- test: `tests/test_r13_execution_identity_uniqueness.py`
- exact test-only head: `02bacee12a8e2c04519beb1be8ffe275234c1581`

Clean CPython 3.12 targeted result:

- **2 failed / 0 passed**

The REDs establish:
1. two distinct strong-independent runs must not share one execution ID;
2. strong-independent execution identity must not simply reuse the TaskSpecification digest as the provenance identifier.

## R13 repair

For strong-independent executions, the runner now issues:

`independent:exec:<node_id>:<uuid4-hex>`

Properties of this boundary:

- a fresh UUID4 value is generated for each actual execution;
- task ID is not included;
- canonical episode ID/version is not included;
- prior event count is not included;
- trace/execution ordinal is not included;
- TaskSpecification digest is not used as execution identity;
- executor, trace, ExecutionResult, admission, and emitted producer provenance continue to bind the same exact runner-issued ID.

R13 also updates the R12 history-leak regression so its UUID source is fixed under test. With randomness held constant, the no-prior-execution and prior-blinded-verifier cases receive the same ID, proving that prior execution count does not participate in identity construction. R13's separate uniqueness test uses actual UUID4 issuance and proves distinct real executions receive distinct IDs.

## Determinism boundary

R13 preserves deterministic scheduler/routing semantics.

Execution provenance IDs are intentionally not byte-for-byte deterministic across separate actual runs. They identify execution instances rather than reasoning truth, support, or scheduler choice.

The canonical epistemic semantics remain inspectable; R13 does not claim repeated runs will serialize identical producer UUIDs.

## Preserved R9-R12 controls

R13 retains:
- context_refs fail-closed for strong independence;
- TaskEnvelope absence from strong-independent executor view;
- TaskSpecification-only task content;
- task ID / authority / privacy / budget / context structural absence;
- empty executor-facing independence attestation;
- runner/audit-side verified independence policy;
- constant strong-independent executor episode-version marker `independent@0`;
- exact audit-side episode version;
- trace binding of executor-visible episode version;
- non-independent workers retaining true episode version and full TaskEnvelope;
- admission binding emitted outputs to the exact runner-issued execution ID.

## Exact executable qualification

Fresh clean checkout of exact executable head `46e1999448a9431cc13634b360acdbaec6dfb4b4` under CPython 3.12:

- pytest: **124 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS

Focused R12/R13 identity/isolation controls before push:

- **6/6 PASS**

## Hosted qualification

R13 was added to the existing `Rezon kernel tests` workflow without changing its commands.

Hosted GitHub Actions on CI-enablement head `5337ea39cae6610e1bcf60413e706301f31cbbb1`:

- run: `35400691144`
- install: PASS
- compile: PASS
- test: PASS
- diff-check: PASS
- overall: **success**

## Explicit trust boundaries / non-claims

R13 does not establish:

- independent hostile PASS on the final R13 subject;
- cryptographic executor/model/provider identity;
- absolute mathematical impossibility of UUID collision;
- protection against a malicious trusted host replacing/controlling the UUID source;
- semantic proof that literal TaskSpecification content is non-adversarial;
- a qualified shared-context/shared-read independence class;
- byte-identical execution IDs across repeated runs;
- merge authority;
- deployment, installation, activation, runtime effect, provider/model mutation, or learned-routing qualification;
- reasoning superiority.

The trusted-host boundary remains explicit. UUID4 is used as an opaque per-execution provenance identifier, not as authorization, evidence, truth, identity attestation, or a security credential.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
