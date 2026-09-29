# Rezon Kernel V0 R26 Exact Canonical Episode Boundary

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R26 is the bounded successor to failed whole-Kernel R25 exact subject
`c1f445e29b56711ad451cab91f8d5e55c3817351`.

R25's execution-result admission hardening remains valid within that narrower
boundary, but fresh hostile review found that the public `Episode` mutation
surface could still corrupt canonical state through ordinary Python runtime
annotation/equality behavior.

## R25 hostile failure

Exact R25 admitted or permitted all nine frozen direct-boundary attacks:

1. `Episode` accepted a `str` subclass as canonical episode identity.
2. Public `episode_id` could be reassigned after canonical state existed.
3. A foreign custom-equality proposition `episode_id` impersonated the episode.
4. A custom-equality proposition ID entered canonical state.
5. A `Proposition` subclass entered canonical state directly.
6. A forged retract ID removed a real canonical proposition.
7. A forged relation participant ref resolved to a real active proposition.
8. A custom-string relation type entered canonical state.
9. A `Hyperrelation` subclass entered canonical state directly.

Disposition:
`R25_DIRECT_EPISODE_CANONICAL_BOUNDARY = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R25 remains preserved, draft, and unmerged.

## Frozen R26 RED

Regression file:

`tests/test_r26_exact_episode_boundary.py`

Exact RED commit:

`e295ae28f916d7040d11facdcfbe9bf074884484`

Fresh exact-R25 result:

**9 failed / 0 passed**.

## R26 repair

Executable repair:

`63cea8582e10fb495e4cd42ef29730d4905fcb33`

R26 hardens the canonical `Episode` boundary before equality, membership,
duplicate detection, retraction, dependency traversal, or persistence.

The repair:

- requires the constructed episode ID to be a non-empty exact built-in `str`;
- stores canonical episode identity privately and exposes a read-only public property;
- rejects public episode-identity reassignment;
- requires exact `Proposition` objects on direct proposition mutation;
- requires exact non-empty proposition identity/episode/content strings;
- requires exact `PropositionKind`;
- requires exact-string/tuple provenance fields and producer identity;
- requires exact `float` confidence when confidence is present;
- requires exact non-empty retract ID and reason strings;
- requires exact `Hyperrelation` objects on direct relation mutation;
- requires exact non-empty relation identity/episode/type strings;
- requires exact `Participant` objects with exact non-empty ref/role strings;
- requires exact-string/tuple relation provenance and producer identity.

R25's admission validator remains in place. R26 adds protection at the canonical
state object itself so trusted and non-runner callers cannot bypass those
constraints through direct public mutation.

## Qualification

CI-enablement head:

`a729632f8ca34b7c3e94b61bbf43c56b32cf108d`

Fresh clean checkout qualification:

- R26 hostile regressions: **9/9 PASS**;
- focused R16-R26 controls: **48/48 PASS**;
- full suite: **177/177 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35457686513`;
- exact head `a729632f8ca34b7c3e94b61bbf43c56b32cf108d`;
- test job `105935777695`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R25 final: `c1f445e29b56711ad451cab91f8d5e55c3817351`
- R26 branch: `work/rezon-kernel-v0-r26-exact-episode-boundary`
- frozen RED: `e295ae28f916d7040d11facdcfbe9bf074884484`
- executable repair: `63cea8582e10fb495e4cd42ef29730d4905fcb33`
- CI-enablement head: `a729632f8ca34b7c3e94b61bbf43c56b32cf108d`

## Explicit scope / non-claims

R26 establishes ordinary in-process runtime hardening for the public canonical
Episode mutation boundary.

It does not establish:

- cryptographic caller identity or authorization;
- resistance to deliberate mutation of private Python attributes or source code;
- semantic truth;
- persistence/database durability;
- crash consistency;
- cross-process/distributed transactionality;
- independent hostile PASS on R26;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Freeze and requalify the exact final documentation head.
2. Obtain fresh exact-head independent hostile rereview.
3. Preserve any failing exact subject and continue RED-first if another canonical
   boundary bypass is found.
4. Do not merge without Patrick's explicit authority.
