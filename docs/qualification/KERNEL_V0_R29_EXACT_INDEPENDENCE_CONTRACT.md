# Rezon Kernel V0 R29 Exact Independence Verification Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R29 is the bounded successor to failed whole-Kernel R28 exact subject
`f6e1da75ec62ea732e58253b4c12b0c2c87bab8b`.

R28's retrieval/provenance hardening remains valid within that narrower boundary.
Fresh hostile review found that independence-required execution still trusted
duck/subclass policy capability and ordinary Python runtime equality/container
behavior.

## R28 hostile failure

Exact R28 failed all eleven frozen R29 cases:

1. a duck-typed policy authorized an independence-required execution;
2. an `IndependenceVerificationPolicy` subclass overrode verification semantics;
3. an `IndependenceMetadata` subclass overrode claim completeness and authorized
   execution despite empty identity fields;
4. policy verified evidence accepted a list instead of an exact tuple;
5. an `IndependenceVerificationEvidence` subclass was accepted;
6. a forged basis ref matched a claimed basis through custom equality/hash;
7. a forged executor identity matched metadata through custom equality;
8. metadata basis refs accepted a list instead of an exact tuple;
9. a forged consumed-evidence ref matched visible evidence through custom
   equality/hash and authorized execution;
10. identical underlying worker identities were treated as pairwise independent
    through custom inequality;
11. shared consumed evidence was hidden from pairwise overlap detection through
    custom inequality.

Several cases reached the actual runner and admitted worker output with no
`CONTRACT_VIOLATION`.

Disposition:
`R28_INDEPENDENCE_VERIFICATION_RUNTIME_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R28 remains preserved, draft, and unmerged.

## Frozen R29 RED

Regression file:

`tests/test_r29_exact_independence_contract.py`

Exact RED commit:

`92ea9b14d0770e69d61b1a96f5000afc4c08d34a`

Fresh exact-R28 result:

**11 failed / 0 passed**.

## R29 repair

Receipts contract repair:

`e5bfe6da1ead22f0af6d515be0fb48e7499c965f`

Runner dispatch repair:

`dfd794ef21fd13c6e6076bdd8f48b737d1c81b14`

R29 hardens both the declarative independence data model and the runner authority
boundary.

For a demonstrably independent claim, `IndependenceMetadata` must now be the
exact base type and must contain:

- non-empty exact built-in strings for executor, model, provider, prompt lineage,
  and context lineage;
- literal `False` for `saw_other_answer`;
- exact tuples containing only non-empty exact strings for common evidence,
  consumed evidence, and independence-basis refs;
- at least one exact governed-namespace basis ref;
- no common-evidence refs.

Pairwise independence is evaluated only after both metadata objects satisfy that
exact contract, preventing caller-controlled equality/hash semantics from
fabricating worker distinction or hiding shared consumed evidence.

`IndependenceVerificationPolicy.verify()` now fails closed unless:

- the policy is the exact base policy type when its base method is used;
- metadata is exact `IndependenceMetadata`;
- `verified_evidence` is an exact tuple;
- every evidence item is exact `IndependenceVerificationEvidence`;
- identity/lineage/basis fields are non-empty exact strings;
- verification refs are a non-empty exact string tuple;
- negative-answer and evidence-attestation fields are exact and complete.

At the actual runner boundary, policy method dispatch occurs only for an exact
`IndependenceVerificationPolicy`. Duck policies and policy subclasses cannot
supply executable authorization. Metadata subclasses are rejected before their
overridden completeness properties can be trusted.

## Qualification

CI-enablement head:

`a5321bf383b781747a25446b60d9f861620b0b8b`

Fresh detached-checkout qualification:

- R29 hostile regressions: **11/11 PASS**;
- focused R16-R29 controls: **72/72 PASS**;
- existing independence/hostile controls: **24/24 PASS** before remote cut;
- full suite: **201/201 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35459920005`;
- exact head `a5321bf383b781747a25446b60d9f861620b0b8b`;
- test job `105941815768`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R28 final: `f6e1da75ec62ea732e58253b4c12b0c2c87bab8b`
- R29 branch: `work/rezon-kernel-v0-r29-exact-independence-contract`
- frozen RED: `92ea9b14d0770e69d61b1a96f5000afc4c08d34a`
- receipts repair: `e5bfe6da1ead22f0af6d515be0fb48e7499c965f`
- runner repair: `dfd794ef21fd13c6e6076bdd8f48b737d1c81b14`
- CI-enablement head: `a5321bf383b781747a25446b60d9f861620b0b8b`

## Explicit scope / non-claims

R29 establishes ordinary in-process runtime hardening for the current
independence metadata, verification-evidence, policy, pairwise comparison, and
runner dispatch boundary.

It does not establish:

- cryptographic authenticity of an independence policy/evidence producer;
- actual physical/provider/model independence beyond the governed evidence
  represented by the policy;
- semantic truth of worker output;
- malicious source replacement / monkeypatching resistance;
- cross-process/distributed isolation;
- persistent/database durability;
- independent hostile PASS on R29;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. Pressure adjacent visibility/scheduler/execution-view independence channels
   without broadening the accepted claim.
5. Preserve any failing exact subject and continue RED-first.
6. Do not merge without Patrick's explicit authority.
