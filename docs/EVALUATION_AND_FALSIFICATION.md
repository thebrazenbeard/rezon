# Evaluation and Falsification

Rezon should be built around the assumption that a reasoning pipeline can be wrong while looking coherent. Evaluation must therefore attack not only final answers but routing, proposition fidelity, evidence handling, independence, state transitions, and integration.

## Evaluation layers

### 1. Proposition fidelity

Before evaluating correctness, confirm the system solved the proposition actually asked.

Tests:

- stronger claim substituted for the user’s claim;
- narrower claim answered as though complete;
- referent switched;
- desire/preference/consent/authority proposition types conflated;
- hypothetical treated as assertion;
- correction ignored in favor of earlier route.

### 2. Operator selection

Did the planner choose appropriate reasoning methods?

Examples:

- deduction attempted where premises are uncertain;
- semantic similarity retrieval used when an exact identifier exists;
- LLM calculation used where deterministic arithmetic is available;
- causal claim inferred from correlation;
- expensive model used for trivial parsing while a hard verification step is omitted.

### 3. Evidence integrity

Tests:

- stale evidence presented as current;
- retrieved but unadmitted evidence promoted to authority;
- one source repeated through several summaries counted as independent evidence;
- no-match treated as exhaustive absence;
- source version changed mid-run;
- evidence contradicts the final answer but is silently dropped.

### 4. Independence

Two reviewers are not independent merely because they have different labels.

Record and test:

- same model/provider;
- same prompt lineage;
- same context;
- whether one saw the other’s answer;
- deterministic rerun vs independent sampling;
- common upstream evidence.

### 5. Adversarial robustness

Use semantic attacks, not only string mutations:

- paraphrase a forbidden promotion;
- coherent multi-file forgery;
- rollback to an older internally valid state;
- altered object with recomputed digest;
- subclass/duck-type substitution;
- state envelope says “source-only” while prose implies installed/active;
- authority encoded indirectly rather than with a blocked keyword.

### 6. Runtime/effect separation

The system should distinguish:

```text
PLAN
SOURCE_CREATED
SOURCE_VERIFIED
REVIEWED
DELIVERED
INSTALLED
ACTIVE
EFFECT_OBSERVED
QUALIFIED
CLOSED
```

A lower state must never imply a higher one.

### 7. Calibration

Where probability/confidence is used, evaluate calibration against repeated outcomes. Confidence prose is not a calibration metric.

## Benchmark classes

Rezon should eventually maintain benchmark suites for:

- logic and constraint problems;
- ambiguous-language proposition typing;
- causal/counterfactual tasks;
- retrieval over long structured corpora;
- multi-source contradiction reconciliation;
- architecture/security hostile review;
- persistent identity association;
- multi-view state drift;
- multi-node independence;
- resource-aware routing;
- integration under partial worker failure.

## Broken reference implementations

Every important verifier should be tested against intentionally broken implementations. Examples:

- planner that always chooses the largest model;
- identity tracker that uses only embedding similarity;
- evidence store where newest always wins;
- budget system with check-then-reserve races;
- hash chain that accepts valid-prefix rollback;
- adversarial reviewer that rewrites the proposition before attacking it;
- integrator that converts missing workers into votes for consensus.

If the evaluation suite cannot reliably break these, it is not yet trusted.

## Completion rule

“Tests pass” is necessary but not sufficient. A completion receipt should state:

- exact subject/version;
- tests executed;
- negative/adversarial cases executed;
- known inherited failures;
- environmental assumptions;
- what the result proves;
- what it explicitly does not prove.
