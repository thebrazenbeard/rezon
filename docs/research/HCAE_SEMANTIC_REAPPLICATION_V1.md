# HCAE Semantic Reapplication V1

Status: `RESEARCH DESIGN / UNIMPLEMENTED / NO AUTHORITY CLAIM`

Reconciles and extends:

- `docs/MULTIVIEW_HYPERGRAPH_STATE.md`
- `docs/research/HCAE_EPISODE_HYPERCONNECTOME.md`
- `docs/architecture/REZON_ARCHITECTURE_V0.md`
- `docs/BRANCH_RECONCILIATION_20260915.md`

Source subject reviewed directly: `basiralab/HCAE@ed13937a5266aadbfa34cd57e6c9a703470c77e9`.

The source README states MIT licensing. This document transfers mechanism and semantics only; it does not import HCAE source code into Rezon.

## 1. The literal mechanism worth transferring

HCAE is not useful to Rezon merely because the word *hyperconnectome* sounds cognitively relevant. Its code implements a concrete transformation:

1. one subject is represented by one or more relational views over the same node set;
2. each view is converted into a hypergraph incidence structure;
3. view-specific hyperedge families are concatenated for multi-view encoding;
4. a normalized hypergraph propagation matrix is derived;
5. hypergraph convolution produces a compressed structural representation;
6. the representation is trained against reconstruction, with an adversarial regularizer in the source experiment.

The source propagation operator is:

```text
G = Dv^(-1/2) H W De^(-1) H^T Dv^(-1/2)
```

and the convolutional pattern is effectively:

```text
X' = G X Theta
```

where `H` is the incidence structure, `W` contains hyperedge weights, `Dv` and `De` are vertex/hyperedge degree terms, and `Theta` is learned.

The transferable mechanism is therefore **multi-view higher-order relational encoding**, not a brain classifier and not a claim that Rezon should imitate biological cognition.

## 2. Critical semantic correction: the HCAE carrier set must stay coherent

The canonical Rezon episode may contain heterogeneous object kinds:

```text
propositions
sources
rules
actors
executions
measurements
artifacts
policies
receipts
```

That does **not** imply that all such objects belong in one HCAE node matrix.

The source HCAE implementation assumes that every view describes the same `m` nodes for a subject. Its multi-view path accepts several `m x m` matrices and constructs one hyperconnectome per view over that shared carrier set.

For Rezon, the safest initial carrier set is therefore a homogeneous set such as:

```text
P = {canonical propositions participating in one reasoning episode}
```

Sources, policies, actors, executions, and runtime receipts may determine the values of a view, annotate a hyperedge, or remain linked in the canonical epistemic graph without themselves becoming HCAE carrier nodes.

Example:

```text
canonical state:
  proposition P17
  source S4
  authority rule R2
  runtime receipt X9

HCAE projection:
  carrier node = P17
  provenance-view relations involving P17 are derived from S4/X9
  authority compatibility involving P17 is derived from R2
```

This distinction prevents the learned geometry from conflating semantically different object types merely because they coexist in the episode.

A heterogeneous carrier set is not prohibited forever, but it requires an explicit typed projection design and evidence that the mixed geometry is meaningful.

## 3. Rezon should distinguish three HCAE-related states

The existing foundation already distinguishes explicit multi-view hypergraph state from an optional episode encoder. This document adds a third mode needed for cross-case reasoning.

### 3.1 Explicit deterministic multi-view state

This is canonical Rezon structure, not a neural model.

```text
canonical episode
    -> selected carrier set P
    -> typed view projections
    -> explicit incidence / hyperedge structures
```

Uses:

- exact inspection,
- deterministic neighborhood queries,
- provenance-preserving state,
- contradiction/currentness constraints,
- reproducible input to learned experiments.

This state remains inspectable even if every learned model is disabled.

### 3.2 Episode-local structural encoder

Mode label: `HCAE_EPISODE_LOCAL`.

The source implementation trains an encoder separately for each supplied subject. That makes an episode-local interpretation faithful to the source mechanism.

Purpose:

- discover proposition coalitions within one episode,
- detect within-episode structural outliers,
- identify regions of high reconstruction mismatch,
- compress one episode while retaining structural coverage,
- provide local routing/metareasoning signals.

Important limitation:

> Embeddings learned independently per episode are not automatically coordinates in one shared cross-episode space.

Therefore an episode-local embedding must not be used for cross-case nearest-neighbor retrieval unless an explicit alignment method is introduced and validated.

### 3.3 Corpus-shared structural encoder

