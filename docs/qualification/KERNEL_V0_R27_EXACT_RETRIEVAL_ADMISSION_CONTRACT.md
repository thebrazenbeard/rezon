# Rezon Kernel V0 R27 Exact Retrieval Admission Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R27 is the bounded successor to failed whole-Kernel R26 exact subject
`c82229f115e7bd9bd14f23ce0a975a3f034c20be`.

R26's direct canonical Episode hardening remains valid within that narrower
boundary. Fresh hostile review found that retrieval admission still trusted
runtime annotations, ordinary equality/hash behavior, and duck-typed policy
objects before evidence could be promoted into canonical Episode state.

## R26 hostile failure

Exact R26 false-accepted all eleven frozen retrieval-admission attacks:

1. an arbitrary duck-typed policy object self-authorized retrieval;
2. a `RetrievalAdmissionPolicy` subclass overrode verification semantics;
3. a `RetrievalReceipt` subclass was accepted;
4. a `RetrievalAdmissionEvidence` subclass was accepted;
5. trusted admissions accepted a list instead of an exact tuple;
6. a forged evidence source ID matched the receipt through custom equality;
7. a forged evidence source version matched through custom equality;
8. a forged authoritative scope matched the required scope through custom equality;
9. a forged content digest matched the real digest through custom equality;
10. a forged locator authorized a returned ref through custom hash/equality;
11. a forged required scope matched the evidence scope through custom equality.

Disposition:
`R26_RETRIEVAL_ADMISSION_RUNTIME_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R26 remains preserved, draft, and unmerged.

## Frozen R27 RED

Regression file:

`tests/test_r27_exact_retrieval_admission_contract.py`

Exact RED commit:

`da62fd672aa103c2499b2420a4a5a7b4898b4edc`

Fresh exact-R26 result:

**11 failed / 0 passed**.

All eleven were false accepts: canonical evidence promotion completed instead of
failing closed.

## R27 repair

Executable repair:

`39ccf37094c5338b89e09093ca3d4a7dc443b2db`

R27 validates the retrieval-admission runtime contract before policy dispatch,
content hashing, tuple/set membership, equality comparisons, or provenance
promotion.

The repair requires:

- exact `Episode` at the promotion boundary;
- exact non-empty proposition ID and retrieved content strings;
- exact `RetrievalAdmissionPolicy`;
- an exact tuple of verified admissions;
- exact `RetrievalAdmissionEvidence` entries;
- exact non-empty evidence source ID, source version, authority ref,
  currentness ref, authoritative scope, and content digest;
- exact tuples of non-empty verification refs and locator refs;
- exact `RetrievalReceipt`;
- exact non-empty receipt retrieval ID, query, source ID, source version, and method;
- exact non-empty returned-ref tuple;
- exact `AdmissionStatus`;
- exact receipt verification-ref tuple and exact optional receipt authority,
  currentness, and scope strings;
- exact non-empty required authoritative scope.

`digest_retrieved_content()` also rejects non-exact or empty strings before
caller-controlled `str` subclass behavior can influence hashing.

After validation, source/version/scope/content/locator matching operates only on
exact built-in strings and tuples.

## Qualification

CI-enablement head:

`2e35c93199c2b7bd231daaea0c38235e3b19e35e`

Fresh detached-checkout qualification:

- R27 hostile regressions: **11/11 PASS**;
- focused R16-R27 controls: **59/59 PASS**;
- retrieval-focused existing controls: **25/25 PASS** before remote cut;
- full suite: **188/188 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35459095049`;
- exact head `2e35c93199c2b7bd231daaea0c38235e3b19e35e`;
- test job `105939588411`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R26 final: `c82229f115e7bd9bd14f23ce0a975a3f034c20be`
- R27 branch: `work/rezon-kernel-v0-r27-exact-retrieval-admission`
- frozen RED: `da62fd672aa103c2499b2420a4a5a7b4898b4edc`
- executable repair: `39ccf37094c5338b89e09093ca3d4a7dc443b2db`
- CI-enablement head: `2e35c93199c2b7bd231daaea0c38235e3b19e35e`

## Explicit scope / non-claims

R27 establishes ordinary in-process runtime contract hardening for the current
retrieval-admission and retrieval-to-Episode promotion boundary.

It does not establish:

- cryptographic authenticity of the policy object or evidence authority;
- trusted-caller identity or authorization outside the supplied policy capability;
- semantic truth of retrieved content;
- malicious source replacement / monkeypatching resistance;
- a globally canonical encoding for arbitrary source IDs/versions containing
  provenance delimiter characters;
- persistent/database durability or crash consistency;
- cross-process/distributed transactionality;
- independent hostile PASS on R27;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Obtain fresh exact-head independent hostile rereview.
3. Ask independent review to pressure policy-capability assumptions, direct
   `RetrievalAdmissionPolicy.verify()` use, source/version provenance encoding,
   duplicate/locator semantics, and retrieval-to-Episode composition.
4. Preserve any failing exact subject and continue RED-first.
5. Do not merge without Patrick's explicit authority.
