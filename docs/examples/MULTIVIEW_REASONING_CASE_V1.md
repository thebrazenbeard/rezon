# Multi-View Reasoning Case V1

Status: `WORKED_EXAMPLE / NON-PRODUCTION`

Purpose: demonstrate how one reasoning subject can be represented simultaneously across deterministic and learned views without collapsing all relationships into one graph.

## Scenario

A system has two statements about a configuration value:

- an older design document says `MAX_RETRIES = 3`,
- the current approved source says `MAX_RETRIES = 5`.

A model retrieves the older document first because its wording is semantically closer to the user's question.

The reasoning problem is not simply "3 versus 5." Rezon must determine whether this is a contradiction, supersession, stale-currentness risk, or a scoped divergence.

## Nodes

```text
N1  QUESTION
    "What is the current MAX_RETRIES value?"

N2  CLAIM
    MAX_RETRIES = 3

N3  SOURCE
    design-v1.md

N4  CLAIM
    MAX_RETRIES = 5

N5  SOURCE
    config/current.yaml

N6  RULE
    current approved source outranks historical design material

N7  OBSERVATION
    semantic retriever ranked design-v1.md first

N8  RESULT
    current MAX_RETRIES = 5

N9  RESULT
    older value is historical/superseded, not current authority
```

## Provenance view

```text
HP1 EXPLICIT:
  { N2, N3 }

HP2 EXPLICIT:
  { N4, N5 }

HP3 EXPLICIT:
  { N7, retriever-model-version, query-snapshot }
```

This view answers where each claim/result came from. It does not decide which claim governs.

## Authority view

```text
HA1 EXPLICIT:
  { N4, N5, N6 }
```

Interpretation: claim `N4` participates in an authority context established by source `N5` and rule `N6`.

No equivalent current-authority hyperedge exists for `N2`.

## Temporal/currentness view

```text
HT1 DETERMINISTIC_DERIVED:
  relation_type = SUPERSEDES
  { N4, N2, N5, N3 }
```

A derivation receipt records how source timestamps/version identities established the supersession relation.

## Semantic view

```text
HM1 LEARNED:
  relation_type = SEMANTIC_NEIGHBORHOOD
  { N1, N2, N3 }
  weight = 0.94

HM2 LEARNED:
  relation_type = SEMANTIC_NEIGHBORHOOD
  { N1, N4, N5 }
  weight = 0.79
```

The semantic view prefers the stale material. This is permitted because semantic closeness is not authority.

## Contradiction view

A naive system might create:

```text
{ N2, N4 } => CONTRADICTION
```

Rezon should not.

The temporal and authority context show that the values apply to different source generations. The correct deterministic classification is:

```text
SUPERSESSION
```

not:

```text
CONTRADICTION_CONFIRMED
```

A contradiction would require both claims to assert incompatible values over the same subject, scope, validity interval, and governing authority context.

## Result construction

The reasoning trace can be summarized as explicit operators:

```text
1 EXACT_LOOKUP
  -> find claims about MAX_RETRIES

2 TEMPORAL_CURRENTNESS_CHECK
  -> establish N4/N5 as current and N2/N3 as historical

3 RULE_EVALUATION
  -> apply N6

4 CONTRADICTION_CHECK
  -> classify N2 vs N4 as SUPERSESSION

5 RESULT
  -> create N8 and N9 with receipt linking input-state digest and operators
```

The semantic retrieval result `N7` remains in the state because it is diagnostically useful: it shows why the wrong material was initially attractive.

## HCAE-derived use

Now suppose a training corpus contains many cases with this structural pattern:

```text
question
+ semantically strong stale claim
+ weaker semantic current claim
+ supersession edge
+ authority rule
+ correct final result
```

A multi-view hypergraph encoder may learn that shape.

For a new case, it may produce:

```text
SIMILAR_CASES:
  case_17 score 0.91
  case_42 score 0.88

ANOMALY_SCORE:
  0.71

MISSING_RELATION_SUGGESTION:
  "Current candidate has no temporal/currentness hyperedge."
```

Those are useful outputs because they direct investigation toward the missing relation.

They still do not establish the current value. Only explicit source and authority/currentness evidence can do that.

## Why the hypergraph matters

A pairwise graph can represent individual links:

```text
claim -> source
claim -> rule
source -> timestamp
```

But the reasoning event often depends on a bundle:

```text
{current claim, current source, authority rule, superseded claim, historical source}
```

The bundle itself is the context. A typed hyperedge preserves that higher-order relation and allows Rezon to compare entire reasoning structures across cases.

## Cross-view disagreement is signal

This example intentionally produces disagreement:

```text
SEMANTIC view:
  stale source looks best

AUTHORITY view:
  current source governs

TEMPORAL view:
  stale source is superseded
```

Rezon should expose this disagreement rather than average it into one score.

That is one of the central reasons for a multi-view architecture.