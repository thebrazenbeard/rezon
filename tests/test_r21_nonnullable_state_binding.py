import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor


def test_explicit_none_snapshot_binding_fails_closed_without_mutation():
    episode = Episode("r21-none-binding")
    episode.add_proposition(
        Proposition(
            proposition_id="new-input",
            episode_id=episode.episode_id,
            kind=PropositionKind.OBSERVATION,
            content="state changed",
        )
    )
    before = episode.snapshot()

    result = ExecutionResult(
        execution_id="attempt-r21",
        node_id="generator",
        emitted_propositions=(
            Proposition(
                proposition_id="stale-output",
                episode_id=episode.episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="stale",
                producer_execution_id="attempt-r21",
            ),
        ),
    )

    with pytest.raises(AdmissionError, match="canonical episode state changed"):
        admit_execution_result(
            episode,
            NodeDescriptor(
                "generator",
                (PropositionKind.HYPOTHESIS,),
            ),
            result,
            expected_episode_snapshot_digest=None,
            expected_execution_id="attempt-r21",
        )

    assert episode.snapshot() == before
