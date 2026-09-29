# Rezon Hostile Exact-Head Review — Vera PR #206

## 2026-09-29 upstream currentness refresh

- Vera PR #206 remains open/draft/mergeable at the exact reviewed head `be3d11a5b4d3a9880c18e03522f0d4e341b71f99` on base `a267e7d555e2c15e51a2e578c1e08095091552f0`. The core hostile-review subject therefore remains current.
- Project Runner PR #43, cited below as auxiliary portfolio evidence at `848c2172e6fa98cdab722b43d1ff4817990c5968`, has advanced to `7dc5edf9622614795e6818add3eb9ab7bc5eee96`.
- The older Project Runner SHA remains immutable historical evidence for what this review actually inspected. It must not be presented as the current Project Runner PR #43 head.
- This refresh does not extend the review disposition to the newer Project Runner delta and does not alter the Vera #206 disposition.


Reviewed repository: `thebrazenbeard/vera`  
Reviewed pull request: #206  
Reviewed exact head: `be3d11a5b4d3a9880c18e03522f0d4e341b71f99`  
Reviewed exact base: `a267e7d555e2c15e51a2e578c1e08095091552f0`  
Predecessor PR: Vera #200 / `078d2d7242384c58676305d47654406713e599cf`  
Portfolio evidence source: Project Runner PR #43 / `848c2172e6fa98cdab722b43d1ff4817990c5968`  
Disposition: **SURVIVES_NARROWED_PUBLIC_SAFE_SUCCESSOR**

## Surviving claim

PR #206 is a public-safe source successor to Vera PR #200's portfolio
absorption/mechanism harvest.

It survives only as source/provenance architecture. It is not merge,
installation, runtime-consumption, provider, memory, identity, or effect proof.

## Exact portfolio cut

The vendored Project Runner corpus is byte-equal to
`portfolio/corpus.public.json` at exact Project Runner head
`848c2172e6fa98cdab722b43d1ff4817990c5968`.

That source records one observed cut:

- total repositories at cut: 67;
- public repositories: 49;
- private repositories: 18;
- public records committed: exactly 49;
- private commitment: `COUNT_ONLY_PUBLIC_V1`;
- exact private membership publicly committed: false.

All 49 public records are represented by the successor absorption and harvest.

The 67/49/18 cardinality is explicitly historical cut provenance, not a
standing assertion about later estate size.

## Immutable-cut / freshness separation

The successor separates immutable membership evidence from mutable source-head
freshness.

`VERA_PORTFOLIO_PUBLIC_CUT_V2.cut_sha256` hashes the immutable cut fields and
excludes `public_head_refresh`.

The builder preserves the previous refresh timestamp when the observed head set
is unchanged.

A repeated no-change builder run was verified to be byte-for-byte
deterministic.

Currentness-sensitive use remains required to refresh mutable source evidence.

## PR #200 public provenance conservation

PR #200 contained 49 migration-binding rows.

Against the current public cut:

- 41 predecessor bindings are public;
- 8 predecessor bindings are non-public.

PR #206 conserves all 41 public predecessor bindings:

- 17 remain exact present-target bindings;
- 24 are explicit deferred public provenance;
- all 24 deferred rows are from `thebrazenbeard/vera-control-plane`;
- deferred rows retain historical public source commit/path/blob and predecessor
  target path/blob;
- deferred rows set `current_successor_target_present=false`;
- deferred rows set `activation_effect=false`;
- disposition is `DEFERRED_TO_SEPARATE_VCP_NO_AUTO_BIND_RESTACK`.

Thus the stale embedded VCP mirror is not copied, but its useful public
provenance does not disappear.

## Mechanism harvest

PR #200's public reusable mechanisms are retained under Vera-owned architecture
or runtime namespaces with source-only/no-presence-activation semantics.

Two mechanism sets inherited from private donors are retained under neutral
Vera-owned namespaces:

