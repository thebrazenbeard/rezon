# Rezon Plugin Autopilot V1

## Subject

- Repository: `thebrazenbeard/rezon`
- Discovery/conversion source: PR #92 head `b88206929a72ae3d7abc790c8c346cd9d78e4dd9`
- Current source base after PR #92 squash merge: `main@ff6d34ca283d977d4f9ce48ec006f37fd06f7d9a`
- Plugin branch: `plugin/rezon-v1-main-20260925`
- Exact packaged-artifact source head: `704dc826bfe8314bbdedc5724b3b1970ebd2542b`
- Package: `plugin/rezon`
- Package version: `0.1.0`

This plugin work did not merge PR #92. PR #92 was squash-merged while conversion was in progress, so the plugin package was restacked onto the resulting current `main` without rewriting the original conversion branch.

The conversion is source-only. It does not install, submit, publish, activate a provider, deploy a runtime, or establish reasoning superiority.

## Discovery and product boundary

Reusable public jobs selected from the source repository:

| Source capability | Disposition | Plugin surface |
| --- | --- | --- |
| Rezon foundation and heterogeneous reasoning method | `compile_skill` | `rezon-analysis` |
| Evaluation, falsification, independence and semantic attack method | `compile_skill` | `rezon-hostile-review` |
| Provenance, currentness, state/effect and evidence reconciliation method | `compile_skill` | `rezon-evidence-reconciliation` |
| Python Kernel V0 implementation | `reference_only` | not bundled as a claimed runtime |
| Benchmark/replay implementation and fixtures | `reference_only` | verification evidence, not a public Skill |
| Provider activation, deployment and operational effects | `internal_only` | excluded |
| Historical branch/review maintenance material | `internal_only` | excluded |

Architecture: **skills-only**. No MCP server, credentials, external account, provider binding, or runtime service is required for the selected user jobs.

## Public package

The package contains a portable Agent Plugins `plugin.json`, an OpenAI compatibility manifest, three Skills with references, and a Rezon-specific light/dark/composer SVG identity set.

Package authorship is bound to the documented GitHub repository owner, `thebrazenbeard`. This is not treated as proof of the verified OpenAI directory publisher identity.

Directory category: `Education & Research`.

Submission preparation now includes:

- `submission/listing.json`;
- `submission/golden-prompts.json`;
- `submission/reviewer-tests.json`;
- `submission/release-notes.md`;
- `submission/SUBMISSION_PREP.md`.

Reviewer material contains exactly five positive and three negative cases. The discovery set contains three direct, three indirect, and three negative prompt families. These discovery cases are expected-routing evidence only; the Plugin has not been installed for runtime routing tests in this workstream.

## Validation

Exact package content at `704dc826bfe8314bbdedc5724b3b1970ebd2542b`:

- repository suite with `PYTHONPATH=src`: **337 passed**;
- GitHub `Rezon kernel tests`: **success**;
- GitHub `Rezon Benchmark V1 tests`: **success**;
- custom deterministic structural/package validation: **PASS**;
- Skills detected: `rezon-analysis`, `rezon-evidence-reconciliation`, `rezon-hostile-review`;
- two independently built ZIPs were byte-identical;
- package ZIP SHA-256: `c9b04c58ae2706b3e6c08ec13079c23d7683708702d6ce75ee8d1007af4a6f6f`;
- reviewer-case/discovery-count validation: **PASS**.

The bundled Autopilot validator has two Windows-host portability defects in this environment: fd-based directory enumeration is unavailable and Git checkout converts Skill newlines to CRLF while its parser requires LF. A local compatibility copy changed only those platform checks. With those compatibility changes, Autopilot preflight detects all three Skills.

The repository-maintained directory helper reports `not_ready` with `developerName` missing. Its checked-in baseline treats public URLs as optional for a skills-only package. Current OpenAI public-submission documentation checked on 2026-09-27 requires website, support, privacy-policy, and terms URLs in the public listing, so this report applies the stricter live requirement rather than silently accepting the older local baseline.

## Repository regression note

Without `PYTHONPATH=src`, the suite reports `3 failed, 334 passed`; each failure is in `tests/test_benchmark_v1_runner.py` because the benchmark subprocess exits with `ModuleNotFoundError: No module named 'rezon'`.

The exact discovery source `b88206929a72ae3d7abc790c8c346cd9d78e4dd9` reproduces the same `3 failed, 334 passed` result and the same import failure. The plugin changes therefore do not introduce that regression.

## Remaining gates

Status: **not_ready** for public submission.

Unresolved public-submission inputs:

- verified OpenAI developer or business identity;
- public website URL;
- public customer-support URL;
- public privacy-policy URL;
- public terms-of-service URL;
- country or region availability.

Runtime discovery behavior from an installed copy is also untested. Creating or installing a private/workspace Plugin would be a separate effect and is not performed by this source-preparation work.

Public submission, installation, approval, and publication are not established.
