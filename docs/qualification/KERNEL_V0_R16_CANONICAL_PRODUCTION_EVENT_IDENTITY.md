# Rezon Kernel V0 R16 Canonical Production Event Identity

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R16 is the bounded successor to failed R15 exact subject `b6256a487727caf8e1bc0425651d8699e86afb44`.

R15 bound durable producer provenance to the exact pre-execution canonical EpisodeSnapshot digest, fixing R14's same-version state collision. A fresh retry/no-output hostile probe then exposed a different ambiguity: two distinct actual attempts from the same unchanged canonical state shared one canonical producer ID even though the first produced nothing and the second produced the durable proposition.

R16 separates actual attempt identity, canonical input-state identity, attempted output identity, and admitted durable production identity.

## Exact ancestry

- failed R15 review head: `b6256a487727caf8e1bc0425651d8699e86afb44`
- failed R15 tree: `49338a95c0d6ea954ec8162b8484209c7ee3b6d3`
- R16 branch: `work/rezon-kernel-v0-r16-canonical-production-event-identity`
- production-event RED: `403260481da77711f47d9a8a6329bba8a59c6e4f`
- initial executable repair: `2f0ad4de662c45943ca38951c1103a3fb0ff47f4`
- CI enablement: `1dea29d497db8eb4878f9eec4807bb639f8a42f8`
- relation fixture attempt: `67c36913af626071f600dbe0fe87c5b7ab04c924`
- relation fixture correction attempt: `8f37e93094f7e4a7cc0b5e39f30d72e0fa030dac`
- corrected relation regression: `315cfc367e844a762a787940e1e70ab8166c1c9b`
- failed-output regression: `d69011204e42e7dcdd017f828e35f642f0edaf33`
- admission-control RED: `227302fab81c2b17e440cb1adf239d08618c993d`
- admission-owned provenance repair: `65a431c0410592be602e5587434e8910b9adbfc4`
- repair tree: `89db5185e02b6aaf484ecce09284810450b3dec2`

## R15 failure — retry/no-output provenance ambiguity

Fresh exact-R15 probe ran the same node twice against an unchanged Episode:

1. first actual attempt returned a successful ExecutionResult with no propositions or relations;
2. canonical state therefore remained unchanged;
3. second actual attempt started from the same canonical snapshot and emitted proposition `h-retry`;
4. actual attempt UUIDs differed.

Observed:

- `STATE_UNCHANGED_AFTER_FIRST=True`
- `ATTEMPT_IDS_EQUAL=False`
- `SNAPSHOT_DIGESTS_EQUAL=True`
- `CANONICAL_PRODUCER_IDS_EQUAL=True`
- first emitted IDs: empty
- second emitted IDs: `h-retry`
- durable proposition producer ID matched the canonical producer ID attached to both attempts
- both receipts had no failures

Therefore input-state identity alone was insufficient to identify a durable production event.

## Frozen production-event RED

R16 froze the intended semantics before production repair:

- test: `tests/test_r16_canonical_production_event_identity.py`
- exact test-only head: `403260481da77711f47d9a8a6329bba8a59c6e4f`
- clean targeted result: **3 failed / 0 passed**

Requirements:

1. a successful no-output attempt has no canonical output digest and no durable canonical producer ID;
2. a later producing retry from the same canonical state gets a durable producer ID;
3. same canonical input + same semantic durable output reproduces one canonical output digest and producer ID despite different attempt UUIDs;
4. same canonical input + different durable output yields different output digests and producer IDs.

## R16 provenance model

R16 distinguishes:

### Actual attempt identity

Strong-independent execution attempt:

`independent:exec:<node_id>:<uuid4-hex>`

Properties:

- unique per actual attempt;
- opaque to task/history/order;
- presented to the executor;
- required on ExecutionResult and worker-emitted proposition/relation producer fields before admission;
- never used directly as durable canonical producer provenance.

### Canonical input-state digest

