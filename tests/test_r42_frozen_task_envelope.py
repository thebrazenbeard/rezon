from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor, VerificationStatus
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class MutatingVerifier:
    node_id = "verifier-a"

    def __init__(self, mutation):
        self.mutation = mutation
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        self.mutation(view)
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "ta",
                    episode_id,
                    PropositionKind.TEST_RESULT,
                    "a passed",
                    source_refs=("o1",),
                    producer_execution_id=view.execution_id,
                ),
            ),
            verification_status=VerificationStatus.PASSED,
            verification_target_ids=("o1",),
        )


class ObservingVerifier:
    node_id = "verifier-b"

    def __init__(self):
        self.calls = 0
        self.seen = None

    def execute(self, view, episode_id):
        self.calls += 1
        self.seen = (
            view.task_specification.literal_request,
            view.task_envelope.literal_request,
        )
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "tb",
                    episode_id,
                    PropositionKind.TEST_RESULT,
                    "b passed",
                    source_refs=("o1",),
                    producer_execution_id=view.execution_id,
                ),
            ),
            verification_status=VerificationStatus.PASSED,
            verification_target_ids=("o1",),
        )


def _node(node_id, executor):
    return RunnerNode(
        NodeDescriptor(
            node_id,
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
            verification_target_ids=("o1",),
        ),
        executor,
        VisibilityPolicy(),
    )


def _run(envelope, mutation):
    first = MutatingVerifier(mutation)
    second = ObservingVerifier()
    episode = Episode("e1")
    episode.add_proposition(
        Proposition("o1", "e1", PropositionKind.OBSERVATION, "input")
    )
    initial_digest = envelope.digest

    outcome = EpisodeRunner(
        (
            _node("verifier-a", first),
            _node("verifier-b", second),
        ),
        budget_limit=2,
    ).run(
        episode,
        task_id="t-r42",
        task_envelope=envelope,
    )
    return first, second, outcome, initial_digest


def test_executor_view_gets_isolated_task_envelope_copy():
    envelope = TaskEnvelope("t-r42", "original-request")

    first, second, outcome, initial_digest = _run(
        envelope,
        lambda view: object.__setattr__(
            view.task_envelope,
            "literal_request",
            "tampered-request",
        ),
    )

    assert outcome.receipt.failures == ()
    assert first.calls == 1
    assert second.calls == 1
    assert second.seen == ("original-request", "original-request")
    assert envelope.literal_request == "original-request"
    assert outcome.receipt.task_envelope_digest == initial_digest


def test_external_original_task_envelope_mutation_cannot_change_current_run():
    envelope = TaskEnvelope("t-r42", "original-request")

    first, second, outcome, initial_digest = _run(
        envelope,
        lambda _view: object.__setattr__(
            envelope,
            "literal_request",
            "external-tamper",
        ),
    )

    assert outcome.receipt.failures == ()
    assert first.calls == 1
    assert second.calls == 1
    assert second.seen == ("original-request", "original-request")
    assert envelope.literal_request == "external-tamper"
    assert outcome.receipt.task_envelope_digest == initial_digest
