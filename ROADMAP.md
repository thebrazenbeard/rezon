# Roadmap

Rezon has moved past its original knowledge-foundation phase. The near-term goal
is to turn the existing kernel into a useful assurance component that can sit
beside real agent and workflow runtimes.

## Completed foundation

The repository now contains:

- a provider-independent executable Kernel V0 lineage;
- typed task, node, proposition, relation, receipt, trace, and admission contracts;
- exact source-version and provenance binding;
- independence and contamination controls;
- canonical Episode mutation and rollback controls;
- deterministic producer/output identity binding;
- frozen replay benchmarks and hostile cases;
- deterministic run-evidence export and independent artifact verification.

The estate reconciliation candidate records 337 passing tests on the composed
R51 + Benchmark R4 + canonical Episode-method subject.

## Current frontier — external assurance boundary

The current improvement stack adds:

- independently verifiable serialized Rezon run evidence;
- a minimal CLI for evidence verification;
- generic current-branch / pull-request CI;
- dependency-free OTLP/JSON GenAI trace inspection;
- fail-closed duplicate-key and malformed semantic-metadata handling;
- per-event telemetry schema visibility and dropped-attribute gaps;
- exact trace-to-Rezon-evidence digest/schema cross-binding;
- binding digests that include the full canonical telemetry-intake digest;
- explicit preservation of unresolved authority/effect/currentness/independence
  gaps instead of treating a successful trace as proof.

This remains source/build/test candidate work until separately integrated.

## Next — real-runtime qualification

The next question is empirical: does this boundary catch useful failures on real
external traces rather than merely validating synthetic fixtures?

Use at least two independent agent/workflow runtimes and freeze held-out cases
covering:

- correlated workers presented as independent consensus;
- stale or version-ambiguous evidence;
- hidden or dropped telemetry;
- evidence-artifact substitution;
- tool success misrepresented as authorization;
- effect claims that exceed available receipts;
- runtime-specific fields lost during translation.

Compare Rezon assurance against simpler trace-only baselines on detection
accuracy, false blocks, runtime overhead, and evidence size.

## Next — runtime-specific adapters and MCP surface

Only after real-runtime qualification:

- add thin runtime-specific exporters/adapters where OTLP alone loses necessary
  identity, provenance, or effect semantics;
- evaluate an MCP-facing assurance service so external agents can submit and
  verify evidence without importing the Python package;
- keep hosted/service deployment separately authorized and separately qualified.

## Later — adaptive routing

Only after the external assurance boundary is useful should Rezon promote
learned or adaptive routing experiments.

Candidate work:

- cost/latency/information-gain scheduling;
- heterogeneous provider/model capability discovery;
- HCAE/HyPER/hyperbolic structural signals as advisory routing inputs;
- dynamic rerun and starvation controls;
- durable checkpoint/resume semantics where Rezon itself owns the state.

Learned signals remain advisory unless separately governed. They do not gain
provenance, currentness, authority, or effect rights by improving benchmark
scores.

## Continuous research questions

- Which external trace fields are sufficient to reconstruct a trustworthy Rezon
  execution record?
- How should independence be measured when workers share providers, prompts,
  retrieval corpora, or upstream generated context?
- Which epistemic controls produce measurable gains rather than ceremonial
  complexity?
- When does multi-agent deliberation improve truth-seeking, and when does it
  merely increase correlated confidence?
- What is the smallest portable evidence format that remains reconstructible and
  independently auditable?
