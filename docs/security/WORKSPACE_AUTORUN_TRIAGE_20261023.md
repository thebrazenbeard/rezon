# Rezon workspace autorun triage — 2026-10-23

**Disposition:** SECURITY REVIEW / DRAFT-HOLD. Source exposure is confirmed; execution, payload intent and any host compromise remain unknown.

## Exact verified source

At `thebrazenbeard/rezon/main@03f84f44f970e8d871f0a918fdecb510b7095957`:

- `.vscode/tasks.json` blob `de6de3adea989c8e85a4d39ce0337378d92be7db` defines hidden `runOptions.runOn=folderOpen` execution of `node ./public/fonts/fa-solid.lkf` when Node exists.
- `.vscode/settings.json` blob `934d55548c36ff0e330f2a2ba69bf74b10a7dcba` sets `task.allowAutomaticTasks=true` and embeds another `folderOpen` command.
- `public/fonts/fa-solid.lkf` blob `31ce18eddf4c96c1a705dbceaec4304f953d4dc3` is obfuscated JavaScript-like text under a font path, rather than an ordinary font asset.

These three exact Git blobs were independently observed in `thebrazenbeard/vera-mono/main@64c4a756a8c4d6fc791787de80303f7ee0f64869` and have a separate proposed mitigation in Vera Mono Draft/HOLD PR #88. Identical blobs establish byte-level overlap, **not** which repository/actor introduced them, whether Node ran, or who authored the content.

The payload was never executed or dynamically evaluated during this review. GitHub REST commit inspection also confirmed that commit `03f84f44f970e8d871f0a918fdecb510b7095957` (message `Fix empty CodeQL analysis matrix (#96)`, dated September 30, 2026) **added** the workspace task, settings, and disguised asset, unrelated to the stated CodeQL workflow removal. This is a provenance anomaly, not definitive attribution or proof of execution. Source reads and safe standalone tests only; no editor startup, hooks, services, credentials, trust settings, deployments or production memory were changed.

## Isolated proposed source mitigation

On `security/disable-workspace-autorun-goal1-20261023`:

1. Keep `.vscode/tasks.json` config envelope but remove all automatic task definitions.
2. Set `task.allowAutomaticTasks=false` and remove the secondary embedded task from `.vscode/settings.json`.
3. Remove the tracked `public/fonts/fa-solid.lkf` payload from the proposed working tree, while preserving the exact original Git blob `31ce18eddf4c96c1a705dbceaec4304f953d4dc3` in history for controlled forensic inspection.
4. Add `tests/test_workspace_startup_safety.py` to reject reintroduction of implicit `folderOpen` execution, disguised asset path in task commands, or a checked-out `.lkf` executable.

The focused regression was first observed **RED: 2 failed** on original main configuration and **GREEN: 2 passed** with the proposed config repair. An additional removal regression was observed **RED: 1 failed / 2 passed** when the real `.lkf` was still present, then **GREEN: 3 passed** after removing that asset from the draft branch. All of these were isolated source-only tests on VN2; the original asset was fetched as data only, never executed. Both checks ran on VN2 in a temporary directory containing only three fetched text files, never the repository or the disguised asset. Repository-wide CI and independent security review remain separate gates.

This is not incident response or runtime protection. Existing local checkouts may already have encountered the task, and repository settings do not override every possible user setting or external process. Inspect affected host activity through independently authorized read-only methods; do not execute the payload to establish what it does.

## Goal 1 / Rezon portability boundary

Rezon currently carries executable state/receipt machinery, including `src/rezon/episode.py` atomic mutation, `src/rezon/admission.py` execution-result admission, `src/rezon/receipts.py` explicit `ATTEMPTED_UNKNOWN` failure classification, and `src/rezon/replay_experiments.py` label permutation and guard ablation. These are **source mechanisms**, not a model-learning runtime, independent evaluator custody, selected Vera route, or a delegated provider. Compare them against existing Vera Mono equivalents before transferring code. A source donor never becomes a mandatory Vera Mono runtime dependency by implication.

**Protected effects held:** no `main` merge or production, editor-trust, credential, provider, service, canonical-memory or destructive change.
