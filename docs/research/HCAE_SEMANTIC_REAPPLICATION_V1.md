# HCAE Semantic Reapplication V1

Status: `DESIGN_EVIDENCE / NO_RUNTIME_CLAIM`

Source subject: `basiralab/HCAE@ed13937a5266aadbfa34cd57e6c9a703470c77e9` (default branch `master` at review time)

License reported by the source README: MIT. No HCAE source code is copied into Rezon by this document.

## 1. Why HCAE matters to Rezon

HCAE should not be reduced to "a brain-state classifier." Its reusable idea is the representation and learning of **multi-view heterogeneous higher-order relational state**.

The original application models a subject through multiple connectome views. For each view, a hypergraph is constructed. A hypergraph differs from an ordinary graph because one hyperedge can connect an arbitrary set of vertices at once. The implementation then combines per-view hyperedge families, derives a normalized propagation operator, and learns an embedding by hypergraph convolution and reconstruction.

For Rezon, the semantic substitution is direct:

| HCAE object | Rezon object |
| --- | --- |
| subject | one reasoning case, decision, problem, or system snapshot |
| vertex / ROI | claim, observation, source, rule, action, hypothesis, decision, agent-state, artifact |
| view | one relation semantics such as provenance, authority, causal, temporal, support, contradiction, semantic, participant, or policy |
| hyperedge | one typed many-to-many reasoning context |
| incidence matrix `H` | membership and optional strength of reasoning objects in typed contexts |
| normalized propagation `G` | bounded propagation of contextual influence through a view or fused view-set |
| latent embedding | learned structural representation of a reasoning state |
| reconstruction residual | structural anomaly, incompleteness, or unfamiliarity signal |
| reconstructed membership | candidate missing contextual relation, never automatic truth |
| downstream prediction | optional classification or ranking of reasoning-state properties |

The brain domain is therefore an example data domain, not a mathematical requirement.

## 2. The reusable mathematical core

For hypergraph incidence matrix `H`, hyperedge-weight matrix `W`, vertex-degree matrix `Dv`, and hyperedge-degree matrix `De`, the source computes the normalized hypergraph propagation matrix:

```text
G = Dv^(-1/2) H W De^(-1) H^T Dv^(-1/2)
```

The source hypergraph convolution applies a learned feature transform and then propagates through `G`:

```text
X' = G X Theta
```

The HCAE encoder stacks hypergraph-convolution stages to obtain a latent embedding and trains against reconstruction of the input relational representation. An adversarial regularizer is used in the original system to shape the embedding distribution.

Rezon should preserve the semantic consequences of that structure without preserving the obsolete TensorFlow-1-era implementation.

## 3. Why ordinary pairwise graphs are insufficient

Many reasoning relations are natively set-valued.

Example:

```text
{user directive, source commit, runtime readback, reviewer finding, resulting decision}
```

This is not faithfully represented by asserting that every pair has the same relationship. The meaningful object is the whole contextual bundle: the directive was evaluated against that source and that runtime readback by that review to produce that decision.

Flattening the bundle into pairwise edges either:

1. invents relationships that were never asserted,
2. loses the identity of the original context, or
3. requires an artificial relation-node to recover what a hyperedge already expresses directly.

Rezon should therefore treat a typed hyperedge as a first-class reasoning object with its own identity, provenance, type, confidence, scope, time interval, and authority constraints.

## 4. Rezon view families

The first implementation should support explicit, separately inspectable views rather than one undifferentiated graph.

### 4.1 Provenance view

Connects a claim or state to the evidence bundle that establishes where it came from.

Example hyperedge:

```text
provenance_case_17 = {
  claim:C17,
  file:F4,
  commit:G81,
  runtime_receipt:R22,
  reviewer_review:V9
}
```

The existence of this hyperedge does not say the claim is true. It says these objects jointly define its provenance context.

### 4.2 Authority view

Represents which instruction, policy, branch, runtime, or actor has authority over a proposition or effect.

This view is deliberately separate from provenance because "where a statement came from" and "whether it is authoritative" are different questions.

### 4.3 Support / opposition view

Represents bundles of evidence supporting or opposing a hypothesis. One hyperedge can contain several mutually dependent observations that should not be counted as independent votes.

