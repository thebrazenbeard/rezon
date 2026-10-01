# WorkBridge Family Exact-Source Topology Review — 2026-09-30

Review class: source/provenance/topology review. No merge, installation, endpoint activation, workstation authority, or runtime-effect claim.

## Exact subjects

- `thebrazenbeard/WorkBridgeMCP@f091f6be6e85f489e3e7839e10612204b89a4a9e`
- `thebrazenbeard/workbridgecommander@c2b95be79ca011a539c20bfee60fcbc46cfea177`
- `thebrazenbeard/workbridge@7caab29eb5667897a0a03d0ce67d733380b01685`

Relevant open source candidates at review time:

- WorkBridgeMCP PR #19 @ `88db4d9f05466a16f03eb8fcc28fe58a35c192ae`: bounded Go process-grant argument hardening.
- WorkBridgeMCP PR #20 @ `37a878868e9182b03e2680e863af1a6b94b75944`: Desktop Commander process-capacity alignment candidate.
- standalone workbridge PR #4 @ `0344d14551ea7e5a4309adb782e3f8b48c7b8b8c`: carry argument hardening into the extracted Go lineage.

## Provenance findings

`workbridge` explicitly records that its generic Go MCP server was extracted from WorkBridgeMCP commit `f51a75d927346a172bb7cc3e4e3f18cd3f52d701`, with module path changed to `github.com/thebrazenbeard/workbridge`. It also imports a standalone Synology media-bridge source cut from Vera Synology. It explicitly excludes VeraMesh/Relay/Port, control-plane material, and Desktop Commander duplicate mode.

`workbridgecommander` explicitly identifies WorkBridgeMCP as the primary implementation/design authority for its workstation path and DesktopCommanderMCP as the workstation behavior reference. Commander is a remote MCP ingress/device-attachment orchestration layer and preserves the unrestricted Desktop Commander command-string semantics of that path. It is not the bounded native WorkBridge Go surface.

WorkBridgeMCP itself currently exposes two deliberately different source models: the bounded native Go server and the exact Desktop Commander duplicate path. Those models must not be collapsed into one authority claim.

## Exact blob-overlap evidence

At the exact main subjects above:

| Pair | Files A/B | Common paths | Identical same-path blobs | Shared blob SHA at any path |
| --- | ---: | ---: | ---: | ---: |
| WorkBridgeMCP ↔ workbridgecommander | 70 / 59 | 4 | 0 | 0 |
| WorkBridgeMCP ↔ workbridge | 70 / 65 | 25 | 10 | 10 |
| workbridgecommander ↔ workbridge | 59 / 65 | 4 | 0 | 0 |

This supports a bounded lineage conclusion:

- `workbridge` is a source-derived, now-diverging implementation lineage from WorkBridgeMCP, not an unrelated repository and not automatically a canonical replacement.
- `workbridgecommander` is a distinct transport/orchestration surface rather than a source fork of either implementation.
- same-family naming alone is insufficient to infer shared runtime authority, deployment, or substitutability.

## Security-drift finding

Because `workbridge` copied the bounded Go server before later WorkBridgeMCP hardening, security fixes can diverge across the two implementation lineages.

Concrete example: WorkBridgeMCP PR #19 adds deny-by-default caller argument authority to executable grants. The current standalone `workbridge` main still carried the earlier broad caller-argument behavior at review time. A separate standalone workbridge PR #4 now carries the equivalent hardening and must qualify independently.

Therefore donor lineage must not be treated as continuing patch propagation.

## Corpus classification guidance

For descriptive portfolio classification only:

- **WorkBridgeMCP**: workstation implementation + qualification source; contains bounded native server and exact Desktop Commander duplicate packaging/qualification.
- **workbridgecommander**: remote transport/orchestration and device-attachment surface for the Commander path; source presence does not establish a deployed endpoint or remote effect.
- **workbridge**: standalone extracted bounded-Go implementation plus Synology packaging; derived lineage with independent currentness and qualification requirements.

The three repositories may compose, but none should be silently aliased to another. Their source, install, runtime, transport, authority, and effect states remain separate.

## Hostile challenges

> If WorkBridgeMCP remains the primary workstation implementation authority for Commander, what prevents the standalone `workbridge` extraction from becoming an untracked competing implementation as security patches accumulate?

Current answer: nothing automatic. Exact-source currentness and explicit patch propagation/review are required; the existence of provenance text is not a synchronization mechanism.

> Does WorkBridge Commander make bounded WorkBridge safer remotely?

No such conclusion follows. Commander explicitly preserves the unrestricted Desktop Commander workstation semantics for its path. Transport authentication/integrity is separate from bounding the workstation capability surface.

> Can the repositories be consolidated merely because source overlap exists?

No. The observed overlap establishes provenance/duplication, not which product/runtime boundary should survive. Consolidation would require consumer, packaging, deployment, and migration evidence not established by this review.

## Disposition

`SURVIVES_NARROWED_AS_THREE_DISTINCT_SOURCE_ROLES_WITH_EXPLICIT_DERIVED_LINEAGE`

Claim ceiling:

`WORKBRIDGE_FAMILY_20260930__EXACT_SOURCE_TOPOLOGY_AND_PROVENANCE_ONLY__NO_ALIAS__NO_DEPLOYMENT__NO_RUNTIME_EFFECT`

## Merged standalone WorkBridge current-main requalification — 2026-10-01

Standalone `thebrazenbeard/workbridge` PR #4 has since merged.

Current exact main:

`e88e14ea25f25abd723bb50909b3e25e67f889fd`

The merged main carries the deny-by-default caller-argument authority boundary and the separately versioned `WorkBridgeRelay 0.1.0-0003` candidate.

Exact-main hosted qualification:

- `WorkBridge source checks` run `36792749209`: PASS
- `WorkBridgeRelay ARMv7 SPK` run `36792749216`: PASS

This closes the prior source/build/package qualification gap for the standalone current main. It does **not** establish installation on a NAS, a live listener, workstation attachment, remote endpoint reachability, or downstream effect.

### Refreshed exact blob topology

At:

- `WorkBridgeMCP@f091f6be6e85f489e3e7839e10612204b89a4a9e`
- `workbridgecommander@c2b95be79ca011a539c20bfee60fcbc46cfea177`
- `workbridge@e88e14ea25f25abd723bb50909b3e25e67f889fd`

the exact overlap is:

| Pair | Files A/B | Common paths | Identical same-path blobs | Shared blob SHA at any path |
| --- | ---: | ---: | ---: | ---: |
| WorkBridgeMCP ↔ workbridgecommander | 70 / 59 | 4 | 0 | 0 |
| WorkBridgeMCP ↔ workbridge | 70 / 65 | 25 | 8 | 8 |
| workbridgecommander ↔ workbridge | 59 / 65 | 4 | 0 | 0 |

The standalone lineage now shares fewer exact blobs with WorkBridgeMCP than at the earlier review cut. That supports the existing hostile finding: provenance does not create automatic patch propagation, synchronization, or runtime aliasing.

### Updated disposition

`SURVIVES_NARROWED_AS_THREE_DISTINCT_SOURCE_ROLES__STANDALONE_WORKBRIDGE_CURRENT_MAIN_SOURCE_BUILD_PACKAGE_QUALIFIED`

Updated claim ceiling:

`WORKBRIDGE_FAMILY_20261001__EXACT_SOURCE_TOPOLOGY__STANDALONE_MAIN_SOURCE_BUILD_PACKAGE_PASS__NO_ALIAS__NO_INSTALL__NO_RUNTIME_EFFECT`
