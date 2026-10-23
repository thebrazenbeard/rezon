"""Four external client processes exercise the opt-in T'Kal hearing via Rezon HTTP.

All clients use localhost. This is not a physical four-host/TLS qualification.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from http.client import HTTPConnection

from rezon.collective import CollectiveStore
from rezon.collective_http import make_server

AGENTS=("vera-lappy","vera-vn1","vera-vn2","malaphor")
LENSES={"purist_logic":"vera-vn1","pragmatism":"vera-vn2","bridge":"malaphor"}
ADMIN="test-only-admin-rezon-virtual-token"
TOKENS={agent:"test-only-rezon-virtual-"+agent+"-token" for agent in AGENTS}

CLIENT=r"""
import http.client,json,os,sys
port,method,path=sys.argv[1:4]
data=json.loads(sys.argv[4])
conn=http.client.HTTPConnection("127.0.0.1",int(port),timeout=6)
headers={"Authorization":"Bearer "+os.environ["REZON_TEST_CLIENT_TOKEN"],
         "Content-Type":"application/json"}
conn.request(method,path,body=None if data is None else json.dumps(data).encode(),
             headers=headers)
r=conn.getresponse()
print(json.dumps({"status":r.status,"data":json.loads(r.read())}))
conn.close()
"""

def as_client(port,token,method,path,data=None):
    env=dict(os.environ,REZON_TEST_CLIENT_TOKEN=token)
    p=subprocess.run([sys.executable,"-c",CLIENT,str(port),method,path,
                      json.dumps(data)],env=env,capture_output=True,text=True,timeout=12)
    assert p.returncode==0,p.stderr
    return json.loads(p.stdout)

def test_four_agent_hearing_over_authenticated_shared_gateway():
    with TemporaryDirectory() as tmp:
        store=CollectiveStore(Path(tmp)/"collective.sqlite3")
        ep=store.create("One question shared by four workers",AGENTS)
        # Existing first round and peer-review barrier must be complete first.
        for a in AGENTS:store.submit_answer(ep,a,"Initial claim from "+a)
        for i,a in enumerate(AGENTS):
            store.submit_review(ep,a,"Review "+a,("answer:"+AGENTS[(i+1)%4],))
        digest=store.snapshot(ep).digest
        from rezon.tkal_network import TkalVirtualNetwork
        server=make_server(store,ADMIN,TOKENS,tkal_network=TkalVirtualNetwork(store))
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            path="/v1/episodes/"+ep+"/tkal"
            opening={"expected_digest":digest,"proposer":"vera-lappy",
                     "lenses":LENSES,"hypothesis":"A testable hypothesis",
                     "falsifier":"A contradicting observable result"}
            assert as_client(server.server_port,TOKENS["vera-vn1"],"POST",path,opening)["status"]==403
            opened=as_client(server.server_port,ADMIN,"POST",path,opening)
            assert opened["status"]==201,opened
            assert opened["data"]["verdict"] is None
            assert as_client(server.server_port,TOKENS["vera-vn2"],"GET",path)["status"]==200
            assert as_client(server.server_port,"wrong-credential","GET",path)["status"]==401
            assert as_client(server.server_port,ADMIN,"POST",path+"/verdict",
                             {"verdict":"SUSTAIN","rationale":"premature"})["status"]==409
            for i,reviewer in enumerate(("vera-vn1","vera-vn2","malaphor")):
                cid="cross-"+str(i)
                challenge={"challenge_id":cid,"target":"vera-lappy",
                           "question":"What evidence would falsify lens "+str(i)+"?"}
                entered=as_client(server.server_port,TOKENS[reviewer],"POST",
                                  path+"/challenges",challenge)
                assert entered["status"]==201,entered
                if i==0:
                    wrong=as_client(server.server_port,TOKENS["vera-vn2"],"POST",
                                    path+"/defenses",{"challenge_id":cid,
                                    "response":"pretending defender","evidence_ref":"test-ref"})
                    assert wrong["status"]==400,wrong
                    concurrent=as_client(server.server_port,TOKENS["malaphor"],"POST",
                                         path+"/challenges",{"challenge_id":"concurrent",
                                         "target":"vera-lappy","question":"second pending?"})
                    assert concurrent["status"]==409,concurrent
                defended=as_client(server.server_port,TOKENS["vera-lappy"],"POST",
                                   path+"/defenses",{"challenge_id":cid,
                                   "response":"Bounded defense "+str(i),
                                   "evidence_ref":"test-receipt-"+str(i)})
                assert defended["status"]==201,defended
                resolved=as_client(server.server_port,ADMIN,"POST",
                                   path+"/resolutions",{"challenge_id":cid,
                                   "disposition":"ANSWERED","rationale":"evidence noted"})
                assert resolved["status"]==201,resolved
            finished=as_client(server.server_port,ADMIN,"POST",
                               path+"/verdict",{"verdict":"REFINE",
                               "rationale":"All lenses challenged; retain falsifier"})
            assert finished["status"]==201,finished
            assert finished["data"]["verdict"]=="REFINE"
            assert len(finished["data"]["challenges"])==3
            assert finished["data"]["authority"]=="NONE"
            assert not finished["data"]["independence_verified"]
            # Persistence is native Rezon state, not a second journal/store.
            from rezon.tkal_network import TkalVirtualNetwork
            reopen=TkalVirtualNetwork(CollectiveStore(Path(tmp)/"collective.sqlite3"))
            assert reopen.snapshot(ep).verdict=="REFINE"
            assert as_client(server.server_port,TOKENS["vera-vn1"],"POST",
                             path+"/challenges",{"challenge_id":"after-close",
                             "target":"vera-lappy","question":"new"})["status"]==409
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)
