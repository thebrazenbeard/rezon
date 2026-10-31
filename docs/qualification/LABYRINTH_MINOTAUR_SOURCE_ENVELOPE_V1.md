# Rezon ↔ Labyrinth/Minotaur coordination source gate

This is an **importable, source-only** experimental fixture stored exclusively in Rezon's `experiments/` tree for the
**Labyrinth/Minotaur regenerative-learning coordination** recorded on
[`chat-communication-bus` issue #393](https://github.com/thebrazenbeard/chat-communication-bus/issues/393).
It does not modify Rezon, Labyrinth, model-training, or any host. It is **not**
part of a general portfolio-consolidation event.

It ties together exact source identities and commitments for:

- Rezon's independently executed whole-model reasoning episode;
- the Labyrinth/Minotaur signed development event and five-arm MiniLM Maze
  exposure/control matrix;
- a training task-roster and checkpoint digest (as a **provenance link**, not
  an assumption that model-training R18 consumed Labyrinth PR #62 data);
- separately keyed, exact host-lease, route and effect *claims*.

Known reference revisions used by the synthetic tests:

| Subject | Git commit |
| --- | --- |
| Rezon main | `b25518b525b8d31c8e8730a3b4d23088d2c66cdc` |
| Labyrinth Draft PR #62 | `b698ede24d9a69e551e1cad83dee83a825feb9a6` |
| model-training Draft PR #143 | `a14118e87dbba9fd436ef2ae6ad04293966d4d8b` |

These source references are **test fixtures**. A future run must fresh-pin its
own exact heads and cryptographically measured episode, exposure, control,
checkpoint and external authority-head digests.

## Run

```bash
PYTHONPATH=src python -m unittest discover -s tests -p test_labyrinth_minotaur_receipts_source.py -v
```

`qualify_source_envelope(...)` returns separate non-authorizing evidence decisions:

- `source_envelope=SOURCE_ONLY` and `source_receipts_verified=True` mean only
  that the presented role-separated HMACs are canonical, syntactically valid
  and equal the **caller's own pins**. Missing/partial receipts never set the
  verified flag. **No value of `source_envelope` is a deployment qualification.**
- `physical_execution=UNKNOWN` **always**. Offline receipt validation does
  not authenticate the operating-system issuer, independent observation of
  model computation, deployed provider key custody or external clock.
- `distributed_single_model=UNKNOWN` **always**. Independent Rezon model
  calls are not tensor, KV, or gradient sharding.
- `host_identity_verified=False`, `external_monotonic_replay_protected=False`,
  `per_arm_learning_verified=False` and `can_authorize_execution=False`
  **always**. These are deliberately not promoted from the source HMAC result.

The guard `require_qualified_distributed_execution` always fails in this
fixture; no caller can promote a source receipt into a physical authorization.

## Hostile limits retained

> Two clones of the same key, authority-head snapshot and receipt store can
> both produce source-valid signatures. This test explicitly demonstrates the
> duplication. Only a genuinely external monotonic host authority can stop it.

> A signed provider effect receipt is a **provider assertion**, not an
> independently observed optimizer update or inter-host tensor transfer.

> An invented host and locally generated signing keys can satisfy this
> source-only fixture. A one-host claim of distributed single-model inference,
> or replaying one valid receipt bundle in another invocation, never establishes
> physical host identity or a genuine monotonic authority.

> All HMAC test keys are synthetic, intentionally unprivileged fixtures. A
> production trust root must remain outside trainer/Rezon/LLM processes.

The frozen Qwen R18 four-control MeZO/QLoRA comparison and its exact R16
Labyrinth PR #59 corpus manifest are separate from this five-arm MiniLM
sentiment path. The validator rejects any attempt to interchange them.

No physical host, model, protected credential, private exam, training process,
remote Git branch, or deployment was used for this fixture.
