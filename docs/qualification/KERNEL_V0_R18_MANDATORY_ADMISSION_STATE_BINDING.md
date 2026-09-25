# Rezon Kernel V0 R18 Mandatory Admission State Binding

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R18 is the bounded successor to failed R17 exact subject `5369f7e14cc8d732f3dc61717ed196c4f1b9a6ca`.

R17 correctly bound durable producer identity to canonical input state, executor-visible TaskSpecification, and canonical output while preserving admission ownership. A fresh hostile probe then found that the public admission API still allowed callers to omit the expected pre-execution snapshot digest entirely. A stale worker result could therefore be admitted after canonical state changed, because admission simply rebound it to the new state at mutation time.

R18 makes pre-execution state binding mandatory for every execution-result admission.

## Exact ancestry

- failed R17 review head: `5369f7e14cc8d732f3dc61717ed196c4f1b9a6ca`
- failed R17 tree: `8bd573933e0fac4278662d288d8b6051d475c452`
- R18 branch: `work/rezon-kernel-v0-r18-mandatory-state-binding`
- R18 RED: `84b282344b4575f09a07df09d29b634684ce4b81`
- executable repair: `20483207680a7c80013712b4f652c8cd805906d6`
- executable tree: `e98e9662fb2524eef402947f3d7d1d8fcc8888b4`
- CI enablement: `80af2bf6715f3a80110a7cc0705d05ba831bcbe7`

## R17 failure — optional stale-state binding

Fresh exact-R17 hostile probe:

1. captured canonical digest of an empty Episode;
2. created a worker result representing computation from that old state;
3. mutated the Episode by adding a new Observation;
4. called public `admit_execution_result()` with the stale result while omitting `expected_episode_snapshot_digest`.

Observed:

- captured digest and mutation-time digest differed;
- admission succeeded;
- stale output was durably added alongside the new input.

This bypassed the claimed stale-state / TOCTOU guarantee by simply not supplying the optional binding.

## Frozen RED

R18 froze the public API contract before production repair:

- test: `tests/test_r18_mandatory_state_binding.py`
- exact test-only head: `84b282344b4575f09a07df09d29b634684ce4b81`
- targeted result: **1 failed / 2 passed**

The failing requirement:

- omission of the pre-execution snapshot digest must be impossible.

The already-passing controls:

- an explicit current-state digest admits normally;
- an explicit stale digest fails without mutating canonical state.

## R18 repair

`admit_execution_result()` now requires this keyword for every call:

`expected_episode_snapshot_digest: str`

There is no default and no implicit fallback to current state.

Admission still:

1. computes the actual current canonical EpisodeSnapshot digest at mutation time;
2. requires exact equality with the caller's pre-execution binding;
3. rejects mismatch before durable mutation;
4. performs all existing node, attempt, source, output, task, and relation checks;
5. derives canonical producer identity internally;
6. returns the exact AdmissionReceipt readback.

The runner already supplied the exact digest captured from the snapshot used to build the ExecutionView, so production runner behavior required no semantic redesign.

## Direct/local admission callers

Historical direct-admission tests were updated to state their intended canonical input state explicitly by calculating:

`canonical_episode_snapshot_digest(ep.snapshot())`

immediately at the call boundary.

This preserves the previous test intent while removing an API mode that silently meant "whatever state exists when admission runs."

The direct-admission producer-forgery test also supplies the explicit state digest, so its expected TypeError still tests the forbidden caller-selected `canonical_producer_execution_id` argument rather than accidentally passing because another required argument is missing.

## Call-path audit

Fresh source audit on R18 found:

- one definition of `admit_execution_result()`;
- one production caller: `EpisodeRunner`;
- direct calls otherwise occur only in tests.

Direct Episode mutation sites in `src/rezon` are:

- execution-result mutation inside `admission.py`;
- separately governed retrieval-evidence admission inside `retrieval.py`.

No alternate execution-result mutation path was found that bypasses the mandatory state-binding API.

## Qualification

R18 focused contract controls after repair:

- R18 mandatory-state binding;
- R17 task-bound production identity;
- R16 admission-owned producer control;
- R16 canonical production-event identity.

Result:

- **14/14 PASS**

Full local suite after repair:

- **143/143 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact executable repair `20483207680a7c80013712b4f652c8cd805906d6`:

- pytest: **143/143 PASS**
- compileall PASS
- diff-check PASS

Hosted CI-enablement head `80af2bf6715f3a80110a7cc0705d05ba831bcbe7`:

- run `35410572521`
- overall: **SUCCESS**

## Preserved R9-R17 controls

R18 retains:

- strong-independent task-surface isolation;
- executor-hidden canonical state/history metadata;
- unique opaque actual attempt IDs;
- deterministic canonical input-state digest;
- deterministic canonical output digest;
- task-bound canonical production identity;
- admission-owned durable producer identity;
- exact attempt provenance validation before canonical rewrite;
- no-output/failed/preflight/exception no-producer semantics;
- proposition and relation output coverage;
- direct producer-forgery rejection;
- stale-state mismatch rejection;
- same task/state/output deterministic replay;
- different state, task, or output changes durable producer identity.

## Reported provenance clarification

A separate exact-R17 self-hostile probe showed that top-level `ExecutionResult.source_refs/source_versions` may contain worker-reported values not present in governed consumed provenance.

Existing Mune regressions explicitly define this as intentional:

- `TraceRecord.source_refs/source_versions` are governed consumed provenance;
- `TraceRecord.reported_source_refs/reported_source_versions` preserve the worker's self-report for audit;
- worker-reported values do not enter the ResultReceipt's governed source versions;
- fabricated provenance on emitted durable propositions/relations still fails admission.

This was therefore classified as an intentional diagnostic boundary, not a source defect.

## Explicit non-claims

R18 does not establish:

- fresh independent hostile PASS on the final R18 subject;
- cryptographic executor/model/provider identity;
- cryptographic authenticity of the supplied pre-execution digest;
- protection against a malicious trusted process that controls both snapshot capture and admission;
- semantic truth of state/task/output;
- cross-language canonicalization outside current Python 3.12 V0;
- SHA-256 collision impossibility;
- merge authority;
- deployment, installation, activation, runtime effect, training, provider/model mutation, or learned-routing qualification;
- reasoning superiority.

The mandatory digest closes omission/rebinding at the admission API boundary. It is a provenance/TOCTOU binding, not an authority credential.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
