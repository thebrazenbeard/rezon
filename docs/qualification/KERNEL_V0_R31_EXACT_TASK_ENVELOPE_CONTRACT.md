# Rezon Kernel V0 R31 Exact Task Envelope Contract

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R31 is the bounded successor to failed whole-Kernel R30 exact subject
`ac38eeed02c508fbdf10cfaf47a1e54aba326782`.

R30's exact NodeDescriptor and scheduler-to-execution binding repairs remain
valid within their narrower scope. Fresh hostile review found a separate
TaskEnvelope / TaskSpecification runtime-contract boundary that could defeat
independence isolation before those repaired controls became relevant.

## R30 hostile failure

Exact R30 false-accepted all eight corrected R31 cases.

Critical execution path:

1. an independence-required node received a `TaskEnvelope` subclass whose
   ordinary fields declared no auxiliary context;
2. the subclass overrode `to_task_specification()`;
3. the override returned an exact `TaskSpecification` containing hidden peer
   answer context;
4. the runner's `context_refs` independence check remained empty and passed;
5. the independent executor received the injected task specification;
6. the executor copied the hidden peer material into output;
7. admission accepted the output;
8. the trace recorded `independence_demonstrated=True`;
9. the run completed with no failures.

Exact reproduction admitted:

`independent task; hidden auxiliary context: peer-answer:H1=compressor`

Additional frozen cases demonstrated:

- custom-equality TaskEnvelope task IDs matching the runner task ID;
- list-backed `subject_refs`;
- list-backed `constraints`;
- list-backed `available_authority`;
- list-backed `context_refs`;
- `bool` accepted as an integer resource budget;
- malformed exact `TaskSpecification` fields accepted by direct admission.

Disposition:
`R30_TASK_ENVELOPE_SPEC_RUNTIME_CONTRACT = FAIL / CHANGES_REQUIRED`
for whole-Kernel acceptance.

R30 remains preserved, draft, and unmerged.

## Frozen R31 RED

Regression file:

`tests/test_r31_exact_task_envelope_contract.py`

Initial test-only RED:
`60c127403b0749f020917d82ce1b20d103616adf`

Corrected frozen RED:
`c1729f42860cba15c71756ff1ded73653d06c50f`

The correction changed only hostile-string deepcopy/reconstruction behavior so
all cases reached the intended assertions.

Fresh exact-R30 result after that fixture correction:

**8 failed / 0 passed**.

## R31 repair

Envelope/specification contract:
`10c40228372bb2f460607d7e8df2493c9985e79b`

Runner pre-dispatch enforcement:
`53c08ca1d4b8e4f7f6f7f17d2740f25e2f22d5a0`

Direct-admission specification enforcement:
`95b9a0314279951f83685f6bc3136c2f3dae45b2`

Final regression-file normalization:
`787e8fa70dccdc20589041f749bce53c8be55d58`

R31 defines explicit exact runtime contracts for both task artifacts.

An accepted `TaskEnvelope` must now be:

- exact base `TaskEnvelope`;
- non-empty exact built-in string task ID;
- non-empty exact built-in string literal request;
- exact tuples containing exact built-in strings for subject refs, constraints,
  available authority, and context refs;
- `privacy_scope=None` or an exact built-in string;
- `resource_budget=None` or an exact built-in non-negative integer, excluding
  bool and integer subclasses;
- convertible through the base TaskEnvelope method to an exact valid
  TaskSpecification.

The runner validates that contract before reading `.digest`, comparing task
identity, consuming the resource budget, or building the execution view.
Therefore TaskEnvelope subclasses cannot dispatch overridden task-specification
semantics into an independence-required worker.

An accepted `TaskSpecification` must now be:

- exact base `TaskSpecification`;
- non-empty exact built-in string literal request;
- exact tuples containing exact built-in strings for subject refs and
  constraints.

Direct admission uses the same TaskSpecification contract before digest binding.

## Qualification

CI-enablement head:

`bf7fdac57281c5d6e4a6ac56950d67ab5f350c26`

Fresh detached-checkout qualification:

- R31 hostile regressions: **8/8 PASS**;
- focused R16-R31 controls: **89/89 PASS**;
- task-envelope/specification focused set: **19/19 PASS** before remote cut;
- full suite: **218/218 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted GitHub Actions:

- run `35462093049`;
- exact head `bf7fdac57281c5d6e4a6ac56950d67ab5f350c26`;
- test job `105947653605`;
- install / compile / test / diff-check: PASS;
- conclusion: **SUCCESS**.

## Exact ancestry

- failed R30 final: `ac38eeed02c508fbdf10cfaf47a1e54aba326782`
- R31 branch: `work/rezon-kernel-v0-r31-exact-task-envelope-contract`
- corrected frozen RED: `c1729f42860cba15c71756ff1ded73653d06c50f`
- envelope/specification repair: `10c40228372bb2f460607d7e8df2493c9985e79b`
- runner repair: `53c08ca1d4b8e4f7f6f7f17d2740f25e2f22d5a0`
- admission repair: `95b9a0314279951f83685f6bc3136c2f3dae45b2`
- test normalization: `787e8fa70dccdc20589041f749bce53c8be55d58`
- CI-enablement head: `bf7fdac57281c5d6e4a6ac56950d67ab5f350c26`

## Explicit scope / non-claims

R31 establishes ordinary in-process exact runtime validation of the current
TaskEnvelope / TaskSpecification path used by EpisodeRunner and direct
admission.

It does not establish:

- cryptographic authenticity of task-envelope origin;
- semantic truth or safety of literal task content;
- protection against malicious source replacement or private monkeypatching;
- arbitrary executor side-effect safety outside the governed runner;
- persistent/database or distributed durability;
- independent hostile PASS on R31;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Requalify the exact final documentation head locally and in hosted CI.
2. Run the accepted Benchmark R4 local composition probe.
3. Obtain fresh exact-head independent hostile rereview.
4. If review remains pending, pressure only adjacent effect-bearing runtime
   boundaries; do not expand into cleanup-only typing work.
5. Preserve every failing exact subject.
6. Do not merge without Patrick's explicit authority.
