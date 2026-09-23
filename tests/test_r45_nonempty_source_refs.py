import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


def test_episode_rejects_empty_proposition_source_ref():
    episode = Episode("e1")
    proposition = Proposition(
        "p-empty-source",
        "e1",
        PropositionKind.OBSERVATION,
        "input",
        source_refs=("",),
        source_versions=("source@v1",),
    )

    with pytest.raises(EpisodeInvariantError, match="source refs"):
        episode.add_proposition(proposition)

    assert episode.snapshot().current_propositions == ()


def test_direct_admission_rejects_empty_proposition_source_ref():
    episode = Episode("e1")
    before = episode.snapshot()
    result = ExecutionResult(
        "attempt-r45",
        "generator",
        emitted_propositions=(
            Proposition(
                "h-empty-source",
                "e1",
                PropositionKind.HYPOTHESIS,
                "candidate",
                source_refs=("",),
                source_versions=("source@v1",),
                producer_execution_id="attempt-r45",
            ),
        ),
    )

    with pytest.raises(AdmissionError, match="source refs"):
        admit_execution_result(
            episode,
            NodeDescriptor(
                "generator",
                (PropositionKind.HYPOTHESIS,),
            ),
            result,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
                before
            ),
            expected_execution_id="attempt-r45",
        )

    assert episode.snapshot() == before


def test_episode_rejects_empty_relation_source_ref():
    episode = Episode("e1")
    episode.add_proposition(
        Proposition("o1", "e1", PropositionKind.OBSERVATION, "input")
    )
    before = episode.snapshot()
    relation = Hyperrelation(
        "r-empty-source",
        "e1",
        "supports",
        (Participant("o1", "subject"),),
        source_refs=("",),
        source_versions=("source@v1",),
    )

    with pytest.raises(EpisodeInvariantError, match="source refs"):
        episode.add_relation(relation)

    assert episode.snapshot() == before
