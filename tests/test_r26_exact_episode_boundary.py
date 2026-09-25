import pytest

from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind


class EvilStr(str):
    def __new__(cls, value, target=None):
        obj = str.__new__(cls, value)
        obj.target = value if target is None else target
        return obj

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash(self.target)


class EvilProposition(Proposition):
    pass


class EvilRelation(Hyperrelation):
    pass


def test_episode_id_constructor_requires_exact_str():
    with pytest.raises(EpisodeInvariantError):
        Episode(EvilStr("canon"))


def test_episode_id_is_immutable_after_construction():
    episode = Episode("canon")
    with pytest.raises(EpisodeInvariantError):
        episode.episode_id = "rewritten"
    assert episode.episode_id == "canon"


def test_direct_proposition_foreign_episode_custom_equality_is_rejected():
    episode = Episode("canon")
    proposition = Proposition(
        "p1",
        EvilStr("foreign", "canon"),
        PropositionKind.OBSERVATION,
        "payload",
    )
    with pytest.raises(EpisodeInvariantError):
        episode.add_proposition(proposition)
    assert episode.snapshot().current_propositions == ()


def test_direct_proposition_id_custom_equality_is_rejected():
    episode = Episode("canon")
    proposition = Proposition(
        EvilStr("forged-id", "p1"),
        "canon",
        PropositionKind.OBSERVATION,
        "payload",
    )
    with pytest.raises(EpisodeInvariantError):
        episode.add_proposition(proposition)
    assert episode.snapshot().current_propositions == ()


def test_direct_proposition_subclass_is_rejected():
    episode = Episode("canon")
    proposition = EvilProposition(
        "p1",
        "canon",
        PropositionKind.OBSERVATION,
        "payload",
    )
    with pytest.raises(EpisodeInvariantError):
        episode.add_proposition(proposition)
    assert episode.snapshot().current_propositions == ()


def test_forged_retract_id_cannot_remove_canonical_proposition():
    episode = Episode("canon")
    episode.add_proposition(
        Proposition("victim", "canon", PropositionKind.OBSERVATION, "payload")
    )
    before = episode.snapshot()
    with pytest.raises(EpisodeInvariantError):
        episode.retract_proposition(EvilStr("forged", "victim"), "hostile")
    assert episode.snapshot() == before


def test_direct_relation_forged_participant_ref_is_rejected():
    episode = Episode("canon")
    episode.add_proposition(
        Proposition("seed", "canon", PropositionKind.OBSERVATION, "seed")
    )
    relation = Hyperrelation(
        "r1",
        "canon",
        "supports",
        (Participant(EvilStr("forged-ref", "seed"), "supporter"),),
    )
    before = episode.snapshot()
    with pytest.raises(EpisodeInvariantError):
        episode.add_relation(relation)
    assert episode.snapshot() == before


def test_direct_relation_type_custom_string_is_rejected():
    episode = Episode("canon")
    episode.add_proposition(
        Proposition("seed", "canon", PropositionKind.OBSERVATION, "seed")
    )
    relation = Hyperrelation(
        "r1",
        "canon",
        EvilStr("forged-type", "supports"),
        (Participant("seed", "supporter"),),
    )
    before = episode.snapshot()
    with pytest.raises(EpisodeInvariantError):
        episode.add_relation(relation)
    assert episode.snapshot() == before


def test_direct_relation_subclass_is_rejected():
    episode = Episode("canon")
    episode.add_proposition(
        Proposition("seed", "canon", PropositionKind.OBSERVATION, "seed")
    )
    relation = EvilRelation(
        "r1",
        "canon",
        "supports",
        (Participant("seed", "supporter"),),
    )
    before = episode.snapshot()
    with pytest.raises(EpisodeInvariantError):
        episode.add_relation(relation)
    assert episode.snapshot() == before
