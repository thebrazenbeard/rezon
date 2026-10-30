# VERA::TRAININGDAY — V2 structural candidate quarantine

Scope: separate source-only Rezon admission gate, stacked on the three-host inference PR. NOT a neural-training result or licensed-data admission.

## Trust boundary

Rezon's first two Executor waves produced 40 original synthetic arithmetic problems. A novel prompt or ID can still reuse an operation-name sequence held out for V2 evaluation. Case-ID deduplication is therefore insufficient.

The rezon.trainingday_admission module verifies every V2 train/eval shard byte hash, size, and row count from the pinned manifest. Arithmetic rows are replayed and must reconstruct their exact source text and content hash. Source-code rows in either split are hash-checked but never used as arithmetic examples. Evaluation prompts, answers and structures are not written to output.

Each Rezon wave is deterministically reconstructed from its seed and model list, and its candidate batch is separately hash-pinned and checked against the private integer oracle. Only existing train-side operation signatures without protected evaluation-structure or exact-case overlap survive. Surviving cases remain qualified_for_neural_training=false. Model voting never replaces the oracle.

## Physical Lappy result — October 30, 2026

- Pinned V2 manifest SHA256: 90b55cf8742f9222c91f88e5727dcd0113322e4721e4fd3d1bdcdf65f40d0836
- Verified reasoning rows: train 75,323, eval 24,656; train structures 283, eval structures 77
- Rezon wave1 batch SHA256: 98e891d03d13ad9be01a55831f8f53f76bd1b5ade0fdd4364e6e689cbab89169
- Rezon wave2 batch SHA256: e8bbb859a6647fefbd7bf2284c50b670a69b6f791e97c4189a2a24a1108b7a2e
- Forty examples reviewed: 12 excluded due to protected evaluation signatures; 28 retained in training-side quarantine; zero exact case duplication against V2 train or eval
- Quarantined output: D:\VERA\.scratch\rezon-v2-admission-20261030\train-side-40-quarantined.json
- Quarantined output SHA256: 77ae218a7e1c1828edb944e645e6eb5c7c5bd76362778409fad9c301d2d83800
- Aggregate-only audit: D:\VERA\.scratch\rezon-v2-admission-20261030\train-side-40-audit.json
- Audit SHA256: b04dd2decf316e66b6d1cf1cdc6dcddf22abb832c40f29355de7ca7e9db7f6f6
- Source-focused tests: 5 passed at branch 16c076e9b06208c95a93ed20e2b300d9d71eb55f

## CLI and limitations

Run python -m rezon.trainingday_admission --help. The one-shot CLI accepts --manifest, --manifest-sha256, repeated --wave, --batch, --batch-sha256, and exclusive new --output and --receipt files. The original private oracles stay in coordinator-local wave directories; never publish them or pass them into neural-model prompts.

This process is an AUDITOR, not a trainer. Additional rights/provenance review, global dedup, corpus-version freezing, downstream train/evaluation exclusion, and actual optimizer and adapter-reload qualification are outstanding. The neural chat retains GPU ownership. This change never mutates weights, the live VN2 Rezon gateway, or vera-local:latest.