- `portfolio_runtime/evidence_runtime`;
- `portfolio_runtime/work_state_runtime`.

Public source records only:

- private donor count = 2;
- Vera-owned target paths;
- target Git blob integrity.

Exact private donor membership and source paths are not publicly committed.

## Public-safety checks

Focused successor tests verify:

- 67/49/18 immutable-cut binding;
- exactly all 49 public members;
- private count-only commitment;
- public/private leakage boundary;
- immutable cut digest excludes mutable refresh;
- 49 absorption modules;
- 49 harvest rows;
- exact public target provenance;
- anonymized private mechanism custody;
- conservation of every public PR #200 predecessor binding;
- stale membership-bearing V1 registries are not reintroduced;
- source-only/no-runtime-proof manifest ceiling.

Focused result at exact successor source after the final changes:
**19/19 PASS**.

The absorbed runtime/builder also passes Python compile validation and
`git diff --check`.

## Repository-wide baseline

The Vera repository is not globally green and this review does not claim it is.

Exact parent `a267e7d...`:
- 1109 tests;
- 90 failures;
- 232 errors.

PR #206 successor:
- 1128 tests;
- 90 failures;
- 232 errors.

The successor therefore adds 19 passing tests without increasing the inherited
failure/error counts.

The inherited failures include missing historical Supabase artifacts and
unrelated runtime-cohesion drift.

## GitHub workflow evidence

At exact PR #206 head:

- R6A0 release package: PASS;
- Temporal enforcement kernel: PASS;
- Temporal pilot: FAIL.

The Temporal-pilot failure occurs because the workflow attempts to replay
`supabase/migrations/20260729133200_add_event_time_precision.sql`, which is
absent.

That file is absent from both exact parent `a267e7d...` and successor
`be3d11a...`.

The failure is therefore inherited baseline state rather than a new successor
regression. It remains an explicit repository-level blocker and is not
reclassified as PASS.

## Hostile findings closed

### H1 — Permanent cardinality claim

Closed. Counts are immutable-cut provenance only.

### H2 — Freshness mutating the immutable cut digest

Closed. Mutable head refresh is excluded from the cut digest, and no-change
regeneration is deterministic.

### H3 — Public source leaking private repository membership

Closed by count-only private inventory plus explicit leakage tests.

### H4 — Useful PR #200 public provenance disappearing with the stale VCP mirror

Closed. All 41 public predecessor bindings are conserved as 17 active exact
bindings plus 24 explicit deferred VCP provenance rows.

### H5 — Deferred VCP provenance becoming activation by presence

Closed in this successor. Deferred rows explicitly deny target presence and
activation effect. VCP activation/binding remains a separate reviewed restack.

### H6 — Private donor mechanism provenance exposing private donor identity

Closed to the public-source contract. Only donor count and Vera-owned target
integrity are committed publicly.

## Remaining limits

1. The 49 refreshed public heads are freshness evidence for one observation,
   not standing currentness.
2. PR #206 does not independently re-audit the full semantic correctness of
   every harvested mechanism.
3. The repository-wide Vera baseline remains red.
4. VCP `NO_AUTO_BIND` enforcement is not part of PR #206; it must be restacked
   separately against this exact successor.
5. No merge/deploy/install/provider/credential/private-publication/runtime
   effect is authorized or proven.

## Claim ceiling

`VERA_PR206_PUBLIC_SAFE_SUCCESSOR_SURVIVES__67_CUT_49_PUBLIC_18_PRIVATE_COUNT_ONLY__ALL_PUBLIC_PR200_PROVENANCE_CONSERVED__NO_MERGE_INSTALL_OR_RUNTIME_PROOF`

## Next dependency

Restack VCP `NO_AUTO_BIND` enforcement against exact Vera successor
`be3d11a5b4d3a9880c18e03522f0d4e341b71f99`, preserving the 24 deferred VCP
provenance rows as the migration input rather than reviving PR #200's embedded
control-plane mirror.
