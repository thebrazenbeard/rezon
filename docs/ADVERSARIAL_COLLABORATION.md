# Adversarial Collaboration

## Purpose

Adversarial collaboration is not reflexive disagreement. It is a disciplined method for testing a proposition without silently rewriting it into a stronger or easier-to-defend version.

The method should be usable as a Rezon reasoning operator and as a review mode for architecture, code, claims, and plans.

## Core sequence

1. **Literalize the proposition.** Preserve referent, scope, proposition type, and explicit qualifiers.
2. **Mark it unproven.** Do not improve it first.
3. **Attack the literal proposition.** Search for counterexamples, hidden assumptions, scope errors, alternative explanations, boundary failures, and disconfirming evidence.
4. **Decide the literal result.** If it survives, support it. Do not manufacture objections to appear independent.
5. **Only after literal failure, infer the underlying objective.** Ask what the proposer was actually trying to accomplish.
6. **Generate a stronger route.** Preserve the objective without falsely claiming the original implementation was correct.
7. **Separate result types.** “Literal proposal fails” and “objective is still achievable” are distinct outputs.

## Why this matters

A common reasoning failure is benevolent substitution:

```text
User proposes A
Reasoner sees flaw in A
Reasoner silently constructs A'
Reasoner evaluates A'
Reasoner answers as if A survived
```

That is semantically dishonest even when the replacement is better.

The opposite failure is performative opposition:

```text
User proposes A
A is sound
Reviewer invents weak objections to look independent
```

That is equally bad.

## Operator contract

Input:

```text
AdversarialReviewRequest {
  literal_proposition
  proposition_type
  referent
  scope
  success_criteria
  known_evidence[]
  protected_assumptions[]?   # assumptions that are explicitly part of the proposal, not exempt from challenge
}
```

Output:

```text
AdversarialReviewResult {
  literal_verdict
  counterexamples[]
  unsupported_assumptions[]
  scope_failures[]
  alternative_explanations[]
  surviving_claim
  inferred_objective?        # only populated after literal failure or when explicitly requested
  stronger_route?
  confidence
  unresolved[]
}
```

## Hostile review classes

- proposition substitution;
- stronger/weaker claim promotion;
- referent drift;
- hidden precondition;
- boundary-condition failure;
- state/effect conflation;
- stale evidence;
- circular validation;
- correlated-reviewer consensus;
- test oracle that trusts the subject under test;
- missing negative case;
- adversarial input that remains semantically equivalent while bypassing lexical filters;
- coherent multi-artifact forgery;
- rollback/replay of a formerly valid state;
- authority laundering through role, confidence, or model strength.

## Behavioral boundary

Adversarial collaboration is a **task method**, not a permanent personality.

It should not turn a system into a contrarian assistant. When the method is not relevant, the system should return to its baseline behavior/personality configuration. In Vera-specific use, this method must not redefine identity, relational posture, consent, desire, or authority.

## When to invoke automatically

Candidate triggers:

- architecture changes;
- security boundaries;
- production mutations;
- identity/admission claims;
- causal claims;
- irreversible or expensive actions;
- “this is definitely fixed” completion claims;
- new control-plane trust roots;
- claims based on consensus of similar workers.

For low-stakes factual requests, automatic opposition should be minimal or absent.
