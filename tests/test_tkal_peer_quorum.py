"""Reject sham peer participation in a four-worker Rezon hearing."""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from rezon.collective import CollectiveConflict, CollectiveStore
from rezon.tkal_network import TkalVirtualNetwork

ROSTER=("vera-lappy", "vera-vn1", "vera-vn2", "malaphor")
LENSES={"purist_logic":"vera-vn1", "pragmatism":"vera-vn2", "bridge":"malaphor"}

def test_self_targeted_reviews_do_not_open_four_worker_hearing():
    with TemporaryDirectory() as root:
        store=CollectiveStore(Path(root)/"shared.sqlite")
        episode=store.create("One shared question",ROSTER)
        for agent in ROSTER:
            store.submit_answer(episode,agent,"Initial claim "+agent)
        for reviewer in ROSTER[1:]:
            store.submit_review(episode,reviewer,"My own self-check",
                                ("answer:"+reviewer,))
        with pytest.raises(CollectiveConflict, match="peer"):
            TkalVirtualNetwork(store).open(
                episode,expected_digest=store.snapshot(episode).digest,
                proposer="vera-lappy",lenses=LENSES,
                hypothesis="Unverified",falsifier="New evidence refutes it")

def test_cross_targeted_reviews_open_four_worker_hearing():
    with TemporaryDirectory() as root:
        store=CollectiveStore(Path(root)/"shared.sqlite")
        episode=store.create("One shared question",ROSTER)
        for agent in ROSTER:
            store.submit_answer(episode,agent,"Initial claim "+agent)
        for reviewer in ROSTER[1:]:
            store.submit_review(episode,reviewer,"Objection targeting a peer",
                                ("answer:vera-lappy",))
        opened=TkalVirtualNetwork(store).open(
            episode,expected_digest=store.snapshot(episode).digest,
            proposer="vera-lappy",lenses=LENSES,
            hypothesis="Still open",falsifier="Peer objection refutes it")
        assert opened.proposer=="vera-lappy"
