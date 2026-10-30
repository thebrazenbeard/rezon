"""TRAININGDAY delegated inference tests."""
import unittest
import json
from rezon.trainingday_pool import build_job

class PoolTests(unittest.TestCase):
    def setUp(self):
        self.workers = {"vn1": "qwen-coder", "vn2": "granite"}
        self.job, self.oracle = build_job(seed=29037, count=6, workers=self.workers)

    def test_no_answers_in_job(self):
        self.assertEqual(len(self.job["cases"]), 6)
        self.assertNotIn("answer", str(self.job))
        self.assertEqual(self.oracle["job_sha256"], self.job["job_sha256"])

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
        # An identical retried delivery is one piece of evidence, not two workers.
        summary, rows = collect(self.job, self.oracle, [receipt, receipt])
        self.assertEqual(summary["status"], "PARTIAL_WORKER_EVIDENCE_NOT_ADMITTED")
        self.assertEqual(summary["workers_completed"], 1)
        self.assertEqual(rows, [])
        # Two independently valid but different answers for one worker conflict.
        conflicting = run_worker(
            self.job, "vn1", base_url="http://127.0.0.1:11434/v1",
            model=Mock(complete=Mock(return_value="18")),
        )
        with self.assertRaisesRegex(PoolError, "conflicting duplicate"):
            collect(self.job, self.oracle, [receipt, conflicting])
        with self.assertRaisesRegex(PoolError, "replay limit"):
            collect(self.job, self.oracle, [receipt] * 9)
        with self.assertRaisesRegex(PoolError, "replay limit"):
            collect(self.job, self.oracle, [receipt] * 5)
        receipt["answers"][0]["text"] = "999"
        with self.assertRaisesRegex(PoolError, "digest"):
            collect(self.job, self.oracle, [receipt])

    def test_self_hashed_oversized_first_answer_rejected_before_aggregation(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import (PoolError, _digest, _peer_snapshot,
                                            collect, run_worker)
        receipts = [run_worker(self.job, worker,
                               base_url="http://127.0.0.1:11434/v1",
                               model=Mock(complete=Mock(return_value="7")))
                    for worker in self.workers]
        bad = receipts[0]
        bad["answers"][0]["text"] = "x" * 2001
        bad["answers"][0]["parsed_integer"] = None
        bad["receipt_sha256"] = _digest({k: v for k, v in bad.items()
                                         if k != "receipt_sha256"})
        with self.assertRaisesRegex(PoolError, "worker answer text"):
            collect(self.job, self.oracle, receipts)
        with self.assertRaisesRegex(PoolError, "worker answer text"):
            _peer_snapshot(self.job, receipts)

    def test_exact_answer_text_cap_is_accepted(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import collect, run_worker
        receipts = [run_worker(self.job, worker,
                               base_url="http://127.0.0.1:11434/v1",
                               model=Mock(complete=Mock(return_value="x" * 2000)))
                    for worker in self.workers]
        summary, rows = collect(self.job, self.oracle, receipts)
        self.assertEqual(summary["status"], "REPLAYED_ORACLE_NOT_MODEL_CONSENSUS")
        self.assertEqual(len(rows), len(self.job["cases"]))

    def test_transport_json_input_is_bounded_before_full_read(self):
        import tempfile
        from pathlib import Path
        from rezon.trainingday_pool import PoolError, load_json
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "oversized-receipt.json"
            path.write_text('{"filler":"' + ('x' * 600_000) + '"}', encoding="utf-8")
            with self.assertRaisesRegex(PoolError, "JSON input too large"):
                load_json(path)

    def test_unbounded_extra_field_or_parsed_number_rejected_before_digest(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import PoolError, collect, run_worker
        receipt = run_worker(self.job, "vn1", base_url="http://localhost:11434/v1",
                             model=Mock(complete=Mock(return_value="7")))
        receipt["unexpected"] = "x" * 600_000
        with self.assertRaisesRegex(PoolError, "worker receipt fields"):
            collect(self.job, self.oracle, [receipt])
        del receipt["unexpected"]
        receipt["answers"][0]["parsed_integer"] = 1 << 200_000
        with self.assertRaisesRegex(PoolError, "worker parsed integer"):
            collect(self.job, self.oracle, [receipt])

    def test_identical_replays_keep_aggregate_and_peer_review_outputs_stable(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import collect, collect_reviews, run_worker, run_review
        first = [run_worker(self.job, worker, base_url="http://127.0.0.1:11434/v1",
                            model=Mock(complete=Mock(return_value="7")))
                 for worker in self.workers]
        reviews = [run_review(self.job, first, worker,
                              base_url="http://127.0.0.1:11434/v1",
                              model=Mock(complete=Mock(return_value="8")))
                   for worker in self.workers]
        expected = collect(self.job, self.oracle, first)
        self.assertEqual(collect(self.job, self.oracle, first + first), expected)
        reviewed = collect_reviews(self.job, self.oracle, first, reviews)
        self.assertEqual(collect_reviews(self.job, self.oracle, first + first,
                                         reviews + reviews), reviewed)

    def test_conflicting_peer_review_replay_denied(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import PoolError, collect_reviews, run_worker, run_review
        first = [run_worker(self.job, worker, base_url="http://127.0.0.1:11434/v1",
                            model=Mock(complete=Mock(return_value="7")))
                 for worker in self.workers]
        reviews = [run_review(self.job, first, worker,
                              base_url="http://127.0.0.1:11434/v1",
                              model=Mock(complete=Mock(return_value="8")))
                   for worker in self.workers]
        alternate = run_review(self.job, first, "vn1",
                               base_url="http://127.0.0.1:11434/v1",
                               model=Mock(complete=Mock(return_value="9")))
        with self.assertRaisesRegex(PoolError, "conflicting duplicate"):
            collect_reviews(self.job, self.oracle, first, reviews + [alternate])

    def test_review_receipt_shape_is_checked_before_digest(self):
        from copy import deepcopy
        from unittest.mock import Mock
        from rezon.trainingday_pool import (PoolError, _digest, collect_reviews,
                                            run_worker, run_review)
        first = [run_worker(self.job, worker, base_url="http://127.0.0.1:11434/v1",
                            model=Mock(complete=Mock(return_value="7")))
                 for worker in self.workers]
        valid = [run_review(self.job, first, worker,
                            base_url="http://127.0.0.1:11434/v1",
                            model=Mock(complete=Mock(return_value="8")))
                 for worker in self.workers]

        for mutation, expected in (
            (lambda r: r["answers"].__setitem__(0, 42), "review answer fields"),
            (lambda r: r["answers"][0].__setitem__("text", "x" * 2001),
             "review answer text"),
            (lambda r: r["answers"][0].__setitem__("parsed_integer", 1 << 200_000),
             "review parsed integer"),
            (lambda r: r.__setitem__("unexpected", "x" * 600_000),
             "review receipt fields"),
        ):
            with self.subTest(expected=expected):
                reviews = deepcopy(valid)
                mutation(reviews[0])
                # The malformed object can have a syntactically valid self-hash;
                # shape checks still must precede hash canonicalization.
                if expected == "review answer fields":
                    reviews[0]["receipt_sha256"] = _digest({
                        k: v for k, v in reviews[0].items()
                        if k != "receipt_sha256"
                    })
                with self.assertRaisesRegex(PoolError, expected):
                    collect_reviews(self.job, self.oracle, first, reviews)

    def test_review_exact_text_limit_remains_valid(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import collect_reviews, run_worker, run_review
        first = [run_worker(self.job, worker, base_url="http://localhost:11434/v1",
                            model=Mock(complete=Mock(return_value="7")))
                 for worker in self.workers]
        reviewed = [run_review(self.job, first, worker,
                               base_url="http://localhost:11434/v1",
                               model=Mock(complete=Mock(return_value="x" * 2000)))
                    for worker in self.workers]
        summary, rows = collect_reviews(self.job, self.oracle, first, reviewed)
        self.assertEqual(summary["status"], "REVIEWED_WITH_ORACLE_NOT_TRAINING_ADMITTED")
        self.assertEqual(len(rows), len(self.job["cases"]))
        self.assertTrue(all(not row["qualified_for_neural_training"] for row in rows))

    def test_lone_surrogate_receipt_digest_is_controlled_failure(self):
        from rezon.trainingday_pool import PoolError, _digest
        with self.assertRaisesRegex(PoolError, "Unicode"):
            _digest({"text": "\ud800"})

    def test_lone_surrogate_model_answer_is_controlled_failure(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import PoolError, run_worker
        with self.assertRaisesRegex(PoolError, "Unicode"):
            run_worker(self.job, "vn1", base_url="http://127.0.0.1:11434/v1",
                       model=Mock(complete=Mock(return_value="\ud800")))

    def test_lone_surrogate_review_answer_is_controlled_failure(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import PoolError, run_review, run_worker
        first = [run_worker(self.job, worker, base_url="http://127.0.0.1:11434/v1",
                            model=Mock(complete=Mock(return_value="7")))
                 for worker in self.workers]
        with self.assertRaisesRegex(PoolError, "Unicode"):
            run_review(self.job, first, "vn1", base_url="http://127.0.0.1:11434/v1",
                       model=Mock(complete=Mock(return_value="\ud800")))

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

    def test_windows_utf8_bom_config_is_read_as_json(self):
        import tempfile
        from pathlib import Path
        from rezon.trainingday_pool import load_json
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "workers.json"
            path.write_bytes(b"\xef\xbb\xbf" + b'{"vn1":"qwen","vn2":"granite"}')
            self.assertEqual(load_json(path)["vn1"], "qwen")


    def test_second_round_peer_review_cannot_see_oracle(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import run_worker, run_review, collect_reviews
        first = [
            run_worker(self.job, worker, base_url="http://127.0.0.1:11434/v1",
                       model=Mock(complete=Mock(return_value="999999")))
            for worker in self.workers
        ]
        fake_model = Mock(complete=Mock(return_value="0"))
        reviewed = [
            run_review(self.job, first, worker, base_url="http://127.0.0.1:11434/v1",
                       model=fake_model)
            for worker in self.workers
        ]
        summary, rows = collect_reviews(self.job, self.oracle, first, reviewed)
        self.assertEqual(summary["workers_completed"], 2)
        self.assertEqual(summary["review_workers_completed"], 2)
        self.assertEqual(summary["model_exact_total"], 0)
        self.assertEqual(summary["review_model_exact_total"], sum(
            r["answer"] == 0 for r in self.oracle["cases"]) * 2)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(r["qualified_for_neural_training"] is False for r in rows))
        for call in fake_model.complete.call_args_list:
            self.assertNotIn('"answer":', str(call))

    def test_peer_review_digest_must_bind_exact_first_round(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import run_worker, run_review, collect_reviews, PoolError
        first = [
            run_worker(self.job, worker, base_url="http://127.0.0.1:11434/v1",
                       model=Mock(complete=Mock(return_value="7")))
            for worker in self.workers
        ]
        reviewed = [
            run_review(self.job, first, worker, base_url="http://127.0.0.1:11434/v1",
                       model=Mock(complete=Mock(return_value="8")))
            for worker in self.workers
        ]
        reviewed[0]["peer_receipts_sha256"] = "f" * 64
        with self.assertRaisesRegex(PoolError, "peer"):
            collect_reviews(self.job, self.oracle, first, reviewed)

    def test_consistently_poisoned_oracle_must_match_literal_question(self):
        from rezon.trainingday_pool import PoolError, collect
        altered = json.loads(json.dumps(self.oracle))
        case = altered["cases"][0]
        # Change both operations and the answer together; each passes a
        # simple replay, but the literal public question is now different.
        case["operations"][0] = ["add", 30000]
        value = case["start"]
        for op, n in case["operations"]:
            value = {"add": lambda a,b:a+b, "subtract":lambda a,b:a-b,
                     "multiply":lambda a,b:a*b}[op](value,n)
        case["answer"] = value
        with self.assertRaisesRegex(PoolError, "oracle"):
            collect(self.job, altered, [])

    def test_candidate_provenance_does_not_claim_two_independent_oracles(self):
        from unittest.mock import Mock
        from rezon.trainingday_pool import collect, run_worker
        first = [run_worker(self.job, w, base_url="http://localhost:11434/v1",
                            model=Mock(complete=Mock(return_value="99")))
                 for w in self.workers]
        _, rows = collect(self.job, self.oracle, first)
        self.assertEqual(rows[0]["source"], "SYNTHETIC_ORIGINAL_INTEGER_REPLAY_V1")
