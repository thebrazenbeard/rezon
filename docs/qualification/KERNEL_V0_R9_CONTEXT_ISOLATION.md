# Rezon Kernel V0 R9 TaskEnvelope Context Isolation Evidence

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R9 is a bounded successor to exact R8 after a self-hostile contamination failure in the strong-independence boundary. It preserves R8's authority fail-closed rule and the earlier independence/provenance repairs while preventing auxiliary TaskEnvelope context from bypassing the episode-view contamination controls.

## Exact ancestry

- repository: `thebrazenbeard/rezon`
- failed R8 subject: `c88ab7f480a1b6658951e3d6290a422d8b0e737c`
- failed R8 tree: `cd66d07f61f16c439da5bf95649e257889b30702`
- R9 branch: `work/rezon-kernel-v0-r9-context-isolation`
- R9 hostile RED head: `1c31bc24265fa1398f3c0905a4ac8c667588e9ec`
- R9 executable GREEN head: `9fdc1b56984801069a197a5c34f48ee5162a467d`
- hosted-CI enablement head: `691874d40cb43dbce74dfc805015c1ebbf1aa638`

## Source-design basis

The Kernel V0 design defines `TaskEnvelope` as carrying the literal request, subject references, constraints, context references, available authority, and budget. It separately requires independence metadata to record prompt/context lineage and common upstream evidence.

The hierarchical/distributed reasoning design likewise states that multiple nodes are not automatically independent and that Rezon should record shared context sources and whether one node saw another node's result before answering.

Therefore `TaskEnvelope.context_refs` is not semantically invisible transport metadata. It is an explicit auxiliary context channel that can carry answer-bearing material and must be included in the independence boundary.

## Exact R8 self-hostile failure

A fresh clean checkout of exact R8 `c88ab7f4…` constructed:

- an `independence_required` `echo_hypothesis` node;
- complete R8 independence metadata and matching verification policy;
- no visible episode evidence, propositions, or relations that violated the R8 preflight;
- `TaskEnvelope.context_refs=("peer-answer:H1",)`.

The executor read:

`view.task_envelope.context_refs[0]`

and emitted that value into a hypothesis.

Observed exact-R8 result:

- receipt failures: `()`;
- unresolved: `()`;
- trace `independence_demonstrated=True`;
- admitted proposition `h-envelope-leak` with content `copied:peer-answer:H1`.

Thus R8 could certify strong independence while exposing an unbound auxiliary context channel.

## Frozen RED evidence

R9 froze that bypass before repair:

- test: `tests/test_r9_task_envelope_independence.py`;
- exact test-only head: `1c31bc24265fa1398f3c0905a4ac8c667588e9ec`.

Fresh CPython 3.12 targeted execution produced:

`1 failed / 0 passed`

because the independence-required executor still ran with non-empty `context_refs`.

## R9 repair — strong independence excludes auxiliary context refs

For an `independence_required` node, Kernel V0 now checks the exact TaskEnvelope before executor invocation.

If:

`task_envelope is not None and task_envelope.context_refs`

then the runner:

- records `CONTRACT_VIOLATION`;
- records unresolved marker `independence_context:<node_id>`;
- appends a preflight trace with `independence_demonstrated=False`;
- does not execute the worker;
- admits no worker output.

This is deliberately narrow. R9 does **not** strip the task specification.

The following TaskEnvelope fields remain available to a strong-independence worker:

- `literal_request`;
- `subject_refs`;
- `constraints`.

Those fields define the task being solved. R9 treats `context_refs` as the auxiliary dynamic/shared-context channel.

## Positive control

R9 freezes the opposite case:

- `independence_required=True`;
- complete exact independence metadata and matching external policy evidence;
- TaskEnvelope contains literal request, one subject ref, and one constraint;
- `context_refs=()`.

That worker executes successfully, receives the task specification, emits a hypothesis, and the trace reports `independence_demonstrated=True`.

Therefore the R9 boundary is not "independence means no TaskEnvelope." It specifically rejects auxiliary context refs under the strong-independence contract.

## Concurrency meaning

R9 distinguishes two concepts that must not be collapsed:

- **strong independence**: no auxiliary TaskEnvelope context refs, no prior worker-produced proposition/relation exposure, and the existing exact independence-lineage/evidence rules;
- **shared-context/shared-read work**: may legitimately consume auxiliary context, but cannot be promoted as strong independence under Kernel V0.

R9 does not yet define or qualify a richer shared-context independence score/classification.

## Inherited boundaries preserved

R9 retains:

- R8 fail-closed behavior for every non-empty `required_authority`;
- R7 conservative visible-EVIDENCE consumption binding;
- R7 exact governed source-ref/source-version association checks;
- R7 fail-closed handling for prior worker-produced proposition and relation channels;
- R6 generic ResultReceipt non-dispositional semantics;
- earlier scheduler identity, admission, provenance, and failure-state hardening.

## Exact executable qualification

Fresh clean clone of executable head `9fdc1b56984801069a197a5c34f48ee5162a467d` under CPython 3.12:

- pytest: **113 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS

## Hosted qualification

R9 was added to the existing `Rezon kernel tests` push workflow without changing its test commands.

Hosted GitHub Actions on CI-enablement head `691874d40cb43dbce74dfc805015c1ebbf1aa638`:

- run: `35387635216`
- event: push
- install: PASS
- compile: PASS
- test: PASS
- diff-check: PASS
- overall: **success**

## Explicit unresolved / non-claims

R9 does not establish:

- independent hostile PASS on R9;
- a qualified shared-context/shared-read independence class;
- that the literal task request, subject references, or constraints are mechanically proven free of adversarial or answer-bearing content;
- semantic observation of arbitrary executor cognition or which visible evidence it actually used;
- a usable positive protected-authority path;
- cryptographic model/provider/executor identity;
- merge authority;
- deployment, installation, activation, provider/model mutation, or runtime effect;
- learned-routing qualification;
- reasoning superiority.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact subject from a fresh checkout and hosted CI, then request fresh independent hostile rereview.

No merge is requested by this record.
