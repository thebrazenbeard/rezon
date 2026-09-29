import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


def _result():
    return ExecutionResult(
        execution_id="",
        node_id="generator",
        emitted_propositions=(
            Proposition(
                "h-empty-execution",
                "e1",
                PropositionKind.HYPOTHESIS,
                "must not acquire canonical producer identity",
                producer_execution_id="",
            ),
        ),
    )


def _descriptor():
    return NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
    )


def test_direct_admission_rejects_empty_result_and_expected_execution_identity():
    episode = Episode("e1")
    before = episode.snapshot()

    with pytest.raises(AdmissionError, match="execution result identity"):
        admit_execution_result(
            episode,
            _descriptor(),
            _result(),
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
                before
            ),
            expected_execution_id="",
        )

    assert episode.snapshot() == before


def test_direct_admission_rejects_empty_result_identity_when_expected_is_omitted():
    episode = Episode("e1")
    before = episode.snapshot()

    with pytest.raises(AdmissionError, match="execution result identity"):
        admit_execution_result(
            episode,
            _descriptor(),
            _result(),
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(
                before
            ),
        )

    assert episode.snapshot() == before
