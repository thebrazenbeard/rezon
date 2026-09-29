# Rezon Kernel V0 R25 Exact Admission Runtime Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R25 is the bounded successor to failed R24 exact subject
`0f112eda3dafa18ea81fac86b86f08978524a8a4`.

## R24 hostile failure

R24 hardened a first set of identity comparisons, but neighboring admission
fields still trusted Python annotations and ordinary equality/hash/lower
behavior at runtime.

Fresh exact-R24 hostile probes froze nine cases. Eight could bypass a governed
admission check or hide a reported failure; one malformed proposition-kind case
failed closed only through an unhandled `AttributeError` rather than a governed
`AdmissionError`.

Observed on exact R24:

- emitted forged source ref matched an allowed governed source ref: false PASS;
- emitted forged source version matched an allowed governed version: false PASS;
- forged relation participant ref matched an active canonical object: false PASS;
- malformed forged proposition kind escaped typed rejection and raised `AttributeError`;
- forged relation type supplied caller-controlled `.lower()`: false PASS;
- forged value on trusted `allowed_source_refs` authorized output: false PASS;
- non-empty falsey `failures` tuple hid a reported failure and admitted mutation: false PASS;
- forged value on trusted `allowed_source_versions` authorized output: false PASS;
- forged values inside trusted `allowed_source_bindings` authorized output: false PASS.

Disposition:
`R24_ADMISSION_CONTRACT_RUNTIME_TYPING = FAIL / CHANGES_REQUIRED`.

R24 remains preserved, draft, and unmerged.

## Frozen R25 RED

Regression file:

`tests/test_r25_exact_admission_contract.py`

Exact RED commit:

`9ab8cee33fc426c461d8df62a60502ae7f1ce5d7`

When the frozen test file is run against exact R24 head
`0f112eda3dafa18ea81fac86b86f08978524a8a4`, result is:

- **9 failed**;
- eight failures are false-PASS governed checks;
- one is the unhandled malformed-kind `AttributeError`.

## R25 repair

Admission now performs an explicit runtime contract validation before canonical
output hashing or equality/membership authorization checks.

The validator requires exact built-in/runtime types for the values whose
semantics admission relies on:

- exact `Episode`, `NodeDescriptor`, and `ExecutionResult` objects;
- exact `PropositionKind` entries in permitted-output contracts;
- exact-string permitted relation types;
- exact `FailureState` tuples;
- exact tuples for emitted propositions and relations;
- exact `Proposition` objects with exact-string identity/content/provenance fields;
- exact `PropositionKind` proposition kind values;
- exact `Hyperrelation` objects with exact-string identity/type/provenance fields;
- exact `Participant` objects with exact-string reference/role fields;
- exact-string tuples for governed source refs and source versions;
- exact two-string tuples for governed source bindings.

R24's exact-string checks for node, execution, episode, and producer identities
remain in force. R23's exact-`TaskSpecification` boundary remains in force.

This change deliberately validates before `canonical_output_digest()` so a
malformed executor value cannot first trigger arbitrary deep-copy/equality
behavior inside hashing.

## Qualification

Repair commit:

`4862a5f9be683242402092f7ed8f5a0c68bba0d9`

CI-enablement head:

`ab8898435c04c53ec695e9ab15d3d41cd879aaf9`

Fresh qualification of the remote CI-enablement head:

- R25 hostile regressions: **9/9 PASS**;
- focused R16-R25 controls: **39/39 PASS**;
- full suite: **168/168 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS;
- hosted GitHub Actions run `35457121996`: **SUCCESS**.

## Exact ancestry

- failed R24 head: `0f112eda3dafa18ea81fac86b86f08978524a8a4`
- R25 branch: `work/rezon-kernel-v0-r25-exact-admission-contract`
- frozen RED: `9ab8cee33fc426c461d8df62a60502ae7f1ce5d7`
- executable repair: `4862a5f9be683242402092f7ed8f5a0c68bba0d9`
- CI-enablement head: `ab8898435c04c53ec695e9ab15d3d41cd879aaf9`

## Explicit scope / non-claims

R25 establishes ordinary in-process runtime contract hardening for the current
execution-result admission boundary.

It does not establish:

- cryptographic authenticity or trusted-caller identity;
- semantic truth;
- resistance to malicious source replacement / monkeypatching;
- persistence or crash-consistent durability;
- cross-process/distributed transactionality;
- independent hostile PASS on R25;
- merge, deployment, installation, activation, provider/model/credential mutation;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Route that exact final head for fresh independent hostile rereview.
3. Preserve any failing exact subject and continue RED-first if another bypass is found.
4. Do not merge without Patrick's explicit authority.