### 4.4 Contradiction view

Represents a contradiction context, including the propositions, scope, authority domain, and temporal qualifiers required for the contradiction to actually exist.

This is important because two different values are not necessarily contradictory if they apply at different times, branches, subjects, or authority layers.

### 4.5 Temporal/currentness view

Connects observations, snapshots, replacements, supersessions, validity intervals, and currentness receipts. This view is essential for preventing semantically similar but stale evidence from being treated as current.

### 4.6 Causal/dependency view

Represents sets of preconditions, actions, and effects. This permits reasoning over dependency bundles rather than pretending each prerequisite independently caused an effect.

### 4.7 Semantic view

Captures semantic similarity or conceptual relatedness. This may be constructed from language-model embeddings or other semantic models, but it has **no authority by itself**.

### 4.8 Participant/agent view

Represents which actors, models, tools, reviewers, or execution lanes participated in a reasoning event and in what roles.

### 4.9 Policy view

Connects actions or decisions to the policies, permissions, prohibitions, scopes, and exceptions that govern them.

## 5. Hyperedge construction: do not inherit KNN as dogma

The source HCAE implementation constructs hyperedges from K-nearest-neighbor structure because that construction made sense for its connectome input.

Rezon should not confuse that data-preparation method with the HCAE mathematical requirement. The encoder requires a usable incidence representation; it does not require that every hyperedge be inferred by KNN.

Rezon should support three construction classes:

### A. Deterministic semantic hyperedges

Created directly from structured evidence or explicit relations.

Examples:

- one Git commit and the files it changes,
- one PR review and its reviewed exact head,
- one runtime receipt and its measured subject,
- one policy and the actions governed by it,
- one contradiction with its scope qualifiers.

These are the highest-value hyperedges because their meaning is auditable.

### B. Derived rule hyperedges

Created by deterministic transformation from other trusted state.

Examples:

- all evidence items that jointly satisfy a qualification rule,
- all claims superseded by a newer exact-subject record,
- all actions participating in one dependency cut.

Every derived hyperedge needs a derivation receipt.

### C. Learned/similarity hyperedges

Created using embeddings, KNN, clustering, or learned retrieval.

These are useful for analogy, discovery, retrieval, and hypothesis generation. They are **suggestive**, not authoritative. They must remain labeled as learned or heuristic.

## 6. A reasoning case as a multi-view hypergraph

A Rezon reasoning case should compile into:

```text
ReasoningCase
  nodes: V
  views:
    provenance: Hp
    authority: Ha
    support: Hs
    contradiction: Hc
    temporal: Ht
    causal: Hk
    semantic: Hm
    participant: Hg
    policy: Hy
```

Each `H*` is an incidence family with its own typed hyperedges. Views may be encoded separately, jointly, or through a learned fusion layer, but Rezon must preserve view identity through the pipeline so a latent result can be traced back to contributing relation classes.

A naive concatenation similar to the original HCAE multi-view implementation is an acceptable baseline for experimentation, but it is not automatically the final fusion architecture.

## 7. What Rezon can literally use this for

### 7.1 Structural analogy retrieval

Two reasoning cases may use completely different words but share the same higher-order shape:

- a current claim,
- an older contradictory claim,
- a supersession record,
- an authority rule,
- a reviewer resolution.

A multi-view hypergraph embedding can retrieve such structural analogies even when lexical similarity is weak.

### 7.2 Missing-context suggestion

If a case is structurally similar to known complete cases but reconstruction repeatedly fails around a missing provenance or authority membership, Rezon can suggest:

```text
"This decision resembles cases that normally have an exact-source receipt. No such relation is present."
```

It must not manufacture the missing receipt.

### 7.3 Anomaly detection

High reconstruction residual can identify an unusual reasoning state: an unreviewed authority transition, a claim with support but no provenance, a decision whose policy relations are unlike known qualified decisions, etc.

Anomaly means "structurally unfamiliar," not "wrong."

### 7.4 Cross-view conflict detection

A node can be close in semantic view but distant or incompatible in authority/currentness view. This is exactly the failure mode of many naive RAG systems: semantically relevant stale material is retrieved as though it were current.

Rezon should explicitly expose cross-view disagreement rather than averaging it away.

