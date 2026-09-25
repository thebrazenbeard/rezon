# Rezon Benchmark V1 Layer 1 Reference Evidence R3

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / REPLAY_OBSERVED / INDEPENDENT_QUALIFICATION_PENDING`

R3 is a narrow semantic hardening delta over R2. It preserves the R2 corpus, metrics, fairness/accounting repairs, and non-claims. It does not qualify live model/provider reasoning, deployment, installation, activation, runtime effect, or general reasoning superiority.

## Exact subject

- repository: `thebrazenbeard/rezon`
- branch: `rezon/benchmark-v1-r3-ambiguity`
- R2 review ancestor: `e9a1e3ab070a5f4146d2c1ff63ed419e3953fb87`
- R3 RED head: `6e6aa86f85f48bdde39cc86373341fe72b2c96f8`
- R3 RED tree: `e1eeddf0274e1fe68c0b9198936ad86162d5a881`
- R3 executable/GREEN head: `a7875deee9c537702e47aa54af15ee0732ffcfd6`
- R3 executable/GREEN tree: `bc30d87af1b26371ce55529b0f54af6bb0324ae7`
- R2 adverse fixture SHA-256: `a6244ff59da30bb2f6571b1e5abf89f2121d158af5a84d4b090891c7dc4039c4`
- R2 clean-control SHA-256: `2bd93ec82fb9c8bd281c4d3e19d7708fa325f6f5494a7b8ca132873d62481925`
- composite fixture-manifest SHA-256: `9a6d277f80d3bea4552aad745cb6204538ecf0b150590bc5965dcaa73498087c`
- composite strategy-input digest: `56b31ca66fe52425840626a8eab190fbc2114201b62748ac005cbda1c6e1a43a`

## Defect

R2's `rezon_guarded` integrator selected the first candidate encountered when two or more otherwise eligible normalized answers tied for the highest count. A 1-1 disagreement therefore answered `A` in one candidate order and `B` in the reverse order.

That behavior violated the Rezon requirement to preserve unresolved ambiguity rather than laundering input ordering into epistemic authority. Existing case-order permutation controls did not exercise candidate-order permutation.

## Frozen RED evidence

R3 added two tests before production repair:

1. an equally eligible independent 1-1 disagreement must abstain with machine-readable unresolved reason `eligible_answer_tie`;
2. reversing candidate order must preserve that abstention and unresolved state.

Hosted GitHub Actions on exact RED head `6e6aa86f...` produced:

- install: PASS
- compile: PASS
- pytest: **2 failed / 99 passed**

The two failures were exactly the new ambiguity tests. The forward ordering answered `A`; the reverse ordering answered `B`.

## Repair

Only `rezon_guarded` integration semantics changed. After governance filtering:

- answer counts are computed as before;
- all normalized answers tied at the maximum count are identified deterministically;
- if more than one maximum-count answer remains, the strategy returns `ABSTAIN`, accepts no candidate, and records `eligible_answer_tie`;
- candidate order no longer selects a winner under an unresolved tie;
- deterministic integration operation accounting still includes each eligible candidate.

`single_pass` and `fixed_multipass` were not changed. The fixed multipass baseline intentionally retains its simple order-sensitive tie behavior.

## Exact GREEN reproduction

GitHub Actions freshly checked out exact executable head `a7875deee9c537702e47aa54af15ee0732ffcfd6` on Ubuntu 24.04.5 / CPython 3.12.14 and passed:

- editable install: PASS
- `python -m compileall -q src scripts`: PASS
- pytest: **101 passed / 0 failed**
- balanced 24-case reference replay: PASS
- `git diff --check`: PASS

The frozen 24-case R2 reference metrics and digests were unchanged because the existing corpus contains no equally eligible top-count answer tie. In particular, `rezon_guarded` remains 21/24 disposition-correct, 2 false accepts, 174 deterministic operations, and 9/15 evaluator-required violation labels detected on that exact population.

This unchanged score is important: R3 repairs an independently discovered mechanism defect without editing adverse cases, clean controls, evaluator gold, or benchmark labels to improve the reported result.

## Scope and non-claims

R3 supports only the narrow observation that the guarded replay integrator no longer resolves an equally eligible top-count answer tie by candidate ordering.

It does **not** prove:

- general reasoning superiority;
- that the guarded strategy is fully correct;
- that all ambiguity classes are represented;
- that source/evidence sufficiency is fully modeled;
- live provider/model quality;
- justified production cost;
- deployment, installation, activation, runtime effect, or behavioral qualification.

Known R2 misses remain open unless independently repaired and requalified: contradiction omission, malformed receipt, and the ABSTAIN-vs-FAIL_CLOSED mandatory-verification mismatch.

## Remaining gate

R3 remains `INDEPENDENT_QUALIFICATION_PENDING`. Independent hostile review must verify the exact R3 head/tree, the RED-to-GREEN transition, candidate-order invariance, absence of regression in non-tied integration, unchanged frozen R2 replay evidence, and whether any additional ambiguity/order-dependent bypass remains.
