from dataclasses import replace

from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class EvilStr(str):
    def __new__(cls, value, target):
        obj = str.__new__(cls, value)
        obj.target = target
        return obj

    def __eq__(self, other):
        return str(other) == self.target

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.target)

    def startswith(self, prefix, *args):
        return self.target.startswith(prefix, *args)


class DifferentStr(str):
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __hash__(self):
        return id(self)


class EvidenceSubclass(IndependenceVerificationEvidence):
    pass


class PolicySubclass(IndependenceVerificationPolicy):
    def verify(self, metadata):
        return True


class MetadataSubclass(IndependenceMetadata):
    @property
    def is_demonstrably_independent(self):
        return True


class DuckPolicy:
    def verify(self, metadata):
        return True


class IndependentEmitter:
    node_id = "echo_hypothesis"

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h1",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "candidate",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _metadata(**changes):
    values = dict(
        executor_id="executor-a",
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="prompt-a",
        context_lineage="context-a",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:a",),
    )
    values.update(changes)
    return IndependenceMetadata(**values)


def _evidence(metadata, cls=IndependenceVerificationEvidence, **changes):
    values = dict(
        basis_ref=metadata.independence_basis_refs[0],
        executor_id=metadata.executor_id,
        model_id=metadata.model_id,
        provider_id=metadata.provider_id,
        prompt_lineage=metadata.prompt_lineage,
        context_lineage=metadata.context_lineage,
        verification_refs=("review:a",),
        saw_other_answer=False,
        common_evidence_refs=metadata.common_evidence_refs,
        consumed_evidence_refs=metadata.consumed_evidence_refs,
    )
    values.update(changes)
    return cls(**values)


def _policy(metadata, **evidence_changes):
    return IndependenceVerificationPolicy((_evidence(metadata, **evidence_changes),))


def _run(metadata, policy, episode=None):
    episode = Episode("e1") if episode is None else episode
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=IndependentEmitter(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(episode, task_id="t-r29")
    return episode, outcome


def _assert_runner_rejects(metadata, policy, episode=None):
    episode, outcome = _run(metadata, policy, episode)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "h1" not in {p.proposition_id for p in episode.snapshot().current_propositions}


def test_duck_policy_cannot_authorize_independence_required_execution():
    _assert_runner_rejects(_metadata(), DuckPolicy())


def test_policy_subclass_cannot_override_independence_verification():
    metadata = _metadata()
    _assert_runner_rejects(metadata, PolicySubclass((_evidence(metadata),)))


def test_metadata_subclass_cannot_override_claim_completeness():
    metadata = MetadataSubclass()
    _assert_runner_rejects(metadata, DuckPolicy())


def test_policy_verified_evidence_must_be_exact_tuple():
    metadata = _metadata()
    policy = IndependenceVerificationPolicy([_evidence(metadata)])
    assert policy.verify(metadata) is False


def test_verification_evidence_subclass_is_rejected():
    metadata = _metadata()
    policy = IndependenceVerificationPolicy((_evidence(metadata, cls=EvidenceSubclass),))
    assert policy.verify(metadata) is False


def test_forged_basis_ref_cannot_match_claimed_basis():
    metadata = _metadata()
    policy = _policy(metadata, basis_ref=EvilStr("forged-basis", "policy:a"))
    assert policy.verify(metadata) is False


def test_forged_executor_identity_cannot_match_metadata():
    metadata = _metadata()
    policy = _policy(metadata, executor_id=EvilStr("forged-executor", "executor-a"))
    assert policy.verify(metadata) is False


def test_metadata_basis_refs_must_be_exact_tuple():
    metadata = _metadata(independence_basis_refs=["policy:a"])
    assert metadata.is_demonstrably_independent is False


def test_forged_consumed_evidence_ref_cannot_match_visible_evidence():
    forged = EvilStr("forged-evidence", "ev1")
    metadata = _metadata(consumed_evidence_refs=(forged,))
    episode = Episode("e1")
    episode.add_proposition(Proposition("ev1", "e1", PropositionKind.EVIDENCE, "input"))
    _assert_runner_rejects(metadata, _policy(metadata), episode)


def test_pairwise_same_worker_identities_cannot_hide_behind_custom_inequality():
    left = _metadata(
        executor_id=DifferentStr("same-executor"),
        model_id=DifferentStr("same-model"),
        provider_id=DifferentStr("same-provider"),
        prompt_lineage=DifferentStr("same-prompt"),
        context_lineage=DifferentStr("same-context"),
        independence_basis_refs=("policy:left",),
    )
    right = _metadata(
        executor_id=DifferentStr("same-executor"),
        model_id=DifferentStr("same-model"),
        provider_id=DifferentStr("same-provider"),
        prompt_lineage=DifferentStr("same-prompt"),
        context_lineage=DifferentStr("same-context"),
        independence_basis_refs=("policy:right",),
    )
    assert left.demonstrably_independent_from(right) is False


def test_pairwise_shared_consumed_evidence_cannot_hide_behind_custom_inequality():
    left = _metadata(
        executor_id="executor-left",
        model_id="model-left",
        provider_id="provider-left",
        prompt_lineage="prompt-left",
        context_lineage="context-left",
        consumed_evidence_refs=(DifferentStr("shared-evidence"),),
        independence_basis_refs=("policy:left",),
    )
    right = _metadata(
        executor_id="executor-right",
        model_id="model-right",
        provider_id="provider-right",
        prompt_lineage="prompt-right",
        context_lineage="context-right",
        consumed_evidence_refs=(DifferentStr("shared-evidence"),),
        independence_basis_refs=("policy:right",),
    )
    assert left.demonstrably_independent_from(right) is False
