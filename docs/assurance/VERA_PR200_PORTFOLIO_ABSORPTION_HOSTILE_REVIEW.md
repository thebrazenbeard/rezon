# Rezon Hostile Exact-Head Review — Vera PR #200

Reviewed repository: `thebrazenbeard/vera`  
Reviewed pull request: #200  
Reviewed exact head: `078d2d7242384c58676305d47654406713e599cf`  
Reviewed exact base: `87aa888cb7543875ffa11c9c7a1eb9e5b60c35cf`  
Review class: portfolio-completeness / provenance / public-privacy / authority-boundary review  
Disposition: **REVIEW_STALE__PUBLIC_SAFE_RESTACK_REQUIRED**

## Exact source state

PR #200 is draft, mergeable, and based on the exact current Vera main head
observed for this review.

Its internal portfolio architecture and tests are consistently bound to a
65-repository snapshot.

The current independently qualified Project Runner/Discovery corpus is:

- 67 repositories total;
- 49 public;
- 18 private;
- public corpus Git blob
  `886e9be586c37584c17afdc540c38a1d95deaaa6`.

Comparing the PR #200 runtime-source snapshot against the current 49-public
corpus shows only 46 public overlaps.

Three current public repositories are absent from PR #200's claimed complete
live portfolio snapshot:

- `thebrazenbeard/fuckup`;
- `thebrazenbeard/sql-connectome`;
- `thebrazenbeard/vera-mono`.

Therefore the PR's "complete live portfolio" / exact-65 currentness claim is
stale.

## Public privacy conflict

`thebrazenbeard/vera` is a public repository.

PR #200's public source artifacts enumerate repository membership that includes
repositories classified as private/governed in its own records.

The current hardened Project Runner/Discovery public-corpus rule intentionally
keeps private repository membership **count-only** and rejects deterministic
public fingerprints of the private set.

Accordingly, PR #200 is not compatible with the current public-safe portfolio
privacy contract.

This review does not repeat the private repository membership.

## Useful mechanisms that survive

The stale/currentness finding does not invalidate every mechanism in PR #200.

The following remain potentially reusable in a successor:

- exact Git-blob donor/target provenance bindings;
- explicit distinction between mechanism absorption and identity/memory/authority
  transfer;
- no-runtime-dependency-by-presence semantics;
- Vera-owned internal capability-plane mapping;
- source-only effect ceiling;
- external reviewer/runtime boundaries;
- exact VCP source mirrors where their individual source bindings remain current;
- tests that recompute target Git blobs from checked-out bytes.

Those mechanisms should be carried forward only after rebinding to a current,
public-safe inventory subject.

## Findings

### H1 — Complete-live-portfolio claim is stale

**Open / blocks current-completeness claim.**

The PR hard-codes and tests for 65 repositories while current governed portfolio
evidence is 67 total.

The public subset alone proves incompleteness without requiring disclosure of
private membership.

### H2 — Public privacy boundary conflicts with private-set enumeration

**Open / requires successor design.**

A public source artifact should not enumerate the private repository set when
the accepted public corpus contract is count-only.

Historical Git objects already published by the draft are not rewritten or
destroyed by this review.

### H3 — "65 modules = exact runtime portfolio snapshot" tests can preserve staleness

**Open.**

The current tests prove internal consistency with the stale snapshot, not live
portfolio currentness.

A successor should bind to an immutable current corpus subject and separately
prove freshness/currentness rather than assert a literal cardinality forever.

### H4 — Mechanism absorption could transfer identity or authority

**Closed in the reviewed design.**

PR #200 repeatedly distinguishes source/mechanism provenance from identity,
memory, consent, runtime activation, installation, and effect authority.

That boundary should be preserved in the successor.

### H5 — Exact-copy provenance could be mistaken for runtime qualification

**Closed by the reviewed claim ceiling.**

Migration bindings prove source-byte equality only. They do not prove runtime
activation, installation, or behavior.

### H6 — Runtime-cohesion CI could be falsely claimed

**Closed by the PR's own reporting.**

The PR states that its runtime-cohesion workflow is workflow-dispatch-only and
was not dispatched for this source subject. It does not claim an executable
runtime PASS from source presence.

## Required successor/restack

Do not merge PR #200 as the current complete portfolio absorption.

A successor should:

1. preserve the useful source/provenance and authority-boundary mechanisms;
2. bind its public inventory to the current Project Runner/Discovery corpus;
3. include all 49 current public repositories, including the three publicly
   demonstrated omissions;
4. represent private inventory count-only on public source surfaces;
5. keep any exact private inventory on a separately governed non-public surface,
   if needed at all;
6. replace hard-coded perpetual cardinality assertions with immutable-cut
   binding plus a freshness/currentness check;
7. re-run donor/path/blob provenance checks against the new exact subject;
8. retain the source-only/no-install/no-runtime/no-effect claim ceiling.

## Claim ceiling

`VERA_PR200_REVIEW_STALE__USEFUL_ABSORPTION_MECHANISMS_SURVIVE__65_REPO_CURRENTNESS_FALSE__PUBLIC_PRIVATE_SET_ENUMERATION_INCOMPATIBLE_WITH_CURRENT_PRIVACY_BOUNDARY`
