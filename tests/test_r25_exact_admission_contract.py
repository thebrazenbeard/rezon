import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


class ForgedStr(str):
    _targets = {
        "forged-source": "allowed-source",
        "forged-version": "allowed-version",
        "forged-ref": "seed",
        "forged-kind": PropositionKind.HYPOTHESIS,
        "forged-type": "supports",
        "wrapper": "forged-source",
    }

    def __new__(cls, value, target=None):
        obj = str.__new__(cls, value)
        obj.target = cls._targets[value] if target is None else target
        return obj

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash(self.target)

    def lower(self):
        return str(self.target).lower()


def _admit(prop=None, relation=None, **kwargs):
    episode = Episode("r25-contract")
    if relation is not None:
        episode.add_proposition(Proposition("seed", episode.episode_id, PropositionKind.OBSERVATION, "seed"))
    result = ExecutionResult(
        "issued",
        "generator",
        emitted_propositions=(prop,) if prop is not None else (),
        emitted_relations=(relation,) if relation is not None else (),
    )
    before = episode.snapshot()
    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            NodeDescriptor("generator", (PropositionKind.HYPOTHESIS,), permitted_relation_types=("supports",)),
            result,
            expected_execution_id="issued",
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(before),
            **kwargs,
        )
    assert episode.snapshot() == before


def _prop(**changes):
    values = dict(
        proposition_id="p-r25",
        episode_id="r25-contract",
        kind=PropositionKind.HYPOTHESIS,
        content="payload",
        source_refs=(),
        producer_execution_id="issued",
        source_versions=(),
    )
    values.update(changes)
    return Proposition(**values)


def test_forged_source_ref_cannot_match_governed_ref():
    _admit(prop=_prop(source_refs=(ForgedStr("forged-source", "allowed-source"),)), allowed_source_refs=("allowed-source",))


def test_forged_source_version_cannot_match_governed_version():
    _admit(prop=_prop(source_versions=(ForgedStr("forged-version", "allowed-version"),)), allowed_source_versions=("allowed-version",))


def test_forged_participant_ref_cannot_match_active_object():
    relation = Hyperrelation(
        "rel-r25",
        "r25-contract",
        "supports",
        (Participant(ForgedStr("forged-ref", "seed"), "supporter"),),
        producer_execution_id="issued",
    )
    _admit(relation=relation)


def test_forged_proposition_kind_cannot_match_permitted_kind():
    _admit(prop=_prop(kind=ForgedStr("forged-kind", PropositionKind.HYPOTHESIS)))


def test_forged_relation_type_cannot_lower_to_permitted_type():
    relation = Hyperrelation(
        "rel-r25",
        "r25-contract",
        ForgedStr("forged-type", "supports"),
        (Participant("seed", "supporter"),),
        producer_execution_id="issued",
    )
    _admit(relation=relation)


def test_forged_governed_ref_cannot_authorize_exact_output_ref():
    _admit(prop=_prop(source_refs=("forged-source",)), allowed_source_refs=(ForgedStr("wrapper", "forged-source"),))



class FalseFailureTuple(tuple):
    def __bool__(self):
        return False


def test_falsey_failure_tuple_cannot_hide_reported_failure():
    episode = Episode("r25-contract")
    result = ExecutionResult(
        "issued",
        "generator",
        emitted_propositions=(_prop(),),
        failures=FalseFailureTuple(("contract_violation",)),
    )
    before = episode.snapshot()
    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            NodeDescriptor(
                "generator",
                (PropositionKind.HYPOTHESIS,),
                permitted_relation_types=("supports",),
            ),
            result,
            expected_execution_id="issued",
            expected_episode_snapshot_digest=canonical_episode_snapshot_digest(before),
        )
    assert episode.snapshot() == before


def test_forged_allowed_source_version_cannot_authorize_output_version():
    _admit(
        prop=_prop(source_versions=("forged-version",)),
        allowed_source_versions=(ForgedStr("wrapper-version", "forged-version"),),
    )


def test_forged_allowed_source_binding_cannot_authorize_output_binding():
    _admit(
        prop=_prop(
            source_refs=("source-a",),
            source_versions=("version-a",),
        ),
        allowed_source_bindings=(
            (
                ForgedStr("wrapper-ref", "source-a"),
                ForgedStr("wrapper-version-a", "version-a"),
            ),
        ),
    )
