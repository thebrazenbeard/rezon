# Rezon Benchmark V1 Design

Status: APPROVED DESIGN / SELF-REVIEW HARDENED / IMPLEMENTATION NOT YET QUALIFIED

## Purpose

Rezon Benchmark V1 exists to falsify the claim that Rezon's additional orchestration/governance structure produces enough semantic-quality improvement to justify its extra reasoning cost.

It must not reward Rezon merely for doing more work, using more workers, receiving better source material, or seeing gold labels unavailable to comparison strategies.

Benchmark V1 implements the deterministic replay layer only. Later live/model-routing layers are specified here as gates so replay results cannot silently expand into broader reasoning claims.

## Benchmark program layers

Kernel V0 hostile/regression qualification is a prerequisite, not one of the comparative benchmark layers.

### Layer 1 — deterministic recorded-output replay

All strategies receive the same frozen candidate outputs, source records, worker metadata, and failure events. Only integration/governance behavior differs.

This isolates integration/governance value from model intelligence, retrieval differences, and sampling variance.

Benchmark V1 implements this layer.

### Layer 2 — live matched-budget orchestration comparison

Deferred until Layer 1 is trustworthy and Kernel V0 has fresh independent qualification.

Comparison arms should include, when technically supportable:

1. one ordinary model call;
2. the same model/provider with higher reasoning effort or equivalent additional compute;
3. fixed deterministic multipass/self-critique;
4. dynamic Rezon orchestration.

Model/provider, prompt/task wording, source/tool access, maximum budget, and evaluator population must be matched or explicitly recorded as unmatched. Seeds/sampling parameters must be recorded where supported.

Layer 2 is the first layer that may contribute evidence about end-to-end reasoning effectiveness. It must report the stated task population and execution conditions rather than generalizing to "reasoning" as a whole.

### Layer 3 — learned/advisory routing and representation experiments

Deferred until deterministic Rezon demonstrates value in Layer 2.

HCAE-style multi-view structural signals, HyPER-style confidence/diversity/entropy/novelty/path scores, hyperbolic geometry, or learned routing weights compete against deterministic routing controls under matched budgets.

These signals remain advisory. They never define gold truth, evidence, identity, authority, currentness, or qualification.

## Layer 1 comparison principle

The three initial replay strategy families are:

1. `single_pass`: select the designated primary candidate without cross-worker governance;
2. `fixed_multipass`: combine a fixed set of candidate outputs using a simple deterministic majority/first-valid rule without Rezon epistemic governance;
3. `rezon_guarded`: apply proposition fidelity, provenance/currentness, independence, admission, failure, and authority/effect-state controls.

No strategy may receive information unavailable to its peers for the same case.

## Gold-label isolation

Gold labels are evaluator-only state.

The evaluator loads a `ReplayCase` containing gold disposition/answer plus the frozen replay material, then constructs a separate `StrategyInput` that omits every gold field. Strategy functions accept only `StrategyInput`.

Required invariant:

```text
ReplayCase -- evaluator strips gold --> StrategyInput --> strategy
          \-------------------------> evaluator only
```

A strategy API that accepts `ReplayCase`, evaluator state, expected violation labels, fixture answer keys, or any object from which gold can be derived directly is invalid.

Expected violation labels are also evaluator-only unless a case explicitly models a real input that names an externally observable policy violation. Fixture bookkeeping labels are never strategy input.

## Replay case classes

V1 must include at least:

- literal proposition substitution;
- stale source vs current authoritative source;
- valid-prefix rollback to an older internally coherent source;
- duplicate evidence repeated through multiple summaries;
- correlated workers presented as independent consensus;
- retrieved-but-unadmitted material presented as evidence;
- confidence/path-score/learned-geometry/model-prestige used as authority;
- contradictory evidence silently omitted from a candidate answer;
- partial worker failure hidden behind apparent consensus;
- mandatory verification unavailable;
- malformed or semantically contradictory candidate receipt;
- correct abstention when evidence is insufficient;
- clean controls where additional governance should not alter the correct answer.

The corpus must contain both cases where Rezon should reject/abstain and cases where all strategies should succeed. This prevents a trivial reject-everything policy from scoring well.

## Recorded case contract

Evaluator-only `ReplayCase` binds:

