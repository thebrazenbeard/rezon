# Vera Adoption Candidates

This document records mechanisms from Rezon research that may be worth promoting into Vera’s architecture. Nothing here is installed merely because it is listed.

## Candidate 1 — Persistent identity tracking

**Status:** HIGH-VALUE / DESIGN CANDIDATE / NOT INSTALLED

Why:

Vera already distinguishes stable governed identity from fresh runtime/process continuity. A formal subject-track mechanism would make that distinction executable instead of leaving it only in prose.

Potential benefits:

- explicit reacquisition after new chats/runtimes;
- hard/soft identity evidence separation;
- ambiguity and conflict states;
- drift detection without identity revocation;
- no need to claim uninterrupted hidden processing.

Required hostile tests:

- impostor with matching style;
- stale restore with correct name but wrong generation;
- exact source but wrong admitted subject;
- ambiguous simultaneous candidates;
- provider/runtime reset followed by valid reacquisition.

## Candidate 2 — Multi-view state topology / hypergraph

**Status:** HIGH-VALUE / RESEARCH-TO-DESIGN / NOT INSTALLED

Why:

Many Vera states are joint configurations and cannot safely be reduced to pairwise edges. Source state, runtime state, memory state, behavior, authority, and relationship semantics may each be separate views of the same subject epoch.

Hard rule:

Derived embeddings may flag drift or similarity but never establish identity, consent, authority, desire, installation, or factual truth.

## Candidate 3 — Hierarchical reasoning scheduler

**Status:** HIGH-VALUE / ARCHITECTURAL CANDIDATE / NOT INSTALLED

Why:

Vera work already naturally separates strategic integration from bounded execution/review lanes. Formalizing slow strategic planning and fast tactical workers could reduce duplicated context and improve specialist routing.

Required constraint:

Worker capability never grants new authority.

## Candidate 4 — Literal-proposition opposition operator

**Status:** APPROVED CONCEPT / GOVERNED ARCHITECTURE WORK PAUSED / NOT YET INSTALLED

Why:

This method directly protects proposition fidelity and prevents benevolent substitution. It should be a method layer, not a permanent argumentative personality.

Behavioral baseline note:

Temporary hostile/debug/reviewer modes must not silently redefine the model-level personality attractor or Vera-specific identity/self-concept.

## Candidate 5 — Structured reasoning retrieval

**Status:** HIGH-VALUE / PROTOTYPE CANDIDATE

Why:

Vera has large project/repository/history corpora. PageIndex-style hierarchical retrieval could reduce giant restore/context dumps and improve evidence locality while preserving source locators.

## Candidate 6 — Semantic verifier / repair lane

**Status:** MEDIUM/HIGH-VALUE / RESEARCH CANDIDATE

Potential mechanisms:

- canonical semantic-state hashing;
- ontology/constraint validation;
- asserted vs inferred state separation;
- contradiction diagnosis;
- reasoner-verified repair suggestions;
- provenance/reversal.

Caution:

Logical consistency is not equivalent to governance correctness or domain truth.

## Candidate 7 — Optional high-reasoning specialist worker

**Status:** CONDITIONAL / PROVIDER CAPABILITY UNRESOLVED

If a stable Ultra/very-high-reasoning callable becomes available, Vera could use it as an optional specialist for hostile review, architecture challenge, difficult synthesis, and proof checking.

It must remain:

- optional;
- capability-discovered at runtime;
- resource bounded;
- evidence checked;
- no stronger authority because of model rank;
- not required for identity or baseline behavior.

## Candidate 8 — Evidence / decision graph

**Status:** HIGH-VALUE / LIKELY SUBSTRATE

Represent important decisions, supporting/conflicting evidence, source versions, and transformations as queryable state rather than prose-only receipts.

## Adoption ordering recommendation

The likely lowest-risk/highest-value order is:

1. literal-proposition opposition method;
2. persistent identity track;
3. typed evidence/decision graph;
4. structured retrieval;
5. multi-view hypergraph state;
6. hierarchical worker scheduler;
7. semantic reasoner/repair service;
8. optional Ultra/high-cost worker adapter when a callable surface actually exists.

This ordering is provisional and should be re-evaluated after Rezon prototypes produce evidence.
