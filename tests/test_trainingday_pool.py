"""TRAININGDAY delegated inference tests."""
import unittest
from rezon.trainingday_pool import build_job

class PoolTests(unittest.TestCase):
    def test_no_answers_in_job(self):
        job, oracle = build_job(seed=29037, count=6, workers={"vn1": "qwen-coder", "vn2": "granite"})
        self.assertEqual(len(job["cases"]), 6)
        self.assertNotIn("answer", str(job))
        self.assertEqual(oracle["job_sha256"], job["job_sha256"])
