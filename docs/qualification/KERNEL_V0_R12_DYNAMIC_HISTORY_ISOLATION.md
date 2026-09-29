# Rezon Kernel V0 R12 Dynamic-History Isolation

Status: `SOURCE_CREATED / BUILD_PASS / TEST_PASS / HOSTED_CI_PASS / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R12 is the bounded successor to failed R11 exact subject `8d30b04728488d0d1fcc3bb9d176e77c49923478`. R11 structurally separated task specification, task envelope, execution identity, and audit-side independence metadata, but still exposed dynamic execution history to strong-independent workers through two metadata fields.

## Exact ancestry

- failed R11 review head: `8d30b04728488d0d1fcc3bb9d176e77c49923478`
- failed R11 tree: `58cfd2b0f0254c16d1b1605263016b2cd667e189`
- R12 branch: `work/rezon-kernel-v0-r12-episode-version-isolation`
- episode-version RED1: `21585dfdf7ec2f8f85f45a98e4c809ee78cbc145`
- execution-ordinal RED2: `96c437e03cd82a55bd3ba8db116188641c8bacb0`
- executable GREEN: `dd8af9b4fd5414f3a2ea6b3af2d8e6e21b3992ba`
- executable GREEN tree: `060fb41c333a9176a2f0174b1e7fd131d81e9fd2`
- CI-enablement head: `9b52b40c9bc78664802b0771ac879f8e3b5eef9e`

## R11 failure 1 — dynamic episode-version side channel

Fresh exact-R11 hostile execution used:

- trusted opaque episode identifier;
- one prior peer-produced hidden hypothesis;
- zero visible proposition IDs for the strong-independent worker;
- valid independently attested independence metadata/policy.

The worker copied only `view.episode_version`.

Observed on exact R11:

- failures: empty;
- unresolved: empty;
- visible proposition IDs: empty;
- `independence_demonstrated=True`;
- admitted output included `seen-version:trusted-opaque-episode@1`.

The `@<event_count>` suffix therefore exposed hidden episode activity even though the hidden peer proposition itself was not visible.

RED1 test-only head `21585dfd…` froze this family before production repair and produced **2 failures**:
- executor-visible episode version changed across clean vs prior-history cases;
- trace lacked an explicit executor-visible episode-version binding.

The final R12 tests strengthen this further by using the same episode ID for clean and hidden-history runs, so event count is the only version difference.

## R11 failure 2 — execution ordinal side channel

R11 strong-independent execution IDs used:

`independent:exec:<record_ordinal>:<node_id>`

A fresh hostile control compared the same strong-independent generator and task specification:

- once with no earlier node execution;
- once after a mandatory verifier ran first and its output was blinded from the independent generator.

Exact RED2 `96c437e0…` reproduced:

- clean: `independent:exec:1:echo_hypothesis`
- prior execution: `independent:exec:2:echo_hypothesis`

Targeted result: **1 failed / 0 passed**.

Thus an otherwise isolated worker could infer prior execution history from its execution identifier.

## R12 repair

For strong-independent executors:

1. `ExecutionView.episode_version` is replaced with constant non-history-bearing marker:

   `independent@0`

2. The canonical audit version remains unchanged in `TraceRecord.episode_version`.

3. `TraceRecord.executor_episode_version` explicitly records what the executor actually saw.

4. Preflight failure traces also bind the sanitized executor-visible version.

5. Strong-independent execution IDs are now derived only from:
   - static node identity; and
   - digest of the allowed `TaskSpecification` (or `no-task-spec` when absent).

They no longer depend on task ID, total trace-record count, hidden event count, or prior execution ordinal.

Non-independent execution retains the real episode version and existing task-derived execution-ID behavior.

## Preserved predecessor controls

R12 retains R9-R11 guarantees:

- non-empty `context_refs` fail closed before strong-independent execution;
- full `TaskEnvelope` is not visible to strong-independent executors;
- allowed `TaskSpecification` contains only literal request, subject refs, and constraints;
- task ID / authority / privacy / budget / context refs remain structurally absent from the task specification;
- executor-facing independence metadata remains empty;
- complete attestation remains runner/audit-side and gates preflight;
- admission binds outputs to the exact runner-issued execution ID;
- non-independent workers retain full TaskEnvelope and true episode version.

## Exact executable qualification

Fresh clean checkout of exact executable head `dd8af9b4fd5414f3a2ea6b3af2d8e6e21b3992ba` under CPython 3.12:

- pytest: **122 passed / 0 failed**
- `python -m compileall -q src tests`: PASS
- `git diff --check`: PASS

Focused R12 controls before push:

- episode-version / execution-ID isolation: **4/4 PASS**

## Hosted qualification

R12 was added to the existing `Rezon kernel tests` push workflow without changing its commands.

Hosted GitHub Actions on CI-enablement head `9b52b40c9bc78664802b0771ac879f8e3b5eef9e`:

- run: `35399955230`
- install: PASS
- compile: PASS
- test: PASS
- diff-check: PASS
- overall: **success**

## Explicit trust boundaries / non-claims

R12 does not establish:

- independent hostile PASS on the final R12 subject;
- semantic proof that literal task-specification content is non-adversarial;
- a shared-context/shared-read independence class;
- cryptographic model/provider/executor identity;
- protection against a malicious trusted orchestrator intentionally encoding answers into trusted static identifiers;
- a positive protected-authority path;
- merge authority;
- deployment, install, activation, runtime effect, or provider/model mutation;
- learned-routing qualification;
- reasoning superiority.

The existing V0 contract still treats `episode_id` and `node_id` as trusted orchestration identifiers. R12 removes dynamic hidden-history metadata from the executor-facing strong-independence surface; it does not redefine that trust model.

The Issue #5 donor/learned-routing gate remains closed pending fresh exact-head independent acceptance.

## Remaining gate

Freeze this documentation/review head, requalify that exact immutable subject locally and in hosted CI, then request fresh exact-head independent hostile rereview.

No merge is requested by this record.