- `case_id`;
- `fixture_version`;
- `fixture_provenance`;
- `literal_request`;
- `primary_candidate_id`;
- `gold_disposition`: `ANSWER`, `ABSTAIN`, or `FAIL_CLOSED`;
- optional `gold_answer`;
- expected evaluator-only violation labels;
- frozen strategy-visible payload.

Strategy-visible `StrategyInput` binds:

- `case_id` and fixture version for traceability, but no answer-key semantics;
- `literal_request`;
- `primary_candidate_id`;
- candidate outputs with exact candidate/worker/execution IDs;
- source records and exact source/version/currentness/admission metadata when relevant;
- worker model/provider/prompt/context lineage when relevant;
- candidate exposure and common-evidence metadata;
- worker/tool failures;
- candidate receipt/effect/authority claims;
- advisory routing/geometry/confidence signals where the fixture needs them.

`ReplayCandidate` must make worker/execution identity explicit. `ReplaySource` must make source ID/version, locator, admission/currentness and origin identity explicit rather than encoding them in prose.

Schema validation is structural and fail-closed. Semantically suspicious but structurally valid candidate claims must remain representable so strategies can be tested against them; the loader must not "repair" the attack before a strategy sees it.

## Strategy output contract

Use a replay-specific type such as `ReplayStrategyOutcome` rather than overloading the existing legacy `benchmark.StrategyOutcome` name.

Each strategy returns:

- disposition: `ANSWER`, `ABSTAIN`, or `FAIL_CLOSED`;
- optional answer;
- accepted candidate/claim IDs;
- rejected candidate/claim IDs;
- violations detected;
- unresolved items;
- operation count;
- optional token/cost/latency fields when available;
- trace listing the candidate/source metadata actually consulted.

A strategy is not allowed to rewrite the literal proposition before evaluation.

### Baseline determinism

`single_pass` selects `primary_candidate_id` exactly.

`fixed_multipass` uses this deterministic rule:

1. ignore candidates that have an explicit execution failure or no answer;
2. count exact normalized answer strings;
3. choose the unique highest-count answer;
4. on a tie, choose the earliest eligible candidate in fixture candidate order;
5. if no eligible candidate exists, return `FAIL_CLOSED`.

It may not inspect provenance/currentness/independence metadata except explicit execution failure needed to define "valid" for this baseline.

`rezon_guarded` may inspect only strategy-visible governance metadata. It may not call live models/tools, Kernel executors, evaluator gold state, or fixture expected-violation labels.

## Guard configuration and ablation

Rezon safeguards must be explicit named controls, not hard-coded branches that cannot be disabled independently.

Minimum guard names:

- `proposition_fidelity`;
- `provenance_currentness`;
- `admission_integrity`;
- `independence_contamination`;
- `failure_visibility`;
- `authority_effect_boundary`.

`rezon_guarded(input, guards=...)` must support leave-one-control-out ablation while holding all other logic and the replay payload constant.

An ablation result is evidence about this replay implementation, not proof that the analogous production mechanism has the same causal effect.

## Metrics

Primary semantic metrics:

- disposition accuracy;
- answer accuracy conditional on gold `ANSWER` and strategy `ANSWER`;
- false accept count: strategy answers when gold is `ABSTAIN` or `FAIL_CLOSED`, or answers incorrectly on an answer case;
- false reject count: strategy `FAIL_CLOSED` when a correct answer was expected;
- false abstain count: strategy `ABSTAIN` when a correct answer was expected;
- unsupported-claim acceptance;
- provenance/currentness violations accepted;
- correlated-consensus laundering accepted;
- hidden-failure acceptance;
- authority/effect-state promotion errors;
- required violation-detection recall.

Cost metrics:

- operation/execution count;
- wall-clock time;
- token count when available;
- provider cost when available.

Do not collapse all metrics into one opaque score in V1. Report the metric vector and pairwise deltas.

A strategy that always abstains therefore accumulates false-abstain errors on clean answer cases even if it avoids false accepts.

## Statistical / experimental controls

Borrow the experimental pattern, not the neuroscience domain, from `yixial-1736/connectome_fingerprint`: use ablation and permutation/null comparisons to test whether a component contributes signal beyond chance or bookkeeping.

