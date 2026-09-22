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
- deterministic run-evidence export.

The estate reconciliation candidate records 337 passing tests on the composed
R51 + Benchmark R4 + canonical Episode-method subject.

## Current frontier — portable assurance

Deliverables:

- independently verify serialized Rezon run evidence;
- expose verification through a minimal CLI;
- run CI on current branches and pull requests rather than historical branch
  names only;
- define Rezon's role as an epistemic assurance layer rather than a competing
  general-purpose orchestrator.

Success: another process can retain a Rezon evidence artifact and validate its
internal bindings later without rerunning the original reasoning job.

## Next — external runtime adapters

Define a dependency-light adapter contract for completed execution events from
external agent/workflow systems.

First adapters should prove the shape before multiplying integrations. Candidate
surfaces include:

- agent SDK traces;
- explicit workflow runtimes;
- MCP tool activity;
- A2A task exchanges.

Adapters must preserve identity, provenance, source version/currentness,
executor lineage, failures, and authority/effect boundaries. Text-only
flattening is not acceptable.

## Next — cross-runtime adversarial qualification

Build fixtures where simpler orchestration traces look healthy while the
epistemic state is not:

- correlated workers presented as independent consensus;
- stale or version-ambiguous evidence;
- hidden execution failures;
- output/producer substitution;
- tool success misrepresented as authorization;
- receipt summaries that conceal trace failures.

Compare Rezon assurance against simpler baselines on detection accuracy, false
blocks, runtime overhead, and evidence size.

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
