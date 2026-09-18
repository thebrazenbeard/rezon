from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.receipts import (
    IndependenceMetadata,
    IndependenceVerificationEvidence,
    IndependenceVerificationPolicy,
)
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class PassingVerifier:
    def execute(self, view, episode_id):
        result = Proposition(
            proposition_id="verification-result",
            episode_id=episode_id,
            kind=PropositionKind.TEST_RESULT,
            content="verified",
            source_refs=("o1",),
            producer_execution_id=view.execution_id,
        )
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="verifier",
            emitted_propositions=(result,),
            verification_status=VerificationStatus.PASSED,
            verification_target_ids=("o1",),
        )


class ExecutionIdProbe:
    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id="h-execution-id",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content=view.execution_id,
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _independence():
    metadata = IndependenceMetadata(
        executor_id="exec-r12-ordinal",
        model_id="model-r12-ordinal",
        provider_id="provider-r12-ordinal",
        prompt_lineage="prompt-r12-ordinal",
        context_lineage="context-r12-ordinal",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r12-execution-id",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r12-execution-id",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r12-execution-id",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    return metadata, policy


def _run(with_prior_verifier: bool):
    episode = Episode("opaque-ordinal")
    episode.add_proposition(Proposition(
        proposition_id="o1",
        episode_id=episode.episode_id,
        kind=PropositionKind.OBSERVATION,
        content="shared task observation",
    ))
    metadata, policy = _independence()
    generator = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=ExecutionIdProbe(),
        visibility=VisibilityPolicy(allow_kinds=(PropositionKind.OBSERVATION,)),
        independence=metadata,
        independence_policy=policy,
    )
    nodes = (generator,)
    if with_prior_verifier:
        verifier = RunnerNode(
            descriptor=NodeDescriptor(
                "verifier",
                (PropositionKind.TEST_RESULT,),
                mandatory_verification=True,
                verification_target_ids=("o1",),
            ),
            executor=PassingVerifier(),
            visibility=VisibilityPolicy(),
        )
        nodes = (verifier, generator)

    envelope = TaskEnvelope(
        task_id="t-r12-ordinal",
        literal_request="generate an independent hypothesis",
    )
    outcome = EpisodeRunner(nodes, budget_limit=2).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )
    emitted = next(
        proposition
        for proposition in episode.snapshot().current_propositions
        if proposition.proposition_id == "h-execution-id"
    )
    return outcome, emitted.content


def test_strong_independence_execution_id_does_not_reveal_prior_execution_count():
    clean_outcome, clean_execution_id = _run(False)
    prior_outcome, prior_execution_id = _run(True)

    assert clean_outcome.receipt.failures == ()
    assert prior_outcome.receipt.failures == ()
    assert clean_execution_id == prior_execution_id
    assert "t-r12-ordinal" not in clean_execution_id
