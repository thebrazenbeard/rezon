import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

PROBE = """
import sys,json
sys.path.insert(0,sys.argv[1])
from rezon.episode import Episode
from rezon.epistemics import Proposition,PropositionKind,Hyperrelation,Participant
from rezon.provenance import canonical_episode_snapshot_digest
e=Episode("e1")
def p(name,refs=()):
    e.add_proposition(Proposition(name,"e1",PropositionKind.CLAIM,name,source_refs=refs))
p("root");p("unrelated")
for i in range(8):p("p"+str(i),("root",))
if sys.argv[2]=="mixed":
    for i in range(8):
        e.add_relation(Hyperrelation("r"+str(i),"e1","supports",(Participant("p"+str(i),"source"),)))
        p("q"+str(i),("r"+str(i),))
    e.add_relation(Hyperrelation("keep","e1","supports",(Participant("unrelated","source"),)))
before=e.snapshot()
try:
    with e.atomic_mutation():
        e.retract_proposition("root","rollback")
        raise RuntimeError("rollback")
except RuntimeError: pass
if e.snapshot()!=before:raise RuntimeError("rollback changed snapshot")
e.retract_proposition("root","test")
after=e.snapshot()
print(json.dumps({"digest":canonical_episode_snapshot_digest(after),"active_p":[x.proposition_id for x in after.current_propositions],"active_r":[x.relation_id for x in after.current_relations],"all_p":len(after.all_propositions),"all_r":len(after.all_relations),"old_prefix":after.events[:len(before.events)]==before.events,"event_ids":[x.event_id for x in after.events]}))
"""

@pytest.mark.parametrize("case",["direct","mixed"])
def test_retraction_snapshot_is_seed_independent(case):
    src=Path(__file__).resolve().parents[1]/"src"
    results=[]
    for seed in range(1,9):
        env=dict(os.environ,PYTHONHASHSEED=str(seed))
        proc=subprocess.run([sys.executable,"-B","-c",PROBE,str(src),case],env=env,capture_output=True,text=True,timeout=10,check=True)
        results.append(json.loads(proc.stdout))
    for r in results:
        assert r["active_p"]==["unrelated"]
        assert r["active_r"]==(["keep"] if case=="mixed" else [])
        assert r["all_p"]==(18 if case=="mixed" else 10)
        assert r["all_r"]==(9 if case=="mixed" else 0)
        assert r["old_prefix"]
        assert r["event_ids"]==[f"e1:event:{i+1}" for i in range(len(r["event_ids"]))]
    assert len({r["digest"] for r in results})==1
