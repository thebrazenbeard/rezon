# TrainingDay R28-05: synthetic three-node recovery simulation

**Status: SOURCE_ONLY_HOLD.** This is a small deterministic Python state machine,
not a Rezon live trainer, OS-enforced lease manager, production adapter loader,
evaluator, daemon controller, or model-release gate. It never starts an optimizer,
opens a network connection, writes a checkpoint or accesses Lappy/VN1/VN2.

The isolated source is `src/rezon/trainingday_r28_recovery_sim.py`; tests are
`tests/test_trainingday_r28_recovery_sim.py`. Lineage is Rezon R26 dual-
coordinator shadow, the source-equivalent tree of Draft #141. Inputs are
synthetic public declarations; an event digest proves only the declared
scenario's byte continuity, not its provenance or accuracy.

## Bounded event protocol

- Exactly 8 fields per event: `kind`, `actor`, `node`, `epoch`, `step`,
  `mono_ms`, `wall_ms`, `digest`; at most 128 events, sorted monotonic clocks.
- Once at function entry the module copies the bounded exact dict/scalar
  events into private immutable mapping proxies and a tuple. Validation,
  canonical digest and replay use that same snapshot; postvalidation caller
  edits or aliased original rows cannot alter accepted state. This closes a
  tested source time-of-check/time-of-use vulnerability. Concurrent mutation
  *during input snapshot acquisition* is not an authenticated atomic capture;
  upstream callers still need a real transaction/lock for host evidence.
- Nodes are literal `lappy`, `vn1`, `vn2`. Only fake roots A/B may request
  an owner slot. `host-shadow` cannot create a real fencing acknowledgement.
- All three fake tunnel witnesses and both fake resumed inference workers
  are needed before a fake owner can start a fake optimizer step; every fake
  host/worker witness must be no older than 30,000 ms at use.
- A step requires `BEGIN_STEP → PARTIAL_WRITE → SEAL → COMMIT`, same step,
  owner, epoch and SHA-256; partial/unsealed output never counts as progress.
- `CLAIM_SUCCESS` requires that exact committed digest, once per generation.
  Old committed checkpoints can `ROLLOVER` only after a newer claimed
  generation, and the result explicitly reports `deletion_executed=false`.
- `TUNNEL_DOWN` or `STANDBY` aborts in-flight work and invalidates all old
  tunnel/worker witnesses. The original fake owner remains in conflict until
  TTL expiry, all post-fault fake witnesses and sequential fake `FENCE_ACK`.
- Cumulative monotonic/wall drift above 5,000 ms permanently quarantines
  subsequent step operations in that scenario. These clocks are declared by
  the caller, not authenticated against Windows sleep/wake.

## CPU fault matrix

| Scenario | Deterministic result | What remains unproved |
| --- | --- | --- |
| Three-node clean A→B handoff, sealed steps 1/2 | Both fake successes; step 1 rollover only after step 2 claimed | Host ownership, actual checkpoint bytes |
| Partial step 2, tunnel loss, standby, renewed workers, expiry, fake fence | Aborted partial denied; B can redo fake step 2 without double-commit | OS stop/fence and GPU resource release |
| A active while B requests/start/commits | Collision and B step denied | Physical concurrent-process exclusion |
| Partial without matching seal | Commit and success denied | Disk flush, crash durability |
| Replayed commit or success | No double optimizer count / success | External receipt identity, signed attestations |
| Premature or unsolicited fake fence | Denied | Real independent fencing custodian |
| Missing fresh post-fault witnesses | Denied | True host-level wake/tunnel state |
| Cumulative clock drift | Subsequent step denied | Windows Modern Standby mitigation |
| Malformed input, bool integer, huge clock, path-like node, extra fields | Rejected before canonical digest | Adversarial multi-thread concurrent input mutation |
| Original actor mutated to root-c after validation | Immutable validated root-a still replayed/hash-bound | Caller identity authentication |

Run: `PYTHONPATH=src python -m unittest tests/test_trainingday_r28_recovery_sim.py -v`.

Every result unconditionally reports:

```json
{
  "status": "SOURCE_ONLY_HOLD",
  "authorizes_optimizer_start": false,
  "host_lease_authenticated": false,
  "fencing_host_authenticated": false,
  "checkpoint_bytes_verified": false,
  "physical_optimizer_steps_executed": 0,
  "authorizes_model_release": false,
  "distributed_gradient_compute_proven": false
}
```

## Unresolved release/physical gates

No authenticated shared-exclusive Lappy GPU lease, preserved real optimizer
state, MeZO/QLoRA equal-time CPU/GPU pairing, Qwen3.5-4B tensor-delta reload,
private OOD bank custody, host pause/resume probe, signed receipts, or
independently measured behavior. R18 historical 531-second budget versus
19,813.562-second elapsed MeZO run stays **TIME_BUDGET_OVERRUN_INVALID**.
Never infer shared gradient compute merely from distributed Rezon inference
receipts. This simulation cannot authorize live training, sleep policy edits,
network restarts, merge, deployment, quantization, model promotion, or release.
