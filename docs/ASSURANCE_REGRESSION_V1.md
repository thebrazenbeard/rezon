# Assurance Regression V1

Status: INTERNAL MANUALLY AUTHORED ADVERSARIAL REGRESSION

This document classifies the subject previously named "external assurance
evaluation" in file and fixture names.

The current corpus is useful, but it is not independent validation.

## Exact meaning

The frozen fixture:

- `tests/fixtures/external_assurance_v1.json`

contains ten manually authored cases created inside the Rezon development
process. Eight cases exercise known assurance failure classes and two are clean
controls.

The runner compares:

- a primary-answer baseline with no cross-worker governance;
- an ungoverned exact-answer vote;
- `rezon_guarded`.

The comparison is valuable for regression detection and for exposing whether the
known guards actually change behavior on their intended failure classes.

It is not evidence of general superiority.

## Machine-readable classification

The report emitted by
`scripts/run_external_assurance_eval_v1.py` identifies itself as:

- `evaluation = rezon-assurance-regression-v1`;
- `evaluation_classification = internal_manual_adversarial_regression`;
- `independent_evaluation = false`;
- `pre_registered_before_guard_design = false`;
- `external_runtime_evidence = false`.

The historical file names remain for continuity. They must not be used to
upgrade the evidence class.

## Current regression result

On the exact source subject that introduced this classification, the regression
contains:

- 10 total cases;
- 2 clean ANSWER controls;
- 8 adversarial ABSTAIN cases;
- all six current replay guard classes represented.

The guarded strategy detects all eight expected violations without false-blocking
the two clean controls on this frozen corpus. The two deliberately ungoverned
baselines accept all eight adversarial cases.

Those numbers describe only this fixture.

## Independence repair

The replay independence guard now fails closed for multi-worker agreement when
any answering worker lacks the minimum explicit provider, model, prompt-lineage,
or context-lineage bindings needed to test obvious correlation.

Distinct labels are still not proof of independence.

Shared source references are handled separately:

- overlap is surfaced in trace evidence;
- overlap is emitted as machine-readable unresolved
  `shared_evidence_overlap:<source_ref>`;
- source overlap alone does not falsely classify distinct workers as the same
  worker lineage;
- downstream consumers must not treat duplicated use of one source as multiple
  independent evidence sources.

## What this regression does not prove

It does not prove:

- independent benchmark performance;
- generalization beyond the frozen manually authored corpus;
- live external runtime behavior;
- live provider or model quality;
- universal external-runtime compatibility;
- producer authenticity;
- worker independence beyond fixture-visible bindings;
- semantic truth outside the frozen fixture labels;
- deployment, installation, authorization, or external effect completion.

## Next qualification step

A stronger evaluation must be frozen before inspecting Rezon behavior on that
subject and should contain independently sourced or externally generated cases.
Where practical, cases should be bound to immutable external artifacts or
runtime captures rather than written directly from Rezon's current guard
taxonomy.

The existing real-runtime OpenAI/Microsoft OTLP qualification is a separate
evidence class and must remain separate from this manually authored regression.
