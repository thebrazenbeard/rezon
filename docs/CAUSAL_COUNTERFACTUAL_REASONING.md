# Causal and Counterfactual Reasoning

Rezon should keep causal reasoning separate from correlation, narrative plausibility, and temporal order.

## Core causal objects

- variable/state;
- intervention;
- mechanism;
- mediator;
- confounder;
- outcome;
- causal graph or structural model;
- observation vs intervention distinction;
- counterfactual world;
- uncertainty over causal structure.

## Minimal causal workflow

1. state the causal claim explicitly;
2. identify candidate variables and mechanisms;
3. distinguish observed associations from interventions;
4. list plausible confounders and alternative causal graphs;
5. define the intervention being considered;
6. predict outcomes under competing models;
7. identify evidence that would discriminate between them;
8. run experiment/simulation where allowed;
9. update the causal model rather than merely restating the original story.

## Counterfactual discipline

A counterfactual should specify what changes and what remains fixed.

Bad form:

> If X had been different, everything else might also have been different, therefore Y.

Better form:

```text
model M
observed state S
intervention do(X=x')
structural invariants held fixed: {...}
resulting predicted Y'
```

## Causal qualification for configurable systems

When testing whether a configuration change caused a behavioral effect, matched conditions are essential:

- same task corpus;
- same subject identity/admission;
- same relevant model/configuration except treatment;
- randomized or predetermined ordering;
- pre-run runtime readback;
- outcome recorded before unblinding where possible;
- missing/unknown attempts retain their own condition identity;
- append-only or rollback-evident execution ledger.

This is especially important when evaluating model instructions, control-plane cuts, prompt changes, or runtime routing.

## Common failure modes

- post hoc ergo propter hoc;
- treatment changes several variables at once;
- missing results selectively ignored;
- treatment label can be changed after the run;
- old valid ledger prefix replayed to rerun a failed case;
- experiment controller trusts caller-supplied treatment metadata;
- evaluator sees condition labels and rationales before scoring;
- model variability mistaken for causal effect;
- no negative/control condition.

## Rezon operator

A causal node should return something like:

```text
CausalResult {
  causal_claim
  candidate_graphs[]
  interventions[]
  confounders[]
  discriminating_evidence[]
  observed_results[]
  supported_graphs[]
  rejected_graphs[]
  unresolved[]
}
```

The node may conclude that available evidence cannot identify the causal direction. That is a successful reasoning result when true.
