---
name: rezon-evidence-reconciliation
description: Use when a user needs conflicting, duplicated, versioned, stale, or differently authoritative evidence reconciled while preserving provenance, currentness, independence, and uncertainty.
---

# Rezon Evidence Reconciliation

Build an evidence ledger before synthesizing.

1. Identify the exact subject and claim each source bears on. Similar wording or a shared name is not enough to establish subject identity.
2. For every material source, record origin, version or date when available, scope, directness, transformation lineage, and whether it is current for the claim being made.
3. Separate direct evidence from summaries, interpretations, hypotheses, and generated explanations.
4. Collapse duplicate lineage. Several downstream summaries of one upstream source count as one evidentiary lineage unless genuinely independent evidence is shown.
5. Prefer exact identifiers, versions, and source bindings over semantic similarity when exact matching is available.
6. Preserve contradictions rather than averaging them away. Distinguish:
   - VERIFIED
   - CONFLICTING
   - UNRESOLVED
   - UNKNOWN
   - UNAVAILABLE
   - STALE
7. For currentness claims, fresh live evidence outranks older receipts or historical snapshots, but freshness alone does not grant broader authority than the source actually has.
8. Keep evidence authority separate from operational authority. A source can establish a fact without authorizing an action.
9. Keep effect states separate. Do not infer higher states from lower ones. Useful states include PLAN, SOURCE_CREATED, SOURCE_VERIFIED, REVIEWED, DELIVERED, INSTALLED, ACTIVE, EFFECT_OBSERVED, QUALIFIED, and CLOSED.
10. Synthesize only after the ledger is explicit. State which conclusion is supported, which evidence is controlling, what remains disputed, and what additional observation would resolve the uncertainty.

Consult `references/reconciliation-contract.md` for the compact ledger schema.
