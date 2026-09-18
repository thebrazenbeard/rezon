# Rezon Kernel V0 R8 Authority Fail-Closed Evidence

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R8 is a bounded successor to exact R7 after a self-hostile authority-boundary failure. It preserves R7's evidence-consumption, ref/version-association, and worker-output-blinding repairs while removing R7's false implication that an in-process authority-policy object could prove authority.

## Exact ancestry

- repository: `thebrazenbeard/rezon`
- failed R7 subject: `aa82fb952c5d892e852348449f000cddb1a4f076`
- failed R7 tree: `4b05ccd5e5967f8b9a304f5f51fb490821347a0b`
- R8 branch: `work/rezon-kernel-v0-r8-authority-fail-closed`
- R8 authority RED head: `f974f1f3175288274fc2ec970d1df654d8cb0f04`
- R8 executable GREEN head: `475061f0e327a138793eca4606413879c0e21a2a`
- hosted-CI enablement head: `bbf28d9375522a030fb8beb3a2170c5603031b0a`

## Failure trigger

R7 introduced `AuthorityVerificationEvidence` and `AuthorityVerificationPolicy` and required exact task/envelope/issuer/source/currentness reference strings.

A fresh self-hostile probe on exact R7 `aa82fb95…` demonstrated that this remained structurally caller-mintable.

The same caller could create:

- `TaskEnvelope.available_authority=("authority:protected",)`;
- matching `AuthorityVerificationEvidence`;
- arbitrary non-empty issuer/source/currentness/verification refs;
- a matching `AuthorityVerificationPolicy`;
- a `RunnerNode` carrying that policy.

Observed R7 result:

- receipt failures: empty;
- `h-self-minted-authority`: admitted.

Therefore the R7 policy shape was structured assertion, not independent authorization proof.

## Frozen RED evidence

R8 froze the bypass before repair:

- test: `tests/test_r8_authority_boundary.py`;
- exact test-only head: `f974f1f3175288274fc2ec970d1df654d8cb0f04`.

Fresh CPython 3.12 execution produced:

`1 failed / 0 passed`

The failure was the required assertion that a caller-minted authority policy must not satisfy protected authority. R7 instead executed the worker and admitted its output.

## R8 repair — authority is unavailable in Kernel V0

Kernel V0 has no independently governed, externally anchored, qualified authority verifier.

R8 therefore adopts the smaller fail-closed rule:

- if a node declares any non-empty `required_authority`, Kernel V0 returns `CONTRACT_VIOLATION`;
- the worker is not executed;
- caller-supplied `TaskEnvelope.available_authority` strings cannot authorize;
- caller-supplied `AuthorityVerificationPolicy` objects cannot authorize;
- no in-process issuer/source/currentness strings can authorize.

`AuthorityVerificationEvidence` and `AuthorityVerificationPolicy` remain representable only as candidate structured evidence for a future separately governed verifier boundary. Their class documentation explicitly states that Kernel V0 does not accept the policy object as an authorization grant.

The general task-envelope binding test no longer uses `required_authority`; it continues to verify exact envelope propagation/digest binding independently of authorization.

The existing required-authority negative path and the new caller-mint hostile test both require fail-closed behavior.

## Why R8 does not implement a replacement authority verifier

Implementing another in-process matcher would only move the self-mint boundary.

A future positive authority path requires a separately governed trust boundary with qualification appropriate to the protected effect. Until then, the correct Kernel V0 behavior is refusal.

This is a capability limitation by design, not evidence that protected authority can never be implemented.

## Inherited R7 controls

R8 retains the R7 repairs and tests for:

- conservative visible-EVIDENCE consumption attestation;
- exact source-ref/source-version association checks;
- fail-closed prior worker proposition/relation channels for independence-required execution;
- positive exact-evidence independence controls;
- positive exact ref/version association admission.

The R7 authority policy is no longer treated as a positive authorization path.

## Exact executable qualification

Fresh clean clone of executable head `475061f0e327a138793eca4606413879c0e21a2a` under CPython 3.12:

- pytest: **111 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS
- tracked source clean; only test-created environment/install/bytecode artifacts were untracked

## Hosted qualification

R8 was added to the existing `Rezon kernel tests` branch trigger without changing its test commands.

Hosted GitHub Actions on CI-enablement head `bbf28d9375522a030fb8beb3a2170c5603031b0a`:

- run: `35382129994`
- event: push
- install: PASS
- compile: PASS
- test: PASS
- diff-check: PASS
- overall: **success**

## Explicit unresolved / non-claims

R8 does not establish:

- independent hostile PASS on R8;
- any usable positive protected-authority path in Kernel V0;
- cryptographic issuer identity;
- an external authority provider/verifier implementation;
- merge authority;
- deployment, installation, activation, or provider/model mutation;
- semantic observation of arbitrary executor evidence consumption;
- final general-purpose provenance typing;
- learned-routing qualification;
- reasoning superiority.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, qualify that exact head locally and in hosted CI, then request fresh independent hostile rereview.

No merge is requested by this record.
