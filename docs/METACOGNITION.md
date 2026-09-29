# Metacognition and Strategy Selection

Metacognition in Rezon means reasoning about the reasoning process: whether the current operator, evidence, decomposition, or resource allocation is appropriate. It is not a claim of subjective self-awareness.

## Questions a metacognitive node should ask

- What exact proposition are we trying to establish?
- Is the current reasoning method suitable for that proposition type?
- What assumptions are currently carrying the conclusion?
- Which assumptions are evidence-backed vs merely convenient?
- What evidence would most reduce uncertainty?
- Are we solving a substitute problem?
- Are several workers actually independent?
- Has the subject/version changed since the plan was formed?
- Is a deterministic tool preferable to another model call?
- Is the current confidence justified by evidence quality?
- Has further reasoning reached diminishing returns?

## Strategy-change triggers

Examples:

```text
retrieval returns conflicting sources -> switch to provenance reconciliation
symbolic proof fails due uncertain premise -> switch to evidence acquisition
large search space -> add heuristic/planner
causal direction unresolved -> design intervention/counterfactual test
multiple candidate explanations -> invoke adversarial discrimination
state subject changed -> invalidate stale downstream work
resource budget low -> prioritize high-information tasks
```

## Calibration

Metacognition should track uncertainty in structured form where possible:

- unknown because evidence unavailable;
- uncertain because evidence conflicts;
- uncertain because model is underdetermined;
- uncertain because source quality is low;
- uncertain because worker output is unstable;
- uncertain because proposition itself is ambiguous.

These causes imply different next actions.

## Stop / continue decision

A metacognitive controller can estimate expected value of another reasoning step:

```text
continue if expected_information_gain > marginal_cost
```

This is conceptual rather than a requirement for a precise numeric utility model. The key is that continuation has a reason.

## Failure modes

- endless self-critique without new evidence;
- treating more tokens as more rigor;
- “confidence” generated from tone rather than calibration;
- asking unnecessary clarification when the request is already clear;
- repeatedly re-planning instead of executing a bounded next step;
- using metacognition as a hidden authority override.

## Relation to adversarial collaboration

Metacognition chooses when opposition is useful. The opposition node then attacks the literal proposition. The integrator/metacognitive controller decides what to do with the result. Keeping those roles separate prevents the critic from becoming the final authority merely because it was asked to be hostile.
