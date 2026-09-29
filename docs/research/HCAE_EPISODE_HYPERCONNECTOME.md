# HCAE as a Literal Rezon Subsystem

Status: RESEARCH DESIGN / UNIMPLEMENTED

Source studied: `basiralab/HCAE` (HyperConnectome AutoEncoder, MIT-licensed repository at time of study).

## Why HCAE matters beyond the word "hyperconnectome"

The useful mechanism is not merely that HCAE uses hypergraphs. Its implementation constructs a hypergraph incidence matrix `H`, derives a normalized propagation matrix

```text
G = Dv^(-1/2) H W De^(-1) H^T Dv^(-1/2)
```

and applies hypergraph convolution by transforming node features and propagating them through `G`.

For multi-view data, the implementation constructs one hyperconnectome per view and concatenates the view-specific hyperedge sets before encoding. The model learns a compressed embedding while reconstructing the hyperconnectome structure.

The repository also trains an encoder separately for each supplied subject rather than relying only on one globally fixed subject embedding. That makes a per-reasoning-episode interpretation plausible.

## Literal semantic mapping to Rezon

HCAE concept -> Rezon concept:

```text
subject                 -> one reasoning episode
brain ROI/node          -> one canonical proposition
connectivity view       -> one compatible relational view over the same proposition set
view hyperconnectome    -> high-order neighborhoods induced from that view
fused hyperconnectome   -> combined episode structural representation
latent embedding        -> learned structural coordinates for episode propositions
reconstruction error    -> structural mismatch / unexplained organization signal
```

The proposition set must be homogeneous enough for the view matrices to be semantically comparable. Tools, models, schedulers, and permissions should not be casually mixed into the same node matrix merely because they exist in the episode.

## Candidate relational views

For canonical propositions `P1..PN`, Rezon can construct several `N x N` view matrices. Early candidates:

1. `SEMANTIC_VIEW`: semantic relatedness between proposition contents.
2. `EVIDENCE_VIEW`: overlap or relationship in evidentiary support paths.
3. `PROVENANCE_VIEW`: shared or correlated source provenance.
4. `COMPATIBILITY_VIEW`: compatibility/contradiction structure transformed into a suitable symmetric structural view.
5. `COACTIVATION_VIEW`: propositions repeatedly consumed or produced together by reasoning executions.

A later experiment may add causal or temporal views only if their directional semantics can be represented without destroying meaning. Canonical directional causal/logical relations remain outside the HCAE latent geometry regardless.

## Proposed episode flow

```text
canonical epistemic graph
        |
        +--> choose canonical proposition set
        |
        +--> build compatible view matrices
                 |
                 +--> construct view hyperconnectomes
                 |
                 +--> fuse hyperedges
                 |
                 +--> derive propagation matrix G
                 |
                 +--> encode/reconstruct
                          |
                          +--> proposition embeddings
                          +--> reconstruction diagnostics
                          +--> coalition/outlier candidates
                                   |
                                   +--> scheduler/metareasoner
```

## What Rezon can literally use the output for

### 1. Coalition discovery

If propositions repeatedly occupy the same high-order neighborhoods across several views, Rezon can schedule a reasoning operation over that coalition rather than treating every proposition independently.

### 2. Structural outlier detection

A proposition that is semantically near a cluster but structurally distant under evidence/provenance views may deserve scrutiny. This can expose unsupported narrative glue.

### 3. Reconstruction-error targeting

High local or episode reconstruction error can be treated as a metareasoning signal that current relational views do not fit together cleanly. The scheduler can spend additional reasoning budget in that region.

Reconstruction error is not epistemic uncertainty by definition; it is a structural-model error signal that may correlate with useful uncertainty and must be empirically calibrated.

### 4. Context compression

When an LLM node cannot ingest the whole episode, Rezon can select structurally representative propositions from distinct latent regions while retaining the complete canonical graph outside the LLM context.

### 5. View ablation

Re-encoding after removing one view can measure whether a coalition or apparent coherence is dependent on a single structural lens. A particularly important case is provenance ablation: repeated statements from one source must not masquerade as independent support.

### 6. Routing

The scheduler can incorporate latent region, outlier status, and reconstruction diagnostics alongside explicit contradiction, cost, and node health when deciding the next operation.

## What not to copy blindly from HCAE

The studied implementation includes brain-dataset-specific dimensions and fixed K-neighbor settings. These are experimental parameters, not Rezon invariants.

Its adversarial regularization derives a distributional prior suited to the source experiment. Rezon must not reuse that prior without an epistemic justification.

The original codebase uses an older TensorFlow stack. A Rezon experiment should reimplement only the required mechanism in a modern, isolated research module rather than importing the old runtime wholesale.

The latent embedding is advisory. Explicit provenance, logical implication, contradiction, causal direction, and formal proof objects remain authoritative structured state and cannot be replaced by latent geometry.

## Falsifiable experiment

Construct a benchmark set of reasoning episodes with known answers and injected structural defects. Compare:

- kernel without HCAE-derived state;
- kernel with HCAE-derived coalition/outlier/reconstruction signals.

Measure correctness, calibration, unsupported-claim detection, contradiction discovery, reasoning cost, and latency.

The HCAE-derived subsystem earns promotion only if it improves a predeclared metric or gives a measurable efficiency benefit without unacceptable correctness loss.
