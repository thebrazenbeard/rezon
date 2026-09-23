import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor


class AlwaysEqual:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class EvilStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


def _exercise(binding):
    episode = Episode("r22-binding")
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
        execution_id="attempt-r22",
        node_id="generator",
        emitted_propositions=(
            Proposition(
                proposition_id="stale-output",
                episode_id=episode.episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="stale",
                producer_execution_id="attempt-r22",
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
            expected_episode_snapshot_digest=binding,
            expected_execution_id="attempt-r22",
        )

    assert episode.snapshot() == before


def test_nonstring_custom_equality_cannot_impersonate_snapshot_digest():
    _exercise(AlwaysEqual())


def test_str_subclass_custom_equality_cannot_impersonate_snapshot_digest():
    _exercise(EvilStr("forged"))
