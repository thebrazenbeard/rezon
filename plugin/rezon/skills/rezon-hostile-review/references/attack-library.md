# Hostile review attack library

Use semantic attacks, not just keyword or formatting mutations.

High-value attacks include:
- strengthen or weaken the proposition and see whether the verifier notices;
- switch the referent while preserving similar language;
- use stale but internally valid evidence against a currentness claim;
- duplicate one source through several summaries and test whether it is miscounted as independent evidence;
- present several workers that share executor, model, provider, prompt lineage, context lineage, or common evidence;
- recompute an integrity digest after altering the meaning;
- roll back to an older internally consistent state;
- encode an authority or effect promotion indirectly rather than with obvious blocked words;
- hide a failed or unavailable worker behind a consensus summary;
- provide a source-only artifact while prose implies installation or activation.

A trusted verifier should break on intentionally broken implementations of these patterns.
