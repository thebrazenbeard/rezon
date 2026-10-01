# Hostile Exact-Head Review — On-Theo PR #168 Rebase-Precondition Repair

Reviewed repository: `thebrazenbeard/on-theo`  
Reviewed PR: #168  
Reviewed exact head: `98cea0dcb9bdf83ac352f02ce94808ac4670105c`  
Reviewed exact base: `2fdc9614fa4f45eb038772d736b146809e10a7f1`

Review class: source-recorded hostile exact-head review. This does not claim a separately executed external-model review.

## Disposition

`SURVIVES_NARROWED`

The candidate survives as a test-contract repair for squash-canonicalized Git topology. It does not modify research registries, source packets, claims, witness identities, review receipts, or scholarly conclusions.

## Changed surface

Exactly one file changes:

`tests/test_registry_rebase_preconditions.py`

The repair removes hard-coded historical ancestry cardinalities:

- ancestor extensions = 11
- divergent extensions = 39
- divergent unique bases = 36

Those values belonged to an older pre-squash audit subject and are not invariant after PR #167 squash-canonicalized current main.

## Invariants preserved by the repair

The repaired test still requires:

1. exactly 50 extensions;
2. the report to enumerate exactly all 50;
3. ancestor + divergent counts to partition the full extension set;
4. at least one divergent extension to exist;
5. divergent unique-base count not to exceed divergent extension count;
6. referential-precondition mismatch count = 0;
7. referential preconditions equivalent = true;
8. every reported divergent extension to have mismatch_count = 0;
9. the historical witness-registry absence check at the fixed historical subject to remain true.

The repair therefore stops treating Git ancestry cardinalities as semantic/referential invariants while retaining the actual rebase-precondition contract.

## Exact-head executable evidence

On `98cea0dcb9bdf83ac352f02ce94808ac4670105c`:

- `Validate registries` run `36797514717`: PASS

## Hostile challenges

> Does this repair prove current main is qualified?

No. It qualifies the repair candidate head. Current main remains a different exact subject until the repair is integrated and exact-main validation reruns.

> Could the looser assertions hide lost extensions?

Not under the preserved checks. The candidate still requires `extension_count == 50`, `len(extensions) == extension_count`, and ancestor + divergent counts to equal the full extension count.

> Could the looser assertions hide referential drift?

Not under the preserved checks. Referential mismatch count must remain zero, overall equivalence must remain true, and every divergent extension must remain mismatch-free.

> Does passing the validator elevate historical/religious claims?

No. Repository integrity/registry validation is evidence about source structure and referential consistency only. It does not elevate claim confidence, source authenticity, historical reconstruction, or theological interpretation.

## Remaining limits

1. The candidate is unmerged.
2. Exact current main remains unqualified with respect to this repaired test contract.
3. The large historical/research PR graph remains separate from this infrastructure repair.
4. No source claim, witness, composition date, authenticity judgment, historical reconstruction, or research confidence is changed by this review.

## Claim ceiling

`ON_THEO_PR168_98CEA0DC_SURVIVES_NARROWED__SQUASH_TOPOLOGY_TEST_REPAIR_ONLY__REFERENTIAL_PRECONDITIONS_PRESERVED__NO_RESEARCH_CLAIM_ELEVATION`
