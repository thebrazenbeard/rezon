# Rezon Kernel V0 R22 Exact-String Admission State Binding

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R22 is the bounded successor to failed R21 exact subject `2075511f48c88c8b113c5afe85a9204e30f41c45`.

R21 removed the explicit `None` bypass by comparing the supplied state-binding value unconditionally. A fresh hostile probe then showed that Python's dynamic equality dispatch still let caller-controlled objects impersonate the canonical digest. An arbitrary object or `str` subclass with forged equality semantics could make `snapshot_digest != binding` evaluate False and admit stale output.

R22 requires the state-binding value to be an exact built-in `str` before equality comparison.

## Exact ancestry

- failed R21 review head: `2075511f48c88c8b113c5afe85a9204e30f41c45`
- failed R21 tree: `3df26c4a1f6ad519e756b11a0adbe04da0bc1216`
- R22 branch: `work/rezon-kernel-v0-r22-exact-string-state-binding`
- R22 RED: `5a7465bc97b387b9324ec4f7dfca120b4f20f001`
- executable repair: `44c86f9273da1d424207f221900de8d9f6958914`
- executable tree: `cfcc39a61a53ac06162ffdd3804bd28a32689efc`
- CI-enablement head: `9b18817773780acce555b8d9376a33ee118604b2`
- CI-enablement tree: `5508ddf4cd7936b1e8c7a35e27d883c491db8ad5`

A later R21 branch head `73795ebef8bca7a8a1612b1ff53bcc603965bb64` is a zero-tree-delta child of `2075511f…`; it does not alter the R21 source/docs tree or invalidate the exact failure reproduced on `2075511f…`.

## R21 failure — caller-controlled equality

Fresh exact-R21 hostile probe supplied:

1. a non-string object with `__eq__ -> True` and `__ne__ -> False`;
2. a `str` subclass overriding equality the same way.

Observed:

- forged comparison reported equality against a value that was not the real digest;
- stale execution output was admitted;
- canonical state retained both the newer input and stale output.

The type annotation `expected_episode_snapshot_digest: str` did not enforce runtime type identity.

## Frozen RED

R22 freezes both hostile cases in:

`tests/test_r22_exact_string_state_binding.py`

Exact RED head:

`5a7465bc97b387b9324ec4f7dfca120b4f20f001`

Fresh predecessor reproduction:

- non-string custom equality case: FAIL;
- equality-overriding `str` subclass case: FAIL;
- exact targeted total: **2 failed / 0 passed**.

Both regressions require rejection with no Episode mutation.

## R22 repair

Admission now rejects unless:

`type(expected_episode_snapshot_digest) is str`

and then requires exact equality with the live canonical EpisodeSnapshot digest.

The mutation boundary therefore follows:

`type(binding) is str AND snapshot_digest == binding`

Consequences:

- omitted argument -> Python `TypeError`;
- `None` -> `AdmissionError`;
- arbitrary object -> `AdmissionError`;
- `str` subclass -> `AdmissionError`;
- empty/wrong/stale built-in string -> `AdmissionError`;
- exact built-in digest string -> allowed to continue through the remaining admission checks.

No producer, task, output, concurrency, or rollback semantics changed.

## Qualification

Fresh exact RED reproduction `5a7465bc…`:

- **2/2 FAIL as expected**.

Exact executable repair `44c86f9273da1d424207f221900de8d9f6958914`:

- focused R16-R22 controls: **20/20 PASS**
- full suite: **149/149 PASS**
- compileall PASS
- diff-check PASS

Exact CI-enablement head `9b18817773780acce555b8d9376a33ee118604b2`:

- fresh local: **149/149 PASS**
- compileall PASS
- diff-check PASS
- hosted run `35454665734`: **SUCCESS**

## Preserved R16-R20 guarantees

R22 retains:

- admission-owned durable producer identity;
- task-bound canonical production identity;
- canonical input/output hashing;
- opaque actual attempt identity;
- required pre-execution state-binding argument;
- explicit-null rejection;
- per-Episode RLock concurrency exclusion;
- rollback of current in-memory Episode containers on transaction failure;
- lock release after rollback;
- direct producer-forgery rejection;
- stale-state mismatch rejection;
- same task/state/output deterministic replay.

## Explicit scope / non-claims

R22 establishes ordinary in-process runtime type/equality hardening for the state-binding input.

R22 does NOT establish:

- cryptographic authenticity of the supplied digest;
- proof that the caller derived the digest from the same execution context;
- persistence/database rollback;
- crash-consistent durability;
- cross-process/distributed transactionality;
- protection against malicious replacement of Python runtime/source internals;
- semantic truth;
- independent hostile PASS on the final R22 subject;
- merge authority;
- deployment, installation, activation, runtime effect, training, provider/model mutation, or learned-routing qualification.

The exact built-in-`str` requirement is a boundary-hardening measure, not an authority credential.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
