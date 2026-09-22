# Rezon

Rezon is an experimental multi-faceted reasoning substrate.

Its first architectural thesis is that a reasoning state is better represented as a **typed, multi-view hypergraph** than as a flat chain of text or a single undifferentiated graph. Claims, evidence, rules, actions, hypotheses, decisions, actors, runtime observations, and artifacts can participate in higher-order contexts across distinct views such as provenance, authority, temporal/currentness, support/opposition, contradiction, causal/dependency, semantic, participant, policy, and workflow.

Rezon deliberately separates two classes of reasoning state:

- **Deterministic state** owns exact identity, provenance, authority, policy, currentness, explicit derivation, and protected-effect boundaries.
- **Learned state** may provide structural similarity, anomaly scores, embeddings, retrieval ranking, missing-relation suggestions, and state classification. Learned outputs are advisory unless an explicit deterministic policy says otherwise.

The HCAE research line is a major architectural input. Rezon reinterprets HCAE's multi-view hyperconnectome representation literally: a reasoning case is the subject, reasoning objects are vertices, each relation semantics is a view, and typed many-to-many reasoning contexts are hyperedges. The brain-classification application is not the reusable constraint; the reusable core is heterogeneous multi-view hypergraph representation and learning.

## Current foundation

- [`HCAE_SEMANTIC_REAPPLICATION_V1.md`](docs/research/HCAE_SEMANTIC_REAPPLICATION_V1.md) — source-grounded reinterpretation of HCAE as a reasoning substrate.
- [`EXTERNAL_REASONING_SYSTEMS_SURVEY_V1.md`](docs/research/EXTERNAL_REASONING_SYSTEMS_SURVEY_V1.md) — research survey of HCAE, Semantica, PageIndex, KAG, Ontosphere, Zelph, HRM, SGR, and other supplied repositories.
- [`Rezon Reasoning Foundation V1 Design`](docs/superpowers/specs/2026-09-15-rezon-reasoning-foundation-v1-design.md) — typed object model, view registry, deterministic/compiler boundary, HCAE-derived learned layer, hybrid operators, provenance, failure behavior, and acceptance gates.
- [`MULTIVIEW_REASONING_CASE_V1.md`](docs/examples/MULTIVIEW_REASONING_CASE_V1.md) — worked case where semantic retrieval prefers stale evidence but authority/currentness correctly defeats it.
- [`Rezon V1 Implementation Plan`](docs/superpowers/plans/2026-09-15-rezon-reasoning-foundation-v1.md) — test-first executable path from deterministic state to a frozen HCAE-derived comparison experiment.

## Status

The current repository cut is architecture and implementation planning only.

It does **not** claim:

- an installed Rezon runtime,
- trained or qualified reasoning models,
- production authority,
- behavioral qualification,
- superiority over baseline reasoning approaches.

Those claims require executable implementation and exact-subject verification.