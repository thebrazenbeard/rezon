# TrainingDay R25 three-node receipt custody — source-only

This module assesses **declared** Lappy/VN1/VN2 inference job provenance. Its
content-addressed caller-claimed synthetic corpus manifest is *not* corpus admission,
license review, signed host identity, permission to train, or proof of weight
changes. The test HMAC keys are fixtures, never service credentials.

It validates job/corpus/worker/device/model references, bounded receipt shape,
claimed timestamps, content hashes, optional caller-supplied signature checks,
duplicate replay collapse, conflicting replay rejection, partial delivery,
and stable order-independent summary hashes. It exposes no answers or prompts
in its summary. The source distinction between `INFERENCE_RESULT_CLAIM` and
`TRAINING_GRADIENT_UPDATE` is strict: inference worker receipts are **not**
neural gradients and cannot be counted as neural learning evidence.

The assessor freezes canonical JSON copies of job/corpus/routes/receipts
*before* running a caller-supplied verification callback. A second canonical
comparison detects synchronous mutations to the original caller objects and
adds `INPUT_CHANGED_DURING_VERIFICATION` instead of falsely reporting a
complete chain. The frozen-input digest identifies what was actually checked;
this is not an atomic host-side snapshot or durable external evidence.
Bounded pre-admission checks reject malformed jobs, routes, corpus claims, and
more than twelve receipt deliveries *before* any deep snapshot is constructed.

Even a fully matching synthetic fixture returns `HOLD_SYNTHETIC_CHAIN` and
`dispatch_authorized=false`, `training_candidate_admitted=false`,
`host_identity_authenticated=false`, `host_lease_authenticated=false`, and
`shared_gradient_computation_proven=false`. Receipt hashes are continuity
evidence against accidental alteration, not cryptographic host identity.

To qualify live operation requires independently authenticated physical
device/transport identity, signer key custody, attested host clocks, fresh
atomic resource leases and counters, reproducible original inference outputs,
independent corpus rights/split admission, and a separately authorized
training runner. No open LAN endpoint, host configuration or GPU job is
created by this source-only patch.
