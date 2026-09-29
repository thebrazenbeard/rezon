# Rezon

Rezon is an experimental heterogeneous reasoning fabric.

Its goal is to combine human-style reasoning operations with AI-native, symbolic, statistical, retrieval, simulation, and tool-based computation without collapsing them into one opaque chain-of-thought or a committee of differently prompted agents.

The working architectural thesis is:

> Rezon dynamically composes partially independent computational processes over a provenance-preserving temporal epistemic hypergraph, allocating additional reasoning according to uncertainty, contradiction, information value, cost, and verification need.

## Status

Architecture bootstrap. No behavioral qualification is claimed yet.

This repository distinguishes design, implementation, experiment results, and verified runtime behavior. Documentation or green tests alone do not prove improved reasoning.

## Core principles

- Evidence, inference, hypothesis, assumption, observation, question, test result, and decision are different semantic objects.
- Repetition or model consensus does not promote a hypothesis into evidence.
- A reasoning node is defined by its constrained epistemic operation, accepted inputs, forbidden information, executor, output contract, resource profile, and verification requirements—not merely by a persona label.
- Rezon should support heterogeneous executors: LLMs, symbolic reasoners, numerical code, retrieval systems, simulations, causal models, search, and external tools.
- The shared reasoning state must support typed many-to-many relations and temporal evolution; a typed temporal epistemic hypergraph is the current target.
- Routing allocates computation. Routing, arbitration, confidence, and truth are distinct concepts.
- One verified counterexample may outweigh broad generative consensus.
- Reasoning should be inspectable through provenance, structured intermediate artifacts, and execution traces without claiming access to hidden model-internal chain-of-thought.
- Fast and slow reasoning loops should be separable.
- Expensive reasoning should be targeted by unresolved uncertainty, contradiction, expected information value, or verification need rather than invoked uniformly.

## First bounded target

The first executable kernel should be able to:

1. represent a reasoning episode as typed epistemic state;
2. invoke heterogeneous reasoning operators under explicit contracts;
3. preserve provenance, uncertainty, contradiction, and execution traces;
4. route work dynamically while supporting isolation and blinding between operators;
5. compare single-model and multi-node reasoning on correctness, calibration, cost, latency, and error discovery;
6. experimentally evaluate an HCAE-inspired episode hyperconnectome encoder as a transient structural-perception subsystem.

See `docs/architecture/REZON_ARCHITECTURE_V0.md`, `docs/contracts/`, and `docs/research/` for the current design basis.
