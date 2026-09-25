# Rezon Kernel V0 R21 Non-Nullable Admission State Binding

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R21 is the bounded successor to failed R20 exact subject `71ff317cb2e086088866c551854e8b9e3bca708b`.

R20 preserved mandatory argument syntax, in-process mutual exclusion, and rollback, but a fresh hostile probe showed that explicitly passing `expected_episode_snapshot_digest=None` still disabled the equality check because admission retained nullable bypass logic.

R21 removes that bypass. The supplied value must equal the current canonical EpisodeSnapshot digest exactly.

## Exact ancestry

- failed R20 review head: `71ff317cb2e086088866c551854e8b9e3bca708b`
- failed R20 tree: `b1daee6b5db3e3887835cd89f1072dfaeca477ae`
- R21 branch: `work/rezon-kernel-v0-r21-nonnullable-state-binding`
- R21 RED: `3e3c6fecc20cb9c7337b774aac178de2689b767d`
- executable repair: `3fc81ebd7338e2c84fcd86f317ff1172d975b5df`
- executable tree: `7f6acc07305339464cedcdd69cb68758113d1a5c`
- CI-enablement head: `7ccf6b3dd830938f95f5dd86a5b8253d2472b7fb`
- CI-enablement tree: `8f88e88ef043f73647f54b8400cfc404b5a9c7e4`

## R20 failure — explicit null state-binding bypass

Fresh exact-R20 hostile probe:

1. mutate Episode state;
2. prepare worker output that should be stale relative to an earlier state;
3. call `admit_execution_result()` with:
   `expected_episode_snapshot_digest=None`.

Observed:

- admission succeeded;
- stale output was added to canonical state;
- current state contained both the new input and stale output.

The argument was syntactically required, but runtime semantics still treated explicit `None` as "skip the binding check."

## Frozen RED

R21 freezes:

`tests/test_r21_nonnullable_state_binding.py`

Exact RED head:

`3e3c6fecc20cb9c7337b774aac178de2689b767d`

Predecessor result:

- **1 failed / 0 passed**
- failure: explicit None did not raise AdmissionError.

The regression also requires the Episode snapshot to remain unchanged after rejection.

## R21 repair

The previous nullable condition:

`if expected_episode_snapshot_digest is not None and snapshot_digest != expected_episode_snapshot_digest:`

is replaced with unconditional exact comparison:

`if snapshot_digest != expected_episode_snapshot_digest:`

Consequences:

- omitted argument remains a Python call-signature TypeError;
- explicit None fails closed;
- empty/arbitrary/wrong strings fail closed;
- stale valid digests fail closed;
- only the exact current canonical snapshot digest passes this boundary.

No producer/task/output/rollback/concurrency logic changed.

## Qualification

Focused R16-R21 provenance/state/concurrency/rollback controls after repair:

- **18/18 PASS**

Full local suite after repair:

- **147/147 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact executable repair `3fc81ebd7338e2c84fcd86f317ff1172d975b5df`:

- pytest: **147/147 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact CI-enablement head `7ccf6b3dd830938f95f5dd86a5b8253d2472b7fb`:

- pytest: **147/147 PASS**
- compileall PASS
- diff-check PASS

Hosted GitHub Actions:

- run `35453058686`
- head `7ccf6b3dd830938f95f5dd86a5b8253d2472b7fb`
- overall: **SUCCESS**

## Preserved R16-R20 guarantees

R21 retains:

- admission-owned durable producer identity;
- task-bound canonical production identity;
- canonical input/output hashing;
- opaque actual attempt identity;
- mandatory pre-execution state-binding argument;
- concurrent mutation exclusion through per-Episode RLock;
- exact rollback of current in-memory Episode containers on transaction failure;
- lock release after rollback;
- direct caller producer-forgery rejection;
- stale-state mismatch rejection;
- same task/state/output deterministic replay.

## Explicit scope / non-claims

R21 establishes fail-closed runtime behavior for the state-binding argument under ordinary Python equality semantics.

R21 does NOT establish:

- cryptographic authenticity of the supplied digest;
- runtime enforcement that the caller genuinely obtained the digest from the execution view rather than another trusted source;
- persistence/database rollback;
- crash-consistent durability;
- cross-process/distributed transactionality;
- protection against malicious replacement of source/runtime internals;
- semantic truth;
- independent hostile PASS on the final R21 subject;
- merge authority;
- deployment, installation, activation, runtime effect, training, provider/model mutation, or learned-routing qualification.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
