# Rezon Plugin Autopilot V1

## Subject

- Repository: `thebrazenbeard/rezon`
- Discovery/conversion source: PR #92 head `b88206929a72ae3d7abc790c8c346cd9d78e4dd9`
- Current source base after PR #92 squash merge: `main@ff6d34ca283d977d4f9ce48ec006f37fd06f7d9a`
- Plugin branch: `plugin/rezon-v1-main-20260925`
- Package: `plugin/rezon`
- Package version: `0.1.0`

This plugin work did not merge PR #92. PR #92 was squash-merged while conversion was in progress, so the plugin package was restacked onto the resulting current `main` without rewriting the original conversion branch.

The conversion is source-only. It does not install or publish a plugin, activate a provider, deploy a runtime, or establish reasoning superiority.

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

## Validation

Exact package content after rebinding the directory pack to `main@ff6d34ca283d977d4f9ce48ec006f37fd06f7d9a`:

- custom deterministic structural/package validation: **PASS**;
- Skills detected: `rezon-analysis`, `rezon-evidence-reconciliation`, `rezon-hostile-review`;
- two independently built ZIPs were byte-identical;
- package ZIP SHA-256: `3056e203533ee1341fc361578902bc92204acb7cac93a7a639e8fd3da30faa1e`;
- clean archive extraction preserved the package surface before the source-ref-only directory-pack rebinding.

The bundled Autopilot validator has two Windows-host portability defects in this environment: fd-based directory enumeration is unavailable and Git checkout converts Skill newlines to CRLF while its parser requires LF. A local compatibility copy changed only those platform checks. With those compatibility changes, Autopilot preflight detects all three Skills and reports one remaining semantic submission error: `interface.developerName is required`.

That error is intentionally not bypassed. The verified OpenAI developer/business identity is not established by repository evidence.

## Repository regression

On the restacked plugin branch with the repository source path exposed:

```text
PYTHONPATH=src
337 passed
```

Without `PYTHONPATH=src`, the suite reports `3 failed, 334 passed`; each failure is in `tests/test_benchmark_v1_runner.py` because the benchmark subprocess exits with `ModuleNotFoundError: No module named 'rezon'`.

The exact discovery source `b88206929a72ae3d7abc790c8c346cd9d78e4dd9` reproduces the same `3 failed, 334 passed` result and the same import failure. The plugin changes therefore do not introduce that regression.

## Remaining gates

- Verified OpenAI `developerName` is unresolved and must not be inferred from GitHub metadata.
- Public directory submission, installation, approval, and publication are not established.
- A future public-release pass should re-run the then-current OpenAI validator/package tooling on a host where its filesystem checks are supported, or after the upstream Windows portability defect is fixed.
