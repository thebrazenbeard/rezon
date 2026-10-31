# TRAININGDAY R34 — public synthetic peer-challenge disposition

Status: `SOURCE_ONLY_HOLD`. No device, identity, training, deployment, or
private/held-out evaluation permission is conferred by these files.

## Narrow change

`rezon.trainingday_r34_peer_evidence.assess_peer_outcomes` consumes the existing
`trainingday_pool` public deterministic integer-arithmetic job/oracle and its
complete first-round / peer-review receipt deliveries. It reuses the production
synthetic oracle replay and peer-snapshot digest checks. The additional result
reports **both** peer corrections and newly regressed answers, case by case.
One worker contributes at most one vote even with bounded retry deliveries.

The result is detached from input lists/dictionaries before receipt checks and
hashing, rejects nested dict/list subclasses, and caps the source envelope at
2,000,000 bytes. The report contains case IDs and counts, not question text or
the oracle's expected answer. Peer disagreement and unanimous-but-wrong votes
are identified without treating model agreement as ground truth.

The R36 source hardening additionally requires the exact oracle root keys
(`schema`, `job_sha256`, `cases`, `verification`) and exact per-case keys
(`id`, `start`, `operations`, `answer`, `prompt_sha256`) on the detached
snapshot. A malformed oracle case now raises the intentional `PoolError`
boundary, and unexpected fields are rejected instead of silently dropping
uncommitted source metadata. This validates only the public synthetic oracle
shape, not independent or confidential oracle custody.

`assessment_sha256` is a deterministic source-integrity hash of the public
report. Receipt SHA-256 values are self-reported, unauthenticated synthetic
digests. Neither constitutes host identity attestation, secure oracle custody,
remote worker execution, or weight-update evidence.

## Synthetic negative proof

Two mocked models answer six seeded public arithmetic questions. First round:

- `vn1` has 5/6 correct, `vn2` 0/6; both return the same wrong answer on the
  first case. Consensus must be labelled `UNANIMOUS_WRONG`, not validated.
- Review fixes the first case for `vn1`, fixes the second for `vn2`, but causes
  `vn1` to regress on the second. The report must show **2 corrections and 1
  regression**; net exact-vote gain is only +1 (5/12 → 6/12).

Tests also reject altered review receipts, wrong peer-snapshot bindings,
poisoned oracle answer, nested custom JSON containers, oversized input, and
mutation after the report is created. R36 regressions cover a `null` oracle
case and extra oracle-case/root metadata. Delivery permutation and identical retry
deliveries leave the report hash unchanged.

## Acceptance and remaining boundary

```bash
PYTHONPATH=src python -m unittest -v tests.test_trainingday_r34_peer_evidence
PYTHONPATH=src python -m unittest discover -s tests -p 'test_trainingday*.py'
```

These are CPU/mock tests only. A real three-node peer comparison requires
separately authenticated host identity, workload and route leases, independent
model/receipt capture, and an admitted oracle. This module is **not** a gradient
pool, an automatic data-admission rule, a physical MeZO/QLoRA comparison, or
an authorization to retrain/replace Vera-local.
