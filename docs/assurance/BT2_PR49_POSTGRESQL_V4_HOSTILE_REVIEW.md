# Rezon Hostile Exact-Head Review — BT2 PR #49

Reviewed repository: `thebrazenbeard/bt2`  
Reviewed pull request: #49  
Reviewed exact head: `7f4c1d5c5bf03ed1f5d869873efc86e50252e83a`  
Reviewed exact base: `9f4409c96eb3e5c529da32ab83421f3fdcd5c284`  
Review class: WoWSQL-retirement / PostgreSQL V4 migration / Lantern currentness contract  
Disposition: **SURVIVES_NARROWED_POSTGRESQL_V4_SOURCE_CANDIDATE**

## Live authority correction

WoWSQL is retired under current live user authority.

PR #49 correctly treats WoWSQL V1-V3 and provider-specific material as historical
evidence rather than an active currentness path.

No WoWSQL runtime read was attempted for this review.

## Exact source/CI state

At the reviewed exact head:

- PR #49 is draft and mergeable;
- base equals current BT2 main head observed for this review;
- database rebuild qualification is green;
- PostgreSQL 16 canonical blank rebuild passes;
- PostgreSQL 17 managed-role compatibility rebuild passes;
- true multi-session Lantern concurrency passes on both admitted PostgreSQL majors;
- same-subject race admits one success;
- different-subject race admits two successes;
- producer-permit invalidation and profile-lineage races pass;
- synthetic race residue is zero;
- reconstructed Lantern state remains the expected source-controlled state;
- current producer authority remains zero;
- qualification reports no runtime-installation, producer-authority, or destructive-retirement effect.

Package digest observed in both PG16 and PG17 qualification:
`f30831e49fe91ce207692cc08e87f024aba7da6b273bb33e8d36e3423d928f30`.

## Surviving claim

PR #49 survives as:

`PROVIDER-NEUTRAL_POSTGRESQL_V4_SOURCE_CANDIDATE + PG16_CANONICAL_REBUILD + PG17_MANAGED_ROLE_COMPATIBILITY + CONCURRENCY_QUALIFICATION`

It does **not** establish:

- installed BT2 replacement runtime;
- V4-qualified SQL Connectome runtime;
- current live Lantern cut;
- Project Instructions V4 installation;
- Project files V4 installation;
- fresh-chat Project consumption;
- producer authority;
- merge/deployment effect.

Accordingly, its own required currentness ceiling is correct:

`LANTERN_CURRENTNESS = UNKNOWN`.

## Hostile findings

### H1 — Retired WoWSQL could remain a hidden currentness fallback

**Closed.**

The V4 instructions, handshake, runtime contract, and read contract explicitly
forbid WoWSQL and Supabase fallback.

Historical V1-V3 and provider artifacts remain retained for provenance rather
than deletion.

### H2 — Provider identity could become semantic Lantern identity

**Closed.**

V4 binds semantics to canonical PostgreSQL objects, governed cut/payload state,
and source qualification. Provider/cloud/region are infrastructure metadata.

### H3 — Hard-coded `postgres` ownership would fail on managed non-superuser owners

**Closed for the tested owner model.**

The producer boundary moves from hard-coded `postgres` ownership to
`CURRENT_USER`; boundary assertions distinguish the migration/schema owner
from unrelated non-superuser login roles.

PostgreSQL 17 CI reconstructs under a managed-service-style
`NOSUPERUSER CREATEROLE CREATEDB` owner and passes the canonical oracle.

### H4 — PostgreSQL 17 compatibility could be claimed from syntax alone

**Closed.**

The PG17 path performs blank reconstruction, canonical state oracle, and true
multi-session concurrency qualification rather than merely parsing migrations.

Canonical PostgreSQL remains major 16; major 17 is explicitly compatibility
qualified, not silently promoted to the canonical version.

### H5 — Currentness could be inferred from object presence

**Closed.**

V4 acceptance requires the full governed cut/payload cross-binding and explicitly
states that object presence alone is not parity.

### H6 — Separate auto-commit reads could mix Lantern snapshots

**Closed at contract level.**