### 7.5 Context assembly

Instead of retrieving the top-N semantically similar chunks, Rezon can retrieve the smallest useful higher-order neighborhood containing the target claim plus provenance, authority, temporal, policy, and contradictory context.

### 7.6 Reasoning-state classification

With validated labels, embeddings may support classifiers for states such as:

- `EVIDENCE_INCOMPLETE`
- `AUTHORITY_CONFLICT`
- `STALE_CURRENTNESS_RISK`
- `CONTRADICTION_UNRESOLVED`
- `QUALIFICATION_READY`
- `REVIEW_REQUIRED`

The classifier remains advisory unless a deterministic policy explicitly grants it a role.

### 7.7 Multi-agent state comparison

Each agent or lane can contribute a view or a subgraph to the same case. Rezon can compare where participants structurally agree and where their evidence/authority/context neighborhoods diverge without collapsing their states into one text summary.

## 8. Heterogeneous distributions are a feature, not noise

Git provenance, natural-language semantics, policy relations, timestamps, numerical measurements, tool actions, and reviewer judgments do not inhabit one natural statistical space.

A multi-view system should preserve that fact instead of forcing every relation through a single embedding metric. HCAE is relevant precisely because it was designed around multiple views whose distributions differ.

For Rezon, this suggests:

1. view-specific feature normalization,
2. view-specific encoders or projection heads where justified,
3. explicit fusion only after each view's semantics are preserved,
4. diagnostics for which views dominate a result,
5. ablation tests proving a claimed capability depends on the intended view rather than a shortcut.

## 9. What must change from the 2020 implementation

Rezon should treat the source implementation as research evidence, not production code.

Required departures:

1. **Modern framework:** use a maintained PyTorch/PyG/DGL-equivalent stack or a minimal project-local implementation rather than TensorFlow 1.x.
2. **Shared embedding space:** do not reset and retrain a new encoder independently for each reasoning case. Train one qualified model/version over a corpus so embeddings are comparable.
3. **Typed views:** preserve relation/view identity instead of blindly concatenating everything and erasing semantics.
4. **Configurable latent dimension:** the source demo's one-dimensional second hidden layer is task-specific, not a Rezon requirement.
5. **Explicit provenance:** every node, hyperedge, feature, derived relation, model version, and inference result needs provenance.
6. **Deterministic baseline first:** before neural learning, compile the same typed hypergraph into inspectable deterministic queries so the learned system has something to be tested against.
7. **No authority laundering:** model score, embedding proximity, reconstruction quality, and classifier output can never silently become source authority.
8. **Frozen evaluation subjects:** learned-model evaluation must use held-out reasoning cases and exact corpus/model digests.

## 10. Neuro-symbolic boundary

Rezon should be explicitly hybrid.

Deterministic layer owns:

- identity,
- provenance,
- authority,
- exact membership,
- policy constraints,
- explicit contradiction rules,
- currentness receipts,
- protected effects.

Learned hypergraph layer may provide:

- similarity,
- anomaly scores,
- likely missing relation suggestions,
- structural clustering,
- retrieval ranking,
- learned state classification,
- latent representations.

A learned result may trigger deterministic investigation. It cannot replace deterministic evidence.

## 11. Minimal experiment worth building

The first HCAE-derived Rezon experiment should be intentionally small.

Corpus: hand-authored synthetic reasoning cases with exact expected structure.

Views:

1. provenance,
2. authority,
3. temporal/currentness,
4. support/opposition.

Tasks:

- reconstruct held-out hyperedge memberships,
- retrieve structurally analogous cases,
- detect deliberately damaged cases,
- distinguish semantic similarity from authority compatibility.

Baselines:

- pairwise graph representation,
- flattened feature vector,
- semantic-embedding-only retrieval,
- deterministic typed-hypergraph query.

The HCAE-derived system is interesting only if it adds measurable value over those baselines without hiding provenance or authority.

## 12. Acceptance principle

The central Rezon interpretation of HCAE is:

> Reasoning is not merely a sequence of tokens or a set of pairwise facts. A reasoning state is a collection of overlapping, typed, higher-order relational views. Learned representations may compress and compare that structure, while deterministic evidence and policy retain authority.

That is the part worth carrying forward.