Mode label: `HCAE_CORPUS_SHARED`.

This is a Rezon extension, not a claim about the original HCAE implementation.

One model is trained across a frozen corpus of reasoning episodes whose view schemas and carrier semantics are compatible.

Purpose:

- retrieve structurally analogous reasoning cases,
- compare episode shapes across time,
- learn recurring structural failure patterns,
- detect missing relation families relative to known complete cases,
- classify advisory reasoning-state categories.

Required additional controls:

```text
model_digest
training_corpus_digest
view_schema_digest
carrier_schema_digest
input_episode_digest
normalization contract
runtime/dependency identity
```

Cross-case comparison is allowed only inside a qualified shared representation domain.

## 4. View construction is the main semantic problem

HCAE's math is straightforward compared with deciding what a view *means*.

A Rezon view should satisfy:

1. all rows/columns refer to the same carrier-node identity set;
2. the view has one declared relation semantics;
3. its numeric value has a defined interpretation;
4. directionality loss, if any, is explicitly justified;
5. provenance exists for deterministic view values;
6. learned/heuristic view values remain labeled as such;
7. missing data is distinguishable from neutral/zero relation.

Initial proposition-carrier views:

### `SEMANTIC_VIEW`

Meaning: conceptual/linguistic relatedness between propositions.

May be learned. Has no authority by itself.

### `EVIDENCE_COSHARE_VIEW`

Meaning: degree to which propositions depend on overlapping evidence bundles.

Critical use: detect repeated claims sharing one source so they do not masquerade as independent support.

### `PROVENANCE_VIEW`

Meaning: structural relatedness induced by common or linked provenance paths.

A high value does not mean two propositions are jointly true; it means their source lineage is structurally related.

### `COMPATIBILITY_VIEW`

Meaning: proposition compatibility after explicit contradiction/scope analysis.

Do not convert directional logical implication into a symmetric compatibility score and then forget the original direction. Canonical directional relations remain outside the latent geometry.

### `COACTIVATION_VIEW`

Meaning: propositions repeatedly consumed, emitted, or jointly selected by reasoning executions.

Useful for discovering operational coalitions, but susceptible to scheduler-induced bias.

### `TEMPORAL_COHERENCE_VIEW`

Candidate experimental view only after semantics are frozen.

Meaning could be similarity of validity windows, supersession neighborhoods, or episode timing. It must not silently collapse "old" into "wrong."

### `AUTHORITY_COMPATIBILITY_VIEW`

Candidate experimental view derived from deterministic authority state.

It can describe whether propositions belong to compatible authority scopes. It may help identify semantically coherent but authority-incompatible clusters.

The canonical authority records remain primary; the view is a projection.

## 5. Hyperedge construction classes

Rezon should record how every hyperedge was created.

```text
EXPLICIT
  directly represented in accepted structured state

DETERMINISTIC_DERIVED
  computed by a versioned deterministic transformation from explicit state

LEARNED
  produced by a model or learned similarity function

HEURISTIC
  produced by a non-learned approximation or search heuristic
```

This classification belongs in both explicit multi-view state and any training/evaluation export.

The original HCAE repository uses a nearest-neighbor-style construction because that was appropriate to its input. Rezon must not elevate KNN into a universal hyperedge law.

Examples:

```text
PROVENANCE hyperedge
  likely DETERMINISTIC_DERIVED from shared source paths

SEMANTIC hyperedge
  likely LEARNED from semantic representations

COACTIVATION hyperedge
  DETERMINISTIC_DERIVED from execution receipts

manually curated benchmark defect
  EXPLICIT in the frozen evaluation fixture
```

## 6. What HCAE output can literally do in Rezon

### 6.1 Episode-local coalition discovery

Find proposition groups occupying the same higher-order neighborhoods across several views.

Consumer: scheduler / metareasoner.

### 6.2 Structural outlier detection

Example:

```text
semantic neighborhood: close
provenance neighborhood: distant
support neighborhood: weak
```

This may identify unsupported narrative glue or suspicious convergence.

Consumer: adversarial verifier.

### 6.3 Reconstruction-targeted reasoning

High local reconstruction error can allocate more reasoning budget to a region whose views do not fit the learned structural model.

The correct statement is:

```text
"this relational structure is poorly reconstructed"
```

not:

```text
"this proposition is false" or "uncertain"
```

unless a separate calibration study supports a narrower inference.

### 6.4 Context compression

Select structurally representative propositions from different latent regions when an executor cannot ingest the whole episode.

The full canonical episode remains outside the compressed context.

