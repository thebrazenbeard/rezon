# Rezon Kernel V0 R51 — Receipt/Trace Failure-Summary Binding

Status: SOURCE REPAIR / HOSTILE REGRESSION ADDED / QUALIFICATION REQUIRED

R50 binds receipt-level source-version provenance to exact trace records, but its run-evidence exporter still allowed the top-level failure summary to contradict those same trace records.

## Defect

`EpisodeRunner` records execution failures twice by design:

1. the affected `TraceRecord.failures` carries the execution-local failure;
2. `add_failure()` adds the same failure to the final `ResultReceipt.failures` ordered-deduplicated summary.

R50 validated execution IDs, source versions, output digests, producer IDs, task-envelope digest, and canonical producer reconstruction. It did not validate the failure-summary relationship.

An otherwise exact real failed `RunOutcome` could therefore be wrapped with:

`replace(outcome.receipt, failures=())`

while preserving the original failed trace. R50 would then export deterministic evidence whose top-level receipt concealed a trace-record failure.

## R51 repair

Before evidence export, R51:

- walks exact trace records in order;
- first-seen deduplicates their `FailureState` values;
- requires every trace-carried failure to appear in `receipt.failures`;
- allows additional receipt failures because scheduler/authority/unavailable paths can legitimately create top-level failures without a trace record.

The hostile regression uses a real runner-generated invalid-execution-result failure, then forges only the receipt failure tuple empty and requires `RunEvidenceError`.

## Claim ceiling

R51 establishes asymmetric fail-closed consistency between execution-local trace failures and the receipt-level failure summary.

It does not prove:
- object origin or signature;
- that every receipt-level failure has a trace record;
- complete unresolved-reason reconstruction;
- episode-version provenance;
- external currentness/authority/fencing/effect/completion truth;
- merge/deploy/install/provider/model/credential authority.

Issue #5 learned routing remains CLOSED.
