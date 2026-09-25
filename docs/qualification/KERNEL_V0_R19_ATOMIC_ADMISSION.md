# Rezon Kernel V0 R19 Atomic Execution-Result Admission

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R19 is the bounded successor to failed R18 exact subject `0bc280fae627684e27543ec666a8360d86055347`.

R18 made the expected pre-execution snapshot digest mandatory, closing caller omission/rebinding. A fresh deterministic thread-race probe then showed that the equality check and durable mutation were still separate operations. Another thread could mutate the same Episode after the digest check but before execution-result admission completed.

R19 makes the in-process check -> validate -> prevalidate -> canonical mutation sequence atomic for a single Episode instance.

## Exact ancestry

- failed R18 review head: `0bc280fae627684e27543ec666a8360d86055347`
- failed R18 tree: `9b9fb6c5b889353f00f88106787aa7d190e4b5ca`
- R19 branch: `work/rezon-kernel-v0-r19-atomic-admission`
- R19 RED: `7f2493388f2d9b953379df498d81a5c5b8e1dd1a`
- executable repair: `d352758e99c7239f92c6046ff2bb1233672f0cbe`
- executable tree: `73b8091cde8eaf8afa4aeb66118bb46ccfe7f8fa`
- CI-enablement head: `a79c769c2cb62e1e9a6780a26027d6f23c9e28bf`
- CI-enablement tree: `c9e55251be5979b0691a8dc77c32d70f84df1534`

## R18 failure — concurrent TOCTOU inside admission

Fresh exact-R18 deterministic concurrency probe used the real Episode object and two threads.

Sequence:

1. capture exact pre-execution snapshot digest;
2. begin `admit_execution_result()` with that mandatory digest;
3. instrument only the existing `_prevalidate_episode_mutation` boundary after the digest equality check;
4. second thread mutates the same Episode by adding `concurrent-input`;
5. ordinary prevalidation and admission resume.

Observed:

- admission succeeded;
- concurrent input remained current;
- worker output computed from the old state was also admitted;
- final Episode version was 2;
- no error occurred.

Therefore the mandatory digest was necessary but not sufficient: the checked state could still change before canonical mutation.

## Frozen RED

R19 freezes a deterministic race regression:

`tests/test_r19_atomic_admission.py`

Exact RED:

`7f2493388f2d9b953379df498d81a5c5b8e1dd1a`

Observed predecessor result:

- mutator completed inside admission;
- `interleaved == [True]`;
- targeted test: **1 failed / 0 passed**.

The required behavior is:

- concurrent mutator may begin attempting the Episode mutation;
- it must not complete while execution-result admission holds its transaction;
- admitted output must commit first;
- concurrent mutation may proceed only after admission releases the Episode transaction guard.

## R19 Episode synchronization

R19 adds one `threading.RLock` per Episode instance.

Canonical operations protected by that same lock:

- `snapshot()`
- `add_proposition()`
- `retract_proposition()`
- `add_relation()`

The lock is reentrant because admission must hold the transaction guard while calling snapshot and mutation primitives that also use the same lock.

Episode also exposes a bounded `atomic_mutation()` context manager.

## R19 admission transaction

`admit_execution_result()` is wrapped with the Episode atomic mutation guard.

The same RLock is therefore held across:

1. descriptor/result identity checks;
2. required pre-execution snapshot digest verification;
3. task/output/provenance derivation;
4. emitted proposition/relation validation;
5. prevalidation against canonical state;
6. canonical proposition/relation mutation;
7. AdmissionReceipt construction.

A concurrent thread calling a lock-protected Episode mutation cannot interleave between the digest check and admission commit.

## Deterministic race regression result

After the repair:

- the concurrent thread reaches the mutation attempt while admission is in prevalidation;
- it cannot finish during the admission transaction;
- `interleaved == [False]`;
- admission commits `admitted-output` first;
- after lock release, concurrent thread commits `concurrent-input`;
- final event order is exactly:
  1. `admitted-output`
  2. `concurrent-input`.

This demonstrates the in-process transaction boundary directly rather than relying on timing luck.

## Qualification

Focused R16-R19 provenance/state/concurrency controls after repair:

- **15/15 PASS**

Full local suite after repair:

- **144/144 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact executable repair `d352758e99c7239f92c6046ff2bb1233672f0cbe`:

- pytest: **144/144 PASS**
- compileall PASS
- diff-check PASS

Fresh clean checkout of exact CI-enablement head `a79c769c2cb62e1e9a6780a26027d6f23c9e28bf`:

- pytest: **144/144 PASS**
- compileall PASS
- diff-check PASS

Hosted GitHub Actions:

- run `35411074313`
- head `a79c769c2cb62e1e9a6780a26027d6f23c9e28bf`
- overall: **SUCCESS**

## Preserved R9-R18 controls

R19 retains:

- strong-independent task-surface isolation;
- executor-hidden canonical history/state metadata;
- unique opaque actual attempt IDs;
- deterministic canonical input-state digest;
- task-bound production identity;
- deterministic canonical output digest;
- admission-owned durable producer identity;
- exact attempt provenance validation before canonical rewrite;
- no-output/failed/preflight/exception no-producer semantics;
- proposition and relation output coverage;
- direct producer-forgery rejection;
- mandatory pre-execution snapshot binding;
- stale-state mismatch rejection;
- same task/state/output deterministic replay;
- different state/task/output producer separation.

## Explicit scope / non-claims

R19 establishes an in-process atomicity boundary for one Episode object when mutation occurs through its lock-protected methods.

R19 does NOT establish:

- cross-process locking;
- distributed transactionality;
- database transaction semantics;
- coordination across two separate Episode objects representing the same logical episode;
- protection against a malicious trusted process directly mutating private Episode internals or replacing source code;
- cryptographic authentication of the snapshot digest;
- semantic truth of state/task/output;
- independent hostile PASS on the final R19 subject;
- merge authority;
- deployment, installation, activation, runtime effect, training, provider/model mutation, or learned-routing qualification;
- reasoning superiority.

The RLock is a concurrency correctness mechanism, not an authority or trust credential.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