The exact pre-execution EpisodeSnapshot is canonically serialized and SHA-256 hashed.

This value remains runner/admission/audit-side and is not injected into the strong-independent executor view.

### Canonical output digest

If a result contains emitted propositions and/or relations, R16 computes a canonical SHA-256 digest over the durable output structure after replacing each worker-supplied random `producer_execution_id` with `None`.

Thus random attempt UUIDs do not contaminate deterministic durable-output identity while all semantic proposition/relation fields remain part of the digest.

A no-output result has:

`canonical_output_digest = None`

### Canonical durable producer identity

Only an admissible durable production event receives a producer identity.

It derives from:

- validated node ID;
- exact canonical pre-admission EpisodeSnapshot digest;
- canonical output digest.

Format:

`canonical:exec:<node_id>:<sha256(...)>`

It does not identify a no-output attempt, failed attempt, exception, or preflight rejection.

## Admission owns durable provenance

A later hostile boundary probe found that exact R16 predecessor `d690112…` still exposed this parameter:

`canonical_producer_execution_id=`

A direct caller could supply `forged-canonical-producer`, pass the ordinary attempt checks, and admission would write that arbitrary string into canonical proposition provenance.

Observed:

- `DURABLE_PRODUCER=forged-canonical-producer`
- `FORGE_ACCEPTED=True`

R16 therefore froze a second RED:

- test: `tests/test_r16_admission_producer_control.py`
- exact test-only head: `227302fab81c2b17e440cb1adf239d08618c993d`
- clean targeted result: **2 failed / 0 passed**

The repair at `65a431c…` makes the mutation boundary itself authoritative for canonical producer derivation.

## Shared provenance module

R16 adds:

`src/rezon/provenance.py`

It is the single implementation for:

- `canonical_episode_snapshot_digest(snapshot)`
- `canonical_output_digest(result)`
- `canonical_producer_execution_id(node_id, episode_snapshot_digest, output_digest)`

Runner and admission no longer carry independent implementations of this hashing logic.

## AdmissionReceipt

`admit_execution_result(...)` now returns an immutable AdmissionReceipt containing:

- exact current canonical EpisodeSnapshot digest used at mutation time;
- canonical attempted output digest, if output exists;
- canonical durable producer execution ID, if durable output was admitted.

The caller cannot supply a canonical producer ID.

Admission itself:

1. validates descriptor/result identity;
2. validates exact opaque attempt provenance on every emitted proposition/relation;
3. rejects failed results;
4. computes the actual current canonical episode digest;
5. optionally verifies it equals the runner's expected pre-execution digest;
6. computes canonical output digest;
7. derives canonical producer ID internally;
8. applies all existing kind/source/relation/provenance checks;
9. rewrites admitted producer provenance only after those checks;
10. mutates Episode;
11. returns the exact provenance readback receipt.

The runner records the returned receipt rather than manufacturing a parallel producer ID.

## Stale-state / TOCTOU protection

A permanent regression captures the pre-execution snapshot digest, mutates the Episode, then attempts to admit a result against the stale digest.

Admission must fail with:

`canonical episode state changed after execution view was captured`

and must not apply the stale result.

This binds execution-view state to mutation-time state rather than assuming no intervening mutation.

## No-output / failed / exception / preflight semantics

R16 preserves:

- no-output attempt -> no durable producer ID;
- preflight failure -> no durable producer ID;
- executor exception -> no durable producer ID;
- result carrying FailureState -> no mutation and no durable producer ID.

A failed result may still have an attempted output digest in trace because output bytes existed, but that digest does not become admitted producer provenance.

## Proposition and relation coverage

R16 permanently tests both durable output classes.

For propositions:

- same input + same semantic output + different attempt UUID => same output digest / producer ID / canonical snapshot;
- same input + different content => different output digest / producer ID.

For relations:

