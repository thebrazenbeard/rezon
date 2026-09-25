import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


def _result(episode_id: str, attempt_id: str):
    return ExecutionResult(
        execution_id=attempt_id,
        node_id="generator",
        emitted_propositions=(
            Proposition(
                proposition_id="h-admission",
                episode_id=episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="same durable output",
                producer_execution_id=attempt_id,
            ),
        ),
    )


def test_direct_caller_cannot_choose_canonical_producer_identity():
    episode = Episode("admission-r16-forge")
    descriptor = NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
    )
    result = _result(episode.episode_id, "attempt-r16")

    with pytest.raises(TypeError):
        admit_execution_result(
            episode,
            descriptor,
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
                episode.snapshot()
            ),
            expected_execution_id="attempt-r16",
            canonical_producer_execution_id="caller-chosen-producer",
        )

    assert episode.snapshot().current_propositions == ()


def test_admission_returns_and_persists_derived_canonical_producer_identity():
    descriptor = NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
    )

    def admit_once(attempt_id: str):
        episode = Episode("admission-r16-derived")
        receipt = admit_execution_result(
            episode,
            descriptor,
            _result(episode.episode_id, attempt_id),
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
                episode.snapshot()
            ),
            expected_execution_id=attempt_id,
        )
        proposition = episode.snapshot().current_propositions[0]
        return receipt, proposition.producer_execution_id

    receipt_a, producer_a = admit_once("attempt-a")
    receipt_b, producer_b = admit_once("attempt-b")

    assert receipt_a.canonical_producer_execution_id == producer_a
    assert receipt_b.canonical_producer_execution_id == producer_b
    assert producer_a == producer_b
    assert producer_a not in {"attempt-a", "attempt-b"}
    assert producer_a.startswith("canonical:exec:generator:")


def test_admission_rejects_stale_preexecution_snapshot_binding():
    episode = Episode("admission-r16-stale")
    descriptor = NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
    )
    captured_digest = canonical_episode_snapshot_digest(episode.snapshot())

    episode.add_proposition(
        Proposition(
            proposition_id="new-input",
            episode_id=episode.episode_id,
            kind=PropositionKind.OBSERVATION,
            content="state changed after view capture",
        )
    )

    with pytest.raises(AdmissionError, match="canonical episode state changed"):
        admit_execution_result(
            episode,
            descriptor,
            _result(episode.episode_id, "attempt-stale"),
            expected_execution_id="attempt-stale",
            expected_episode_snapshot_digest=captured_digest,
        )

    assert tuple(
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    ) == ("new-input",)
