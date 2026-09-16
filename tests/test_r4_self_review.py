import pytest

from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.receipts import (
    EffectState,
    FailureState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
    ResultReceipt,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _p(pid: str, kind: PropositionKind, *, source_refs=()):
    return Proposition(pid, "e1", kind, pid, source_refs=tuple(source_refs))


def _independence_metadata() -> IndependenceMetadata:
    return IndependenceMetadata(
        executor_id="independent-worker",
        model_id="model-a",
        provider_id="provider-a",
        prompt_lineage="prompt-fresh",
        context_lineage="context-blind",
        saw_other_answer=False,
        independence_basis_refs=("policy:independent-generation",),
    )


def _independence_policy(metadata: IndependenceMetadata) -> IndependenceVerificationPolicy:
    return IndependenceVerificationPolicy((IndependenceVerificationEvidence(
        basis_ref="policy:independent-generation",
        executor_id=metadata.executor_id,
        model_id=metadata.model_id,
        provider_id=metadata.provider_id,
        prompt_lineage=metadata.prompt_lineage,
        context_lineage=metadata.context_lineage,
        verification_refs=("receipt:independence-verified",),
    ),))


def test_new_derived_proposition_cannot_depend_on_retracted_canonical_source():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.retract_proposition("o1", "superseded")

    with pytest.raises(EpisodeInvariantError):
        ep.add_proposition(_p("h1", PropositionKind.HYPOTHESIS, source_refs=("o1",)))


def test_mandatory_verifier_cannot_choose_a_different_visible_target():
    class TargetSwitchingVerifier:
        node_id = "verifier"

        def execute(self, view, episode_id):
            result = Proposition(
                "t1",
                episode_id,
                PropositionKind.TEST_RESULT,
                "verified o2 instead",
                source_refs=("o2",),
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id=self.node_id,
                emitted_propositions=(result,),
                verification_status=VerificationStatus.PASSED,
                verification_target_ids=("o2",),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("o2", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("o1",),
        ),
        executor=TargetSwitchingVerifier(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-target-switch")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert any(item.startswith("verification:") for item in outcome.receipt.unresolved)
    assert "t1" not in {p.proposition_id for p in ep.snapshot().current_propositions}


@pytest.mark.parametrize(
    "effect_state",
    (EffectState.INSTALLED, EffectState.ACTIVE, EffectState.EFFECT_OBSERVED),
)
def test_result_receipt_cannot_self_certify_promotional_effect_state(effect_state):
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t-effect",
            episode_version="e1@1",
            effect_state=effect_state,
        )


@pytest.mark.parametrize("answer_kind", (PropositionKind.CLAIM, PropositionKind.DECISION))
def test_independence_required_worker_is_blind_to_visible_answer_bearing_propositions(answer_kind):
    class ShouldNotRun:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            raise AssertionError("independence-required worker saw a peer answer")

    metadata = _independence_metadata()
    ep = Episode("e1")
    ep.add_proposition(_p("peer-answer", answer_kind))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=ShouldNotRun(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=_independence_policy(metadata),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id=f"t-{answer_kind.value}")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert any(item.startswith("independence:") for item in outcome.receipt.unresolved)
