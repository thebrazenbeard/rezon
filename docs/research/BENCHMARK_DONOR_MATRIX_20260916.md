# Rezon Benchmark V1 — External Donor Matrix

Status: SOURCE RESEARCH / BENCHMARK INPUT / NO RUNTIME AUTHORITY

Purpose: record externally motivated benchmark mechanisms so Benchmark V1 does not become a collection of Rezon-specific traps.

## `yixial-1736/connectome_fingerprint`

Transferable mechanism:
- prediction evaluated against a held-out target;
- network-removal ablation across multiple groups;
- permutation comparison against a null distribution.

Benchmark consequence:
- every claimed Rezon safeguard contribution should be testable by disabling that safeguard;
- fixture/order permutations should expose accidental ordering or bookkeeping effects;
- small fixture sets remain descriptive rather than statistical proof.

Not transferred:
- neuroscience target variables;
- ridge regression as Rezon's reasoning model.

## `VectifyAI/PageIndex`

Transferable mechanism:
- explicit separation of retrieval quality from downstream reasoning;
- hierarchical retrieval as a competing retrieval mechanism;
- cost-vs-accuracy reporting rather than accuracy alone;
- traceability to retrieved references.

Benchmark consequence:
- classify failures into at least retrieval/input-availability, integration/governance, and answer-generation strata;
- do not credit Rezon reasoning when a strategy simply receives better evidence;
- live trials must hold retrieval access constant when testing orchestration value.

Not transferred:
- published benchmark scores as evidence for Rezon;
- PageIndex's own retrieval architecture as a required dependency.

## `OpenSPG/KAG`

Transferable mechanism:
- operator decomposition into planning, reasoning, and retrieval;
- mixed use of exact retrieval, text retrieval, numerical calculation, graph/semantic reasoning, and language reasoning;
- static vs iterative planning as separate execution modes.

Benchmark consequence:
- label which operator class a case requires;
- distinguish operator-selection failure from operator-execution failure;
- include cases where deterministic arithmetic/exact lookup should beat free-form language reasoning;
- future live trials should compare static and adaptive routing without changing the evidence set.

Not transferred:
- KAG's knowledge infrastructure as a Kernel V0 dependency;
- KAG benchmark claims as Rezon qualification.

## `ShengxuanQiu/HyPER`

Transferable mechanism:
- path expansion/reduction under a token/resource budget;
- path scoring using confidence, tail confidence, normalized length, novelty, and repetition penalties.

Benchmark consequence:
- treat confidence/diversity/entropy/novelty/path scores as routing hypotheses;
- compare them with deterministic selectors before promotion;
- include cases where a high-confidence/high-novelty path is wrong so score quality cannot be confused with epistemic authority.

Not transferred:
- path score as truth/evidence/authority;
- HyPER's scheduler as an automatic Rezon replacement.

## `basiralab/HCAE`

Transferable mechanism:
- multi-view higher-order structural representation;
- learned structural embeddings as an advisory signal;
- representation/ablation experiments across relational views.

Benchmark consequence:
- future structural-signal trials should compare full-view vs view-ablated routing;
- canonical truth/provenance/currentness remains outside learned geometry;
- replay fixtures may include structural scores but gold labels must not depend on them.

Not transferred:
- TensorFlow implementation as a Kernel dependency;
- embedding proximity as identity/evidence/currentness.

## `koriavinash1/HyperbolicReasoning` and `deadsmash07/hyperbolic-reasoning-probe`

Transferable mechanism:
- alternate geometry for hierarchical structure;
- Euclidean-vs-hyperbolic representation/probe comparison;
- layer/token/representation ablation as diagnostic method.

Benchmark consequence:
- hyperbolic geometry is an experimental representation variable, not a baseline assumption;
- compare structural representation choices on the same task/candidate payload;
- measure whether geometry improves routing/error discovery before adding runtime complexity.

Not transferred:
- geometry score as semantic correctness.

## `lucasdinnouti/custom-reverse-proxy`

Transferable mechanism:
- simple routing-control families: round-robin, weighted selection, metadata selection, learned selection/weights.

Benchmark consequence:
- future router experiments need simple deterministic controls;
- a learned router must beat fixed/metadata/weighted controls under matched budgets before promotion.

Not transferred:
- reverse-proxy deployment/security assumptions.

## `GeorgeVJose/DRISHTE-Public`

Transferable mechanism:
- transient observation vs persistent track identity.

Benchmark consequence:
- persistent-identity cases must separate an observation match from a subject-binding decision;
- similarity alone cannot be counted as association evidence.

Not transferred:
- undocumented/redacted tracking internals.

## `semantica-agi/semantica`, `ThHanke/ontosphere`, `acrion/zelph`

Transferable mechanism families:
- provenance and derivation records;
- deterministic semantic/rule paths;
- asserted vs inferred state;
- validation/repair/reversal;
- proof/derivation chains.

Benchmark consequence:
- provenance integrity and derivation visibility are first-class metrics;
- include valid-looking but provenance-broken cases;
- correction/retraction cases must preserve history while invalidating current dependent state.

Not transferred:
- whole storage/ontology engines as Benchmark V1 dependencies.

## Benchmark attribution taxonomy

Each Benchmark V1 case should identify the intended failure layer where applicable:

1. `INPUT_RETRIEVAL` — required evidence was not available/retrieved;
2. `PROPOSITION_TYPING` — literal task/referent/claim semantics changed;
3. `OPERATOR_SELECTION` — wrong reasoning/retrieval/calculation operator chosen;
4. `OPERATOR_EXECUTION` — selected operator produced an incorrect result;
5. `PROVENANCE_CURRENTNESS` — stale, duplicated, unadmitted, or unverifiable evidence accepted;
6. `INDEPENDENCE_CONTAMINATION` — correlated executions treated as independent;
7. `INTEGRATION` — candidate outputs combined incorrectly;
8. `AUTHORITY_EFFECT` — confidence/consensus/source/build state promoted beyond authority;
9. `FAILURE_HANDLING` — partial/unavailable work hidden or converted into success;
10. `IDENTITY_BINDING` — transient/similar observation promoted to persistent subject identity.

A benchmark report must not collapse these into a single causal explanation. A wrong final answer may have multiple attributed failure layers.

## P0 use

This matrix does not alter Kernel R2 or authorize a new runtime mechanism. It constrains Benchmark V1 case construction and later live-trial design so external mechanisms are tested as competing hypotheses rather than treated as adopted architecture.
