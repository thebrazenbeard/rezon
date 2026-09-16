# Rezon Benchmark V1 Design

Status: APPROVED DESIGN / IMPLEMENTATION NOT YET QUALIFIED

## Purpose

Rezon Benchmark V1 exists to falsify the claim that Rezon's additional orchestration/governance structure produces enough semantic-quality improvement to justify its extra reasoning cost.

It must not reward Rezon merely for doing more work, using more workers, or having access to better candidate outputs.

## Core comparison principle

The first comparative layer uses recorded-output replay: all strategies receive the same frozen candidate outputs, source records, worker metadata, and failure events. Only the integration/governance strategy differs.

This isolates architecture value from model intelligence and sampling variance.

The three initial strategy families are:

1. `single_pass`: take the primary candidate without cross-worker governance;
2. `fixed_multipass`: combine a fixed set of candidate outputs using a simple deterministic rule such as majority/first-valid without Rezon epistemic governance;
3. `rezon_guarded`: use proposition fidelity, provenance/currentness, independence, admission, failure, and authority/effect-state controls.

No strategy may receive information unavailable to its peers for the same case.

## Evaluation layers

### Layer A — deterministic safeguard qualification

The existing Kernel V0 and hostile suites remain the low-level control layer. They test whether encoded invariants fail closed.

Layer A is necessary but cannot establish reasoning superiority.

### Layer B — recorded-output replay

Frozen cases contain candidate answers plus metadata describing evidence origins, source versions, worker lineage, candidate exposure, failures, authority claims, and expected semantic outcome.

All strategies replay exactly the same material.

Layer B measures architecture/integration quality without live-model randomness.

### Layer C — live matched-executor trials

Deferred until Layer B is trustworthy.

Live trials must match model/provider, prompts, source access, budget, and tool access across comparison arms as closely as technically possible. Random seeds/sampling settings must be recorded where supported.

Layer C is the first layer that can contribute evidence about end-to-end reasoning effectiveness. It remains outside Benchmark V1 implementation unless separately authorized.

## Benchmark case classes

V1 replay cases must include at least:

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
- malformed or contradictory result receipt;
- correct abstention when evidence is insufficient;
- a clean-control case where extra governance should not change the correct answer.

The suite must contain both cases where Rezon should reject/abstain and cases where all strategies should succeed, preventing a trivial "reject everything" strategy from scoring well.

## Recorded case contract

Each replay case must bind:

- `case_id`;
- `literal_request`;
- `gold_disposition`: `ANSWER`, `ABSTAIN`, or `FAIL_CLOSED`;
- optional `gold_answer`;
- candidate outputs with exact worker/execution IDs;
- proposition/evidence/source references;
- exact source/version/currentness metadata when relevant;
- worker model/provider/prompt/context lineage when relevant;
- candidate-exposure and common-evidence metadata;
- worker/tool failures;
- effect/authority claims;
- expected violation labels;
- case provenance and fixture version.

The gold label must describe semantic disposition, not merely a string answer.

## Strategy output contract

Each strategy returns:

- disposition: `ANSWER`, `ABSTAIN`, or `FAIL_CLOSED`;
- optional answer;
- accepted candidate/claim IDs;
- rejected candidate/claim IDs;
- violations detected;
- unresolved items;
- execution/operation count;
- optional token/cost/latency fields when available;
- trace sufficient to explain the integration decision.

A strategy is not allowed to rewrite the literal proposition before evaluation.

## Metrics

Primary semantic metrics:

- disposition accuracy;
- answer accuracy conditional on `ANSWER`;
- false-accept count;
- false-reject/false-abstain count;
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

## Statistical / experimental controls

Borrow the experimental pattern, not the neuroscience domain, from `yixial-1736/connectome_fingerprint`: use ablation and permutation/null comparisons to test whether a component contributes signal beyond chance or bookkeeping.

V1 must support:

- leave-one-control-out ablation for Rezon safeguards;
- deterministic case-order permutation to prove order independence;
- label-shuffle/permutation controls where meaningful for aggregate comparisons;
- bootstrap confidence intervals or exact paired counts once the case count is large enough to justify them.

Small fixture sets must be reported as descriptive evidence, not statistical proof.

## Routing-control experiments

HyPER-style confidence/diversity/entropy/novelty/path scores and HCAE/hyperbolic structural signals are post-kernel advisory routing candidates.

Benchmark V1 may represent these signals in fixtures, but they must never define gold truth, evidence, identity, authority, or currentness.

Future routing experiments should compare them against deterministic controls such as round-robin, weighted, metadata-based, and fixed-priority selectors before promotion.

## Fairness and leakage controls

- Same replay payload for all strategies.
- No strategy-specific hidden evidence.
- Gold labels are unavailable to strategies during execution.
- Fixture IDs/order must not encode the expected answer.
- Strategy traces must expose which candidate/source metadata was consulted.
- A Rezon-specific fixture is invalid if its failure cannot plausibly occur under a simpler strategy.
- Clean controls are mandatory.

## Acceptance rule

Benchmark V1 implementation is accepted when:

1. replay schema validation is deterministic and fail-closed;
2. all three initial strategy families can run the same frozen fixture set;
3. metrics distinguish semantic correctness from cost;
4. ablation/order-permutation controls execute reproducibly;
5. intentionally broken integrators lose on the cases they are designed to mishandle;
6. a clean strategy is not rewarded simply for abstaining more often;
7. exact fixture/strategy/version provenance is emitted in the report;
8. a clean checkout reproduces the benchmark tests and reference report.

No result may be described as "Rezon improves reasoning" until comparative evidence demonstrates that claim on a stated population of tasks and execution conditions.

## Non-goals

Benchmark V1 does not:

- train models;
- call live LLM providers;
- establish AGI/general reasoning claims;
- adopt HCAE/HyPER/hyperbolic routing into Kernel V0;
- merge PR #8;
- replace Masa/Mune independent review;
- compress benchmark outcomes into a single prestige score.