- same input + same semantic relation + different attempt UUID => same output digest / producer ID / canonical snapshot;
- changing a semantic relation participant role changes output digest and producer ID;
- admitted relation producer provenance equals admission-derived canonical producer ID.

## Relation test-harness failures — explicitly not production failures

Two intermediate hosted runs failed because the new relation regression did not reach production logic.

`67c36913…` / hosted run `35406948888`:
- test created a relation-only node that the V0 deterministic scheduler never schedules;
- result: no trace record; test failed with IndexError.

`8f37e930…` / hosted run `35407017200`:
- output-kind shape was adjusted but the node ID remained outside the scheduler's fixed V0 rule names;
- again no production execution occurred.

Review of `src/rezon/scheduler.py` confirmed V0 scheduling is intentionally name/rule based for:
- mandatory verification nodes;
- `contradiction_scanner`;
- `echo_hypothesis`;
- `falsifier`.

The fixture was then corrected to execute through the real `echo_hypothesis` scheduler path while emitting only the relation under test.

Corrected exact head `315cfc367e844a762a787940e1e70ab8166c1c9b`:
- fresh local: **134/134 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35407072061`: SUCCESS

These earlier failures are test-harness evidence and must not be mislabeled as production semantic failures.

## Failed-output regression

Exact head `d69011204e42e7dcdd017f828e35f642f0edaf33` adds a worker result containing both emitted output and `FailureState.CONTRACT_VIOLATION`.

Required behavior:
- attempted canonical output digest exists;
- durable canonical producer ID remains None;
- admitted emitted IDs remain empty;
- Episode does not mutate.

Qualification:
- fresh local: **135/135 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35407133216`: SUCCESS

## Final admission-owned provenance qualification

Local repair work after admission-control RED additionally freezes stale-state rejection.

Focused controls:
- admission producer control;
- R16 canonical production-event identity;
- R15 canonical state-digest regressions.

Result: **12/12 PASS**

Full local suite before commit:
- **138/138 PASS**
- compileall PASS
- diff-check PASS

Exact pushed repair:

`65a431c0410592be602e5587434e8910b9adbfc4`

Fresh clean checkout under CPython 3.12:
- pytest: **138/138 PASS**
- compileall: PASS
- diff-check: PASS

Hosted GitHub Actions:
- run `35407770031`
- overall: **SUCCESS**

## Preserved R9-R15 controls

R16 retains:

- auxiliary TaskEnvelope context refs fail closed for strong independence;
- strong-independent executor receives TaskSpecification rather than full TaskEnvelope;
- task ID / authority / privacy / budget / auxiliary context stay absent from allowed task specification;
- executor-facing independence metadata is empty while complete attestation remains runner/audit-side;
- executor-visible episode version remains `independent@0`;
- opaque actual attempt IDs remain unique;
- attempt ID does not reveal task/history/order metadata;
- exact worker attempt provenance is required before any canonical rewrite;
- random attempt IDs do not contaminate canonical state;
- divergent same-version canonical states get different state digests;
- identical canonical multi-step replays reproduce exact canonical state chains;
- no-output attempts cannot claim durable producer provenance;
- semantic output differences change canonical production identity;
- direct callers cannot choose canonical producer identity;
- stale execution views cannot mutate a changed canonical state.

## Explicit trust boundaries / non-claims

R16 does not establish:

- fresh independent hostile PASS on the final R16 review head;
- cryptographic authentication of executor/model/provider identity;
- semantic truth of canonical state or output;
- cross-language canonicalization guarantees outside the current Python 3.12 V0 contract;
- SHA-256 collision impossibility;
- protection against a malicious trusted process mutating Python objects or source code;
- a qualified shared-context/shared-read independence class;
- merge authority;
- deployment, installation, activation, runtime effect, provider/model mutation, training, or learned-routing qualification;
- reasoning superiority.

Snapshot/output hashes and canonical producer IDs are deterministic provenance bindings. They are not evidence, truth, authorization, consent, or security credentials.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