V1 must support:

- leave-one-control-out ablation for named Rezon safeguards;
- deterministic case-order permutation to prove order independence;
- label-shuffle/permutation controls applied only in the evaluator, never to strategy input;
- bootstrap confidence intervals or exact paired counts only once case count is large enough to justify them.

Small fixture sets must be reported as descriptive evidence, not statistical proof.

## Donor-mechanism controls

The external donor matrix constrains experimental design but provides no runtime authority.

- PageIndex motivates separating retrieval/input quality from downstream integration.
- KAG motivates explicit operator-class attribution and deterministic exact/calculation controls.
- HyPER motivates budgeted routing experiments and adversarial cases where high-confidence/high-novelty paths are wrong.
- HCAE and hyperbolic work motivate representation ablation without promoting geometry to truth.
- custom-reverse-proxy motivates round-robin/weighted/metadata deterministic routing controls before learned routing.
- DRISHTE motivates separating transient observation from persistent identity binding.
- Semantica/Ontosphere/Zelph motivate provenance, derivation, asserted-vs-inferred and repair/reversal evaluation.
- connectome_fingerprint motivates ablation/permutation methodology.

## Failure attribution

Use the donor-matrix taxonomy without collapsing causal layers:

1. `INPUT_RETRIEVAL`;
2. `PROPOSITION_TYPING`;
3. `OPERATOR_SELECTION`;
4. `OPERATOR_EXECUTION`;
5. `PROVENANCE_CURRENTNESS`;
6. `INDEPENDENCE_CONTAMINATION`;
7. `INTEGRATION`;
8. `AUTHORITY_EFFECT`;
9. `FAILURE_HANDLING`;
10. `IDENTITY_BINDING`.

A wrong final answer may have multiple attributed layers. Attribution must not be inferred merely from which strategy lost.

## Fairness and leakage controls

- Same strategy-visible payload for all strategies.
- No strategy-specific hidden evidence.
- Gold disposition, answer, expected violation labels, and evaluator state are absent from `StrategyInput`.
- Fixture IDs/order must not encode the expected answer.
- Strategy traces expose which candidate/source metadata was consulted.
- A Rezon-specific fixture is invalid if its failure cannot plausibly occur under a simpler strategy.
- Clean controls are mandatory.
- Retrieval/source availability must be held constant inside Layer 1; better evidence cannot be counted as integration value.

## Acceptance rule for Benchmark V1 / Layer 1

Benchmark V1 implementation is accepted when:

1. replay schema validation is deterministic and fail-closed;
2. gold/evaluator state is structurally absent from strategy inputs;
3. all three initial strategy families run the same frozen strategy-visible payload;
4. baseline tie/failure behavior is deterministic;
5. metrics distinguish semantic correctness from cost and penalize reject-everything behavior;
6. named-guard ablation and order-permutation controls execute reproducibly;
7. intentionally broken integrators lose on the cases they are designed to mishandle;
8. label-shuffle controls operate evaluator-side without changing strategy inputs;
9. exact fixture/strategy/code provenance is emitted in the report;
10. a clean checkout reproduces benchmark tests and the reference report.

No Layer 1 result may be described as "Rezon improves reasoning." It may support narrower claims such as "on frozen candidate set X, guarded integration accepted fewer unsupported/stale/correlated outputs than baseline Y at operation delta Z."

## Non-goals

Benchmark V1 does not:

- train models;
- call live LLM providers;
- implement Layer 2 or Layer 3;
- establish AGI/general reasoning claims;
- adopt HCAE/HyPER/hyperbolic routing into Kernel V0;
- merge or advance PR #8 or PR #10;
- replace Masa/Mune independent review;
- compress benchmark outcomes into a single prestige score.

## Integration boundary with current Kernel work

`work/rezon-benchmark-v1` remains isolated from R3 review subject `work/rezon-kernel-v0-r3-mune` while PR #10 is under independent review.

Benchmark V1 implementation must not modify Kernel source. Before any later integration/rebase, the then-current qualified Kernel subject must be re-read and benchmark tests rerun against the combined exact head. Benchmark evidence from this isolated branch does not qualify Kernel R3 and Kernel R3 evidence does not qualify Benchmark V1.
