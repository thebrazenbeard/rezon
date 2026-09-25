import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


class EvilStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


def _episode():
    return Episode("r24-identities")


def _descriptor():
    return NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
        permitted_relation_types=("supports",),
    )


def _prop(episode_id="r24-identities", producer="issued"):
    return Proposition(
        proposition_id="h-r24",
        episode_id=episode_id,
        kind=PropositionKind.HYPOTHESIS,
        content="payload",
        producer_execution_id=producer,
    )


def _admit(result, expected="issued", descriptor=None):
    episode = _episode()
    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            descriptor or _descriptor(),
            result,
            expected_execution_id=expected,
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(episode.snapshot()),
        )
    assert episode.snapshot().current_propositions == ()
    assert episode.snapshot().current_relations == ()


def test_result_execution_id_cannot_use_custom_equality():
    _admit(ExecutionResult(EvilStr("forged"), "generator", (_prop(),)))


def test_result_node_id_cannot_use_custom_equality():
    _admit(ExecutionResult("issued", EvilStr("forged-node"), (_prop(),)))


def test_descriptor_node_id_must_be_exact_string():
    _admit(
        ExecutionResult("issued", "generator", (_prop(),)),
        descriptor=NodeDescriptor(EvilStr("generator"), (PropositionKind.HYPOTHESIS,)),
    )


def test_proposition_episode_id_cannot_use_custom_equality():
    _admit(ExecutionResult("issued", "generator", (_prop(EvilStr("foreign")),)))


def test_proposition_producer_id_cannot_use_custom_equality():
    _admit(ExecutionResult("issued", "generator", (_prop(producer=EvilStr("forged")),)))


def test_relation_identity_bindings_cannot_use_custom_equality():
    episode = _episode()
    episode.add_proposition(
        Proposition("seed", episode.episode_id, PropositionKind.OBSERVATION, "seed")
    )
    relation = Hyperrelation(
        relation_id="rel-r24",
        episode_id=EvilStr("foreign"),
        relation_type="supports",
        participants=(Participant("seed", "supporter"),),
        producer_execution_id=EvilStr("forged"),
    )
    result = ExecutionResult("issued", "generator", emitted_relations=(relation,))
    before = episode.snapshot()
    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            _descriptor(),
            result,
            expected_execution_id="issued",
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(before),
        )
    assert episode.snapshot() == before
