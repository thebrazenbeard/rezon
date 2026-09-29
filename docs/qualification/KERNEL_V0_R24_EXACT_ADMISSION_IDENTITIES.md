# Rezon Kernel V0 R24 Exact Admission Identity Bindings

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PENDING / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R24 is the bounded successor to failed R23 exact subject
`e3498a1ead2d9dde186c604961bb184dc3b2a764`.

## R23 hostile failure

R23 correctly blocked duck-typed `TaskSpecification` objects, but the admission
boundary still relied on ordinary Python equality for several authoritative
identity comparisons. Type annotations did not enforce runtime string identity.

A hostile `str` subclass / custom equality value could therefore compare equal
to a trusted identifier while carrying different underlying content.

Fresh exact-R23 probing reproduced six false-PASS paths:

1. `ExecutionResult.execution_id` could impersonate the runner-issued execution.
2. `ExecutionResult.node_id` could impersonate the configured node.
3. `NodeDescriptor.node_id` could use custom equality at the boundary.
4. `Proposition.episode_id` could impersonate the active episode.
5. `Proposition.producer_execution_id` could impersonate the issued execution.
6. `Hyperrelation.episode_id` / producer identity could do the same.

The strongest direct reproduction admitted a result whose
`execution_id` was a non-string `AlwaysEqual` object while the caller supplied
the runner-issued producer string on the emitted proposition. Canonical episode
state mutated successfully.

Disposition:
`R23_IDENTITY_EQUALITY_BINDING = FAIL / CHANGES_REQUIRED`.

R23 remains preserved and unmerged.

## Frozen R24 RED

Regression file:

`tests/test_r24_exact_admission_identities.py`

Against exact R23, all six hostile cases failed because no `AdmissionError`
was raised:

- result execution identity: false PASS;
- result node identity: false PASS;
- descriptor node identity: false PASS;
- proposition episode identity: false PASS;
- proposition producer identity: false PASS;
- relation episode/producer identity: false PASS.

Exact targeted RED result: **6 failed**.

## R24 repair

Before equality-based identity checks, admission now requires exact built-in
`str` values for:

- descriptor node identity;
- result node identity;
- result execution identity;
- non-null expected execution identity;
- proposition episode identity;
- non-null proposition producer identity;
- relation episode identity;
- non-null relation producer identity.

This prevents custom equality implementations and `str` subclasses from
participating in those authoritative identity comparisons.

No canonical producer formula, task digest algorithm, canonical output digest,
state snapshot digest, concurrency control, rollback behavior, or scheduling
logic changed.

## Local qualification

Fresh local repair qualification:

- R24 hostile regression file: **6/6 PASS**;
- focused R16-R24 controls: **30/30 PASS**;
- full suite: **159/159 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Fresh checkout of remote R24 CI-enablement head
`cdf2f8bf0f1798807c3b60d2d6c6c57664efd83e`:

- full suite: **159/159 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

## Exact ancestry

- failed R23 head: `e3498a1ead2d9dde186c604961bb184dc3b2a764`
- R24 branch: `work/rezon-kernel-v0-r24-exact-admission-identities`
- repair commit: `02384cc45598b89e6da607b4cf686542c8aaf023`
- regression commit: `b059b27a15ec9af67a4a6f9fe16ae89faac65bf7`
- CI-enablement head: `cdf2f8bf0f1798807c3b60d2d6c6c57664efd83e`

## Preserved guarantees

R24 preserves the accepted mechanics carried through R16-R23, including:

- admission-owned canonical producer identity;
- task-bound producer identity;
- mandatory exact snapshot digest binding;
- per-Episode admission mutual exclusion;
- transaction rollback on admission failure;
- exact `TaskSpecification` admission;
- direct caller producer-selection rejection.

## Explicit scope / non-claims

R24 establishes ordinary in-process runtime type hardening at specific admission
identity comparisons.

It does **not** establish:

- cryptographic execution or node authenticity;
- semantic truth;
- hostile-code / monkeypatch resistance;
- persistence or crash-consistent durability;
- cross-process or distributed transactionality;
- independent hostile PASS on R24;
- merge authority;
- deployment, installation, activation, provider/model/credential mutation;
- learned-routing qualification.

The Issue #5 donor/HCAE/HyPER/hyperbolic learned-routing gate remains CLOSED.

## Remaining gates

1. Obtain hosted CI PASS for the frozen R24 final subject.
2. Route the exact final R24 head for independent hostile rereview.
3. Preserve any failing exact subject and continue RED-first if another bypass is found.
4. Do not merge without Patrick's explicit authority.
