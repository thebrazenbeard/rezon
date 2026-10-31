"""Oracle-grounded peer challenge reporting; synthetic source only."""

from __future__ import annotations

import json
import unittest
from unittest.mock import Mock

from rezon.trainingday_pool import PoolError, build_job, run_review, run_worker
from rezon.trainingday_r34_peer_evidence import assess_peer_outcomes


URL = "http://127.0.0.1:11434/v1"


class PeerOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.job, self.oracle = build_job(
            seed=29037, count=6,
            workers={"vn1": "model-a", "vn2": "model-b"},
        )
        labels = [row["answer"] for row in self.oracle["cases"]]
        self.first = [
            run_worker(self.job, "vn1", base_url=URL,
                       model=Mock(complete=Mock(side_effect=[
                           str(777 if i == 0 else label)
                           for i, label in enumerate(labels)
                       ]))),
            run_worker(self.job, "vn2", base_url=URL,
                       model=Mock(complete=Mock(return_value="777"))),
        ]
        self.reviews = [
            run_review(self.job, self.first, "vn1", base_url=URL,
                       model=Mock(complete=Mock(side_effect=[
                           str(888 if i == 1 else label)
                           for i, label in enumerate(labels)
                       ]))),
            run_review(self.job, self.first, "vn2", base_url=URL,
                       model=Mock(complete=Mock(side_effect=[
                           str(label if i == 1 else 777)
                           for i, label in enumerate(labels)
                       ]))),
        ]

    def assess(self, **replacements):
        return assess_peer_outcomes(
            replacements.get("job", self.job),
            replacements.get("oracle", self.oracle),
            replacements.get("first", self.first),
            replacements.get("reviews", self.reviews),
        )

    def test_reports_corrected_and_regressed_votes_separately(self):
        report = self.assess()
        self.assertEqual(report["status"], "SOURCE_ONLY_HOLD")
        self.assertEqual(report["first_exact_total"], 5)
        self.assertEqual(report["review_exact_total"], 6)
        self.assertEqual(report["corrected_votes"], 2)
        self.assertEqual(report["regressed_votes"], 1)
        self.assertEqual(report["net_exact_delta"], 1)
        self.assertEqual(report["case_dispositions"][0]["first_consensus"], "UNANIMOUS_WRONG")
        self.assertEqual(report["case_dispositions"][0]["review_consensus"], "DISAGREEMENT")
        self.assertEqual(report["case_dispositions"][0]["corrected_workers"], ["vn1"])
        self.assertEqual(report["case_dispositions"][1]["regressed_workers"], ["vn1"])
        self.assertEqual(report["case_dispositions"][1]["corrected_workers"], ["vn2"])
        self.assertTrue(all(row["qualified_for_neural_training"] is False
                            for row in report["case_dispositions"]))
        self.assertFalse(report["authorizes_model_release"])
        self.assertFalse(report["authorizes_optimizer_start"])
        self.assertFalse(report["host_identity_attested"])

    def test_same_answers_cannot_be_promoted_by_consensus(self):
        report = self.assess()
        unanimous = report["case_dispositions"][0]
        self.assertEqual(unanimous["first_exact_votes"], 0)
        self.assertEqual(unanimous["first_consensus"], "UNANIMOUS_WRONG")
        self.assertEqual(report["oracle_scope"], "PUBLIC_DETERMINISTIC_INTEGER_REPLAY")
        self.assertNotIn("answer", unanimous)
        self.assertNotIn("prompt", unanimous)

    def test_delivery_permutation_and_idempotent_retries_stable(self):
        expected = self.assess()
        self.assertEqual(self.assess(first=list(reversed(self.first)),
                                     reviews=list(reversed(self.reviews))), expected)
        self.assertEqual(self.assess(first=self.first + self.first,
                                     reviews=self.reviews + self.reviews), expected)

    def test_changed_review_receipt_and_wrong_peer_binding_rejected(self):
        altered = json.loads(json.dumps(self.reviews))
        altered[0]["answers"][0]["text"] = "99"
        with self.assertRaises(PoolError):
            self.assess(reviews=altered)
        altered = json.loads(json.dumps(self.reviews))
        altered[0]["peer_receipts_sha256"] = "0" * 64
        with self.assertRaises(PoolError):
            self.assess(reviews=altered)

    def test_ambiguous_oracle_cannot_be_supplied_from_vote_consensus(self):
        poisoned = json.loads(json.dumps(self.oracle))
        poisoned["cases"][0]["answer"] = 777
        with self.assertRaises(PoolError):
            self.assess(oracle=poisoned)

    def test_malformed_oracle_case_raises_bounded_pool_error(self):
        poisoned = json.loads(json.dumps(self.oracle))
        poisoned["cases"][0] = None
        with self.assertRaises(PoolError):
            self.assess(oracle=poisoned)

    def test_unrecognized_oracle_metadata_is_not_accepted(self):
        poisoned = json.loads(json.dumps(self.oracle))
        poisoned["cases"][0]["source_override"] = "unattested"
        with self.assertRaises(PoolError):
            self.assess(oracle=poisoned)
        poisoned = json.loads(json.dumps(self.oracle))
        poisoned["source_override"] = "unattested"
        with self.assertRaises(PoolError):
            self.assess(oracle=poisoned)

    def test_unsupported_nested_custom_types_rejected_before_receipt_checks(self):
        class Inconsistent(dict):
            def items(self):
                return iter(())

        poisoned = json.loads(json.dumps(self.first))
        poisoned[0]["answers"][0] = Inconsistent(poisoned[0]["answers"][0])
        with self.assertRaises(PoolError):
            self.assess(first=poisoned)

    def test_input_mutation_after_assessment_cannot_rewrite_evidence(self):
        report = self.assess()
        expected = json.dumps(report, sort_keys=True)
        self.first[0]["answers"][0]["text"] = "-999"
        self.reviews[0]["answers"][0]["text"] = "-999"
        self.assertEqual(json.dumps(report, sort_keys=True), expected)

    def test_unbounded_input_rejected_without_model_calls(self):
        poisoned = json.loads(json.dumps(self.job))
        poisoned["cases"][0]["prompt"] = "X" * 2_100_000
        with self.assertRaises(PoolError):
            self.assess(job=poisoned)


if __name__ == "__main__":
    unittest.main()
