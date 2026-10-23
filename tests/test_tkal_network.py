"""Four-agent virtual hearing protocol and authenticated loopback integration."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from rezon.collective import CollectiveConflict, CollectiveStore
from rezon.collective_http import make_server
from rezon.tkal_network import TkalVirtualNetwork

AGENTS = ("lappy", "vn1", "vn2", "malaphor")
LENSES = {"purist_logic": "vn1", "pragmatism": "vn2", "bridge": "malaphor"}
TOKENS = {agent: "token-for-"+agent+"-abcdef0123456" for agent in AGENTS}
ADMIN = "controller-admin-token-abcdef0123456"


class TkalNetworkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = CollectiveStore(Path(self.tmp.name)/"collective.sqlite")
        self.network = TkalVirtualNetwork(self.store)
        self.episode = self.store.create("One exact falsifiable topic", AGENTS)

    def seal_answers(self):
        for agent in AGENTS:
            self.store.submit_answer(self.episode, agent, "claim from "+agent)

    def seal_reviews(self):
        self.seal_answers()
        for agent in AGENTS:
            target = next(a for a in AGENTS if a != agent)
            self.store.submit_review(self.episode, agent, "peer objection from "+agent,
                                     ("answer:"+target,))

    def open(self):
        return self.network.open(
            self.episode, expected_digest=self.store.snapshot(self.episode).digest,
            proposer="lappy", lenses=LENSES,
            hypothesis="Correction survives cold restart",
            falsifier="Held-out controls show no causal improvement",
        )

    def test_gate_needs_four_answers_and_three_actual_reviews(self):
        with self.assertRaises(CollectiveConflict):
            self.open()
        self.seal_answers()
        with self.assertRaises(CollectiveConflict):
            self.open()
        for agent in ("lappy","vn1","vn2"):
            target = "malaphor" if agent != "malaphor" else "lappy"
            self.store.submit_review(self.episode, agent, "review "+agent,
                                     ("answer:"+target,))
        with self.assertRaises(CollectiveConflict):
            self.open()
        self.store.submit_review(self.episode, "malaphor", "review malaphor",
                                 ("answer:lappy",))
        self.assertEqual(self.open().proposer, "lappy")

    def test_role_spoof_and_concurrent_challenge_blocked(self):
        self.seal_reviews()
        self.open()
        with self.assertRaises(ValueError):
            self.network.challenge(self.episode, reviewer="lappy", challenge_id="c0",
                                   target="vn1", question="why")
        self.network.challenge(self.episode, reviewer="vn1", challenge_id="c1",
                               target="lappy", question="What control?")
        with self.assertRaises(CollectiveConflict):
            self.network.challenge(self.episode, reviewer="vn2", challenge_id="c2",
                                   target="lappy", question="Why now?")
        with self.assertRaises(ValueError):
            self.network.defend(self.episode, challenge_id="c1",
                                defender="malaphor", response="Wrong speaker", evidence_ref="self")
        with self.assertRaises(CollectiveConflict):
            self.network.resolve(self.episode, challenge_id="c1",
                                 disposition="ANSWERED", rationale="silence is not an answer")

    def test_defense_resolution_and_restart_replay(self):
        self.seal_reviews()
        self.open()
        self.network.challenge(self.episode, reviewer="vn1", challenge_id="c1",
                               target="lappy", question="Show cold restart")
        self.network.defend(self.episode, challenge_id="c1", defender="lappy",
                            response="We have not observed one", evidence_ref="source:reported")
        reopened = TkalVirtualNetwork(CollectiveStore(Path(self.tmp.name)/"collective.sqlite"))
        self.assertEqual(reopened.snapshot(self.episode).challenges[0]["response"],
                         "We have not observed one")
        with self.assertRaises(CollectiveConflict):
            reopened.defend(self.episode, challenge_id="c1", defender="lappy",
                            response="changed", evidence_ref="source:forged")
        reopened.resolve(self.episode, challenge_id="c1", disposition="ANSWERED",
                         rationale="Recorded defense does not establish learning")
        with self.assertRaises(CollectiveConflict):
            reopened.challenge(self.episode, reviewer="vn1", challenge_id="c1",
                               target="lappy", question="Replay")

    def test_incomplete_or_unresolved_cannot_determine(self):
        self.seal_reviews()
        self.open()
        with self.assertRaises(CollectiveConflict):
            self.network.determine(self.episode, verdict="SUSTAIN",
                                   rationale="No cross examination")
        for lens, reviewer in LENSES.items():
            cid="challenge-"+lens
            self.network.challenge(self.episode, reviewer=reviewer,
                                   challenge_id=cid, target="lappy",
                                   question="Strongest "+lens+" objection?")
            self.network.defend(self.episode, challenge_id=cid, defender="lappy",
                                response="Insufficient evidence", evidence_ref="synthetic:only")
            self.network.resolve(self.episode, challenge_id=cid,
                                 disposition="PARTLY_ANSWERED" if lens=="bridge" else "ANSWERED",
                                 rationale="Recorded, not qualified")
        with self.assertRaises(CollectiveConflict):
            self.network.determine(self.episode, verdict="SUSTAIN",
                                   rationale="one lens partial is unresolved")

    def test_all_three_lenses_can_refine_but_not_claim_independence(self):
        self.seal_reviews()
        opened=self.open()
        for lens, reviewer in LENSES.items():
            cid="c-"+lens
            self.network.challenge(self.episode, reviewer=reviewer,
                                   challenge_id=cid, target="lappy",
                                   question="Objection from "+lens)
            self.network.defend(self.episode, challenge_id=cid, defender="lappy",
                                response="No causal test yet", evidence_ref="synthetic:review")
            self.network.resolve(self.episode, challenge_id=cid,
                                 disposition="ANSWERED", rationale="Defense recorded")
        done=self.network.determine(self.episode, verdict="REFINE",
                                    rationale="Network and independent tests still missing")
        self.assertEqual(done.verdict, "REFINE")
        self.assertFalse(done.to_dict()["independence_verified"])
        self.assertEqual(done.to_dict()["authority"], "NONE")
        self.assertEqual(done.input_digest, opened.input_digest)
        with self.assertRaises(CollectiveConflict):
            self.network.challenge(self.episode, reviewer="vn1",
                                   challenge_id="late", target="lappy",
                                   question="Must remain closed")

    def test_bad_roster_and_stale_digest_blocked(self):
        self.seal_reviews()
        with self.assertRaises(CollectiveConflict):
            self.network.open(
                self.episode, expected_digest="0"*64, proposer="lappy",
                lenses=LENSES, hypothesis="x", falsifier="y")
        with self.assertRaises(ValueError):
            self.network.open(
                self.episode, expected_digest=self.store.snapshot(self.episode).digest,
                proposer="lappy", lenses={"purist_logic":"vn1",
                "pragmatism":"vn1","bridge":"malaphor"},
                hypothesis="x", falsifier="y")

    def test_http_roles_and_loopback_gate(self):
        self.seal_reviews()
        with self.assertRaises(ValueError):
            make_server(self.store, ADMIN, TOKENS, host="0.0.0.0", tkal_network=self.network)
        server=make_server(self.store, ADMIN, TOKENS, tkal_network=self.network)
        thread=Thread(target=server.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base=f"http://127.0.0.1:{server.server_port}/v1/episodes/{self.episode}/tkal"

        def request(method, path, token=None, data=None):
            headers={}
            if token is not None:headers["Authorization"]="Bearer "+token
            payload=None
            if data is not None:
                headers["Content-Type"]="application/json"
                payload=json.dumps(data).encode()
            q=Request(base+path,data=payload,headers=headers,method=method)
            try:
                with urlopen(q,timeout=3) as r:
                    return r.status,json.load(r)
            except HTTPError as e:
                return e.code,json.load(e)

        attrs=dict(expected_digest=self.store.snapshot(self.episode).digest,
                   proposer="lappy",lenses=LENSES,hypothesis="frozen claim",
                   falsifier="test fails")
        self.assertEqual(request("POST","",TOKENS["vn1"],attrs)[0],403)
        self.assertEqual(request("POST","",ADMIN,attrs)[0],201)
        self.assertEqual(request("GET","")[0],401)
        self.assertEqual(request("GET","",TOKENS["vn2"])[0],200)
        self.assertEqual(request("POST","/challenges",TOKENS["lappy"],
            {"challenge_id":"a1","target":"vn1","question":"spoof"})[0],400)
        self.assertEqual(request("POST","/challenges",TOKENS["vn1"],
            {"challenge_id":"a1","target":"lappy","question":"weakest control?"})[0],201)
        self.assertEqual(request("POST","/defenses",TOKENS["malaphor"],
            {"challenge_id":"a1","response":"fake","evidence_ref":"none"})[0],400)
        self.assertEqual(request("POST","/defenses",TOKENS["lappy"],
            {"challenge_id":"a1","response":"No qualified test","evidence_ref":"source:me"})[0],201)
        self.assertEqual(request("POST","/resolutions",TOKENS["vn1"],
            {"challenge_id":"a1","disposition":"ANSWERED","rationale":"why"})[0],403)
        self.assertEqual(request("POST","/resolutions",ADMIN,
            {"challenge_id":"a1","disposition":"ANSWERED","rationale":"defense recorded"})[0],201)
        self.assertEqual(request("POST","/determination",ADMIN,
            {"verdict":"SUSTAIN","rationale":"premature"})[0],409)
        self.assertEqual(request("POST","/challenges",TOKENS["vn1"],
            {"challenge_id":"a1","target":"lappy","question":"replay"})[0],409)


if __name__=="__main__":
    unittest.main()
