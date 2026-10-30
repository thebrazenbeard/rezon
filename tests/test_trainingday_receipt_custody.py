"""R25 synthetic Lappy/VN1/VN2 receipt custody; never probes hosts or keys."""

import copy
import hashlib
import hmac
import unittest
from unittest.mock import patch

from rezon.trainingday_pool import PoolError, _digest, build_job
from rezon.trainingday_receipt_custody import (
    SCHEMA, assess_synthetic_three_node_chain, build_synthetic_corpus_claim,
    signing_payload_digest,
)


class ThreeNodeReceiptCustodyTests(unittest.TestCase):
    def setUp(self):
        self.job, _ = build_job(seed=715, count=2, workers={
            "lappy_worker": "local-qwen-lappy", "vn1_worker": "local-qwen-vn1",
            "vn2_worker": "local-qwen-vn2",
        })
        self.corpus = build_synthetic_corpus_claim(self.job)
        self.routes = {
            "lappy_worker": "lappy", "vn1_worker": "vn1", "vn2_worker": "vn2",
        }
        self.secrets = {worker: ("synthetic-key-" + worker).encode("ascii")
                        for worker in self.job["workers"]}
        self.receipts = [self.make_receipt(worker) for worker in self.job["workers"]]

    def sign(self, payload, worker):
        return hmac.new(self.secrets[worker], payload, hashlib.sha256).hexdigest()

    def verify(self, payload, signature, worker):
        return hmac.compare_digest(self.sign(payload, worker), signature)

    def make_receipt(self, worker, *, issued=1000, nonce=None, output=None):
        receipt = {
            "schema": SCHEMA + ".inference",
            "job_sha256": self.job["job_sha256"],
            "corpus_sha256": self.corpus["corpus_sha256"],
            "worker": worker,
            "device": self.routes[worker],
            "model_id": self.job["workers"][worker],
            "kind": "INFERENCE_RESULT_CLAIM",
            "issued_at_unix": issued,
            "nonce": nonce or (worker + "-nonce-001"),
            "output_sha256": output or _digest({"synthetic_answer": worker}),
            "signature": "0" * 64,
        }
        receipt["signature"] = self.sign(signing_payload_digest(receipt), worker)
        receipt["receipt_sha256"] = _digest(receipt)
        return receipt

    def assess(self, receipts=None, *, routes=None, corpus=None, now=1001, verify=None):
        return assess_synthetic_three_node_chain(
            self.job, self.corpus if corpus is None else corpus,
            self.routes if routes is None else routes,
            self.receipts if receipts is None else receipts,
            now_unix=now,
            verify_claim=self.verify if verify is None else verify,
        )

    def test_synthetic_public_content_is_hashed_but_not_admitted_for_training(self):
        again = build_synthetic_corpus_claim(self.job)
        self.assertEqual(self.corpus, again)
        self.assertEqual(len(self.corpus["case_handles"]), 2)
        self.assertEqual(self.corpus["rights_status"],
                         "UNVERIFIED_NO_TRAINING_ADMISSION")
        self.assertFalse(self.assess()["training_candidate_admitted"])
        self.assertNotIn(self.job["cases"][0]["prompt"], str(self.corpus))

    def test_complete_synthetic_three_node_chain_never_authorizes_dispatch(self):
        result = self.assess()
        self.assertTrue(result["source_level_chain_complete"])
        self.assertEqual(result["unique_worker_receipts"], 3)
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["status"], "HOLD_SYNTHETIC_CHAIN")
        self.assertFalse(result["dispatch_authorized"])
        self.assertFalse(result["host_identity_authenticated"])
        self.assertFalse(result["host_lease_authenticated"])
        self.assertFalse(result["signature_trust_anchor_authenticated"])
        self.assertFalse(result["shared_gradient_computation_proven"])

    def test_transport_order_does_not_change_aggregate_digest(self):
        original = self.assess()
        reversed_receipts = self.assess(receipts=list(reversed(self.receipts)))
        self.assertEqual(original["assessment_sha256"], reversed_receipts["assessment_sha256"])

    def test_missing_worker_receipt_stays_on_hold(self):
        partial = self.assess(receipts=self.receipts[:2])
        self.assertFalse(partial["source_level_chain_complete"])
        self.assertEqual(partial["unique_worker_receipts"], 2)
        self.assertEqual(partial["missing_workers"], ["vn2_worker"])
        self.assertIn("INCOMPLETE_THREE_NODE_RECEIPTS", partial["blockers"])

    def test_identical_retry_is_collapsed_and_evidenced(self):
        replay = self.assess(receipts=self.receipts + [copy.deepcopy(self.receipts[0])])
        self.assertEqual(replay["unique_worker_receipts"], 3)
        self.assertEqual(replay["delivery_count"], 4)
        self.assertEqual(replay["duplicate_deliveries_collapsed"], 1)
        self.assertIn("REPLAYED_RECEIPT_COLLAPSED", replay["blockers"])
        self.assertFalse(replay["dispatch_authorized"])

    def test_conflicting_retry_same_worker_rejected(self):
        conflicting = self.make_receipt("lappy_worker", nonce="lappy_worker-nonce-002",
                                        output=_digest({"different": "output"}))
        with self.assertRaisesRegex(PoolError, "conflicting duplicate"):
            self.assess(receipts=self.receipts + [conflicting])

    def test_reused_nonce_with_changed_output_rejected(self):
        conflicting = self.make_receipt("lappy_worker",
                                        output=_digest({"different": "output"}))
        with self.assertRaisesRegex(PoolError, "nonce reuse"):
            self.assess(receipts=self.receipts + [conflicting])

    def test_forged_signature_rehashed_receipt_still_fails_check(self):
        forged = copy.deepcopy(self.receipts)
        forged[1]["signature"] = "f" * 64
        forged[1]["receipt_sha256"] = _digest({
            k: v for k, v in forged[1].items() if k != "receipt_sha256"})
        verdict = self.assess(receipts=forged)
        self.assertIn("SYNTHETIC_SIGNATURE_CLAIM_INVALID", verdict["blockers"])
        self.assertFalse(verdict["source_level_chain_complete"])

    def test_missing_or_crashing_verifier_is_not_host_identity(self):
        none = assess_synthetic_three_node_chain(
            self.job, self.corpus, self.routes, self.receipts, now_unix=1001,
            verify_claim=None,
        )
        self.assertIn("NO_EXTERNAL_SIGNATURE_VERIFIER", none["blockers"])
        def crash(*_):
            raise RuntimeError("synthetic verifier unavailable")
        failed = self.assess(verify=crash)
        self.assertIn("SYNTHETIC_SIGNATURE_CLAIM_INVALID", failed["blockers"])
        self.assertFalse(failed["host_identity_authenticated"])

    def test_stale_and_future_receipts_block_aggregation(self):
        stale = copy.deepcopy(self.receipts)
        stale[0] = self.make_receipt("lappy_worker", issued=960)
        self.assertIn("STALE_OR_FUTURE_RECEIPT", self.assess(receipts=stale)["blockers"])
        future = copy.deepcopy(self.receipts)
        future[0] = self.make_receipt("lappy_worker", issued=1002)
        self.assertIn("STALE_OR_FUTURE_RECEIPT", self.assess(receipts=future)["blockers"])

    def test_tampered_job_or_corpus_cannot_be_silently_mixed(self):
        corrupt_job = copy.deepcopy(self.job)
        corrupt_job["seed"] += 1
        with self.assertRaises(PoolError):
            assess_synthetic_three_node_chain(corrupt_job, self.corpus, self.routes,
                                              self.receipts, now_unix=1001)
        corrupt = copy.deepcopy(self.corpus)
        corrupt["case_handles"][0]["prompt_sha256"] = "0" * 64
        with self.assertRaisesRegex(PoolError, "corpus content-addressed"):
            self.assess(corpus=corrupt)

    def test_wrong_worker_device_and_job_hash_rejected(self):
        rows = copy.deepcopy(self.receipts)
        rows[0]["device"] = "vn2"
        rows[0]["receipt_sha256"] = _digest({
            k: v for k, v in rows[0].items() if k != "receipt_sha256"})
        with self.assertRaisesRegex(PoolError, "binding mismatch"):
            self.assess(receipts=rows)
        rows = copy.deepcopy(self.receipts)
        rows[0]["job_sha256"] = "0" * 64
        rows[0]["receipt_sha256"] = _digest({
            k: v for k, v in rows[0].items() if k != "receipt_sha256"})
        with self.assertRaisesRegex(PoolError, "binding mismatch"):
            self.assess(receipts=rows)

    def test_training_gradient_evidence_is_never_accepted_as_inference(self):
        rows = copy.deepcopy(self.receipts)
        rows[0]["kind"] = "TRAINING_GRADIENT_UPDATE"
        with self.assertRaisesRegex(PoolError, "declaration malformed"):
            self.assess(receipts=rows)

    def test_receipt_replay_bounded_to_four_claims_per_worker(self):
        rows = self.receipts + [copy.deepcopy(self.receipts[0]) for _ in range(4)]
        with self.assertRaisesRegex(PoolError, "replay limit"):
            self.assess(receipts=rows)

    def test_overlimit_and_malformed_inputs_reject_before_deep_snapshot(self):
        overlimit = self.receipts * 5  # 15 > three hosts * four deliveries
        # Assert that expensive snapshot/canonicalization is not called at all.
        with patch("rezon.trainingday_receipt_custody._canonical_claim_bytes",
                   side_effect=AssertionError("unbounded preflight reached snapshot")):
            with self.assertRaisesRegex(PoolError, "unbounded"):
                self.assess(receipts=overlimit)
            with self.assertRaisesRegex(PoolError, "route declaration"):
                self.assess(routes={"bad": "lappy"})
            malformed = copy.deepcopy(self.receipts)
            malformed[0]["output_sha256"] = "a" * 10000
            with self.assertRaisesRegex(PoolError, "receipt declaration malformed"):
                self.assess(receipts=malformed)

    def test_invalid_declarations_get_controlled_poolerror(self):
        for bad in (float("nan"), object(), [], {"device": "lappy"}):
            with self.subTest(value=type(bad).__name__):
                routes = dict(self.routes, lappy_worker=bad)
                with self.assertRaises(PoolError):
                    self.assess(routes=routes)
        with self.assertRaises(PoolError):
            self.assess(now=True)

    def test_no_atomic_host_lease_from_two_identical_coordinators(self):
        a = self.assess()
        b = self.assess()
        self.assertEqual(a["assessment_sha256"], b["assessment_sha256"])
        self.assertFalse(a["host_lease_authenticated"])
        self.assertFalse(b["host_lease_authenticated"])

    def test_verifier_mutation_of_receipt_route_job_or_corpus_is_not_silent(self):
        for target in ("receipt", "route", "job", "corpus"):
            with self.subTest(target=target):
                job = copy.deepcopy(self.job)
                corpus = copy.deepcopy(self.corpus)
                routes = copy.deepcopy(self.routes)
                receipts = copy.deepcopy(self.receipts)

                def verifier(_payload, _signature, _worker):
                    if target == "receipt":
                        receipts[0]["output_sha256"] = "0" * 64
                    elif target == "route":
                        routes["vn2_worker"] = "lappy"
                    elif target == "job":
                        job["workers"]["vn2_worker"] = "tampered-model"
                    else:
                        corpus["rights_status"] = "FABRICATED_ADMITTED"
                    return True

                result = assess_synthetic_three_node_chain(
                    job, corpus, routes, receipts,
                    now_unix=1001, verify_claim=verifier,
                )
                self.assertIn("INPUT_CHANGED_DURING_VERIFICATION", result["blockers"])
                self.assertFalse(result["source_level_chain_complete"])
                self.assertFalse(result["dispatch_authorized"])
                self.assertFalse(result["training_candidate_admitted"])

    def test_mutating_verifier_cannot_insert_nonserializable_claim_after_freeze(self):
        routes = copy.deepcopy(self.routes)

        def verifier(*_):
            routes["vn2_worker"] = object()
            return True

        result = self.assess(routes=routes, verify=verifier)
        self.assertIn("INPUT_CHANGED_DURING_VERIFICATION", result["blockers"])
        self.assertFalse(result["source_level_chain_complete"])


if __name__ == "__main__":
    unittest.main()
