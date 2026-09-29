import pytest

from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, execution_result_contract_is_exact


def test_episode_rejects_empty_proposition_producer_execution_id() -> None:
    episode = Episode("e1")
    proposition = Proposition(
        "p-r46-empty-producer",
        "e1",
        PropositionKind.OBSERVATION,
        "input",
        producer_execution_id="",
    )

    with pytest.raises(EpisodeInvariantError, match="producer identity"):
        episode.add_proposition(proposition)

    assert episode.snapshot().current_propositions == ()


def test_episode_rejects_empty_relation_producer_execution_id() -> None:
    episode = Episode("e1")
    episode.add_proposition(
        Proposition("o1", "e1", PropositionKind.OBSERVATION, "input")
    )
    before = episode.snapshot()
    relation = Hyperrelation(
        "r-r46-empty-producer",
        "e1",
        "supports",
        (Participant("o1", "subject"),),
        producer_execution_id="",
    )

    with pytest.raises(EpisodeInvariantError, match="producer identity"):
        episode.add_relation(relation)

    assert episode.snapshot() == before


def test_exact_execution_result_rejects_empty_nested_producer_identity() -> None:
    result = ExecutionResult(
        "attempt-r46",
        "generator",
        emitted_propositions=(
            Proposition(
                "p-r46-output",
                "e1",
                PropositionKind.HYPOTHESIS,
                "candidate",
                producer_execution_id="",
            ),
        ),
    )

    assert execution_result_contract_is_exact(result) is False
