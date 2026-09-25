# Rezon Kernel V0 R23 Exact TaskSpecification Admission Boundary

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R23 is the bounded successor to failed R22 exact subject `f367ef6776fa98ffe6cf455a4101674e8e244a4b`.

R22 hardened the state-binding input against caller-controlled equality. A fresh hostile probe then found a separate provenance bypass: the `task_specification: TaskSpecification | None` annotation was not runtime-enforced. Any duck-typed object exposing a caller-chosen `.digest` value could be accepted, reopening a raw task-digest injection path into canonical producer identity.

R23 allows either the explicit no-task path (`None`) or an exact built-in `TaskSpecification` instance.

## Exact ancestry

- failed R22 review head: `f367ef6776fa98ffe6cf455a4101674e8e244a4b`
- failed R22 tree: `cf29ac76c34bd12ffcd457e5a383c8fb3bc0d5e0`
- R23 branch: `work/rezon-kernel-v0-r23-exact-task-specification`
- R23 RED: `ae58f7b753979ff4d8c35881a4bcd1c667da9e55`
- executable repair: `348200dbe6b9186df7c9a4f41c80044b01323062`
- executable tree: `bddbe7d8b2e8a2c5be527ef5a050358274d6bb9c`
- CI-enablement head: `fd753cf4b2e7e11249a3683225dfbbac65e5aa4d`
- CI-enablement tree: `60d4de292f43c02a8e29ea88f60c0e07bb138074`

## R22 failure — duck-typed task digest injection

Fresh exact-R22 hostile probe supplied a non-`TaskSpecification` object with a caller-selected `.digest`.

Observed:

- caller-selected digest `aaaaaaaa...` was accepted;
- caller-selected digest `bbbbbbbb...` was accepted;
- AdmissionReceipt reflected each selected digest;
- otherwise identical state/output admissions produced different canonical producer IDs solely because the fake object selected a different digest.

This violated the R17/R22 boundary intent that admission derive task provenance from a structured TaskSpecification rather than accept a raw caller-selected digest.

## Frozen RED

R23 freezes four cases in:

`tests/test_r23_exact_task_specification.py`

Exact RED head:

`ae58f7b753979ff4d8c35881a4bcd1c667da9e55`

Fresh predecessor result:

- arbitrary duck-typed task object: FAIL;
- `TaskSpecification` subclass overriding digest: FAIL;
- exact `TaskSpecification`: PASS;
- explicit `None` no-task path: PASS;
- exact targeted total: **2 failed / 2 passed**.

## R23 repair

Before reading `.digest`, admission now requires:

`task_specification is None OR type(task_specification) is TaskSpecification`

Any other value raises `AdmissionError`.

Consequences:

- explicit `None` remains the supported no-task-spec path;
- exact `TaskSpecification` remains supported;
- arbitrary duck-typed objects are rejected;
- subclasses capable of overriding `.digest` semantics are rejected;
- admission continues to compute `TaskSpecification.digest` internally for the exact structured type.

No producer formula, task digest algorithm, state-binding logic, concurrency control, or rollback semantics changed.

## Qualification

Fresh R23 RED reproduction `ae58f7b7…`:

- **2 failed / 2 passed as expected**.

After repair:

- focused R16-R23 controls: **24/24 PASS**
- full suite: **153/153 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact executable repair `348200dbe6b9186df7c9a4f41c80044b01323062`:

- pytest: **153/153 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact CI-enablement head `fd753cf4b2e7e11249a3683225dfbbac65e5aa4d`:

- pytest: **153/153 PASS**
- compileall PASS
- diff-check PASS

Hosted GitHub Actions:

- run `35455579743`
- head `fd753cf4b2e7e11249a3683225dfbbac65e5aa4d`
- overall: **SUCCESS**

## Preserved R16-R22 guarantees

R23 retains:

- admission-owned durable producer identity;
- task-bound canonical production identity;
- canonical input/output hashing;
- opaque actual attempt identity;
- exact built-in-string state binding;
- per-Episode RLock concurrency exclusion;
- in-memory rollback on transaction failure;
- direct caller producer-forgery rejection;
- stale-state mismatch rejection;
- same task/state/output deterministic replay.

## Explicit scope / non-claims

R23 establishes ordinary in-process runtime type hardening for the task-specification input.

R23 does NOT establish:

- cryptographic authenticity of TaskSpecification contents;
- proof that a trusted caller supplied a semantically truthful task;
- protection against malicious replacement/monkeypatching of Python classes or source code;
- persistence/database rollback;
- crash-consistent durability;
- cross-process/distributed transactionality;
- semantic truth;
- independent hostile PASS on the final R23 subject;
- merge authority;
- deployment, installation, activation, runtime effect, training, provider/model mutation, or learned-routing qualification.

The exact-type requirement prevents duck-typed digest injection; it is not an authority credential.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
