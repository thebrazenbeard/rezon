# Rezon Kernel V0 R7 Hostile Hardening Evidence

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

This record binds the R7 successor to exact failed R6 and preserves the distinction between source/build/test evidence and independent hostile qualification.

## Exact ancestry

- repository: `thebrazenbeard/rezon`
- failed R6 review subject: `f94f8f5aa3075179ab9b3eae7fdf8c81773f582a`
- failed R6 tree: `dcff3a2712be7a4606b973b843aa4f6e84fe6e92`
- R7 branch: `work/rezon-kernel-v0-r7-hostile-hardening`
- Masa hostile artifact: `masa/rezon-p0-hostile-r6-v1@839ec4f09c0f1fa557a4cf47efdf3c1e59a2f40e`
- imported R7 test-only RED head: `cc19d1d80caec708a837a0d969fce030f86ae1fc`
- executable R7 GREEN head: `9b4dcc089fd948003fc7d8ef0eaafb94ea62d3b3`
- hosted-CI enablement head: `528adf9f522a13c9c20006e2b1a53a859e81ea95`

## Independent review trigger

Masa returned `CHANGES_REQUESTED / HOSTILE_R6_FAIL` on exact R6 `f94f8f5…`.

R6 materially repaired its predecessor blockers, but fresh hostile review identified three new blocking epistemic failures plus one material authority-boundary gap. R7 does not inherit any PASS from R6 or earlier subjects.

## Frozen RED evidence

Masa's exact hostile test file was imported unchanged as:

- `tests/test_masa_hostile_kernel_p0_r6.py`
- R7 test-only head `cc19d1d80caec708a837a0d969fce030f86ae1fc`

A clean CPython 3.12 execution of that exact test-only head produced:

`4 failed / 0 passed`

The failures reproduced:

1. evidence-consumption attestation could agree only with sidecar metadata while contradicting the actual visible/used execution evidence;
2. independently validated source refs and source versions could be cross-paired from different inputs;
3. raw caller-supplied `TaskEnvelope.available_authority` strings could satisfy required authority;
4. a peer worker answer encoded as a worker-produced `PREDICTION` bypassed proposition blindness.

## R7 repairs

### B1 — conservative execution-view evidence binding

Kernel V0 cannot observe semantic consumption inside an arbitrary executor.

For an independence-required execution, R7 therefore treats every visible `EVIDENCE` proposition as potentially consumed. The governed set contains each visible evidence proposition ID plus its source refs.

The worker's externally verified `consumed_evidence_refs` must exactly equal that governed set and must contain no duplicates.

This is intentionally conservative. It does not claim to identify which visible evidence an executor cognitively or semantically used.

### B2 — exact source-ref/source-version association

R7 preserves source-ref/source-version association rather than validating two unrelated sets.

`source_ref_version_bindings()` establishes an association only by:

- positional pairing when the ref/version tuples have equal cardinality; or
- exact token self-binding when cardinalities differ and the exact version token also appears as a source ref.

No delimiter or string-shape inference is used.

Admission checks every emitted ref/version binding against bindings present in the governed execution view. A worker therefore cannot combine `source:A` with `source:B@v2` merely because each token appears somewhere in the view.

This is a Kernel V0 compatibility rule, not a claim that positional tuples are the final long-term provenance representation.

### B3 — fail closed on prior worker proposition channels

Kernel V0 has no explicit safe-shared worker-proposition class.

An independence-required worker now fails closed if any visible proposition was produced by a prior worker execution, regardless of whether the proposition is typed HYPOTHESIS, CLAIM, DECISION, PREDICTION, TEST_RESULT, ASSUMPTION, or another proposition kind.

The existing fail-closed rule for worker-produced relations remains.

Future safe sharing requires an explicit governed class rather than assuming a proposition kind is harmless.

### M1 — externally verified authority boundary

Raw `TaskEnvelope.available_authority` strings are no longer sufficient for `NodeDescriptor.required_authority`.

R7 introduces `AuthorityVerificationEvidence` and `AuthorityVerificationPolicy`.

A required authority must:

- be declared in the exact task envelope;
- have external verification evidence for that authority;
- bind to exact task ID;
- bind to exact task-envelope digest;
- carry non-empty issuer, source, currentness, and verification references.

The runner fails closed when required authority lacks this external policy evidence.

This establishes a typed trusted-policy boundary. It does not establish cryptographic issuer identity or independently prove that the referenced authority source/currentness receipt is itself valid.

## Positive controls

R7 adds controls showing the repair is not a blanket reject-all policy:

- an independent worker with exact external attestation of every visible evidence ref can execute successfully;
- an emitted source ref/version pair matching the exact governed input association can be admitted successfully;
- the pre-existing positive required-authority path succeeds when supplied exact envelope-bound authority verification evidence.

## Exact executable qualification

Fresh clean clone of executable head `9b4dcc089fd948003fc7d8ef0eaafb94ea62d3b3` under CPython 3.12:

- editable install: PASS
- pytest: **110 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS
- tracked source clean; only test-created local environment/install/bytecode artifacts were untracked

## Hosted qualification

R7 was added to the existing `Rezon kernel tests` push workflow without changing the test commands.

Hosted GitHub Actions on CI-enablement head `528adf9f522a13c9c20006e2b1a53a859e81ea95`:

- run: `35381350224`
- event: push
- GitHub-hosted runner
- install: PASS
- compile: PASS
- test: PASS
- diff-check: PASS
- overall conclusion: **success**

## Explicit unresolved / non-claims

R7 does not establish:

- independent Mune/Masa hostile PASS on R7;
- merge authority;
- deployment, installation, activation, or provider/model mutation;
- cryptographic authority issuer identity;
- validity of the authority evidence's referenced source/currentness claims beyond the trusted external policy boundary;
- semantic observation of which evidence an arbitrary executor actually consumed;
- a final general-purpose typed provenance model beyond the frozen association rule above;
- dynamic rerun/starvation qualification;
- reasoning superiority;
- HCAE/HyPER/hyperbolic learned-routing qualification.

The Issue #5 donor/learned-routing gate remains closed until Kernel V0 receives fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh Mune/Masa hostile rereview bound to that final head.

No merge is requested by this record.
