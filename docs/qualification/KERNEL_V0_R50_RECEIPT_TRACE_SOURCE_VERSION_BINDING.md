# Rezon Kernel V0 R50 — Receipt/Trace Source-Version Binding

Status: SOURCE REPAIR / HOSTILE REGRESSION ADDED / QUALIFICATION REQUIRED

R49 exported receipt-level and trace-level source-version provenance but did not require those two representations to agree.

The runner's canonical construction is deterministic: it accumulates each execution view's input source versions in first-seen order and writes that ordered deduplicated tuple to `ResultReceipt.source_versions`; the same execution input versions are recorded on each `TraceRecord`.

R50 therefore recomputes the expected receipt source-version tuple from the exact trace records using the same ordered-deduplication rule and rejects export unless it exactly equals `receipt.source_versions`.

Hostile regression:
- create a normal exact run;
- replace only the receipt's source-version tuple with forged provenance;
- keep the trace unchanged;
- require `RunEvidenceError`.

Claim ceiling is unchanged. R50 strengthens structural receipt/trace consistency only. It is not a signature, object-origin authentication, external currentness proof, authority proof, lease/fence proof, effect readback, or completion truth.
