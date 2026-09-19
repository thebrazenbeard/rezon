# Rezon Kernel V0 R28 Unambiguous Retrieval Source-Version Binding

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R28 is the bounded successor to failed whole-Kernel R27 exact subject
`5d5c25197995361ecbe39d7e959feeabd2890ffe`.

R27's retrieval runtime-type/equality hardening remains valid within that narrower
boundary. Fresh adjacent hostile review found that the promoted canonical
source/version token itself was ambiguous.

## R27 hostile failure

Retrieval promotion serialized source provenance as:

`source_id@source_version`

without constraining the separator inside either component.

Exact R27 therefore mapped two distinct trusted source/version pairs to the same
canonical provenance token:

- `source_id="repo:a@b", source_version="c"` -> `repo:a@b@c`
- `source_id="repo:a", source_version="b@c"` -> `repo:a@b@c`

The collision appeared identically in both the promoted proposition's first
`source_refs` entry and its `source_versions` entry.

Disposition:
`R27_SOURCE_VERSION_CANONICAL_ENCODING = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R27 remains preserved, draft, and unmerged.

## Frozen R28 RED

Regression file:

`tests/test_r28_unambiguous_source_version_binding.py`

Exact RED commit:

`b7eb35f77307404d54511025cd3b195e91cd473d`

Fresh exact-R27 result:

**2 failed / 0 passed**.

Both separator-bearing component classes were admitted instead of failing closed.

## R28 repair

Executable repair:

`77782d0db4c5b4f9604d6640a8360cc7a6e0b2ca`

R28 preserves the existing simple canonical provenance format while making its
domain explicit and injective.

Before retrieval policy matching or promotion:

- source IDs must remain non-empty exact strings and may not contain `@`;
- source versions must remain non-empty exact strings and may not contain `@`;
- the same separator rule is enforced independently on both receipt and trusted
  admission-evidence components.

Therefore every admitted retrieval binding within this contract has exactly one
separator in the promoted `source_id@source_version` token.

Existing simple bindings such as `repo:policy@abc123` remain unchanged.

## Qualification

CI-enablement head:

`10ef39c86a9e79c7052f1748c4a413a242d2a892`

Fresh detached-checkout qualification:

- R28 collision regressions: **2/2 PASS**;
- focused R16-R28 controls: **61/61 PASS**;
- full suite: **190/190 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35459360186`;
- exact head `10ef39c86a9e79c7052f1748c4a413a242d2a892`;
- test job `105940302019`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R27 final: `5d5c25197995361ecbe39d7e959feeabd2890ffe`
- R28 branch: `work/rezon-kernel-v0-r28-unambiguous-source-version-binding`
- frozen RED: `b7eb35f77307404d54511025cd3b195e91cd473d`
- executable repair: `77782d0db4c5b4f9604d6640a8360cc7a6e0b2ca`
- CI-enablement head: `10ef39c86a9e79c7052f1748c4a413a242d2a892`

## Explicit scope / non-claims

R28 establishes ordinary in-process exact runtime hardening for retrieval
admission plus an unambiguous `source_id@source_version` provenance domain for
admitted retrievals.

It does not establish:

- cryptographic authenticity of retrieval policy/evidence;
- caller authorization outside the supplied policy capability;
- semantic truth of retrieved content;
- support for raw source IDs or versions containing `@`; such values must be
  normalized into a logical identifier/version outside this boundary;
- malicious source replacement / monkeypatching resistance;
- persistent/database durability or crash consistency;
- cross-process/distributed transactionality;
- independent hostile PASS on R28;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Obtain fresh exact-head independent hostile rereview.
3. Pressure other provenance serialization/collision surfaces and retrieval-to-
   Episode rollback behavior without broadening the accepted claim.
4. Preserve any failing exact subject and continue RED-first.
5. Do not merge without Patrick's explicit authority.
