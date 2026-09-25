# Rezon Hostile Exact-Head Review — Discovery PR #43

Reviewed repository: `thebrazenbeard/discovery`  
Reviewed pull request: #43  
Reviewed exact head: `dea7cd5bf54988e0e3ff0e187bfca5604dae3988`  
Reviewed exact base: `694bba641bdadbf6a50b22463c668c5d13e5f786`  
Parent pull request: #41 at `694bba641bdadbf6a50b22463c668c5d13e5f786`  
Disposition: **SURVIVES_NARROWED_67_REPO_DESCRIPTIVE_CENSUS_COMPOSITION**

## Exact stack state

- PR #41 is draft, mergeable, and based on current Discovery main
  `368e8dc8274e89a306039d28462c7547b263e93e`.
- PR #43 is draft, mergeable, and its exact base equals PR #41 head.
- All three Discovery workflows pass for PR #41.
- All three Discovery workflows pass for PR #43.

Despite PR #41's historical branch name containing "66", its exact head carries
the refreshed 67-total / 49-public / 18-private census subject consumed by PR
#43.

## Project Runner corpus binding

PR #43 binds its P0 manifest to:

`thebrazenbeard/project-runner@381559dd07e52105b4e352a90e207a03c6793ff0:portfolio/corpus.public.json`.

That exact file has Git blob:

`886e9be586c37584c17afdc540c38a1d95deaaa6`.

The later Project Runner PR #44 corpus file resolves to the **same exact Git
blob**. Therefore PR #43's older commit locator is not stale for the consumed
corpus file; it is an immutable equivalent source subject.

The newer Project Runner P0 currentness overlay is a separate live-currentness
layer and does not rewrite this frozen corpus subject.

## Claim that survives

PR #43 survives for this bounded claim:

`CURRENT 67-REPOSITORY DISCOVERY CENSUS + DESCRIPTIVE P0 MANIFEST -> PROJECT RUNNER HANDOFF`

with priority and census data explicitly non-authoritative for scheduling or
effects.

## Hostile findings

### H1 — P0 classification could become scheduling/effect authority

**Closed.**

The manifest explicitly states:

- `priority_is_authority=false`;
- scheduling requires currentness;
- effects require explicit authority;
- merge/deploy authority is not granted.

P0 is descriptive triage, not permission.

### H2 — Private repository membership could leak through deterministic fingerprints

The predecessor PR #42 proposed deterministic unkeyed private-set digests.

**Closed by exclusion.**

PR #43 intentionally does not import that artifact and tests that
`private_names_sha256` and `all_names_sha256` do not reappear in the public
P0 manifest.

Private repository membership remains count-only in public artifacts.

### H3 — Historical 66-repository naming could conceal a stale 67-repository claim

**Closed by exact-head evidence.**

The reviewed PR #41 head is the actual current census source used by PR #43 and
its validation asserts:

- total = 67;
- public = 49;
- private = 18;
- archived = 2.

The branch name is historical metadata, not the evidence subject.

### H4 — Project Runner source binding could be stale by content

**Closed.**

The older bound Project Runner commit and the later reviewed Project Runner
corpus resolve to the exact same Git blob
`886e9be586c37584c17afdc540c38a1d95deaaa6`.

No semantic equivalence is inferred from counts; byte identity is established by
the Git object.

### H5 — Discovery could become a competing corpus authority

**Closed by role boundary.**

Discovery remains the census/capability-discovery feeder.

Project Runner owns the portfolio corpus identity and scheduling machinery.
Discovery supplies descriptive evidence rather than a second scheduler or
semantic authority.

### H6 — Census freshness could be inferred permanently from a passing PR

**Closed by currentness design.**

The live public-currentness watcher remains part of the Discovery qualification.
A later membership/default-branch/head/tree/archive change invalidates current
census claims even though the historical PR remains valid as a prior cut.

## Remaining limits

1. The 18 private repositories remain intentionally count-only in public
   evidence, so public reviewers cannot independently enumerate private
   membership.
2. The reviewed 67-repository cut is a timestamped currentness subject, not a
   permanent estate size.
3. PR #43 remains stacked on PR #41; neither is merged by this review.
4. Discovery's census does not itself authorize Project Runner claims,
   execution, source writes, merge, deploy, or other protected effects.
5. Future repository additions/removals require a new census/currentness cut.

## Claim ceiling

`DISCOVERY_PR43_SURVIVES__67_TOTAL_49_PUBLIC_COUNT_ONLY_PRIVATE__EXACT_CORPUS_BLOB_BINDING__DESCRIPTIVE_NOT_AUTHORITY`

## Next Discovery frontier

Treat PR #41 -> PR #43 as the current census composition line and use it as
descriptive input to Project Runner's P0 currentness overlay. The next change
should be triggered by actual portfolio drift, not by creating another parallel
census format.
