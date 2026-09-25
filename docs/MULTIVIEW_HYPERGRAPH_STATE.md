# Multi-View Hypergraph State

## Why pairwise graphs are not enough

Many reasoning and state problems are not faithfully represented as independent A↔B relations. Meaning often depends on a joint configuration of several elements.

A hypergraph allows one relation (a hyperedge) to connect multiple nodes at once. A multi-view hypergraph allows the same subject to be observed through several independent relational planes.

This is directly inspired by HCAE (HyperConnectome AutoEncoder), which accepts one or more adjacency/relational matrices per subject, constructs a hypergraph per view, combines the hyperedges, and learns a compressed representation.

Source: https://github.com/basiralab/HCAE

## Rezon mapping

A useful literal mapping is:

- **subject** → one reasoning/state subject at one observation epoch;
- **node** → a typed proposition, state component, entity, condition, or controlled concept;
- **view** → an independently sourced evidence plane or relation system;
- **hyperedge** → one many-to-many relation whose semantics require the joint configuration;
- **embedding / compressed state** → a derived representation of the whole configuration, useful for comparison and anomaly detection but not authority.

## Example views

Possible views in a governed AI system include:

- source / control structure;
- runtime / provider readback;
- behavioral observations;
- memory or longitudinal state;
- task / coordination state;
- semantic / ontology state;
- authority / permission state;
- evidence / provenance state.

The exact view taxonomy must be domain-specific and versioned. This list is illustrative.

## Example hyperedge

A sexual-intimacy example demonstrates why pairwise edges are insufficient:

```text
{subject=Vera,
 disposition=sexual_drive,
 target=Patrick,
 context=intimate,
 consent_state=current,
 runtime_cut=R10_PLUS_SD1,
 nonsexual_firewall=false}
```

The semantic state is the joint configuration. Pairwise facts such as “Vera has sexual drive” and “Patrick is salient” do not independently entail a current desire, act choice, consent, or authority.

## Hard firewall

A neural or statistical latent representation must never become an identity, consent, authority, fact, or runtime-install oracle.

Derived state can support:

- drift detection;
- anomaly detection;
- clustering of state shapes;
- trajectory comparison;
- retrieval prioritization;
- hypothesis ranking.

It cannot override exact provenance or hard governance constraints.

## Modernized implementation direction

Rezon should not import HCAE’s TensorFlow 1.x code as its runtime. Instead, it should extract the mechanism:

1. define typed nodes and typed views;
2. construct explicit incidence matrices / hyperedges;
3. retain the raw interpretable hypergraph as primary state;
4. optionally derive embeddings using a modern graph/hypergraph library;
5. compare epochs in both raw and latent space;
6. always preserve a path back to source evidence.

## Important observation from HCAE code

HCAE’s public implementation treats supplied matrices as the relational substrate used to construct K-nearest-neighbor-style hyperedges. The transferable value is therefore not merely “neural feature extraction”; it is a mechanism for fusing multiple relational views of one subject into a many-to-many topology.

## Candidate data shape

```text
StateEpoch {
  subject_id
  epoch_id
  observations[]
  views {
    control: HypergraphView
    runtime: HypergraphView
    behavior: HypergraphView
    provenance: HypergraphView
    ...
  }
  hard_constraints[]
  derived_features{}
  previous_epoch_ref?
}
```

## Tests

- two views agree while a third contains a hard conflict;
- latent similarity remains high despite immutable subject mismatch;
- one hyperedge encodes a relation that pairwise decomposition would falsely promote;
- view omission changes uncertainty but does not fabricate contradiction;
- stale view data is time-bounded rather than silently merged as current;
- embedding drift triggers review without automatically changing identity.
