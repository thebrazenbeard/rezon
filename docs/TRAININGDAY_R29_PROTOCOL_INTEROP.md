# TrainingDay R29-05 — Three-node protocol interoperability (source only)

## Custody and exact source baseline

- Parent: Rezon Draft PR #142 at `5138c656d12261711e506433f5f78d4abfd31b51` (stacked #141 and #140).
- Isolated implementation base: local R28 source-equivalent commit `65001073fcda9b3353f079976ebbca0521b8d617`, tree `124258bb72f1569dd0d1569f388b4134e702690d`.
- Coordination context: Bus #404/#406, R29 staged packet `6536082340`, R29-05 only.
- **Evidence class:** deterministic CPU source tests and fake receipts, *not* host probes, genuine GPU lease, adapter tensors, independent signature verification, training improvements, or shared gradients.
- Work surface: `trainingday_r29_interop.py`, its dedicated tests, this document. No existing R25/R26/R28 source is changed.

## Contract

`assess_interop` accepts a content-addressed R25 synthetic three-worker job,
its corpus claim, route map, and receipts, an R26 dual-coordinator lease
timeline, an R28 recovery timeline, and an R29 ACK/progress envelope.

The function first creates one detached, capped JSON snapshot of the entire
fixture **before** invoking the caller's untrusted synthetic verifier. It
delegates to the three upstream scenario assessors, then requires matching
accepted source-only coordinator `(actor, epoch)` claims. It binds each fake
ACK to an R25 receipt hash and exact node, an R28 successful generation and
COMMIT, the COMMIT's actor/epoch, and the corresponding R26 claimed lease.
ACK order does not change the content digest; host state-transition order does.

The protocol ACK fields are *exactly*:

`kind`, `node`, `receipt_sha256`, `generation`, `epoch`, `step`, `mono_ms`,
`sequence`. Permitted kinds are `ACK`, `PROGRESS`, `OPTIMIZER_CLAIM`.

All fields and list lengths are bounded; malformed envelopes are rejected
before attempting cross-plane interpretation. The complete nested envelope is
first traversed **and cloned** using **exact built-in JSON types only** in one
bounded pass, with depth, node count, container count, and string length caps.
The serializer sees only the detached plain-data clone, never the original
caller-owned tree. Dict/list/scalar subclasses are rejected before any
serialization or callback invocation: a subclass cannot hide a raw
`spoofed_worker` by overriding `.items()` or `__iter__`. A hostile callback
that later mutates the caller's original tree cannot change the frozen source
used for the verdict or its content digest.
Ordinary ACKs require three
distinct nodes for a fixture-level generation claim. Progress and optimizer
claim messages are **never** counted as ACKs or genuine optimizer evidence.

### Synthetic negative fault matrix

