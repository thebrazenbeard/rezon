# TRAININGDAY two-model review coordination — source contract

Status: **source-only / no model training / no physical authorization**.

`rezon.trainingday_coordination` supplies a small, bounded, model-neutral plan
for two candidate inference artifacts. It reuses Rezon's existing immutable
collective episode store for *unverified* CPU worker findings. Nothing in this
module starts a model server, optimizer, gradient worker, GPU job, NAS process,
or private host gateway.

## What parallel work means

| Activity | Supported source contract | Execution boundary |
| --- | --- | --- |
| Provenance, dedup, rights and evaluation-custody reviews | Four CPU work orders distributed round-robin across 2–8 named workers | Worker processes and authenticated enrollment are **external**; claims remain unverified |
| Baseline comparison of two models | Two declared evaluation orders against the **same** sealed evaluation commitment | The second GPU order depends on the first; **not executed** by Rezon |
| Model selection | Independent held-out evaluation required | No score, verdict or winner may be manufactured from worker agreement |
| Training the selected model | No optimizer command is emitted | Requires a separately authenticated trainable base, admitted corpus, exclusive host GPU lease, NAS route and evaluator permission |
| Multiple GPU trainers | **Not implemented** | A distributed PyTorch/other trainer would need distinct real GPUs, identical trainable tensor architecture, synchronized gradients and recovery; Rezon's reasoning collective is not this |

For the currently observed Lappy bakeoff, the two local contenders are GGUF
inference artifacts: `vera-gpt-oss4b-q4-k-m` and
`vera-qwen35-4b-q4-k-m-candidate-20261029`. Those names are *orientation*,
not embedded model identities or verified file hashes. The operator must pin
each exact local file SHA-256 before producing a real review plan. A GGUF is
not proof of available training-format model weights; choosing a GGUF winner
does not itself make a compatible LoRA/QLoRA training base available.

The plan deliberately schedules **one** GPU evaluation slot at a time. Two
model processes sharing one 4 GB card would contend for the same VRAM; extra
CPU workers can preprocess evidence concurrently, but they do not combine
compute into additional VRAM. If distinct, authenticated GPU hosts become
available, independent model experiments can run on separate hosts, and a
proper distributed-gradient framework could be evaluated separately. Never
average LoRA/adapters or gradients from unrelated model architectures.

## Admission and privacy invariants

- Exactly two distinct model artifacts, lower-case SHA-256 identity pins, and
  four distinct whole-artifact corpus/provenance commitments are required.
- Both the source planner and the persistence importer revalidate the current
  fields of caller-owned frozen model and corpus declarations; constructor
  validation alone is not treated as durable authorization or integrity.
- TRAIN, DEV and protected-evaluation roster commitments must differ. This
  shape check is **not** a proof of semantic dedup, consent, provenance, rights,
  or protected-evaluation exclusion.
- Training labels, protected prompts and answer-level/low-entropy hashes are
  not accepted as worker claim fields or written to the Rezon episode.
- Every work order's `authorizes_effects` and every plan's training/data
  authorization fields are permanently `false`.
- Only typed CPU work claims can be stored. Each is labeled **unverified**;
  a source artifact digest does not authenticate a worker, host, or evidence.
- The evidence-import boundary rechecks the exact canonical planner roles,
  worker assignments, GPU dependencies, and false authority flags; directly
  constructing or altering a `TrainingDayPlan` cannot inject arbitrary role
  text into a Rezon answer. Duplicate artifact refs by the same worker are
  rejected **before** an episode is created. This is preflight validation,
  not a promise of rollback for unrelated database/IO faults.
- An object with custom equality or rendering—including `str`/`tuple`
  subclasses—is rejected at this boundary even if it compares equal to an
  approved task. Only exact built-in literal field types are accepted, and
  receipts use newly reconstructed canonical task labels. Validated worker
  claims are separately copied to private typed snapshots before persistence,
  so subsequent mutation of caller-owned objects cannot alter receipt text.
- Rezon's CollectiveStore persists self-declared findings but does not
  establish that their source references are true, independent, current, or
  approved for use in model training.
- $0 additional spend is a binding plan constraint. There is no paid fallback.

## Example (dummy file digests; not a qualified Lappy result)

```python
from rezon.trainingday_coordination import ModelArm, CorpusPins, plan_two_model_bakeoff

arms = (
    ModelArm("candidate_a", "local-artifact-a", "a" * 64, "GGUF_INFERENCE_ONLY"),
    ModelArm("candidate_b", "local-artifact-b", "b" * 64, "GGUF_INFERENCE_ONLY"),
)
corpus = CorpusPins("1" * 64, "2" * 64, "3" * 64, "4" * 64)
plan = plan_two_model_bakeoff(arms, corpus, ("cpu_provenance", "cpu_review"), "gpu0")
assert not plan.authorizes_gpu_training
assert [task.phase for task in plan.tasks].count("BASELINE_EVAL") == 2
```

Separate trusted operators must provide the actual corpus permissions,
sealed held-out evaluation and host-owned lease evidence. This API cannot
turn a read-only source plan into physical training authority.
