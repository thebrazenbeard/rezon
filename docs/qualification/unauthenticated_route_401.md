# Rezon gateway: unauthenticated 401 is route-ambiguous

Scope: a negative source-level qualification check, **not** a deployment
qualification or authorization to access a protected endpoint.

An older installed handler answers an unauthenticated `GET /readyz` with 401,
but it also answers a deliberately nonexistent route with the same 401.
That handler checks authentication before matching most routes. The response
therefore cannot establish that `/readyz` is implemented, much less that the
SQLite store is readable or that any worker/provider is available.

The current source has an explicit authenticated `/readyz` route, whose
documented claim is only a bounded store-readability check. `/healthz` is
process liveness, even if an older build used the misleading `ready` status.
The gateway's source revision, package, process identity, and current route
must be bound independently; a source test cannot certify a running host.

## Reproducible source-only negative control

Run `PYTHONPATH=src python -m unittest discover -s tests -p test_collective_gateway_route_ambiguity.py -v`.
The test dispatches two anonymous GETs against an in-memory handler: one to
the registered `/readyz` route and one to a definitely unregistered path.
Both yield the identical 401 with no socket, credentials, database access,
or provider call. The intended result is evidence that **401 alone proves
neither route existence nor readiness**.

## Release-bound gateway qualification still needed

1. Select an exact, reviewed source/PR head, including dependent changes,
   and bind the release artifact to the owner-approved deployment target.
2. Have the authorized host owner independently verify process-bound source
   and startup parameters; a Git working-tree SHA is insufficient to prove
   the code already loaded in a process.
3. Have the authorized owner run an authenticated, read-only `/readyz` probe,
   verify store readability, and independently qualify provider reachability
   and any outstanding after-send effects. Do not infer these from liveness.
4. Record the observed revision and probe receipts. No silent restart,
   secret extraction, provider POST, or automatic rollback is authorized by
   this document or its associated test.
