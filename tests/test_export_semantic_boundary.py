from dataclasses import replace
import pytest
from rezon.interop import RunEvidenceError,export_run_evidence
from rezon.receipts import ResultReceipt
from rezon.runner import RunOutcome
from rezon.trace import TraceRecord,ExecutionTrace

def outcome(ids=("x",)):
    rows=tuple(TraceRecord(execution_id=i,node_id="node",episode_version="e@1",visible_proposition_ids=(),blinded_proposition_ids=(),visible_relation_ids=(),blinded_relation_ids=(),emitted_proposition_ids=(),independence_demonstrated=False) for i in ids)
    return RunOutcome(ResultReceipt(task_id="t",episode_version="e@1",execution_ids=ids),ExecutionTrace(records=rows))

@pytest.mark.parametrize("ids",[("",),("x","x")])
def test_invalid_attempt_identities_rejected(ids):
    with pytest.raises(RunEvidenceError,match="execution id"):
        export_run_evidence(outcome(ids))

@pytest.mark.parametrize("field,value",[("accepted_claim_ids",("a",)),("rejected_claim_ids",("r",)),("claim_disposition_complete",True)])
def test_disallowed_claim_disposition_rechecked(field,value):
    x=outcome()
    object.__setattr__(x.receipt,field,value)
    with pytest.raises(RunEvidenceError,match="claim disposition"):
        export_run_evidence(x)

def test_valid_no_execution_and_multiple_distinct_attempts():
    assert export_run_evidence(outcome(()))["executions"]==[]
    assert [row["execution_id"] for row in export_run_evidence(outcome(("a","b")))["executions"]]==["a","b"]
