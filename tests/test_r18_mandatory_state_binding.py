import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


def _result(episode_id: str, attempt_id: str = "attempt-r18"):
    return ExecutionResult(
        execution_id=attempt_id,
        node_id="generator",
        emitted_propositions=(
            Proposition(
                proposition_id="h-r18",
                episode_id=episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="bound output",
                producer_execution_id=attempt_id,
            ),
        ),
    )


def _descriptor():
    return NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
    )


def test_admission_requires_explicit_preexecution_snapshot_digest():
    episode = Episode("r18-required")

    with pytest.raises(TypeError):
        admit_execution_result(
            episode,
            _descriptor(),
            _result(episode.episode_id),
            expected_execution_id="attempt-r18",
        )

    assert episode.snapshot().current_propositions == ()


def test_explicit_current_snapshot_binding_admits():
    episode = Episode("r18-current")
    digest = canonical_episode_snapshot_digest(episode.snapshot())

    receipt = admit_execution_result(
        episode,
        _descriptor(),
        _result(episode.episode_id),
        expected_execution_id="attempt-r18",
        expected_episode_snapshot_digest=digest,
    )

    assert receipt.canonical_episode_snapshot_digest == digest
    assert tuple(
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    ) == ("h-r18",)


def test_explicit_stale_snapshot_binding_fails_without_mutation():
    episode = Episode("r18-stale")
    stale_digest = canonical_episode_snapshot_digest(episode.snapshot())

    episode.add_proposition(
        Proposition(
            proposition_id="new-input",
            episode_id=episode.episode_id,
            kind=PropositionKind.OBSERVATION,
            content="state changed",
        )
    )

    with pytest.raises(AdmissionError, match="canonical episode state changed"):
        admit_execution_result(
            episode,
            _descriptor(),
            _result(episode.episode_id),
            expected_execution_id="attempt-r18",
            expected_episode_snapshot_digest=stale_digest,
        )

    assert tuple(
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    ) == ("new-input",)
