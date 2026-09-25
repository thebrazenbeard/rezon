---
name: rezon-hostile-review
description: Use when a user asks to hostile-review, red-team, falsify, stress-test, or independently challenge a claim, plan, architecture, proof, or reasoning result without rewriting it into an easier proposition.
---

# Rezon Hostile Review

Attack the exact proposition before trying to improve it.

1. State the literal proposition under review, including scope, subject, version, time frame, dependencies, and claimed effect. If the proposition is composite, split it into atomic claims but preserve the original relationship among them.
2. Record the evidence and assumptions actually available. Mark missing evidence as missing; do not repair the case with unprovided facts.
3. Identify the strongest falsification routes first:
   - proposition substitution or referent drift;
   - stale evidence presented as current;
   - a narrower result presented as complete;
   - repeated lineage counted as independent support;
   - shared model/provider/prompt/context presented as independent review;
   - correlation promoted to causation;
   - consensus promoted to truth;
   - source/build/test state promoted to install/active/effect/qualified state;
   - a valid older snapshot substituted for the current subject;
   - integrity checks that protect bytes but not semantic meaning;
   - failure or unavailable evidence silently converted into success.
4. Look for a concrete counterexample, incompatible case, or stronger rival explanation. Prefer one decisive failure over many cosmetic objections.
5. Distinguish a defect in the proposition from a defect in the evidence, implementation, verifier, or claimed scope.
6. When the claim survives only after narrowing, preserve that narrowing explicitly rather than calling the original claim fully supported.
7. Do not self-award independence. State whether the review shares relevant context, sources, model lineage, or other dependencies with the material being reviewed.

Use one of these dispositions when useful:
- SURVIVES
- SURVIVES_NARROWED
- UNRESOLVED
- REJECTED

The disposition applies only to the exact reviewed subject and evidence available in the current run.

Consult `references/attack-library.md` for reusable semantic attack classes.
