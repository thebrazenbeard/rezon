"""Four-agent virtual hearing protocol and authenticated loopback integration."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
from unittest.mock import patch
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from rezon.collective import CollectiveConflict, CollectiveStore, CollectiveValidationError
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

    def test_self_target_reviews_do_not_satisfy_peer_quorum(self):
        self.seal_answers()
        for agent in ("vn1", "vn2", "malaphor"):
            with self.assertRaises(CollectiveValidationError):
                self.store.submit_review(self.episode, agent, "self-check by "+agent,
                                         ("answer:"+agent,))
        self.assertEqual(self.store.snapshot(self.episode).reviews, ())
        with self.assertRaises(CollectiveConflict):
            self.open()

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

    def test_waived_proposer_questions_cannot_sustain(self):
        self.seal_reviews()
        self.open()
        for lens, reviewer in LENSES.items():
            cid="waived-"+lens
            self.network.challenge(self.episode, reviewer=reviewer,
                                   challenge_id=cid, target="lappy",
                                   question="A critical "+lens+" objection")
            self.network.resolve(self.episode, challenge_id=cid,
                                 disposition="WAIVED", rationale="Chair says waive")
        with self.assertRaises(CollectiveConflict):
            self.network.determine(self.episode, verdict="SUSTAIN",
                                   rationale="Chair waivers cannot replace peer replies")

    def test_three_proposer_defenses_cannot_sustain_without_peer_dialogue(self):
        self.seal_reviews()
        self.open()
        for lens, reviewer in LENSES.items():
            cid="proposer-"+lens
            self.network.challenge(self.episode, reviewer=reviewer,
                                   challenge_id=cid, target="lappy",
                                   question="Challenge the proposer")
            self.network.defend(self.episode, challenge_id=cid, defender="lappy",
                                response="Proposer replies", evidence_ref="synthetic:only")
            self.network.resolve(self.episode, challenge_id=cid,
                                 disposition="ANSWERED", rationale="Response recorded")
        with self.assertRaises(CollectiveConflict):
            self.network.determine(self.episode, verdict="SUSTAIN",
                                   rationale="Need actual peer-to-peer scrutiny")

    def test_three_distinct_targeted_peer_replies_allow_sustain(self):
        self.seal_reviews()
        self.open()
        cycle=(("vn1","vn2"),("vn2","malaphor"),("malaphor","vn1"))
        for reviewer, target in cycle:
            cid="cross-"+reviewer
            self.network.challenge(self.episode, reviewer=reviewer,
                                   challenge_id=cid, target=target,
                                   question="Your strongest evidence?")
            self.network.defend(self.episode, challenge_id=cid, defender=target,
                                response="Reply from "+target,
                                evidence_ref="synthetic:reply:"+target)
            self.network.resolve(self.episode, challenge_id=cid,
                                 disposition="ANSWERED", rationale="Response was logged")
        closed=self.network.determine(self.episode, verdict="SUSTAIN",
                                      rationale="Three directed exchanges recorded")
        self.assertEqual(closed.verdict, "SUSTAIN")
        self.assertFalse(closed.to_dict()["independence_verified"])

    def test_late_collective_review_marks_hearing_stale(self):
        self.seal_answers()
        for reviewer in ("vn1","vn2","malaphor"):
            self.store.submit_review(self.episode, reviewer,
                                     "first peer review from "+reviewer,
                                     ("answer:lappy",))
        opened=self.open()
        self.store.submit_review(self.episode, "lappy", "late additional peer review",
                                 ("answer:vn1",))
        self.assertTrue(self.network.snapshot(self.episode).stale)
        with self.assertRaises(CollectiveConflict):
            self.network.challenge(self.episode, reviewer="vn1",
                                   challenge_id="new-late", target="vn2",
                                   question="New evidence?")

    def test_partial_challenge_blocks_next_until_attributed_followup(self):
        self.seal_reviews()
        self.open()
        self.network.challenge(self.episode, reviewer="vn1", challenge_id="partial1",
                               target="vn2", question="Where is the evidence?")
        self.network.defend(self.episode, challenge_id="partial1", defender="vn2",
                            response="Initial incomplete response", evidence_ref="ref:initial")
        self.network.resolve(self.episode, challenge_id="partial1",
                             disposition="PARTLY_ANSWERED", rationale="More detail required")
        with self.assertRaises(CollectiveConflict):
            self.network.challenge(self.episode, reviewer="malaphor",
                                   challenge_id="premature", target="vn1",
                                   question="Can we proceed?")
        continued=self.network.defend(self.episode, challenge_id="partial1",
                                      defender="vn2", response="Additional qualified evidence",
                                      evidence_ref="ref:followup")
        self.assertIn("Initial incomplete response", continued.challenges[0]["response"])
        self.assertIn("Additional qualified evidence", continued.challenges[0]["response"])
        self.assertIsNone(continued.challenges[0]["disposition"])
        self.network.resolve(self.episode, challenge_id="partial1",
                             disposition="ANSWERED", rationale="Follow-up recorded")
        self.network.challenge(self.episode, reviewer="malaphor",
                               challenge_id="next", target="vn1", question="Challenge now permitted")

    def test_only_proposer_can_withdraw_and_chair_cannot_force_withdraw(self):
        self.seal_reviews()
        self.open()
        with self.assertRaises(ValueError):
            self.network.determine(self.episode, verdict="WITHDRAW",
                                   rationale="Chair overreach")
        with self.assertRaises(ValueError):
            self.network.withdraw(self.episode, proposer="vn1",
                                  reason="I am not the proposer")
        closed=self.network.withdraw(self.episode, proposer="lappy",
                                     reason="Proposer retracts the hypothesis")
        self.assertEqual(closed.verdict, "WITHDRAW")
        self.assertEqual(closed.to_dict()["authority"], "NONE")
        with self.assertRaises(CollectiveConflict):
            self.network.challenge(self.episode, reviewer="vn1",
                                   challenge_id="post-withdraw", target="vn2",
                                   question="Cannot reopen")

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

    def test_cli_flag_enables_hearing_only_when_requested(self):
        from rezon.collective_cli import main
        from unittest.mock import patch as mocked
        import os
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                captured = []
                class Stub:
                    server_port = 8765
                    def serve_forever(self):
                        pass
                    def server_close(self):
                        pass
                def fake_make(store, admin, workers, integrator, **kwargs):
                    captured.append(kwargs.get("tkal_network"))
                    if enabled:
                        self.assertIsInstance(captured[-1], TkalVirtualNetwork)
                        self.assertIs(captured[-1].store, store)
                    else:
                        self.assertIsNone(captured[-1])
                    return Stub()
                cli=["serve", "--db", str(Path(self.tmp.name)/("serve-"+str(enabled)+".sqlite")),
                     "--port", "8765"]
                if enabled:cli.append("--tkal")
                env={"REZON_COLLECTIVE_ADMIN_TOKEN":ADMIN,
                     "REZON_COLLECTIVE_WORKER_TOKENS_JSON":json.dumps(TOKENS)}
                with mocked.dict(os.environ, env), mocked(
                    "rezon.collective_cli.make_server", side_effect=fake_make
                ):
                    self.assertEqual(main(cli), 0)
                self.assertEqual(len(captured), 1)

    def test_four_separate_process_clients_share_one_gateway(self):
        # Four independent Python OS processes on ONE machine, not four hosts.
        server=make_server(self.store, ADMIN, TOKENS, tkal_network=self.network)
        thread=Thread(target=server.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(thread.join, 3)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base=f"http://127.0.0.1:{server.server_port}/v1/episodes/{self.episode}"
        code = """import json,sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError
