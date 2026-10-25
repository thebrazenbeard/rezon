# VN2 Rezon V2 observer preflight and recoverable upgrade contract

Status: **SOURCE-ONLY CANDIDATE / NO DEPLOYMENT AUTHORIZATION**. The VN2
installation observed on 2026-10-25 was a clean Rezon source checkout at
`d27da3cab31ae96aff3c65385fc31354dc8aeb8c`, serving TKIK on
`127.0.0.1:18765`. Its HTTP handler did not implement the V2
`/v1/read-challenge` and `Rezon-Read-HMAC` contract expected by PORTAL Draft
#103. Rezon `main@74e952ccccc96fe7e806b826351faced21eb7fef` includes that
source protocol. These are separate observations, **not** an installed upgrade.

## Source and on-host challenge-only preflight

The standard-library `scripts/collective_state_read_preflight.py` requires an
exact, clean source checkout and checks one bounded anonymous challenge on a
numeric IPv4 loopback port. It does not read the process environment, token,
episode payload or database; it sends no mutation request or bearer credential.

```sh
python scripts/collective_state_read_preflight.py \
  --source-checkout /path/to/exact/rezon-source \
  --expected-head REPLACE_WITH_REVIEWED_40_HEX_COMMIT \
  --port 18765 \
  --episode collective-REPLACE_WITH_REAL_32_HEX_ID
```

Only `CHALLENGE_ONLY` means the exact checkout and challenge *shape* matched.
The response `proof` cannot be authenticated without a separate read-token
holder; a fake loopback service could return structurally valid JSON. The
result always states `authenticated_state_verified=false`,
`independent_host_verified=false`, and `activation_authorized=false`.
`HOLD` includes source mismatch, dirty tracked source, unreachable port,
unconfigured observer secret (HTTP 404), legacy gateway (typically HTTP 401),
malformed response, redirect, overflow, and deadline expiration. Never promote
this preflight to a health, quorum, witness, or protected-effect qualification.

## Staged migration and rollback gates (manual, separately authorized)

1. **Before touching the service**, capture exact Git HEAD, tracked source
   status, service unit/version/port, current listener identity, database
   location and a recoverable offline snapshot. Do not log secrets. Verify
   the snapshot can reconstruct state. Check whether source migration changes
   would prevent returning to the previous binary.
2. Stage a reviewed, immutable Rezon build in a **new** versioned directory,
   retaining the old executable/configuration and rollback path. Do not `git
   pull` inside an active service directory, share a writable live database
   between canary and production, or alter the existing service merely to run
   the source preflight.
3. On a disposable database and isolated numeric-loopback canary port, use a
   fresh private observer token distinct from admin/worker credentials. Pass
   the token through the existing private service configuration mechanism,
   never CLI arguments, repository content, or process/log output. Run the
   source preflight and the genuine V2 challenge/HMAC request/response test;
   repeat with the wrong token, replayed proof, stale challenge, malformed
   HTTP, and unavailable database. An authenticated `GET /readyz` is a
   separate storage check, not proof of PORTAL participation.
4. For PORTAL, the observer is **local-only**. `127.0.0.1:18765` on VN2 is not
   reachable through `127.0.0.1` on VN1. Choose co-location or independently
   qualify a bounded, authenticated local transport whose loopback audience,
   admission, host identity and failure isolation are explicitly preserved.
   Do not silently replace numeric loopback with a LAN/Tailscale URL.
5. Before any cutover, stop writers, prove schema compatibility with the old
   runtime or establish a tested database restoration point, and define a
   health/readiness + authenticated fixed-episode acceptance window. Swap
   service configuration atomically only under separate deployment authority.
   On failure, stop the candidate, restore the prior source/configuration and
   data *only through the tested recovery method*, reverify old readiness,
   and record exact effects. Never run both versions against the same live
   writable SQLite file.

**Still HOLD:** separate actual reader credential + authenticated existing
episode HMAC custody, PORTAL installed route, on-host service restart and
recovery, cross-node transport qualification, effect authority, and all
physical-model independence claims. Unit and synthetic cross-repo smoke tests
do not substitute for these gates.
