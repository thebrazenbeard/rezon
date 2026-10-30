# TRAININGDAY: portable three-node Rezon inference delegation V1

Status: **executed cross-host pilot, source-only Draft PR candidate**. This does not install an unattended cross-machine service, share neural weights, provide a distributed GPU, qualify a four-host federation, or train a neural model.

## Architecture and trust
Rezon `trainingday_pool.py` generates an original arithmetic task envelope and keeps its deterministic integer oracle in a separate owner-local JSON file. Each independently running worker receives only the same job and uses its own loopback OpenAI-compatible model endpoint. Executor is the explicitly authorized task/receipt transport; no peer HTTP ports, worker bearer secrets, persistent gateway data or network tunnels are needed.

Each model returns one answer per case in round one. A second round is optional: all first-round receipt hashes are frozen; each worker receives the other workers' textual guesses as **untrusted data**, never the oracle, and gives a revised answer. Hashes detect ordinary substitution, not physical host attestation, identity, genuine independence, model honesty or semantic truth. Each output is bounded, uses an exclusive new-file path and can never silently replace another job.

After returning portable JSON receipts to the coordinator, `aggregate` validates exact job/worker/model/case IDs, all receipt hashes, every answer parser, the frozen peer snapshot and the separate integer oracle. The oracle's operations must reproduce **both** the answer and the literal public question. If a worker is missing or an input is inconsistent, no candidate batch is exported. A model majority is **not** ground truth.

Job admission also requires the exact synthetic TrainingDay envelope fields and event/case identity, a bounded seed and structurally valid case IDs. Unexpected job fields and non-UTF-8-encodable case prompts fail closed before canonical hashing; this is source validation, not an authenticated sender or training authorization.

Transport retries may deliver an identical first-round or review receipt more than once. The aggregate and peer-review paths collapse up to four **exactly identical, digest-validated deliveries per worker** without increasing completed-worker counts or votes; conflicting valid receipts from the same worker fail closed. Missing workers still prevent candidate export, and more than four deliveries per worker fail closed. This is a bounded receipt-replay property, **not** an unattended submission/retry scheduler, proof of a second independent inference, or network transport reliability. CLI output files remain create-only and cannot be overwritten by retry.

Incoming JSON files are capped at 512 KiB before decoding. Both first-round and review-round receipts must have their exact generated fields, case order, bounded parsed integers and at most 2,000 characters per answer **before** hash verification. A self-hashed oversized answer, non-object review row or extra payload is still rejected; a matching digest is not authorization to process unbounded content. This is a local parser/aggregation resource bound, not a guarantee about upstream network transport or untrusted host identity. Direct Python calls may supply their own in-memory objects and do not enforce the CLI's file-size ceiling.

The candidate batch contains source `SYNTHETIC_ORIGINAL_INTEGER_REPLAY_V1`, target answers computed by the deterministic oracle, model vote counts and `qualified_for_neural_training=false`. Admission into Labyrinth or the model-training runner requires separate deduplication, provenance, train/eval contamination checks and explicit selection. No private V10 final-bank plaintext may be placed into jobs.

## Reproduction commands
From a branch checkout with Python >=3.12 and `PYTHONPATH=src`:

```text
python -m rezon.trainingday_pool create --workers-json workers.json --seed 29037 --cases 8 --job run1/job.json --oracle run1/oracle.private.json
python -m rezon.trainingday_pool worker --job run1/job.json --worker vn1_qwen --model-url http://127.0.0.1:11434/v1 --output run1/vn1_qwen.receipt.json
python -m rezon.trainingday_pool review --job run1/job.json --receipt run1/lappy_qwen.receipt.json --receipt run1/vn1_qwen.receipt.json --receipt run1/vn2_granite.receipt.json --worker vn1_qwen --model-url http://127.0.0.1:11434/v1 --output run1/vn1_qwen.review.json
python -m rezon.trainingday_pool aggregate --job run1/job.json --oracle run1/oracle.private.json --receipt run1/lappy_qwen.receipt.json --receipt run1/vn1_qwen.receipt.json --receipt run1/vn2_granite.receipt.json --review run1/lappy_qwen.review.json --review run1/vn1_qwen.review.json --review run1/vn2_granite.review.json --summary run1/review-summary.json --candidates run1/candidates.unadmitted.json
```

The coordinator must carry the job file to each worker host and carry their response files back using the authorized transport. The file paths in the command examples are local to each host; do not publish or distribute the private oracle. The CLI is one-shot; it does not expose new listening ports, start daemons, distribute credentials, invoke a remote model API or import examples automatically.

## Actual three-node receipt (2026-10-29)
Three distinct host executions: **Lappy** `qwen2.5-coder:1.5b-instruct-q8_0`, **VN1** `qwen2.5-coder:1.5b-instruct-q3_K_M`, **VN2** locally served Granite 3.3 2B Q4_K_M. All three repositories were cloned in separate scratch areas; the already-running VN2 loopback gateway and Granite service were not restarted or mutated.

Eight common synthetic operation-chain prompts, 24 actual first-model responses and 24 new peer-critique responses. Job SHA256 `16364400002e65928e68893a1a7e4f379813ba2dab0df87f6537eb7c310ce81c`; peer-snapshot SHA256 `a853baaa483083285e861a8564097d7e725cf0962d142eaf5310026b74ed9d8e`. First exact scores: Lappy 2/8, VN1 0/8, VN2 2/8 (**4/24**). After seeing peers' guesses: Lappy 0/8, VN1 0/8, VN2 1/8 (**1/24**). Thus peer critique *degraded* accuracy for this small task set. It must not be used as an unqualified answer-improvement step.

Local coordinator aggregate-only review summary file SHA256 `4e31e56fcafc865b2870f1378db8c6ebf62f34f47ba4c59123769a3490fa2d4b`, created under the private local TRAININGDAY scratch. Eight oracle-grounded **unadmitted** candidate rows, no optimizer step and no saved neural adapter.

Evidence: actual model HTTP calls at the three local loopback endpoints and file hash readback through Executor. Physical host claims originate in authorized Executor sessions, not cryptographic host attestation. The SHA-256 values authenticate content continuity within the recorded exchange, not the source of an answer. The prototype does not modify Rezon's existing SQLite/T'Kal gateway.

## Scale and next gates
The job generator intentionally permits 1–32 cases per bounded one-shot exchange, 2–8 assigned workers and 32 output tokens per model response. Scaling into millions of records requires batching, resource scheduling, safe transport retries, drift monitoring, source deduplication, independent holdouts and neural-training gates. Host-specific dedicated models can evaluate code, arithmetic or reasoning separately, but truth must be independently checked; model vote counts alone are not a safe training label.

The pilot demonstrates execution and a negative result for unguarded peer critique. Do not promote this branch as a production multi-host mesh or evidence Vera's reasoning weights improved.
