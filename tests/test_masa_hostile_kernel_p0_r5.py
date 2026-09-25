import pytest

from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.executors import EchoHypothesisExecutor
from rezon.hostile import HostileViolation, audit_hostile_case
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import (
    EffectState,
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
    ResultReceipt,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _p(pid, kind, content=None, source_refs=()):
    return Proposition(pid, "e1", kind, content or pid, source_refs=tuple(source_refs))


def _independence():
    metadata = IndependenceMetadata(
        executor_id="executor-b",
        model_id="model-b",
        provider_id="provider-b",
        prompt_lineage="prompt-b",
        context_lineage="context-b",
        saw_other_answer=False,
        common_evidence_refs=(),
        independence_basis_refs=("policy:independent-b",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:independent-b",
            executor_id="executor-b",
            model_id="model-b",
            provider_id="provider-b",
            prompt_lineage="prompt-b",
            context_lineage="context-b",
            verification_refs=("review:independence-b",),
        ),
    ))
    return metadata, policy


def test_duplicate_node_ids_cannot_substitute_non_verifier_for_mandatory_verifier():
    class BypassExecutor:
        def execute(self, view, episode_id):
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="verifier",
                emitted_propositions=(
                    Proposition(
                        "bypass-hypothesis",
                        episode_id,
                        PropositionKind.HYPOTHESIS,
                        "verification never actually ran",
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("target", PropositionKind.CLAIM, "claim under verification"))
    mandatory = RunnerNode(
        descriptor=NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("target",),
        ),
        executor=None,
        visibility=VisibilityPolicy(),
    )
    shadow = RunnerNode(
        descriptor=NodeDescriptor("verifier", (PropositionKind.HYPOTHESIS,)),
        executor=BypassExecutor(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((mandatory, shadow), budget_limit=2).run(ep, task_id="t-dup")

    assert outcome.receipt.failures
    assert "bypass-hypothesis" not in {
        p.proposition_id for p in ep.snapshot().current_propositions
    }


def test_email_like_source_ref_is_not_promoted_to_source_version():
    ep = Episode("e1")
    ep.add_proposition(
        _p(
            "o1",
            PropositionKind.OBSERVATION,
            "input",
            source_refs=("analyst@example.com",),
        )
    )
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        executor=EchoHypothesisExecutor(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-source-version")

    assert "analyst@example.com" not in outcome.receipt.source_versions


def test_result_receipt_rejects_claim_disposition_complete_with_unresolved_claim():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t1",
            episode_version="e1@1",
            unresolved=("claim_disposition:c1",),
            claim_disposition_complete=True,
            effect_state=EffectState.PLAN,
        )


def test_result_receipt_cannot_self_assert_accepted_claim_without_disposition_evidence():
    with pytest.raises(ValueError):
        ResultReceipt(
            task_id="t1",
            episode_version="e1@1",
            accepted_claim_ids=("c1",),
            claim_disposition_complete=True,
            effect_state=EffectState.PLAN,
        )


def test_independence_required_worker_cannot_see_peer_answer_encoded_in_relation():
    class RelationReader:
        def execute(self, view, episode_id):
            leaked = next(r for r in view.relations if r.relation_id == "peer-answer:H1")
            return ExecutionResult(
                execution_id=view.execution_id,
                node_id="independent-b",
                emitted_propositions=(
                    Proposition(
                        "derived-from-peer-relation",
                        episode_id,
                        PropositionKind.CLAIM,
                        f"copied {leaked.relation_id}",
                        source_refs=(leaked.relation_id,),
                        producer_execution_id=view.execution_id,
                    ),
                ),
            )

    ep = Episode("e1")
    ep.add_proposition(_p("input-a", PropositionKind.OBSERVATION, "premise A"))
    ep.add_proposition(_p("input-b", PropositionKind.OBSERVATION, "premise B"))
    ep.add_relation(
        Hyperrelation(
            relation_id="peer-answer:H1",
            episode_id="e1",
            relation_type="peer_conclusion",
            participants=(
                Participant("input-a", "premise"),
                Participant("input-b", "premise"),
            ),
            producer_execution_id="peer:exec:1",
        )
    )
    metadata, policy = _independence()
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "independent-b",
            (PropositionKind.CLAIM,),
            independence_required=True,
        ),
        executor=RelationReader(),
        visibility=VisibilityPolicy(),
        independence=metadata,
        independence_policy=policy,
    )

    EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-relation-blind")

    assert "derived-from-peer-relation" not in {
        p.proposition_id for p in ep.snapshot().current_propositions
    }


def test_hostile_consensus_audit_fails_closed_when_independence_metadata_missing():
    violations = audit_hostile_case({
        "consensus_counted_as_evidence": True,
        "worker_independence": None,
    })

    assert HostileViolation.CORRELATED_CONSENSUS_LAUNDERING in violations
