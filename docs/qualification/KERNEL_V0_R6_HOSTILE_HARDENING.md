# Rezon Kernel V0 R6 Hostile Hardening Evidence

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

This record binds the R6 successor to the exact failed R5 subject and preserves the distinction between source/build/test evidence and independent hostile qualification.

## Exact ancestry

- repository: `thebrazenbeard/rezon`
- failed R5 review subject: `d60f99d1420b56b2923e6977a3d0c3a7f3412762`
- failed R5 tree: `655dd551f45a3f885060c1cb250e8841e61b5dd5`
- R6 branch: `work/rezon-kernel-v0-r6-hostile-hardening`
- imported Masa hostile artifact head: `ff22ca92eb5e588f3f50c2a5c0d61599655e9b5a`
- expanded R6 test-only RED head: `19c330786c88f01e9e6779784b18921842bb62be`
- R6 executable GREEN head: `5b05fba48c8a93bfb9f9cc41c049a866a1184f2a`
- R6 executable tree: `2186138de06fc04fed987907a3a30193ab35a103`
- hosted-CI enablement head: `d4f94762a1329a61c2c551217e4063440aed30be`

## Independent review trigger

Masa returned:

`HOSTILE QUALIFICATION FAIL / CHANGES_REQUESTED`

against exact R5 `d60f99d…`, with blockers B1-B6 and material M1.

Mune separately corroborated the narrow R5 lineage repair but returned:

`R5_DELTA_SOURCE = PASS / WHOLE_PR_SOURCE = CHANGES_REQUESTED`.

R6 does not inherit a PASS from any earlier subject.

## Frozen RED evidence

Masa's exact hostile file was imported unchanged from:

- branch `masa/rezon-p0-hostile-r5-v1`
- commit `a5d883aa279da9ce8c75e3554e548dcaebe56ace`
- file `tests/test_masa_hostile_kernel_p0_r5.py`

That artifact reproduced five failures and one pass on the R5-derived R6 test-only branch.

The one passing relation-blindness case was not a valid proof of B5 because its generic node ID was never selected by the deterministic scheduler. R6 therefore froze two additional executable independence cases before repair:

1. external independence policy must reject metadata when peer-answer exposure and evidence-lineage negatives are not explicitly attested;
2. a scheduler-selected independence-required `echo_hypothesis` worker must fail closed when a peer answer is visible through a worker-produced relation.

On exact test-only head `19c330786c88f01e9e6779784b18921842bb62be`, the combined hostile surface produced:

`7 failed / 1 passed`

before production repair.

## R6 repairs

### B1 — duplicate node ID descriptor substitution

The deterministic scheduler now rejects duplicate node IDs before scheduling. `ScheduleDecision` also carries the exact descriptor index, and the runner executes that exact indexed descriptor only after verifying the scheduled node ID matches.

This removes the lossy post-schedule `node_id -> RunnerNode` substitution path.

### B2 — delimiter-based source-version inference

Canonical `Proposition` and `Hyperrelation` now have explicit `source_versions` fields.

The runner no longer infers version semantics from `source_refs` containing `@`.

Retrieval admission populates explicit source-version provenance, traces/receipts consume only explicit source versions, and admission rejects worker-emitted source versions that were not present in the governed execution view.

An email-like locator such as `analyst@example.com` therefore remains a locator/ref and is not promoted to source-version evidence.

### B3 — contradictory claim-disposition completeness

`ResultReceipt` now rejects `claim_disposition_complete=True` when any `claim_disposition:<id>` unresolved marker remains.

### B4 — bare accepted/rejected claim self-assertion

Accepted/rejected claim IDs require a typed `ClaimDispositionEvidence` artifact bound to:

- exact task ID;
- exact episode version;
- issuing execution contained in the same receipt;
- exact accepted/rejected claim sets;
- governed authority namespace;
- non-empty supporting evidence refs.

Bare accepted/rejected fields can no longer self-mint a governed-looking disposition receipt.

### B5 — non-proposition peer-answer leakage

Kernel V0 still lacks a typed safe-shared worker-relation class. R6 therefore fails closed when an independence-required execution view contains any worker-produced relation.

This covers relation identity, type, participant roles, and participant structure as potential answer-bearing channels rather than checking only proposition kinds/IDs.

The corrected scheduler-selected hostile case now exercises the path rather than passing because the test node was never scheduled.

### B6 — unattested negative independence claims

`IndependenceVerificationEvidence` now explicitly binds:

- `saw_other_answer`;
- declared common-evidence refs;
- consumed-evidence refs;
- existing executor/model/provider/prompt/context lineage.

`IndependenceVerificationPolicy.verify()` requires exact equality between those external attestations and the worker metadata and requires externally attested `saw_other_answer=False`.

Pairwise independence additionally rejects intersection of externally bound consumed-evidence sets.

Different execution/model/provider strings remain a trusted-host identity boundary; R6 does not claim cryptographic issuer identity or semantic alias resolution.

### M1 — hostile consensus oracle fail-open

When consensus is counted as evidence, missing, empty, false, or partially unknown worker independence now triggers `CORRELATED_CONSENSUS_LAUNDERING`.

Unknown independence no longer passes the hostile oracle silently.

## Additional hostile controls

R6 also freezes positive/negative controls for:

- exact external negative/evidence attestation succeeding;
- consumed-evidence attestation mismatch failing;
- shared attested consumed evidence failing pairwise independence;
- worker attempts to launder an unconsumed explicit source version failing admission;
- claim-disposition evidence with an issuer absent from the receipt execution set failing structurally;
- explicit source-version entries being non-empty and unique.

## Exact executable qualification

Fresh clone of exact executable head `5b05fba48c8a93bfb9f9cc41c049a866a1184f2a` under CPython 3.12.10:

- editable install: PASS
- `python -m compileall -q src`: PASS
- pytest: **104 passed / 0 failed**
- `git diff --check`: PASS

A local virtual environment created for the qualification was untracked runtime state and is not repository evidence.

## Hosted qualification

R6 was added to the existing `Rezon kernel tests` push workflow without changing the test commands.

Hosted GitHub Actions on exact head `d4f94762a1329a61c2c551217e4063440aed30be`:

- run: `35350939812`
- event: push
- runner: GitHub-hosted
- install: PASS
- compile: PASS
- pytest: PASS
- diff-check: PASS
- overall conclusion: **success**

The source delta from executable head `5b05fba…` to `d4f9476…` is workflow configuration only.

## Explicit unresolved / non-claims

R6 does not establish:

- independent Mune/Masa hostile PASS on the new exact head;
- merge authority;
- deployment, installation, activation, or provider/model mutation;
- live-provider identity canonicalization;
- cryptographic issuer trust for independence evidence;
- dynamic rerun/starvation qualification;
- reasoning superiority;
- HCAE/HyPER/hyperbolic learned-routing qualification.

The Issue #5 donor/learned-routing gate remains closed until Kernel V0 receives fresh exact-head independent acceptance.

## Remaining gate

Freeze the final documentation/review head, rerun exact final-head source/build/test qualification, and request fresh Mune/Masa hostile rereview bound to that immutable subject.

No merge is requested by this record.
