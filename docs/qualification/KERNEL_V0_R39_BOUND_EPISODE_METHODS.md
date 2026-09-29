# Rezon Kernel V0 R39 Bound Episode Methods

Status: `SOURCE_CREATED / LOCAL_BUILD_PASS / LOCAL_TEST_PASS / HOSTED_CI_PENDING / INDEPENDENT_HOSTILE_REREVIEW_PENDING`

R39 is the bounded successor to official R38 exact subject
`f2954e63d4e4a1eca90fef8275df0aebdb7600a7`.

R38's exact ExecutionResult transaction-bound validation remains intact.
Fresh hostile review found that exact-type Episode checks still trusted
instance-dispatched methods.

## Hostile findings

Python exact-class instances can still shadow methods on the instance.

### RED 1 — runner snapshot / rollback bypass

Frozen RED:
`e315bf0cbb60c05c1c85809bfa29a8c6e89d9884`

An exact `Episode` instance shadowed `snapshot()` with a fake empty snapshot.
The executor then mutated canonical state through `Episode.add_proposition(...)`.

Exact official R38 behavior:
- executor called once;
- receipt failures: **none**;
- unresolved: **none**;
- receipt version remained the fake `e1@0`;
- actual canonical Episode contained both the malicious direct mutation and the
  returned candidate.

The R37 rollback and R38 exact-result boundary both observed the attacker-owned
instance snapshot, so no rollback occurred.

### RED 2 — direct admission write neutralization

Frozen RED:
`c251ec7060d44589a7d57a5c7a6fcbf49b0cc16e`

An exact Episode instance shadowed `add_proposition()` with a no-op.
`admit_execution_result()` returned an admission receipt without error, but the
admitted proposition was absent from canonical Episode state.

### RED 3 — retrieval admission write neutralization

Frozen RED:
`8b9b10907972bac6134c650b1f743be48517f949`

The same no-op instance shadow on `add_proposition()` caused
`admit_retrieval_as_evidence()` to return an evidence Proposition while
canonical Episode state remained empty.

## R39 repair

Source repair:
`67132ea3e2d521793b550aa5d30e85b4fe6f8867`

Trusted canonical paths no longer dispatch through mutable instance attributes.

Runner:
- all trusted snapshots call `Episode.snapshot(episode)`;
- executor rollback scope calls `Episode.atomic_mutation(episode)`.

Direct admission:
- transaction scope calls `Episode.atomic_mutation(episode)`;
- snapshots call `Episode.snapshot(episode)`;
- canonical proposition/relation writes call base-class
  `Episode.add_proposition(...)` / `Episode.add_relation(...)`.

Retrieval admission:
- canonical evidence write calls `Episode.add_proposition(episode, evidence)`.

Historical R20 rollback tests were updated only in their fault-injection
mechanism: they now monkeypatch the class method, preserving the same rollback
failure semantics without relying on the newly forbidden instance shadow path.

CI / naming normalization:
`91dcdd7ac989c9f5e9785d67c43395d39f8adc6f`

The R39 branch is independently enabled in hosted CI while retaining official
R38's trigger.

## Qualification

Fresh local composed qualification on exact R39:
- R37 rollback + official R38 + R39 + historical R20/R27 focused set:
  **23/23 PASS**;
- full repository: **244/244 PASS**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Hosted exact-head CI and fresh independent hostile rereview remain pending
until the final documentation head is published.

## Exact ancestry

- official R38 subject:
  `f2954e63d4e4a1eca90fef8275df0aebdb7600a7`
- R39 branch:
  `work/rezon-kernel-v0-r39-bound-episode-methods`
- RED 1:
  `e315bf0cbb60c05c1c85809bfa29a8c6e89d9884`
- RED 2:
  `c251ec7060d44589a7d57a5c7a6fcbf49b0cc16e`
- RED 3:
  `8b9b10907972bac6134c650b1f743be48517f949`
- source repair:
  `67132ea3e2d521793b550aa5d30e85b4fe6f8867`
- CI/naming head:
  `91dcdd7ac989c9f5e9785d67c43395d39f8adc6f`

## Claim ceiling

R39 establishes ordinary in-process binding of trusted canonical Episode
operations to the exact base-class implementation across runner, direct
admission, and retrieval admission.

It does not establish:
- sandboxing against arbitrary same-process private-memory mutation;
- protection against source/class monkeypatching;
- filesystem/network/process side-effect rollback;
- semantic truth;
- persistent/database or distributed durability;
- independent hostile PASS on R39;
- merge/deploy/install/runtime/provider/model/credential mutation authority;
- donor/HCAE/HyPER/hyperbolic learned-routing qualification.

Issue #5 learned-routing remains CLOSED.

## Remaining gates

1. Publish final documentation head without rewriting history.
2. Re-run exact-head local and hosted CI.
3. Obtain fresh exact-head independent hostile rereview.
4. Preserve all three frozen RED subjects.
5. Continue only on concrete effect-bearing control bypasses.
6. Do not merge without Patrick's explicit authority.
