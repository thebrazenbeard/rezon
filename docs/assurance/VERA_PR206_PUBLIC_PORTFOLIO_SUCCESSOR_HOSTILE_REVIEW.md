# Rezon hostile review — Vera PR #206 public-safe portfolio successor

Reviewed repository: `thebrazenbeard/vera`  
Reviewed PR: #206  
Reviewed exact head: `e23596726aa292654ee293da4938474174d37454`  
Reviewed base: `a267e7d555e2c15e51a2e578c1e08095091552f0`  
Disposition: **SURVIVES_NARROWED_PUBLIC_SAFE_SUCCESSOR**

## Subject

PR #206 is a clean successor to draft PR #200. It does not rewrite the predecessor's historical bytes.

The new subject binds the immutable Project Runner corpus at
`thebrazenbeard/project-runner@848c2172e6fa98cdab722b43d1ff4817990c5968`,
path `portfolio/corpus.public.json`.

That cut records:
- 67 repositories total;
- 49 public repositories;
- 18 private repositories;
- private membership commitment scheme `COUNT_ONLY_PUBLIC_V1`;
- exact private membership not publicly committed.

## Findings

### R1 — private membership leakage

PASS.

The successor enumerates all 49 public repositories and carries private portfolio membership count-only.

PR #200's membership-bearing V1 portfolio registries are not reintroduced.

The focused public-safety test scans the successor registry, harvested runtime namespaces, public vendor artifacts, and documentation for repository tokens and requires every named repository to belong to the 49-public cut.

### R2 — permanent-cardinality semantics

PASS.

The successor treats 67/49/18 as one immutable observed cut. It does not assert that the later estate must permanently retain those counts.

Mutable repository heads are stored as a separate refresh layer. Currentness-sensitive use is explicitly required to refresh live evidence again.

### R3 — useful mechanism harvest

PASS, narrowed.

Public donor mechanisms retain exact repository/head/path/blob provenance where the harvested target is present. The current public exact-binding set contains 17 byte-bound transfers.

Two mechanism sets inherited from private portfolio donors are retained under neutral Vera-owned namespaces. Public source exposes only anonymous donor count and target Git-blob integrity; exact private donor membership/source paths are deliberately absent.

This is a privacy-preserving provenance ceiling, not full public reconstruction of private provenance.

### R4 — VCP/control-plane carryover

PASS by omission/no-auto-bind.

The predecessor's embedded VCP mirror was not copied because predecessor material contained repository references outside the 49-public cut.

VCP remains represented as a public portfolio source with
`NO_AUTO_BIND_PENDING_SEPARATE_VCP_RESTACK`.

This successor therefore does not smuggle VCP activation/control authority into Vera.

### R5 — reproducibility and byte integrity

PASS for the reviewed source claim.

The successor vendors the exact public Project Runner corpus cut and includes a reproducible builder.

Git provenance checks use filtered `git hash-object --path`, avoiding Windows CRLF working-tree ambiguity.

Fresh detached-checkout validation at the reviewed commit:
- 17/17 focused successor tests PASS;
- `python -m compileall -q portfolio_runtime scripts/build_portfolio_public_successor_v2.py` PASS;
- new registry/docs/tests diff-check PASS.

The global Vera suite is not claimed green: the main baseline already produced 90 failures and 232 errors in 1109 tests on Lappy, dominated by pre-existing missing historical migration artifacts.

### R6 — effect boundary

PASS.

The reviewed subject is source-only:
- no merge;
- no deploy/install;
- no ChatGPT Project replacement;
- no provider mutation;
- no credential/permission change;
- no private membership publication;
- no memory promotion;
- no runtime-effect qualification.

## Claim ceiling

`PR206_PUBLIC_SAFE_PORTFOLIO_SUCCESSOR_SURVIVES__IMMUTABLE_67_CUT__49_PUBLIC_ENUMERATED__18_PRIVATE_COUNT_ONLY__NO_RUNTIME_OR_INSTALLATION_CLAIM`

## Next dependency

VCP `NO_AUTO_BIND` enforcement may now be restacked against Vera PR #206 exact head
`e23596726aa292654ee293da4938474174d37454`.

That restack must preserve this successor's privacy rule and must not reintroduce predecessor V1 private membership.

After VCP, Project Runner should continue the P0 Vera lanes:
1. VeraMesh;
2. Vera model training;
3. Vera Mono;
4. WorkBridgeMCP.

The unfinished Project Runner `EFFECT_CONFIRMED -> VERIFYING -> COMPLETE` finalization branch remains a separate frontier and must not be confused with this Vera qualification.