### 6.5 View ablation

Remove one view and recompute structural state.

Examples:

- remove provenance and see whether apparent support collapses;
- remove semantic similarity and see whether a coalition is still structurally connected;
- remove coactivation and detect scheduler-induced clustering.

### 6.6 Cross-case structural retrieval

`HCAE_CORPUS_SHARED` only.

Retrieve prior reasoning episodes whose relational organization resembles the current case even when wording is different.

This requires a shared model/corpus/schema identity. Episode-local embeddings are insufficient by themselves.

### 6.7 Missing-relation suggestion

`HCAE_CORPUS_SHARED` may learn that cases of one structural type normally contain an authority/provenance/support relation absent from the current case.

The output is a search target:

```text
"look for missing provenance"
```

not fabricated provenance.

## 7. Cross-view disagreement should remain visible

Rezon should not blindly average all views into one score.

A valuable reasoning pattern is precisely disagreement among views:

```text
SEMANTIC_VIEW
  propositions look nearly identical

PROVENANCE_VIEW
  propositions come from different source families

AUTHORITY_COMPATIBILITY_VIEW
  only one belongs to the current governing scope

TEMPORAL_COHERENCE_VIEW
  one belongs to a superseded epoch
```

A fused embedding may be useful, but diagnostics must preserve enough view-level state to explain that the similarity and currentness signals disagree.

## 8. Directionality and logic firewall

HCAE's normalized propagation matrix is naturally suited to symmetric structural relations. Rezon contains many relations that are not symmetric:

```text
A implies B
A causes B
A supersedes B
A derives from B
policy P governs action X
```

Do not destroy those semantics merely to fit HCAE input.

Safe rule:

> The canonical temporal epistemic hypergraph owns directional logic, causal direction, authority, and provenance. HCAE receives only projections whose loss of direction has a declared meaning.

For example, a directional `SUPERSEDES(A, B)` relation could contribute to a symmetric view meaning "participates in the same supersession neighborhood," while the actual direction remains in canonical state.

## 9. Adversarial regularization should not be cargo-culted

The original implementation fits a distributional prior from the source experiment and trains a discriminator against it.

That does not establish that the same prior is epistemically appropriate for Rezon.

The first Rezon experiment should test:

```text
plain reconstruction
vs.
regularized reconstruction
```

and introduce an adversarial prior only when the prior has a stated purpose and improves a frozen metric.

## 10. Minimum experiment matrix

### Experiment A — explicit hypergraph value

Question: does preserving many-to-many structure improve deterministic queries or defect localization compared with pairwise projection?

No neural encoder required.

### Experiment B — episode-local HCAE value

Question: within one episode, do coalition/outlier/reconstruction signals improve routing or contradiction discovery over deterministic structural heuristics?

Compare:

```text
no learned structural state
simple spectral/centrality baseline
HCAE_EPISODE_LOCAL
```

### Experiment C — corpus-shared HCAE value

Question: does a shared multi-view encoder improve cross-case analogy and missing-relation detection?

Compare:

```text
text embedding only
flattened structural features
pairwise graph embedding
multi-view hypergraph encoder
```

### Experiment D — view ablation

Question: which views actually produce the claimed gain?

Remove one view at a time and measure the change.

## 11. Required receipts

Any HCAE-derived result should be reconstructible to this level:

```text
StructuralAnalysisReceipt {
  episode_digest
  carrier_set_digest
  view_schema_digest
  view_input_digests{}
  hyperedge_construction_versions{}
  mode                 # EPISODE_LOCAL or CORPUS_SHARED
  model_digest
  training_corpus_digest?  # required for CORPUS_SHARED
  runtime_identity
  random_seed_contract
  output_digest
  metrics{}
}
```

If the receipt is missing, the output is exploratory and must be labeled accordingly.

## 12. Reconciled architectural position

HCAE has **three** legitimate relationships to Rezon:

```text
1. explicit multi-view hypergraph representation
   canonical / inspectable / non-neural

2. HCAE_EPISODE_LOCAL
   learned per-episode structural perception
   coalition / outlier / reconstruction / compression

3. HCAE_CORPUS_SHARED
   shared learned structural space
   cross-case analogy / missing-relation suggestion / advisory classification
```

All three are subordinate to the canonical temporal epistemic hypergraph for identity, provenance, directional logic, causal direction, authority, currentness, consent, runtime state, and protected effects.

The system should use HCAE seriously enough to preserve what its mathematics actually assumes—and skeptically enough not to turn a useful structural model into an oracle.