# Rezon Kernel V0 R34 Exact Runner Task-ID Contract

Status: `SOURCE_REPAIRED / HOSTED_TEST_PASS / FINAL_DOC_HEAD_REQUALIFICATION_PENDING / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R34 is the bounded successor to R33 exact-final subject
`c9f689cc648684a840a8ea1097db94b0c0d98d67`.

R33's exact runner-budget repair remains valid within its narrower scope. Fresh
hostile review found that the runner-owned `task_id` argument itself did not
have an exact runtime contract when no `TaskEnvelope` was supplied.

## Effect-bearing predecessor defect

`task_id` is used to construct execution/provenance identity.

On exact R33:
- an empty built-in string reached executor/admission, canonical output was
  admitted, and only the final `ResultReceipt` construction raised because the
  task ID was empty;
- a `str` subclass was accepted without rejection;
- a truthy non-string object with a forged string representation was accepted.

The empty-ID case is especially important: invalid identity could cause a
canonical state change before the failure surfaced.

## Frozen RED

Regression:
`tests/test_r34_exact_runner_task_id_contract.py`

RED commit:
`7ccd800736c00d13834cda320408933949fdc68a`

Hosted run:
`35462878752`

Job:
`105949783513`

Result:
**3 failed / 224 passed**.

Observed failures:
1. empty task ID: executor calls = 1 before final receipt failure;
2. string-subclass task ID: expected rejection did not occur;
3. truthy non-string task ID: expected rejection did not occur.

## Repair

Repair commit:
`e7218d47cbd987e6f2cb67a51e2156d88baa432c`

Before TaskEnvelope comparison, episode snapshotting, scheduler creation,
executor invocation, admission, or trace construction, `EpisodeRunner.run()`
now requires:

- exact built-in `str`;
- non-empty value.

Invalid task identity raises `ValueError` immediately because a valid
`ResultReceipt` cannot itself be safely keyed by an invalid task identity.

## Hosted qualification

Repaired-head run:
`35463079139`

Job:
`105950315418`

Result:
- **227/227 PASS**;
- compileall PASS;
- diff-check PASS.

## Claim ceiling

R34 establishes ordinary in-process exact runtime validation of the
runner-owned task identity before governed execution can begin.

It does not establish:
- arbitrary executor side-effect safety outside the governed runner;
- cryptographic caller identity;
- semantic truth;
- distributed/database durability;
- independent hostile acceptance;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the final documentation-bearing head in hosted CI.
2. Run the accepted Benchmark R4 composition probe on the exact final head.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve R33 and the R34 RED as immutable predecessor evidence.
5. Do not merge without Patrick's explicit authority.
