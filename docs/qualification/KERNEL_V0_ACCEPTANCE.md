# Rezon Kernel V0 Acceptance

Status: SOURCE / BUILD / TEST ACCEPTANCE CANDIDATE

This record binds executable qualification evidence for the first provider-independent Rezon Kernel V0 candidate. It does not establish reasoning superiority, production deployment, installation into another system, model training, provider activation, or downstream behavioral qualification.

## Qualified executable payload

- repository: `thebrazenbeard/rezon`
- branch: `work/rezon-kernel-v0-p0`
- executable payload commit: `03e90e8d97ace99a26938372a398d20c3f4da8ef`
- executable payload tree: `558a0fac73aa6f98ff43c867180ac2bfe28c4227`
- predecessor research head: `rezon/hcae-semantic-reapplication-v1@0cf560ce4a573230b94db2982dbec074dd3b1b20`

## Reproduction environment

- Windows host
- Python `3.12.10`
- isolated fresh clone of the remote branch
- branch-local virtual environment
- `pytest` installed into that environment
- package installed editable from the fresh clone

## Qualification sequence

From a fresh clone of the remote branch at the exact executable payload commit:

```text
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install pytest
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m compileall -q src
.venv\Scripts\python.exe -m pytest -q
git diff --check
git status --short
```

Observed result for payload commit `03e90e8d97ace99a26938372a398d20c3f4da8ef`:

```text
32 passed in 0.16s
```

`compileall` completed successfully, `git diff --check` returned clean, and the qualification checkout had no tracked working-tree changes.

## Covered invariants

The executable suite covers:

- typed epistemic kinds without hypothesis/evidence collapse;
- literal task-envelope preservation;
- persistent-subject binding requiring association evidence;
- explicit independence/contamination metadata;
- append-oriented episode history and retraction preservation;
- auditable visibility and blinding;
- atomic output admission and output-kind restrictions;
- version-bound retrieval admission;
- deterministic hypothesis, contradiction, and falsification operators;
- deterministic scheduler priority and budget exhaustion;
- explicit mandatory-worker failure;
- execution trace and effect-state preservation;
- hostile cases for proposition substitution, stale source, rollback, duplicate evidence, correlated consensus, advisory-signal authority laundering, malformed receipts, hidden partial failure, and hidden budget exhaustion;
- provider-neutral strategy benchmark accounting that keeps correctness separate from execution count.

## Known limits

This acceptance does not prove that Rezon reasons better than a simpler baseline. It proves that this exact executable payload satisfies the currently encoded Kernel V0 contracts and hostile checks under the recorded environment.

HCAE-derived encoders, HyPER-derived routing, hyperbolic geometry, live LLM/tool executors, graph databases, learned schedulers, production persistence, provider integration, and downstream adoption remain outside this qualification subject.

Mune and Masa independent specialist reviews were requested separately through the BT2 communication bus. Their findings are not included in this PASS unless and until exact-head reports are received and reconciled.
