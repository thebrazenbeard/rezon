---
name: rezon-analysis
description: Use when a user wants a difficult question, plan, explanation, or conclusion analyzed through multiple explicit reasoning methods with uncertainty, opposition, provenance, and a bounded result receipt.
---

# Rezon Analysis

Use Rezon as a structured reasoning workflow, not as a persona swarm.

1. Freeze the user's literal proposition, decision, or question before analyzing it. Preserve scope, referents, time frame, and modal language. Do not silently strengthen, weaken, or substitute the proposition.
2. Separate the working material into typed items such as observation, evidence, claim, hypothesis, assumption, question, prediction, test, test result, and decision. Treat preferences, authority, identity, consent, and runtime/effect state as distinct when they matter.
3. Choose reasoning operators that fit the problem rather than repeating one method. Candidate operators include deduction, induction, abduction, causal reasoning, counterfactuals, probabilistic reasoning, analogy, numerical calculation, retrieval, simulation, and formal verification.
4. Keep method diversity separate from evidence independence. Different prompts or labels do not make two outputs independent if they share the same source, context, provider, model, or upstream argument.
5. Preserve provenance for material claims. Distinguish source-backed facts from inference, hypotheses, assumptions, and generated alternatives.
6. Run an opposition lane before promotion. Seek counterexamples, scope errors, hidden assumptions, stronger rival explanations, contradictory evidence, and failure modes. A supported counterexample can outweigh broad agreement.
7. Integrate only what survives the available evidence. Do not turn consensus, repetition, confidence, model strength, or repository location into evidence or authority.
8. Keep reasoning quality separate from operational authority and effect state. A good plan is not deployment; source existence is not installation; tests are not proof of live effect.
9. Report unresolved ambiguity explicitly rather than forcing closure.

Finish with a compact result receipt containing:
- the proposition actually analyzed;
- the main supported findings;
- the strongest surviving challenges or rival explanations;
- unresolved or unavailable evidence;
- the confidence or epistemic state justified by the evidence;
- what the result does and does not establish.

Consult `references/core-contract.md` when the task needs the Rezon invariants or a reminder of the typed distinctions.
