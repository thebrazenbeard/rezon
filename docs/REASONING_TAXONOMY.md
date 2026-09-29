# Reasoning Taxonomy

Rezon should not reduce reasoning to “chain of thought.” It should model families of reasoning as different operators with different failure modes, evidence requirements, and useful domains.

## Core inference families

### Deductive reasoning
Derives conclusions that follow from accepted premises and rules. Strength: validity can be checked mechanically. Failure mode: valid conclusions from false, incomplete, or mis-scoped premises.

### Inductive reasoning
Generalizes from observations to broader patterns. Strength: useful under incomplete information. Failure mode: overgeneralization, sampling bias, and confusing frequency with necessity.

### Abductive reasoning
Chooses the best available explanation for observations. Strength: diagnosis and hypothesis generation. Failure mode: premature closure; the best explanation in the current hypothesis set may still be wrong.

### Analogical reasoning
Transfers structure from a known domain to a new one. Strength: mechanism discovery and design. Failure mode: importing irrelevant properties along with the useful relation.

### Causal reasoning
Models interventions, mechanisms, mediators, confounders, and causal direction. Strength: answering “what would change if…” rather than merely correlating. Failure mode: causal stories built from observational coincidence.

### Counterfactual reasoning
Evaluates alternate histories or interventions while holding an explicit structural model. Strength: responsibility, debugging, planning. Failure mode: changing too many assumptions at once or using an incoherent alternate world.

### Probabilistic / Bayesian reasoning
Represents uncertainty explicitly and updates beliefs from evidence. Strength: calibrated uncertainty and competing hypotheses. Failure mode: invented priors, likelihoods, or pseudo-precision.

### Decision-theoretic reasoning
Selects action under uncertainty using outcomes, utilities, costs, constraints, and risk. Failure mode: treating an estimated utility function as an objective moral or governance authority.

## Search and construction families

### Planning
Transforms a goal into ordered or partially ordered actions with dependencies and resource constraints.

### Constraint satisfaction
Searches for assignments satisfying hard and soft constraints. Important for schedules, configuration, architecture, and governance cuts.

### Heuristic search
Uses estimates to prioritize a large search space. A heuristic is a navigation aid, not proof.

### Simulation / model-based reasoning
Runs an explicit model forward to study outcomes. Valuable for concurrency, scheduling, state-machine, and causal tests. The model’s fidelity bounds the conclusion.

### Decomposition
Splits a problem into subproblems. Decomposition quality itself requires review: incorrect boundaries can make all downstream reasoning locally correct but globally wrong.

## Semantic and representational families

### Semantic reasoning
Tracks meaning, proposition type, referent, scope, entailment, contradiction, and equivalence. It prevents solving a subtly different problem than the one stated.

### Pragmatic reasoning
Uses speaker intent, conversational context, social convention, implicature, and task context without silently replacing literal content.

### Symbolic reasoning
Manipulates explicit variables, rules, constraints, formulas, and proof objects.

### Numerical reasoning
Uses arithmetic, statistics, optimization, and quantitative models with dimensional and numerical checks.

### Spatial reasoning
Represents topology, geometry, containment, direction, relative position, and transformations.

### Temporal reasoning
Represents ordering, duration, recurrence, intervals, supersession, causality across time, and event/state/readback time distinctions.

### Graph reasoning
Uses entities and pairwise relations. Useful for knowledge graphs, dependency graphs, provenance, and causal networks.

### Hypergraph reasoning
Uses relations that connect more than two nodes as one semantic unit. Useful when a state or condition is meaningful only as a joint configuration.

## Reflective and adversarial families

### Metacognitive reasoning
Assesses whether the current reasoning method is suitable, what assumptions are active, what remains uncertain, and whether more evidence is needed.

### Adversarial / hostile reasoning
Attempts to falsify a candidate rather than improve it. Useful for security, governance, architecture, tests, and proposition fidelity.

### Dialectical reasoning
Maintains opposing positions long enough to expose assumptions, then seeks a synthesis without forcing false compromise.

### Red-team reasoning
Searches specifically for abuse cases, bypasses, edge conditions, and incentive failures.

### Error-localization reasoning
Separates symptom, proximate cause, root cause, and fix validation. Essential for debugging and runtime diagnostics.

## Human-style mechanisms worth representing without anthropomorphic promotion

- fast heuristic pattern recognition vs slower deliberation;
- selective attention;
- working-memory limits and chunking;
- schema-based interpretation;
- salience and novelty prioritization;
- hypothesis competition;
- narrative/causal coherence checking;
- social-model reasoning;
- confidence and uncertainty calibration;
- exploration vs exploitation;
- memory reconsolidation and revision as an analogy for updating structured state.

These are computational inspirations, not claims that an AI has human phenomenology or biology.

## Multi-node implication

A Rezon run should be able to assign different reasoning families to different nodes and then reconcile their products. The system should prefer operator diversity when the problem benefits from it rather than spawning several indistinguishable copies of one model.