| Injection | Expected fail-closed consequence |
| --- | --- |
| ACK transport reordering | Stable canonical digest; no spurious mismatch |
| Unsolicited receipt hash | `UNSOLICITED_ACK` |
| Conflicting ACK sequence | `CONFLICTING_ACK_SEQUENCE` |
| Replayed ACK | `REPLAYED_ACK`; cannot double count |
| Wrong generation | `GENERATION_NOT_COMMITTED` |
| Wrong epoch | `FENCED_GENERATION_MISMATCH` |
| Wrong step | `ACK_STEP_GENERATION_CONFLICT` |
| Missing or delayed node | `MISSING_NODE_ACK` or `DELAYED_NODE_ACK` |
| ACK before COMMIT | `ACK_BEFORE_GENERATION_COMMIT` |
| ACK at COMMIT or before accepted R28 CLAIM_SUCCESS | `ACK_NOT_AFTER_SUCCESS_CLAIM` |
| ACK same timestamp as CLAIM_SUCCESS | `ACK_NOT_AFTER_SUCCESS_CLAIM` (causal order unauthenticated) |
| Later CLAIM_SUCCESS following an earlier ACK | Earlier ACK remains denied; no retroactive success provenance |
| ACK after claimed lease expiry | `ACK_AFTER_LEASE_EXPIRY` |
| Valid ACK before later clean lease RELEASE | Preserved by historical half-open lease interval |
| ACK after clean lease RELEASE | `ACK_AFTER_LEASE_EXPIRY`; no retroactive acceptance |
| Recovery COMMIT predates R26 owner acquisition | `COMMIT_PRECEDES_LEASE_START` |
| Expired or conflicting R26 lease | `LEASE_DENIAL` |
| R26/R28 owner disagreement | `CROSS_PLANE_OWNER_MISMATCH` |
| Partition, stale worker, invalid fence, rollback, unsafe rollover | `RECOVERY_DENIAL`; downstream generation withheld |
| Standby or tunnel partition after COMMIT, before ACK | `ACK_WITHOUT_LIVE_RECOVERY_WITNESS` |
| R28 wake, node tunnel or worker-resume witness age exceeds 30,000 ms at ACK | `ACK_WITHOUT_FRESH_RECOVERY_WITNESS` |
| R28 witness age exactly 30,000 ms at ACK | Source-boundary permitted, never physically authenticated |
| R28 readiness refreshed at exact ACK timestamp with no cross-stream sequence | Same-tick readiness ignored; old witness expires |
| R28 readiness refreshed one tick before ACK | Synthetic temporal ordering permitted, still unauthenticated |
| Reconnect after COMMIT, but no independently attested buffered-ACK provenance | `ACK_SPANS_UNATTESTED_RECOVERY_FAULT` |
| Missing/invalid R25 node receipt | `CUSTODY_BLOCKER` |
| False progress | `UNVERIFIED_PROGRESS` |
| Untrusted nested container/scalar subclass with custom iterator or serializer hook | `InteropScenarioError` before JSON encoding |
| Caller mutates nested source to a malicious subclass between type checking and JSON encoding | Detached cloned snapshot binds verdict; subclass hook never executes |
| Synthetic optimizer claim | `UNVERIFIED_OPTIMIZER_CLAIM` |
| Future generation reusing R25 inference receipt | `GENERATION_RECEIPT_UNBOUND` |
| External callback mutates original ACKs | Frozen snapshot still determines verdict and digest |

The R25 receipt schema binds job, worker, device, corpus hash, and synthetic
nonce but **not** optimizer generation. Therefore later generation reuse is
explicitly blocked, even when R28 reports a later fake durable COMMIT. A
future authenticated generation-specific receipt protocol is needed before
this conservative hold could be relaxed. Inference receipt hashes do not
establish neural training in any event.

## Review falsifiers and limitations

> **FALSIFIER — Provenance substitution:** A caller can fabricate R25 synthetic
> signature keys, R26 host-ready claims, R28 COMMIT declarations, and R29 ACKs.
> An internally consistent result never authenticates the real three hosts.

> **FALSIFIER — Mixed clock domain:** The synthetic `mono_ms` values are
> asserted to be comparable across R26, R28, and ACK streams. In real systems
> each host can have a different monotonic origin; current simulation is not
> a clock synchronization or lease enforcement mechanism.

> **FALSIFIER — Unknown generation identity:** R25 inference receipts lack
> a protected generation binding. R29 refuses later-generation reuse instead
> of claiming that inferred receipt correlation proves new weights.

> **FALSIFIER — Host transitions after ACK:** This bounded snapshot is not an
> authenticated ongoing host lease. R26 does not expose actual OS-issued
> fencing or Executor resource reservations. No green fake matrix can permit
> Qwen training, quantized release, deployment, or any physical effect.

All outcomes are `SOURCE_ONLY_HOLD`; `physical_optimizer_steps_executed` is
zero; `host_lease_authenticated`, `checkpoint_bytes_verified`,
`distributed_gradients_proven`, `authorizes_optimizer_start`, and
`authorizes_model_release` are all unconditionally `False`. **Never compare
this simulated result to R18 MeZO training evidence.** R18's historical
time-budget overrun remains invalid for equal-time optimization conclusions.

## Reproduction

```sh
PYTHONPATH=src python -m unittest discover -s tests -p 'test_trainingday_r29_interop.py' -v
PYTHONPATH=src python -m unittest discover -s tests -p 'test_trainingday_*' -q
git diff --check
```

Integration is deliberately kept on the isolated branch. An independent
exact-head hostile review is required before any Draft PR; a review pass is
not merge or deployment authority.
