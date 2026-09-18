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
- initial R6 executable GREEN head: `5b05fba48c8a93bfb9f9cc41c049a866a1184f2a`
- hosted-CI enablement head: `d4f94762a1329a61c2c551217e4063440aed30be`
- late B4 self-hostile RED head: `f87e887` (generic receipt could still self-assert disposition completeness)
- current R6 executable GREEN head: `7492271c356f445561a4125a771942b2cf0c95eb`

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

### B3/B4 — generic ResultReceipt is non-dispositional

The first R6 B4 repair introduced a typed disposition-evidence object, but self-hostile review found that a caller could still manufacture that object and matching strings locally.

R6 therefore chose the smaller fail-closed design:

- `claim_disposition_complete` defaults to `False`;
- generic `ResultReceipt` rejects any non-empty accepted/rejected claim IDs;
- generic `ResultReceipt` rejects `claim_disposition_complete=True` even when there are no unresolved markers;
- the runner never emits claim-disposition completeness;
- claim disposition is deferred to a future separately governed artifact rather than represented by the generic task receipt.

Exact late self-hostile test-only head `f87e887` reproduced the remaining completeness self-assertion before this stronger repair.

This closes both contradictory completeness and bare accepted/rejected self-minting without introducing a second trusted-string authority layer.

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
- generic receipt claim-disposition completeness self-assertion failing structurally;
- explicit source-version entries being non-empty and unique.

## Exact executable qualification

Fresh clone of current executable head `7492271c356f445561a4125a771942b2cf0c95eb` under CPython 3.12.10:

- editable install: PASS
- `python -m compileall -q src`: PASS
- pytest: **104 passed / 0 failed**
- `git diff --check`: PASS
- tracked working tree after test-environment cleanup: clean

A local virtual environment created for the qualification was untracked runtime state and is not repository evidence.

## Hosted qualification

R6 was added to the existing `Rezon kernel tests` push workflow without changing the test commands.

Hosted GitHub Actions on current executable head `7492271c356f445561a4125a771942b2cf0c95eb`:

- run: `35351614529`
- event: push
- runner: GitHub-hosted
- install: PASS
- compile: PASS
- pytest: PASS
- diff-check: PASS
- overall conclusion: **success**

Earlier hosted run `35350939812` on CI-enablement head `d4f9476…` was also successful; it is retained as provenance rather than substituted for the current subject.

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
