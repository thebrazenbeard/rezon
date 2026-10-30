"""TRAININGDAY delegated inference tests."""
import unittest
import json
from rezon.trainingday_pool import build_job

class PoolTests(unittest.TestCase):
    def test_no_answers_in_job(self):
        job, oracle = build_job(seed=29037, count=6, workers={"vn1": "qwen-coder", "vn2": "granite"})
        self.assertEqual(len(job["cases"]), 6)
        self.assertNotIn("answer", str(job))
        self.assertEqual(oracle["job_sha256"], job["job_sha256"])
        self.workers = {"vn1": "qwen-coder", "vn2": "granite"}
        self.job, self.oracle = job, oracle

    def test_three_wrong_models_cannot_override_integer_oracle(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import collect, run_worker
        models = {}
        for worker in self.workers:
            models[worker] = run_worker(
                self.job, worker, base_url="http://127.0.0.1:11434/v1",
                model=Mock(complete=Mock(return_value="999999")),
            )
        summary, rows = collect(self.job, self.oracle, list(models.values()))
        self.assertEqual(summary["status"], "REPLAYED_ORACLE_NOT_MODEL_CONSENSUS")
        self.assertEqual(summary["model_exact_total"], 0)
        self.assertEqual(summary["candidate_rows"], 6)
        self.assertTrue(all(row["answer"] != "999999" for row in rows))
        self.assertTrue(all(row["qualified_for_neural_training"] is False for row in rows))

    def test_non_loopback_endpoint_refused_before_any_model_call(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import PoolError, run_worker
        model = Mock()
        for endpoint in ("http://10.0.0.4:11434/v1", "https://example.org/v1",
                         "http://localhost.example.org:11434/v1"):
            with self.subTest(endpoint=endpoint):
                with self.assertRaisesRegex(PoolError, "loopback"):
                    run_worker(self.job, "vn1", base_url=endpoint, model=model)
        model.complete.assert_not_called()

    def test_replayed_and_tampered_model_receipts_refused(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import PoolError, run_worker, collect
        receipt = run_worker(
            self.job, "vn1", base_url="http://127.0.0.1:11434/v1",
            model=Mock(complete=Mock(return_value="17")),
        )
        with self.assertRaisesRegex(PoolError, "duplicate"):
            collect(self.job, self.oracle, [receipt, receipt])
        receipt["answers"][0]["text"] = "999"
        with self.assertRaisesRegex(PoolError, "digest"):
            collect(self.job, self.oracle, [receipt])

    def test_modified_arithmetic_answer_rejected_even_before_worker_results(self):
        from rezon.trainingday_pool import PoolError, collect
        tampered = json.loads(json.dumps(self.oracle))
        tampered["cases"][0]["answer"] += 1
        with self.assertRaisesRegex(PoolError, "oracle"):
            collect(self.job, tampered, [])

    def test_partial_worker_evidence_never_exports_training_candidates(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import run_worker, collect
        receipt = run_worker(
            self.job, "vn1", base_url="http://127.0.0.1:11434/v1",
            model=Mock(complete=Mock(return_value="0")),
        )
        summary, rows = collect(self.job, self.oracle, [receipt])
        self.assertEqual(summary["status"], "PARTIAL_WORKER_EVIDENCE_NOT_ADMITTED")
        self.assertEqual(rows, [])
