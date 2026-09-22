# Rezon Kernel V0 R15 Canonical State Digest Binding

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R15 is the bounded successor to failed R14 exact subject `4361191a9abf5f86f070b0a1c2bea14972c8ec76`.

R14 correctly separated opaque per-attempt identity from deterministic canonical producer provenance, but it derived canonical producer identity from `episode_id@event_count`. That value is a version counter, not a content fingerprint. Two divergent canonical states can share the same episode ID and event count and therefore collided under R14.

## Exact ancestry

- failed R14 review head: `4361191a9abf5f86f070b0a1c2bea14972c8ec76`
- failed R14 tree: `056b620e6b7b22f57c4012d38f3f0f91758cdb07`
- R15 branch: `work/rezon-kernel-v0-r15-canonical-state-digest-binding`
- state-collision RED: `84bec288db402854db715196b1dcc0d7020c9a5c`
- executable GREEN: `00f3c0fe3427be250df8d32b280488187a15943c`
- executable GREEN tree: `64bbcd8c0b8f6fe8ad3ce22b05f9718bac699f53`
- CI-enablement head: `8f2b5e28cafa220f6448955c07df230c0a118e17`
- multistep replay regression head: `408f8145c812d0840a5d584ac89f1ad0a6730be0`
- multistep replay tree: `b6f58bb9afe8d23b9af608202ddc4f5986a4ace1`

## R14 failure — same version, different state

Fresh exact-R14 hostile execution constructed two separate Episodes with:

- the same episode ID;
- the same event count / version reference: `same-episode-id@1`;
- different canonical Observation content: `state A` vs `state B`;
- the same strong-independent node/task/policy.

Observed:

- both executions succeeded;
- canonical input states differed;
- R14 canonical producer IDs were identical.

Therefore `episode_id@event_count` could not serve as the canonical state binding for durable producer provenance.

## Frozen RED

R15 froze the failure before production repair:

- test: `tests/test_r15_canonical_state_digest_binding.py`
- exact test-only head: `84bec288db402854db715196b1dcc0d7020c9a5c`
- clean targeted result: **2 failed / 0 passed**

The frozen requirements establish:

1. divergent canonical states with the same episode ID/version must receive distinct canonical snapshot digests and producer IDs;
2. identical canonical states must reproduce the same snapshot digest and canonical producer ID even when opaque attempt UUIDs differ.

## R15 canonical snapshot digest

R15 captures the exact pre-execution `EpisodeSnapshot` once and uses that same object for:

- canonical snapshot digest computation;
- `ExecutionView` construction.

The digest is:

1. `dataclasses.asdict(snapshot)`;
2. canonical JSON encoding with sorted keys, compact separators, UTF-8, and `ensure_ascii=False`;
3. SHA-256 over those bytes.

The resulting `canonical_episode_snapshot_digest` is audit/canonical metadata only. It is never injected into the strong-independent executor-facing view.

## Canonical producer identity

R15 derives durable producer provenance from:

- node ID;
- exact canonical pre-execution EpisodeSnapshot digest;
- exact executor-visible TaskSpecification digest, or explicit `no-task-spec`.

Format remains:

`canonical:exec:<node_id>:<sha256(...)>`

The opaque worker attempt ID remains independent:

`independent:exec:<node_id>:<uuid4-hex>`

Thus:

- attempt identity is unique and opaque per actual execution;
- canonical producer identity is deterministic for identical canonical execution conditions;
- different state contents at the same version cannot silently collide;
- state/history details remain audit-side and are not exposed to the independent worker.

## Trace binding

`TraceRecord` now records:

- `execution_id` — opaque actual attempt identity;
- `canonical_producer_execution_id` — deterministic durable producer identity;
- `canonical_episode_snapshot_digest` — exact pre-execution canonical state fingerprint used in that derivation.

Normal, exception, and preflight trace paths bind the same snapshot digest captured for the execution.

## Multistep replay determinism

After the first R15 executable repair passed, a stronger recursive replay probe was promoted into a permanent regression.

Two complete two-step sequences used:

- the same initial canonical episode;
- the same task/node/policy;
- deterministic semantic outputs;
- different UUID attempt identities on every step.

Observed:

- attempt IDs differed on step 1 and step 2;
- first-step canonical snapshots were equal across replays;
- final second-step canonical snapshots were equal across replays;
- step-1 canonical snapshot digests matched;
- step-2 canonical snapshot digests matched;
- step-1 canonical producer IDs matched;
- step-2 canonical producer IDs matched;
- all receipts had no failures.

This proves the deterministic producer/digest chain recursively reproduces across multiple canonical mutations despite different attempt UUIDs.

The permanent regression was added at exact head:

`408f8145c812d0840a5d584ac89f1ad0a6730be0`

## Exact executable qualification

Fresh clean checkout of exact executable head `00f3c0fe3427be250df8d32b280488187a15943c` under CPython 3.12:

- pytest: **128 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS

Focused R12-R15 identity/isolation controls before push:

- **10/10 PASS**

Hosted GitHub Actions on CI-enablement head `8f2b5e28cafa220f6448955c07df230c0a118e17`:

- run: `35405320414`
- overall: **success**

## Exact multistep-regression qualification

Fresh clean checkout of exact head `408f8145c812d0840a5d584ac89f1ad0a6730be0`:

- pytest: **129 passed / 0 failed**
- compileall: PASS
- diff-check: PASS

Hosted GitHub Actions:

- run: `35405464016`
- overall: **success**

## Preserved R9-R14 controls

R15 retains:

- TaskEnvelope context refs fail closed for strong independence;
- strong-independent executor receives only the TaskSpecification surface;
- task ID / authority / privacy / budget / auxiliary context remain absent from that surface;
- executor-facing independence metadata is empty while runner/audit attestation remains authoritative;
- executor-visible episode version remains `independent@0`;
- opaque UUID-backed attempt IDs remain unique;
- attempt IDs do not expose task/history/order metadata;
- worker result/proposition/relation IDs must bind the exact issued attempt ID before admission;
- admitted canonical proposition/relation producer provenance is runner-controlled;
- identical canonical executions replay deterministically;
- divergent same-version canonical states are distinguished by content digest.

## Explicit trust boundaries / non-claims

R15 does not establish:

- independent hostile PASS on the final R15 subject;
- cryptographic authentication of snapshot digest or producer identity;
- semantic truth of canonical state content;
- cross-runtime/cross-language canonicalization guarantees beyond the current Python 3.12 V0 contract;
- collision impossibility beyond the chosen SHA-256 construction;
- protection against a malicious trusted orchestrator fabricating canonical state;
- a qualified shared-context/shared-read independence class;
- merge authority;
- deployment, installation, activation, runtime effect, provider/model mutation, or learned-routing qualification;
- reasoning superiority.

The canonical snapshot digest is a deterministic provenance binding, not evidence, authority, truth, or consent.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
