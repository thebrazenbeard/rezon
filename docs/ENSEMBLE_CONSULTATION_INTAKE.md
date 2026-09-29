# Ensemble Consultation Intake V1

Status: SOURCE / BUILD / TEST CANDIDATE

Reference external specimen:

- repository: `anywave/lattice-consult-mcp`
- branch observed: `main`
- exact source head: `675faae4d8ebd32071b656a2344fbd54843c8295`
- files reviewed:
  - `src/lattice_consult_mcp/ensemble.py`
  - `src/lattice_consult_mcp/synthesis.py`
  - `src/lattice_consult_mcp/server.py`
  - `src/lattice_consult_mcp/providers/base.py`
  - `docs/design.md`

The external repository is a qualification specimen, not a dependency and not an
authority source.

## Problem

External multi-model systems can report fields such as:

- synthesized response;
- convergence score;
- confidence label;
- provider list;
- provider failures;
- cost and latency;
- optional raw per-provider/model outputs.

Those fields are useful observations, but they do not establish that workers
were independent, that a consensus is true, that the synthesis belongs to the
current prompt, or that the synthesis has authority.

The reference specimen makes the distinction concrete. Its emitted MCP
`consult_ensemble` result does not include the original prompt, system prompt,
synthesis mode, privacy tier, provider-skip list, or single-provider marker. Raw
outputs are optional. Therefore the emitted artifact alone cannot reconstruct
the exact consultation request or demonstrate the independence of its workers.

## Rezon intake

Use:

    rezon inspect-consultation consultation.json

The current `rezon.ensemble-consultation-intake.v1` intake:

- validates the emitted consultation report shape;
- binds the complete source JSON payload with a canonical digest;
- preserves the reported synthesized response, convergence score, confidence
  label, divergence findings, consulted providers, failed providers, reported
  cost, and latency;
- optionally validates and normalizes raw `provider/model` outputs;
- binds each raw response by digest without treating its content as evidence;
- distinguishes consultation-member count from distinct-provider count;
- permits multiple model workers behind one provider without treating them as
  independent evidence sources;
- reports incomplete or contradictory raw-output/top-level success/failure
  accounting;
- leaves prompt/system/request configuration, synthesis method, privacy tier,
  provider eligibility, worker independence, semantic truth, evidence status,
  and authority unestablished when the artifact does not bind them.

## Consensus promotion

`consultation_promotion_violations()` intentionally treats attempted promotion
of the consultation consensus as hostile unless the necessary governed evidence
exists outside the artifact.

A convergence score is therefore a reported property of a synthesizer. It is
not an evidence multiplier.

A provider label is a reported identity. It is not an independence proof.

A second model behind the same provider is a second reported worker. It is not
automatically a second independent evidence source.

## Reference-specimen findings

The exact Lattice source reviewed above is useful as an adversarial fixture
because its current v0.1 synthesis is deliberately heuristic:

- convergence clusters sentences by fuzzy string similarity;
- the convergence score is the fraction of claim clusters crossing its consensus
  threshold;
- the confidence label is derived mechanically from that score;
- its current `majority` implementation selects the median-length successful
  response rather than computing semantic majority;
- `weighted` currently degrades to convergence;
- the MCP output omits several request/configuration fields present elsewhere in
  the implementation.

Rezon does not reproduce or correct those algorithms. It records their outputs
as advisory reported signals and preserves the missing bindings as assurance
gaps.

## Claim ceiling

A successful consultation intake establishes only structural consistency of the
submitted artifact under the current intake rules.

It does not establish:

- that the submitted artifact is authentic;
- that the reported provider/model labels are authentic;
- that workers were independent;
- that the original prompt or configuration is the one a caller claims;
- that convergence implies truth;
- that a confidence label is calibrated;
- that provider diversity implies evidence diversity;
- that the synthesized answer has authority;
- that the consultation performed an authorized or durable external effect.

Independent qualification, source currentness, and authority must be established
through separately governed evidence.