The direct contract requires one `REPEATABLE READ READ ONLY` transaction.
The preferred SQL Connectome `lantern_cut(PROJECT_LANTERN)` route is required
to encapsulate the cut and payload in the same governed snapshot.

Runtime implementation/installation of that tool remains separately unqualified.

### H7 — Read success could imply producer authority

**Closed.**

Producer authority is separately reported and remains zero in the reconstructed
qualification subject. V4 repeatedly states that a governed read grants no
write/producer authority.

### H8 — V4 source package could be mistaken for installed runtime

**Closed by explicit source-state fencing.**

`PROJECT_FILES_MANIFEST_V4.json` reports:

- SQL Connectome control schema: installed on replacement development PostgreSQL;
- BT2 runtime reconstruction: NOT_ESTABLISHED;
- Lantern state reconstruction: NOT_ESTABLISHED;
- V4 runtime qualification: NOT_ESTABLISHED;
- Lantern currentness: UNKNOWN.

Protected installation/merge/deploy/producer/retirement effects remain fenced.

### H9 — Project-file source binding and database-package source binding could be conflated

**Survives only with a narrowed interpretation.**

`PROJECT_FILES_MANIFEST_V4.json` names
`payload_source_commit=6098b4ecdf2f34d8a1af443c94baac04f28f0ba5`.

The reviewed PR head is 24 commits ahead of that subject. Comparison confirms
the V4 Project-file payload itself remains blob-bound through the manifest, while
database/build/qualification material has advanced after that payload commit.

Separately, `BUILD_MANIFEST_V3.json` binds the current database package by
exact Git trees and package digest, and the qualification tooling verifies those
tree bindings against the checked-out HEAD.

Therefore:

- `6098b4…` is the immutable payload source subject for the V4 Project files;
- it must **not** be described as the entire current PR #49 database/runtime source;
- PR #49 exact head + BUILD_MANIFEST_V3 package digest is the database source
  qualification subject reviewed here.

This split binding is acceptable because the two scopes are explicit and
independently checked. A future document that collapses them into one source
commit would be stale or false.

### H10 — Source-controlled migrated state could silently become live currentness

**Closed.**

The historical/source-controlled expectation of two visible governed materials
and zero current producer authority is reconstruction evidence only.

V4 currentness still requires live qualified runtime readback and exact cut
cross-binding.

### H11 — CI qualification could mutate production/runtime infrastructure

**Closed for the reviewed workflow.**

The observed PG16/PG17 jobs use disposable CI PostgreSQL services and label
qualification/install/retirement effects as NONE.

No live replacement runtime was installed or modified by this review.

## Remaining limits

1. The replacement development PostgreSQL substrate is not the same thing as a
   qualified BT2 runtime.
2. SQL Connectome's `lantern_cut` implementation is not runtime-qualified by
   this PR merely because the source contract specifies it.
3. Provider-independent backup/restore acceptance remains required.
4. Fresh-chat Project Instructions/files installation and behavioral consumption
   remain unqualified.
5. No current live Lantern state can be reported until those gates pass.
6. Actual provider credentials, networking, TLS, backup policy and operational
   custody remain outside this source qualification.
7. The split Project-file/database binding must remain explicit in future
   reporting.

## Claim ceiling

`BT2_PR49_POSTGRESQL_V4_SOURCE_SURVIVES__PG16_CANONICAL_PG17_COMPAT_AND_CONCURRENCY__NO_RUNTIME_INSTALL_OR_LANTERN_CURRENTNESS`

## Next BT2 frontier

Advance the replacement runtime **without installing Project V4 yet**:

1. reconstruct canonical BT2/Lantern state on the designated replacement
   PostgreSQL runtime from the exact qualified package;
2. independently read back runtime identity and reconstruction evidence;
3. qualify SQL Connectome `platform_status`, `migration_state`, and
   one-snapshot `lantern_cut(PROJECT_LANTERN)`;
4. qualify provider-independent recovery/blank-target restore;
5. only then consider Project Instructions/files V4 installation under separate
   authority.

The stale WoWSQL-resilience PRs should be treated as historical/superseded
frontiers rather than restarted as current work.
