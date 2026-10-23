"""Four independent HTTP client processes exercising one native Rezon episode.

The processes are on one loopback host. This is NOT cross-host TLS,
independent inference, Malaphor participation, or a deployed mesh.
"""
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from pathlib import Path
import json
import os
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server
from rezon.epistemics import PropositionKind


AGENTS = ("vera-lappy", "vera-vn1", "vera-vn2", "malaphor")
ADMIN = "synthetic-four-worker-admin-token"
TOKENS = {agent: "synthetic-four-worker-" + agent + "-token" for agent in AGENTS}
CLIENT = r"""
import http.client, json, os, sys
port, ep, action, text, target = sys.argv[1:]
conn = http.client.HTTPConnection("127.0.0.1", int(port), timeout=5)
body = {"content":text}
if action == "reviews":
    body["target_ids"] = [target]
conn.request("POST", "/v1/episodes/"+ep+"/"+action,
             json.dumps(body).encode(),
             {"Authorization":"Bearer "+os.environ["SYNTHETIC_WORKER_TOKEN"],
              "Content-Type":"application/json"})
r = conn.getresponse()
print(json.dumps({"status":r.status,"body":json.loads(r.read())}))
conn.close()
"""


def call(server, method, path, token=None, payload=None):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = "Bearer " + token
    try:
        conn.request(method, path,
                     None if payload is None else json.dumps(payload).encode(),
                     headers)
        response = conn.getresponse()
        return response.status, json.loads(response.read())
    finally:
        conn.close()


def worker(port, episode, agent, action, target=""):
    env = dict(os.environ, SYNTHETIC_WORKER_TOKEN=TOKENS[agent])
    cmd = (sys.executable, "-c", CLIENT, str(port), episode, action,
           "Synthetic "+action+" from "+agent, target)
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class Integrator:
    agent_id = "synthetic-integrator"

    def complete(self, messages):
        return "Four synthetic claims are not verified truth."


def test_four_separate_http_client_processes_complete_one_rezon_cycle():
    with TemporaryDirectory() as tmp:
        database = Path(tmp) / "episode.sqlite3"
        store = CollectiveStore(database)
        server = make_server(store, ADMIN, TOKENS, Integrator())
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            code, made = call(server, "POST", "/v1/episodes", ADMIN,
                              {"prompt":"One shared falsifiable question",
                               "agents":list(AGENTS)})
            assert code == 201
            episode = made["episode_id"]
            path = "/v1/episodes/" + episode
            assert call(server, "GET", path+"/state", TOKENS[AGENTS[0]])[0] == 409
            with ThreadPoolExecutor(max_workers=3) as pool:
                first = list(pool.map(
                    lambda agent: worker(server.server_port, episode, agent, "answers"),
                    AGENTS[:3]))
            assert all(item["status"] == 201 for item in first)
            assert call(server, "GET", path+"/state", TOKENS[AGENTS[0]])[0] == 409
            fourth = worker(server.server_port, episode, AGENTS[3], "answers")
            assert fourth["status"] == 201
            assert call(server, "GET", path+"/state", TOKENS[AGENTS[0]])[0] == 200
            code, provisional = call(server, "POST", path+"/synthesize", ADMIN, {})
            assert code == 201
            targets = tuple("answer:"+AGENTS[(i+1) % 4] for i in range(4))
            with ThreadPoolExecutor(max_workers=4) as pool:
                reviews = list(pool.map(
                    lambda pair: worker(server.server_port, episode,
                                        pair[0], "reviews", pair[1]),
                    zip(AGENTS, targets)))
            assert all(item["status"] == 201 for item in reviews)
            code, state = call(server, "GET", path+"/state", TOKENS[AGENTS[2]])
            assert code == 200
            assert len(state["answers"]) == 4 and len(state["reviews"]) == 4
            assert state["syntheses"][0]["is_current"] is False
            code, final = call(server, "POST", path+"/synthesize", ADMIN, {})
            assert code == 201
            assert final["input_digest"] != provisional["input_digest"]
            reopened = CollectiveStore(database)
            snapshot = reopened.snapshot(episode)
            assert snapshot.complete and not snapshot.missing_agents
            assert len(snapshot.answers) == len(snapshot.reviews) == 4
            assert len(snapshot.syntheses) == 2
            assert sum(s.input_digest == snapshot.digest for s in snapshot.syntheses) == 1
            projection = reopened.project_episode(episode).snapshot()
            assert sum(x.kind is PropositionKind.HYPOTHESIS
                       for x in projection.current_propositions) == 1
            assert sum(x.relation_type == "challenges"
                       for x in projection.current_relations) == 4
            assert call(server, "POST", path+"/answers", TOKENS[AGENTS[0]],
                        {"content":"Changed answer"})[0] == 409
            assert call(server, "GET", path+"/state", "wrong-synthetic-token")[0] == 401
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
