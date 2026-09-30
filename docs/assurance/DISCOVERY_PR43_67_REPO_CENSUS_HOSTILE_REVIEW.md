# Rezon Hostile Exact-Head Review — Discovery PR #43

Reviewed repository: `thebrazenbeard/discovery`  
Reviewed pull request: #43  
Reviewed exact head: `dea7cd5bf54988e0e3ff0e187bfca5604dae3988`  
Reviewed exact base: `694bba641bdadbf6a50b22463c668c5d13e5f786`  
Disposition: **SURVIVES_DESCRIPTIVE_67_REPO_CENSUS_AND_P0_MANIFEST**

## Exact state

- PR #43 is draft and mergeable.
- It stacks the governed P0 manifest on Discovery's V2 census branch.
- Discovery validation, composed lifecycle validation, and public currentness watch are green on the exact PR head.
- Independent authenticated repository inventory read during this review returned:
  - total repositories: 67;
  - public repositories: 49;
  - private repositories: 18;
  - archived repositories: 2.
- The live public membership includes `sql-connectome`, matching the V2 census.

No merge, deployment, repository visibility change, credential/permission mutation,
or other protected effect was performed.

## Surviving claim

Discovery #43 survives as a **descriptive portfolio census + governed P0
classification artifact**.

It does not establish execution authority, merge authority, or a right to
schedule a project merely because that project is P0.

## Hostile findings

### H1 — P0 classification could become authority

**Closed.**

The manifest explicitly records:

- `priority_is_authority=false`;
- scheduling requires currentness;
- effects require explicit authority;
- merge/deploy are not granted.

### H2 — Discovery could compete with Project Runner for corpus ownership

**Closed.**

The manifest preserves `PROJECT_RUNNER_PORTFOLIO_CORPUS_V1` as the corpus
identity and defines Discovery as the census/capability-discovery feeder.

Discovery supplies evidence; Project Runner remains the scheduling/corpus owner.

### H3 — The 67-repository cut could already be stale

**Closed for the reviewed observation.**

A fresh authenticated owner inventory returned exactly the same arithmetic:

`67 = 49 public + 18 private`

with two archived repositories.

The public membership observed during review matches the census's 49 explicit
public names, including `sql-connectome`.

This is a dated observation, not a permanent fact. Future membership changes
invalidate whole-estate currentness.

### H4 — Public artifacts could leak private repository membership through deterministic digests

**Closed.**

The public census exposes only the private count. It does not publish an
unkeyed private-name digest or all-name digest.

The exact private set therefore remains outside the public artifact.

### H5 — Historical 24-public evidence could remain silently current

**Closed.**

V2 explicitly marks prior whole-public graph/intake/blob-overlap/observatory
evidence stale for the new 49-public cut.

Historical predecessor evidence remains preserved as provenance.

### H6 — The Project Runner source_subject could be mistaken for live authority

**Closed by interpretation.**

The manifest cites:

`thebrazenbeard/project-runner@381559dd07e52105b4e352a90e207a03c6793ff0:portfolio/corpus.public.json`

as the classification source subject.

That binding is provenance for why Discovery was classified P0. It is not a
claim that the old Project Runner commit is today's live scheduling authority.

The currentness of the 67-repo census is independently established by
Discovery's live watcher and the fresh inventory read above.

### H7 — Visibility delta could be misreported as repository creation/deletion

**Closed.**

The census explicitly states that the 59 -> 67 and 24-public -> 49-public delta
can include visibility changes and does not infer the mechanism without
per-repository history.

## Remaining limits

1. The private exact membership is intentionally not publicly committed.
2. A complete private-set currentness proof still requires a secret-key HMAC or
   equivalent non-public evidence path.
3. Repository membership/current heads can drift after this review.
4. This census does not itself qualify each repository's semantic status.
5. P0 is a prioritization input only.

## Claim ceiling

`DISCOVERY_PR43_SURVIVES__LIVE_67_TOTAL_49_PUBLIC_18_PRIVATE_DESCRIPTIVE_CENSUS__NO_AUTHORITY_PROMOTION`

## Next Discovery frontier

Feed this current descriptive cut into Project Runner and regenerate the corpus
status fields that have materially changed since the 17:16 cut, especially:

- WoWSQL retirement and BT2 PostgreSQL V4 migration;
- Project Runner PR #41-#44 execution stack;
- current P0 repository PR heads;
- Discovery's own exact 67-repository census qualification.

Then preserve Discovery as the census feeder rather than growing a second
scheduler.
