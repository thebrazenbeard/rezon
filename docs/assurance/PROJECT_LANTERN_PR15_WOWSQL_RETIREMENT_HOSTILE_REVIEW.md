# Rezon Hostile Exact-Head Review — Project Lantern PR #15

Reviewed repository: `thebrazenbeard/project-lantern`  
Reviewed pull request: #15  
Reviewed exact head: `f3c86e0a2d25e760dab5115fe4b220e53d777ad1`  
Reviewed exact base: `8a7c3bada24bae17bcadac8549bc9cd729cfdf17`  
Review class: retired-provider currentness fail-close / successor-boundary review  
Disposition: **SURVIVES_NARROWED_FAIL_CLOSED_CURRENTNESS_GUARD**

## Live authority correction

WoWSQL is retired under current live project authority.

This review does not treat WoWSQL as temporarily unavailable, degraded, or eligible
for fallback.

## Exact qualification

PR #15 is draft, mergeable, and based on the exact current Project Lantern main
head observed for this review.

On the reviewed exact head:

- repository CI passes;
- dependency review passes;
- Python compile passes;
- the new currentness-status regression tests pass;
- no runtime installation, source-effect execution, producer grant, governed
  material append, merge, deploy, credential/permission mutation, or provider
  deletion occurs.

## Surviving claim

PR #15 survives only for:

`PROJECT_LANTERN_SOURCE -> WOWSQL_RETIRED -> NO_QUALIFIED_REPLACEMENT_RUNTIME -> LANTERN_CURRENTNESS_UNKNOWN`

with explicit no-fallback semantics.

It does not establish a replacement Lantern runtime.

## Hostile findings

### H1 — Project Lantern could silently keep treating retired WoWSQL as current

**Closed.**

The package surface now states that WoWSQL is retired from Lantern currentness
and that `LANTERN_CURRENTNESS = UNKNOWN`.

### H2 — An unavailable current backend could trigger an implicit fallback

**Closed.**

The currentness status explicitly rejects fallback to:

- WoWSQL;
- Supabase;
- another unqualified provider;
- Git repository content;
- Project prose;
- benchmark fixtures;
- ChatGPT history;
- model memory or inference.

Historical evidence may still be used as historical evidence when labeled as such.

### H3 — BT2 PR #49 could be laundered into an installed Project Lantern runtime

**Closed.**

Project Lantern names BT2 PR #49 only as the current PostgreSQL/SQL Connectome V4
**source candidate**.

The status and README explicitly state that source existence or source/database
qualification does not establish installation or live Project Lantern currentness.

### H4 — Source/package/runtime/Project effect states could collapse into one PASS

**Closed at the source-contract level.**

The status requires separate reporting of:

- source package readiness;
- database reconstruction;
- runtime qualification;
- Project installation;
- fresh-chat behavioral consumption;
- protected effects.

### H5 — A source currentness guard could itself grant migration authority

**Closed.**

The status explicitly denies authority for replacement-runtime installation,
Project instruction/file changes, producer enablement, material append,
merge/deploy, credential/permission changes, and historical-provider deletion.

### H6 — The repository's minimal runtime surface could be mistaken for a complete backend implementation

**Closed by narrowed wording.**

Project Lantern main currently contains package/benchmark surfaces but does not
itself establish the provider-neutral PostgreSQL runtime defined in BT2.

PR #15 truthfully records that absence rather than manufacturing local runtime
semantics.

## Remaining limits

1. This is a fail-closed **source status contract**, not replacement runtime
   qualification.
2. BT2 PR #49 remains the source candidate for PostgreSQL V4 and is not installed
   here.
3. No live Lantern cut can be reported from Project Lantern until an accepted
   successor runtime is reconstructed and qualified.
4. Project Instructions/files installation remains separately authorized and
   verified.
5. The README/status tests prove source wording and boundaries, not live backend
   behavior.

## Claim ceiling

`PROJECT_LANTERN_PR15_SURVIVES__WOWSQL_RETIRED__CURRENTNESS_UNKNOWN__NO_FALLBACK__SOURCE_GUARD_ONLY`

## Next frontier

Do not add another provider abstraction inside Project Lantern.

The next runtime frontier belongs to BT2's reviewed PostgreSQL V4 reconstruction
and SQL Connectome qualification. Project Lantern should consume that runtime
only after it is separately reconstructed, accepted, and installed under the
appropriate authority.

Until then, Project Lantern currentness remains `UNKNOWN`.
