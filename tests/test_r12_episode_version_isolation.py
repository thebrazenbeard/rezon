from rezon.envelopes import TaskEnvelope
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


def _independence():
    metadata = IndependenceMetadata(
        executor_id="exec-r12",
        model_id="model-r12",
        provider_id="provider-r12",
        prompt_lineage="prompt-r12",
        context_lineage="context-r12",
        saw_other_answer=False,
        common_evidence_refs=(),
        consumed_evidence_refs=(),
        independence_basis_refs=("policy:r12-episode-version",),
    )
    policy = IndependenceVerificationPolicy((
        IndependenceVerificationEvidence(
            basis_ref="policy:r12-episode-version",
            executor_id=metadata.executor_id,
            model_id=metadata.model_id,
            provider_id=metadata.provider_id,
            prompt_lineage=metadata.prompt_lineage,
            context_lineage=metadata.context_lineage,
            verification_refs=("review:r12-episode-version",),
            saw_other_answer=False,
            common_evidence_refs=(),
            consumed_evidence_refs=(),
        ),
    ))
    return metadata, policy


class VersionProbe:
    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id="echo_hypothesis",
            emitted_propositions=(
                Proposition(
                    proposition_id=f"h-version-{episode_id}",
                    episode_id=episode_id,
                    kind=PropositionKind.HYPOTHESIS,
                    content=view.episode_version,
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _run_independent(episode: Episode):
    metadata, policy = _independence()
    envelope = TaskEnvelope(
        task_id="t-r12-version",
        literal_request="generate an independent hypothesis",
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=VersionProbe(),
        visibility=VisibilityPolicy(blind_kinds=(PropositionKind.HYPOTHESIS,)),
        independence=metadata,
        independence_policy=policy,
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )
    emitted = next(
        proposition
        for proposition in episode.snapshot().current_propositions
        if proposition.proposition_id == f"h-version-{episode.episode_id}"
    )
    return outcome, emitted


def test_strong_independence_executor_version_does_not_reveal_hidden_event_count():
    clean = Episode("opaque")
    hidden = Episode("opaque")
    hidden.add_proposition(Proposition(
        proposition_id="peer-hidden",
        episode_id=hidden.episode_id,
        kind=PropositionKind.HYPOTHESIS,
        content="peer answer",
        producer_execution_id="peer:exec:1",
    ))

    clean_outcome, clean_emitted = _run_independent(clean)
    hidden_outcome, hidden_emitted = _run_independent(hidden)

    assert clean_outcome.receipt.failures == ()
    assert hidden_outcome.receipt.failures == ()
    assert clean_outcome.trace.records[0].independence_demonstrated is True
    assert hidden_outcome.trace.records[0].independence_demonstrated is True

    # Hidden peer history must not change executor-visible version metadata.
    assert clean_emitted.content == hidden_emitted.content == "independent@0"

    # Audit trace retains exact canonical episode versions.
    assert clean_outcome.trace.records[0].episode_version == "opaque@0"
    assert hidden_outcome.trace.records[0].episode_version == "opaque@1"
    assert clean_outcome.trace.records[0].executor_episode_version == "independent@0"
    assert hidden_outcome.trace.records[0].executor_episode_version == "independent@0"


def test_non_independent_executor_retains_true_episode_version():
    episode = Episode("ordinary")
    episode.add_proposition(Proposition(
        proposition_id="observation",
        episode_id=episode.episode_id,
        kind=PropositionKind.OBSERVATION,
        content="visible",
    ))
    envelope = TaskEnvelope(
        task_id="t-r12-ordinary",
        literal_request="ordinary work",
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        executor=VersionProbe(),
        visibility=VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    emitted = next(
        proposition
        for proposition in episode.snapshot().current_propositions
        if proposition.proposition_id == "h-version-ordinary"
    )
    assert emitted.content == "ordinary@1"
    assert outcome.trace.records[0].episode_version == "ordinary@1"
    assert outcome.trace.records[0].executor_episode_version == "ordinary@1"


def test_strong_independence_preflight_trace_binds_sanitized_executor_version():
    class ShouldNotRun:
        def execute(self, view, episode_id):
            raise AssertionError("context_refs preflight must reject before execution")

    metadata, policy = _independence()
    episode = Episode("opaque-preflight")
    episode.add_proposition(Proposition(
        proposition_id="peer-hidden-preflight",
        episode_id=episode.episode_id,
        kind=PropositionKind.HYPOTHESIS,
        content="peer answer",
        producer_execution_id="peer:exec:preflight",
    ))
    envelope = TaskEnvelope(
        task_id="t-r12-preflight",
        literal_request="generate an independent hypothesis",
        context_refs=("peer-answer:H7",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        executor=ShouldNotRun(),
        visibility=VisibilityPolicy(blind_kinds=(PropositionKind.HYPOTHESIS,)),
        independence=metadata,
        independence_policy=policy,
    )

    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id=envelope.task_id,
        task_envelope=envelope,
    )

    assert outcome.receipt.failures == (FailureState.CONTRACT_VIOLATION,)
    assert outcome.trace.records[0].independence_demonstrated is False
    assert outcome.trace.records[0].episode_version == "opaque-preflight@1"
    assert outcome.trace.records[0].executor_episode_version == "independent@0"
