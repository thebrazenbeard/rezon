# Rezon Kernel V0 R20 Admission Transaction Rollback

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R20 is the bounded successor to failed R19 exact subject `c180441157c7fb4a52c128455237485e96884be9`.

R19 made execution-result admission mutually exclusive for one in-process Episode object using a shared reentrant lock. A fresh exact-head hostile probe then showed that a commit-stage exception after one emitted object had already been inserted could still leave a durable prefix of the failed execution result in canonical state.

R20 keeps the R19 lock and adds exact in-memory transaction rollback.

## Exact ancestry

- failed R19 review head: `c180441157c7fb4a52c128455237485e96884be9`
- failed R19 tree: `ed825d0857fcc7c30e05c61dcb6395447f4838e3`
- R20 branch: `work/rezon-kernel-v0-r20-transaction-rollback`
- R20 RED: `6fe033f9231fffce44c45fe39e8e91e1bdd2931f`
- executable repair: `b699b684b78b7fcdf37e6a827bde46c299a4e824`
- executable tree: `a1846d91b1955aa42fb2671aa40990cd0ede68ce`
- CI-enablement head: `b7370c7c3f1334960d5dc13617f4992ff10b5e4d`
- CI-enablement tree: `74696e5d5bea5adfb1df02b83b875884686b8c78`

## R19 failure — partial commit after admission failure

Fresh exact-R19 hostile probe used a valid multi-object ExecutionResult containing:

- one emitted proposition;
- one emitted relation referencing that proposition.

The probe injected a deterministic `EpisodeInvariantError` at relation insertion, after proposition insertion had already succeeded.

Observed:

- admission raised `AdmissionError`;
- proposition `h1` remained current;
- relation `rel1` was absent;
- the event log retained `proposition_added:h1`;
- `PARTIAL_COMMIT = True`.

Therefore R19 provided lock-based mutual exclusion but not all-or-nothing mutation semantics.

## Frozen RED

R20 froze two requirements in:

`tests/test_r20_transaction_rollback.py`

Exact RED head:

`6fe033f9231fffce44c45fe39e8e91e1bdd2931f`

Predecessor result:

- rollback snapshot test: FAIL;
- post-failure state test: FAIL;
- exact targeted total: **2 failed / 0 passed**.

Required behavior:

1. failed multi-object admission restores the exact pre-call EpisodeSnapshot;
2. the Episode lock is released after rollback so a later thread may mutate normally.

## R20 repair

`Episode.atomic_mutation()` still acquires the per-Episode `threading.RLock`.

After acquiring that lock it now checkpoints:

- proposition dictionary;
- relation dictionary;
- active proposition set;
- active relation set;
- event list.

The canonical objects stored in those containers are frozen dataclasses, so shallow container copies are sufficient for the current V0 in-memory model.

The guarded operation runs normally.

On any `BaseException`:

- all five canonical state containers are restored from the checkpoint;
- the exception is re-raised;
- normal context-manager exit releases the RLock.

Execution-result admission continues to hold this guard across state verification, validation, prevalidation, mutation, and receipt construction.

## Why BaseException

Rollback is state-integrity cleanup, not error suppression.

The guard restores canonical state before re-raising any exceptional control flow, including ordinary exceptions and process-level interruption classes that inherit from `BaseException`.

R20 does not swallow or convert those exceptions; it only restores the pre-transaction in-memory state before propagation.

## Qualification

Focused R16-R20 provenance/state/concurrency/rollback controls after repair:

- **17/17 PASS**

Full local suite after repair:

- **146/146 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact executable repair `b699b684b78b7fcdf37e6a827bde46c299a4e824`:

- pytest: **146/146 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact CI-enablement head `b7370c7c3f1334960d5dc13617f4992ff10b5e4d`:

- pytest: **146/146 PASS**
- compileall PASS
- diff-check PASS

Hosted GitHub Actions:

- run `35452535604`
- head `b7370c7c3f1334960d5dc13617f4992ff10b5e4d`
- overall: **SUCCESS**

## Preserved R19 concurrency behavior

R20 retains the R19 deterministic thread-race protection:

- concurrent mutation may attempt to acquire the Episode lock;
- it cannot interleave inside execution-result admission;
- successful admission commits before the competing mutation proceeds;
- reentrant nested snapshot/add/relation calls remain supported under the same RLock.

Rollback adds failure atomicity without weakening successful-path mutual exclusion.

## Explicit scope / non-claims

R20 establishes best-effort all-or-nothing restoration for the current in-memory canonical Episode structures when mutation occurs inside `Episode.atomic_mutation()`.

R20 does NOT establish:

- persistence/database rollback;
- crash-consistent durability across process termination or power loss;
- cross-process locking;
- distributed transactions;
- coordination across distinct Episode objects representing one logical episode;
- rollback of external side effects performed by arbitrary caller code while the guard is held;
- protection against malicious direct mutation of private Episode internals;
- cryptographic authentication of state/task/output;
- semantic truth;
- independent hostile PASS on the final R20 subject;
- merge authority;
- deployment, installation, activation, runtime effect, training, provider/model mutation, or learned-routing qualification.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
