# Rezon Branch Reconciliation — 2026-09-15

Status: CONSOLIDATION NOTE / NO MERGE OR RUNTIME CLAIM

## Subjects inspected

- `main` at `e3d7a41eccb49a9f403ef66f511faef677ceec1b`
- `work/rezon-foundation-20260915` at `f92455f1da213abcd9386d3c30a93ab4202981da` (draft PR #2)
- `rezon/bootstrap-architecture-v1` at `71c87b47737fb984bc6bfdae62c2b4d9a9b2ac23` (draft PR #1)

This branch, `rezon/consolidated-foundation-v1`, is derived from PR #2's exact head and layers the non-redundant executable contracts/research from PR #1 on top. It does not merge either PR into `main`.

## Foundation branch retained as primary semantic layer

The `work/rezon-foundation-20260915` material is the broader semantic foundation and remains intact here. In particular it owns the current broad treatments of:

- reasoning taxonomy;
- human/AI reasoning synthesis;
- persistent subject/identity tracking;
- multi-view hypergraph state;
- hierarchical and multi-node topology;
- adversarial collaboration;
- retrieval/context selection;
- semantic provenance and verification;
- causal/counterfactual reasoning;
- metacognition;
- worker routing and resource boundaries;
- state/currentness/effect semantics;
- evaluation/falsification;
- source transfer analysis;
- roadmap and downstream adoption candidates.

## Bootstrap material retained as executable-contract layer

The following PR #1 artifacts are retained because they add concrete contracts or experiments not fully specified by the foundation branch:

- `docs/architecture/REZON_ARCHITECTURE_V0.md`
- `docs/contracts/EPISTEMIC_STATE_V0.md`
- `docs/contracts/REASONING_NODE_V0.md`
- `docs/research/HCAE_EPISODE_HYPERCONNECTOME.md`
- `docs/superpowers/specs/2026-09-15-rezon-kernel-design.md`
- `docs/superpowers/plans/2026-09-15-rezon-kernel.md`

These artifacts should be read under the foundation constraints rather than as competing authority.

## Reconciled semantic decisions

1. Rezon is not a debate swarm. Node diversity must correspond to real epistemic/computational differences, not labels.
2. The canonical reasoning substrate preserves typed propositions, provenance, contradiction, time, subject, and many-to-many relations.
3. A persistent subject is not identical to any one observation epoch. Identity continuity requires association evidence; similarity is advisory only.
4. Latent/learned representations, including HCAE-derived embeddings, are derived state. They may support routing, anomaly detection, clustering, compression, or drift detection but cannot establish identity, consent, authority, fact, runtime installation, or other hard state.
5. The HCAE transfer has two distinct consumers:
   - explicit multi-view hypergraph state representation; and
   - an optional per-episode structural encoder that learns latent coalition/outlier/reconstruction signals from compatible proposition views.
6. Strategic/slow and tactical/fast reasoning are semantic execution tiers, not model prestige classes.
7. Provider/model capability is separate from semantic role and separate again from authority.
8. The integrator aggregates arguments/evidence, not votes. A verified counterexample can defeat broad unsupported consensus.
9. Retrieval is a first-class reasoning operation with exact, structural, semantic, and reasoning-guided modes plus provenance receipts.
10. Metacognition selects or changes reasoning strategy; it is not a hidden authority override.
11. Runtime/effect states must remain typed. Source, review, delivery, installation, activation, observed effect, and qualification do not collapse.
12. Kernel V0 should remain provider-independent and testable with deterministic/mock workers before external model integration.

## HCAE-specific reconciliation

The foundation branch correctly imposes a hard semantic firewall around latent state. The PR #1 HCAE episode experiment is therefore subordinate to the explicit hypergraph and evidence ledger.

The intended relationship is:

```text
canonical typed episode state
    -> compatible relational views over a homogeneous proposition set
    -> explicit view-specific incidence/hypergraph structures
    -> optional learned structural encoder
    -> advisory StructuralAnalysis
    -> scheduler/retrieval/metacognition inputs
```

The learned output never replaces directional logical/causal relations or hard provenance/currentness constraints.

## HCAE semantic reapplication follow-on

A later review lane initially produced `design/rezon-reasoning-foundation-v1@67a30ad4331ddfaa4b5cf51fa877c3e56115fb8d` and draft PR #3 from `main`. That work independently converged on the same deterministic-versus-learned firewall but was created before the lane discovered this consolidation branch. PR #3 is therefore retained as provenance/alternate design material rather than treated as the integration subject.

The integration follow-on is `rezon/hcae-semantic-reapplication-v1`, derived from this consolidated branch.

Material retained from the later lane because it adds non-redundant precision:

1. exact direct HCAE source pin: `basiralab/HCAE@ed13937a5266aadbfa34cd57e6c9a703470c77e9`;
2. explicit hyperedge construction classes: `EXPLICIT`, `DETERMINISTIC_DERIVED`, `LEARNED`, `HEURISTIC`;
3. stricter carrier-set semantics: the canonical Rezon graph may be heterogeneous, but an HCAE projection should normally operate over a coherent node set shared across all views rather than mixing propositions, sources, policies, actors, and tools into one learned geometry without a typed projection contract;
4. separation between `HCAE_EPISODE_LOCAL` and `HCAE_CORPUS_SHARED`.

The fourth point extends the earlier two-consumer model into three related HCAE uses:

```text
A. explicit multi-view hypergraph state
   canonical / inspectable / non-neural

B. HCAE_EPISODE_LOCAL
   per-episode latent structural perception
   coalition / outlier / reconstruction / compression

C. HCAE_CORPUS_SHARED
   one shared representation over a frozen compatible corpus
   cross-case structural analogy / missing-relation suggestion / advisory classification
```

This distinction is necessary because the studied HCAE implementation trains an encoder separately for each subject. That behavior supports an episode-local interpretation but does not by itself justify comparing independently trained episode embeddings as if they occupied one global coordinate system.

`HCAE_CORPUS_SHARED` is therefore explicitly a Rezon extension and must bind model, corpus, view-schema, carrier-schema, and input-state identities before cross-case comparison is qualified.

The later lane also corrected two source-transfer cautions rather than replacing the broader `SOURCE_TRANSFER_MATRIX.md`:

- Ontosphere's actual repository `LICENSE` is Apache-2.0 even though GitHub metadata was observed as `NOASSERTION`.
- `MiXaiLL76/n8n-nodes-sgr-tool-calling` has conflicting license evidence: repository metadata and `LICENSE` indicate GPL-3.0 while the README says AGPL-3.0 and describes AGPL obligations. Treat as reference-only until reconciled.

The detailed follow-on is `docs/research/HCAE_SEMANTIC_REAPPLICATION_V1.md`.

## Next executable frontier

Before writing substantial runtime code, update the Kernel V0 plan against the retained foundation requirements, especially:

- `TaskEnvelope` / `ResultReceipt` semantics;
- subject-track integration boundaries;
- typed failure states;
- retrieval receipts;
- independence metadata;
- lifecycle/effect-state preservation;
- hostile/broken-reference evaluation cases;
- HCAE mode separation and carrier/view-schema receipts where structural encoding is introduced.

Only then begin the provider-independent deterministic kernel implementation.
