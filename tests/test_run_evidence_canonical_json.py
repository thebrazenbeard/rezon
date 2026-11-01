"""Interop evidence must be strict JSON, even for malformed typed objects."""

from dataclasses import replace
from hashlib import sha256
import json
import math
import unittest

from rezon.interop import RunEvidenceError, export_run_evidence
from rezon.receipts import ResultReceipt
from rezon.runner import RunOutcome
from rezon.trace import ExecutionTrace, TraceRecord


def outcome_with_source_ref(source_ref):
    record = TraceRecord(
        execution_id="exec-1", node_id="node-1", episode_version="episode-1",
        visible_proposition_ids=(), blinded_proposition_ids=(),
        visible_relation_ids=(), blinded_relation_ids=(),
        emitted_proposition_ids=(), independence_demonstrated=False,
        source_refs=(source_ref,),
    )
    receipt = ResultReceipt(
        task_id="task-1", episode_version="episode-1",
        execution_ids=("exec-1",),
    )
    return RunOutcome(receipt, ExecutionTrace(records=(record,)))


class CanonicalJsonEvidenceTests(unittest.TestCase):
    def test_valid_reference_exports(self):
        evidence = export_run_evidence(outcome_with_source_ref("public:sha256:abc"))
        self.assertEqual(evidence["executions"][0]["source_refs"], ["public:sha256:abc"])

    def test_nan_reference_fails_closed(self):
        with self.assertRaises(RunEvidenceError):
            export_run_evidence(outcome_with_source_ref(math.nan))

    def test_non_json_reference_fails_closed_with_contract_error(self):
        with self.assertRaises(RunEvidenceError):
            export_run_evidence(outcome_with_source_ref(object()))

    def test_mutable_source_reference_cannot_alias_export(self):
        source = {"ref": "original"}
        with self.assertRaisesRegex(RunEvidenceError, "string tuple"):
            export_run_evidence(outcome_with_source_ref(source))

    def test_mutable_unresolved_receipt_cannot_alias_export(self):
        outcome = outcome_with_source_ref("public:sha256:abc")
        forged = RunOutcome(
            replace(outcome.receipt, unresolved=({"unresolved": "original"},)),
            outcome.trace,
        )
        with self.assertRaisesRegex(RunEvidenceError, "string tuple"):
            export_run_evidence(forged)

    def test_nested_identifier_type_is_checked(self):
        outcome = outcome_with_source_ref("public:sha256:abc")
        record = replace(outcome.trace.records[0], visible_proposition_ids=([],))
        forged = RunOutcome(outcome.receipt, ExecutionTrace(records=(record,)))
        with self.assertRaisesRegex(RunEvidenceError, "string tuple"):
            export_run_evidence(forged)

    def test_non_string_receipt_identifier_is_rejected(self):
        outcome = outcome_with_source_ref("public:sha256:abc")
        forged = RunOutcome(replace(outcome.receipt, task_id=True), outcome.trace)
        with self.assertRaisesRegex(RunEvidenceError, "string"):
            export_run_evidence(forged)

    def test_unpaired_unicode_surrogate_fails_closed(self):
        with self.assertRaisesRegex(RunEvidenceError, "JSON"):
            export_run_evidence(outcome_with_source_ref("\ud800"))

    def test_returned_snapshot_matches_digest(self):
        exported = export_run_evidence(outcome_with_source_ref("public:sha256:abc"))
        body = {key: value for key, value in exported.items() if key != "evidence_digest"}
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.assertEqual(exported["evidence_digest"], sha256(canonical).hexdigest())


if __name__ == "__main__":
    unittest.main()