url,token,method,body=sys.argv[1:]
headers={"Authorization":"Bearer "+token}
data=None if method=="GET" else body.encode()
if data is not None:headers["Content-Type"]="application/json"
try:
 with urlopen(Request(url,data=data,headers=headers,method=method),timeout=8) as r:
  result={"status":r.status,"body":json.load(r)}
except HTTPError as e:
 result={"status":e.code,"body":json.load(e)}
print(json.dumps(result))
"""
        def call(actor, method, suffix, payload=None):
            token=ADMIN if actor=="admin" else TOKENS[actor]
            args=[sys.executable,"-c",code,base+suffix,token,
                  method,json.dumps(payload if payload is not None else {})]
            result=subprocess.run(args,stdin=subprocess.DEVNULL,
                                  text=True,capture_output=True,timeout=18)
            if result.returncode:
                raise AssertionError("child HTTP client failed")
            return json.loads(result.stdout)
        self.assertEqual(call("vn1","GET","/state")["status"],409)
        with ThreadPoolExecutor(max_workers=4) as pool:
            answers=list(pool.map(lambda a:call(a,"POST","/answers",
                            {"content":"independent client message from "+a}),AGENTS))
        self.assertEqual([a["status"] for a in answers],[201]*4)
        self.assertEqual(len(call("vn2","GET","/state")["body"]["answers"]),4)
        targets={"lappy":"vn1","vn1":"vn2","vn2":"malaphor","malaphor":"lappy"}
        with ThreadPoolExecutor(max_workers=4) as pool:
            reviews=list(pool.map(lambda a:call(a,"POST","/reviews",{
                "content":"review authored by process "+a,
                "target_ids":["answer:"+targets[a]]}),AGENTS))
        self.assertEqual([a["status"] for a in reviews],[201]*4)
        frozen=call("admin","GET","/state")["body"]["input_digest"]
        opened=call("admin","POST","/tkal",{
            "expected_digest":frozen,"proposer":"lappy","lenses":LENSES,
            "hypothesis":"exact claim","falsifier":"credible counterexample"})
        self.assertEqual(opened["status"],201)
        for reviewer,defender in (("vn1","vn2"),("vn2","malaphor"),("malaphor","vn1")):
            cid="net-"+reviewer
            self.assertEqual(call(reviewer,"POST","/tkal/challenges",{
                "challenge_id":cid,"target":defender,"question":"Cross challenge by "+reviewer
            })["status"],201)
            self.assertEqual(call(defender,"POST","/tkal/defenses",{
                "challenge_id":cid,"response":"Peer reply from "+defender,
                "evidence_ref":"synthetic:subprocess:"+defender})["status"],201)
            self.assertEqual(call("admin","POST","/tkal/resolutions",{
                "challenge_id":cid,"disposition":"ANSWERED","rationale":"Response logged"
            })["status"],201)
        decision=call("admin","POST","/tkal/determination",{
            "verdict":"SUSTAIN","rationale":"Three process-backed lens exchanges were recorded"})
        self.assertEqual(decision["status"],201)
        self.assertEqual(decision["body"]["verdict"],"SUSTAIN")
        self.assertFalse(decision["body"]["independence_verified"])
        self.assertEqual(call("malaphor","GET","/tkal")["body"]["verdict"],"SUSTAIN")

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
        self.assertEqual(request("POST","/withdrawals",ADMIN,
            {"reason":"Chair cannot withdraw"})[0],403)
        self.assertEqual(request("POST","/withdrawals",TOKENS["vn1"],
            {"reason":"Wrong proposer"})[0],400)
        self.assertEqual(request("POST","/withdrawals",TOKENS["lappy"],
            {"reason":"Proposer voluntarily withdraws"})[0],201)
        self.assertEqual(request("GET","",TOKENS["vn1"])[1]["verdict"],"WITHDRAW")


if __name__=="__main__":
    unittest.main()
