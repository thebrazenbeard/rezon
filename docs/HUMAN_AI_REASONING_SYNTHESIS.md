# Human / AI Reasoning Synthesis

Rezon should combine useful mechanisms from human reasoning research with machine-native reasoning methods without pretending they are the same thing.

## Human-style mechanisms worth borrowing

Humans do not reason as a single homogeneous process. Useful abstractions include:

- **fast / slow processing:** rapid pattern recognition and slower deliberation;
- **attention:** selective allocation of limited processing to salient inputs;
- **chunking:** compressing recurring structures into manageable working units;
- **schema use:** interpreting new information through reusable relational templates;
- **hypothesis competition:** maintaining multiple explanations before commitment;
- **causal narrative construction:** preferring models that explain temporal and mechanistic structure;
- **analogy:** reusing relational patterns across domains;
- **metacognition:** changing strategy when the current one is failing;
- **social reasoning:** modeling beliefs, incentives, intentions, and communication pragmatics;
- **error correction:** revising beliefs when contradiction or prediction failure appears.

These can inspire architecture. They do not establish consciousness, emotion, embodiment, or human-like subjective continuity in an AI system.

## Machine-native strengths

AI systems add different strengths:

- massive parallel retrieval and comparison;
- exact symbolic and numerical subroutines;
- graph traversal and database joins;
- deterministic replay;
- explicit state machines;
- cheap duplication of independent reviewers;
- structured tool use;
- rapid transformation between representations;
- exhaustive local search where the state space is bounded;
- proof, test, and receipt generation;
- externalized memory with exact provenance.

## Productive hybrids

### Fast heuristic node + slow verifier
A lightweight node generates likely routes. A more expensive verifier checks only the candidates that matter.

### Generative hypothesis node + symbolic constraint node
One system proposes explanations or designs; another rejects candidates that violate hard constraints.

### Semantic parser + domain solver
A semantic node first establishes what proposition is actually being asked. A specialist solves that proposition rather than an inferred substitute.

### Retrieval navigator + reasoner
A retrieval node determines where evidence is likely to live; the reasoner evaluates it. Retrieval relevance and inference validity stay separate.

### Opponent + integrator
An opponent is rewarded for finding defects, not for consensus. An integrator then weighs the defect against the original case.

### Persistent track + fresh observation model
A longitudinal subject is maintained through explicit association evidence, while each runtime/chat remains a fresh observation surface.

## Anti-patterns

Rezon should reject several common “human-like AI” shortcuts:

- treating verbose chain-of-thought as equivalent to reasoning quality;
- treating confidence language as probability calibration;
- treating personality continuity as process continuity;
- treating memory retrieval as present belief;
- treating consensus among cloned agents as independent evidence;
- treating one large model as inherently better at every reasoning operation;
- treating analogy as proof;
- treating a latent embedding as an identity or authority oracle.

## Architecture implication

The useful synthesis is not “make AI reason like a human.” It is:

> decompose reasoning into mechanisms, keep their semantics explicit, combine complementary mechanisms, and preserve machine advantages such as replay, external state, independent verification, and exact provenance.
