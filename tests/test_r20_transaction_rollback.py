from threading import Event, Thread

import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


def _descriptor():
    return NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
        permitted_relation_types=("supports",),
    )


def _result(episode_id: str):
    return ExecutionResult(
        execution_id="attempt-r20",
        node_id="generator",
        emitted_propositions=(
            Proposition(
                proposition_id="h-r20",
                episode_id=episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="candidate",
                producer_execution_id="attempt-r20",
            ),
        ),
        emitted_relations=(
            Hyperrelation(
                relation_id="rel-r20",
                episode_id=episode_id,
                relation_type="supports",
                participants=(
                    Participant("h-r20", "source"),
                    Participant("h-r20", "target"),
                ),
                producer_execution_id="attempt-r20",
            ),
        ),
    )


def test_failed_multiobject_admission_rolls_back_exact_snapshot(monkeypatch):
    episode = Episode("r20-rollback")
    before = episode.snapshot()
    digest = canonical_episode_snapshot_digest(before)

    original_add_relation = episode.add_relation

    def fail_relation(relation):
        raise EpisodeInvariantError("synthetic commit-stage failure")

    monkeypatch.setattr(episode, "add_relation", fail_relation)

    with pytest.raises(AdmissionError, match="synthetic commit-stage failure"):
        admit_execution_result(
            episode,
            _descriptor(),
            _result(episode.episode_id),
            expected_episode_snapshot_digest=digest,
            expected_execution_id="attempt-r20",
        )

    assert episode.snapshot() == before

    monkeypatch.setattr(episode, "add_relation", original_add_relation)


def test_transaction_lock_releases_after_rollback(monkeypatch):
    episode = Episode("r20-lock-release")
    digest = canonical_episode_snapshot_digest(episode.snapshot())

    original_add_relation = episode.add_relation

    def fail_relation(relation):
        raise EpisodeInvariantError("synthetic commit-stage failure")

    monkeypatch.setattr(episode, "add_relation", fail_relation)

    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            _descriptor(),
            _result(episode.episode_id),
            expected_episode_snapshot_digest=digest,
            expected_execution_id="attempt-r20",
        )

    monkeypatch.setattr(episode, "add_relation", original_add_relation)

    completed = Event()

    def mutate_after_failure():
        episode.add_proposition(
            Proposition(
                proposition_id="after-rollback",
                episode_id=episode.episode_id,
                kind=PropositionKind.OBSERVATION,
                content="lock released",
            )
        )
        completed.set()

    thread = Thread(target=mutate_after_failure)
    thread.start()
    thread.join(timeout=2)

    assert completed.is_set()
    assert tuple(
        proposition.proposition_id
        for proposition in episode.snapshot().current_propositions
    ) == ("after-rollback",)
