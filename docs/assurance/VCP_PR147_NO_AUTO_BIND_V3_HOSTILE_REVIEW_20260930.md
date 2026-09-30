# Hostile Exact-Head Review — VCP PR #147 NO_AUTO_BIND V3

Reviewed repository: `thebrazenbeard/vera-control-plane`  
Reviewed PR: #147  
Reviewed exact head: `83eda677f6daa95a4ebe494f4cadacb9a8d4a2a9`  
Reviewed base: `5ea58cfc2dd184ef916532d3b4e2bd13b99c2709`  
Qualified Vera upstream: PR #206 @ `dff171a8cee0b2dd3c6fd4627499330800499fdd`  
Bound prior Vera assurance: Rezon PR #95 @ `d22abc8f7b4649ca0b9e21e77673f263283d98bf`

Review class: source-recorded hostile exact-head review. This artifact does not claim an independently executed external-model review.

## Disposition

`SURVIVES_NARROWED_AFTER_HOSTILE_REPAIR`

The reviewed subject survives as source-policy enforcement only. It establishes neither merge, installation, runtime activation, provider effect, identity transfer, nor protected-effect authority.

## Preserved invariants

- V3 remains byte-bound to Vera PR #206 public-cut blob `19c20a5fceae81f3324d477317f1ec79062cd9f2` and absorption blob `15499b3a8f3b4d5033a4cf8e0d6a1953c2826cb9`.
- Public membership is exactly 49 rows: 14 `NO_AUTO_BIND`, one `PREDECESSOR_EVIDENCE_ONLY`.
- All 14 predecessor V2 `NO_AUTO_BIND` rows remain `NO_AUTO_BIND`; none is weakened.
- Repository availability never implies activation.
- Private inventory remains count-only: 18, `COUNT_ONLY_PUBLIC_V1`, exact private membership not publicly committed, names absent.
- Outside-cut and unbound-private sources fail closed.
- Mutable head drift yields `STALE_CURRENTNESS`; it does not corrupt the immutable observed cut.
- 67/49/18 remains cut-local historical evidence rather than permanent estate-cardinality policy.

## Hostile finding H1 — competing canonical activation authority

At predecessor head `659c2b3fc04bc8bc98db3f702b00490b0dc21612`, V3 declared itself the activation-disposition authority while `VERA_PORTFOLIO_CAPABILITY_REGISTRY_V1.json` still labeled the superseded Vera V1 runtime-source registry `EXACT_CANONICAL_BINDING`. Its validator actively required that stale designation.

That produced two simultaneous canonical-looking activation sources. Disposition of that predecessor subject: **REJECTED UNTIL REPAIRED**.

## Repair readback

PR #147 advanced to exact head `83eda677f6daa95a4ebe494f4cadacb9a8d4a2a9`.

The capability registry now:
- marks V1 `SUPERSEDED_HISTORICAL_EVIDENCE_ONLY`;
- marks its semantics `HISTORICAL_EVIDENCE_ONLY_NOT_ACTIVATION_AUTHORITY`;
- binds activation authority to exact V3 artifact blob `66279e3e612309673fb5a6403f48ced536d63f66`;
- binds Vera upstream `dff171a8cee0b2dd3c6fd4627499330800499fdd`;
- binds prior Rezon Vera assurance `d22abc8f7b4649ca0b9e21e77673f263283d98bf`.

Both validators now fail if the legacy registry regains activation authority or if exact V3/Vera/Rezon bindings drift. A regression restores `EXACT_CANONICAL_BINDING` in a mutant and requires rejection.

## Executed exact-head evidence

On `83eda677f6daa95a4ebe494f4cadacb9a8d4a2a9`:
- `VCP Vera Runtime Source Binding V3` run 36768313899: PASS.
- `Control-plane consolidation validation` run 36768314090: PASS.
- `VCP integrity` run 36768313861: PASS.

Intermediate repair head `70511b2ddfb71fcff33839195d13b32f7ad21be9` failed integrity on one extra blank line at EOF. The failure was not waived; it was repaired and the full exact-head gate reran successfully.

## Remaining limits

1. This does not establish semantic correctness of every source in Vera's immutable cut.
2. Mutable head evidence still requires refresh before currentness-sensitive use.
3. Private exact membership is intentionally absent from this public surface.
4. Source qualification does not establish deployment, installation, live control-plane consumption, runtime identity, or downstream effect.
5. No merge is authorized by this review.

## Claim ceiling

`VCP_PR147_83EDA677_SURVIVES_NARROWED__V3_SINGLE_ACTIVATION_POLICY_AUTHORITY__NO_AUTO_BIND_PRESERVED__PRIVATE_COUNT_ONLY__IMMUTABLE_CUT_SEPARATE_FROM_FRESHNESS__SOURCE_ONLY`
