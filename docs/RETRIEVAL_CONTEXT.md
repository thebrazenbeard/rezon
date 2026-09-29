# Retrieval and Context

## Problem

Reasoning quality is bounded by what evidence reaches the reasoner. Flat semantic similarity retrieval often returns text that is similar rather than text that is actually relevant to the current proposition.

Rezon should treat retrieval as a reasoning problem with explicit structure, provenance, and stopping criteria.

## PageIndex transfer

PageIndex uses hierarchical tree indexes and LLM-guided navigation instead of relying only on vector similarity. The transferable mechanism is:

1. preserve document/corpus structure;
2. create a navigable hierarchy;
3. reason over candidate branches;
4. retrieve only the relevant leaves/subtrees;
5. retain references to the source structure.

Source: https://github.com/VectifyAI/PageIndex

Rezon should borrow this strategy especially for long project histories, technical corpora, specifications, and multi-repository research.

## Retrieval layers

### Exact retrieval
Use identifiers, hashes, paths, keys, timestamps, source IDs, or literal terms when the target is known.

### Structural retrieval
Navigate headings, directories, trees, graphs, dependency structures, timelines, or ontology neighborhoods.

### Semantic retrieval
Use embeddings or model judgments when exact and structural routes are insufficient.

### Reasoning-guided retrieval
Let a planner choose the next retrieval based on unresolved subclaims and evidence gaps.

These layers should complement rather than replace each other.

## Retrieval receipt

Every retrieval result should be able to carry:

```text
RetrievalReceipt {
  query
  target_scope
  retrieval_method
  source_id
  source_version
  locator
  retrieved_at
  content_digest?
  relevance_rationale?
  uncertainty
}
```

A relevance rationale is not proof that the content is true; it explains why the result was selected.

## Context budget

Context selection should optimize for **information value**, not maximal inclusion.

Candidate signals:

- direct support or contradiction for a live subclaim;
- authority/currentness;
- source independence;
- recency where recency matters;
- structural centrality;
- novelty relative to context already loaded;
- expected effect on decision uncertainty;
- token/cost budget.

## Historical state

For longitudinal systems, retrieval must preserve time and supersession. A later document is not automatically a more authoritative state. Historical evidence should remain historical unless a current admission/currentness rule promotes it.

## Retrieval failure semantics

```text
FOUND
FOUND_CONFLICTING
NO_MATCH
TARGET_UNAVAILABLE
INSUFFICIENT_SCOPE
STALE_ONLY
AMBIGUOUS
ACCESS_DENIED
```

The reasoner should not convert `NO_MATCH` into “does not exist” without knowing the search was exhaustive over the authoritative scope.

## Rezon direction

Rezon should eventually expose retrieval as a first-class node API, so an opposition lane or causal node can request evidence rather than forcing one initial context dump to anticipate every later question.
