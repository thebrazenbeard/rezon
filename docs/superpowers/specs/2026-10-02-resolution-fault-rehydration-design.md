# Rezon Resolution-Fault and Selective-Rehydration Design

Status: DESIGN SPEC / IMPLEMENTATION NOT YET CLAIMED  
Date: 2026-10-02  
Source subject: `thebrazenbeard/rezon@ec401810990337bf07a5d6473782ba13eba1bb3f`

## Purpose

Extend Rezon's retrieval/context architecture so reasoning nodes can operate from compact representations and explicitly request higher-resolution evidence when the current representation is insufficient.

Rezon owns the reasoning decision to seek more detail. It does not own Vera memory authority or turn a latent representation into exact evidence.

## Resolution fault

A reasoning node may emit:

```text
ResolutionFault {
  proposition_or_subtask
  evidence_ref
  available_resolution
  required_resolution
  exactness_required
  reason
  expected_information_gain
}
```

Typical triggers:

- exact quote/number/code needed;
- unresolved referent;
- contradiction among compact representations;
- causal/counterfactual step depends on omitted detail;
- verification lane cannot establish a claim at current fidelity;
- opposition lane identifies compression-induced ambiguity.

## Planner behavior

The strategic tier may respond by:

- retrieving a specific exact span;
- promoting one compact block;
- expanding a structural subtree;
- requesting an alternate representation;
- stopping with `INSUFFICIENT_EVIDENCE` when the higher-resolution source is unavailable.

It should not default to loading the entire historical context.

## Retrieval receipt extension

Resolution-aware retrieval records should preserve:

- source/version/locator;
- requested and returned resolution;
- exactness requirement;
- representation/codec identity where applicable;
- backing-source digest;
- bytes/tokens promoted;
- reason for promotion.

## Budget interaction

Context selection continues to optimize information value rather than maximal inclusion. Resolution becomes another scheduling dimension alongside authority/currentness, novelty, expected uncertainty reduction, latency, and token/cost budget.

## Failure rule

`NO_HIGHER_RESOLUTION_AVAILABLE` does not mean the compact representation is exact. Exact-required reasoning must remain unresolved or fail verification.

## First implementation slice

Add typed resolution metadata and a deterministic planner/retrieval simulation around existing retrieval-context concepts. Tests should prove that only the implicated evidence is promoted and that exact-required tasks fail closed without verified backing material.
