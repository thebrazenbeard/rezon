"""R29 three-plane synthetic protocol interoperability; no physical work."""

from __future__ import annotations

import copy
import hashlib
import hmac
import unittest
from unittest.mock import patch

from rezon.trainingday_pool import _digest, build_job
import rezon.trainingday_r29_interop as interop_module
from rezon.trainingday_receipt_custody import (
    SCHEMA as RECEIPT_SCHEMA, build_synthetic_corpus_claim,
    signing_payload_digest,
)
from rezon.trainingday_r29_interop import InteropScenarioError, assess_interop


RUN = "a" * 64
TENSOR = "b" * 64


def lease(kind, t, *, actor="host-shadow", epoch=0, lid="", ttl=0):
    return {"kind": kind, "actor": actor, "host": "lappy", "lease": lid,
            "epoch": epoch, "mono_ms": t, "wall_ms": t, "ttl_ms": ttl}


def recovery(kind, t, *, actor="host-shadow", node="lappy", epoch=0,
             step=0, digest=""):
    return {"kind": kind, "actor": actor, "node": node, "epoch": epoch,
            "step": step, "mono_ms": t, "wall_ms": t, "digest": digest}


def ack(node, receipt_hash, t, *, kind="ACK", generation=1, epoch=1,
        step=1, sequence=1):
    return {"kind": kind, "node": node, "receipt_sha256": receipt_hash,
            "generation": generation, "epoch": epoch, "step": step,
            "mono_ms": t, "sequence": sequence}


class InteroperabilityTests(unittest.TestCase):
    def setUp(self):
        self.job, _ = build_job(seed=819, count=2, workers={
            "lappy_worker": "local-qwen-lappy", "vn1_worker": "local-qwen-vn1",
            "vn2_worker": "local-qwen-vn2",
        })
        self.corpus = build_synthetic_corpus_claim(self.job)
        self.routes = {"lappy_worker": "lappy", "vn1_worker": "vn1",
                       "vn2_worker": "vn2"}
        self.keys = {w: ("fake-key-" + w).encode("ascii")
                     for w in self.job["workers"]}
        self.receipts = []
        for worker in self.job["workers"]:
            row = {"schema": RECEIPT_SCHEMA + ".inference",
                   "job_sha256": self.job["job_sha256"],
                   "corpus_sha256": self.corpus["corpus_sha256"],
                   "worker": worker, "device": self.routes[worker],
                   "model_id": self.job["workers"][worker],
                   "kind": "INFERENCE_RESULT_CLAIM", "issued_at_unix": 1000,
                   "nonce": worker + "-nonce-01",
                   "output_sha256": _digest({"worker": worker}),
                   "signature": "0" * 64}
            row["signature"] = hmac.new(self.keys[worker],
                signing_payload_digest(row), hashlib.sha256).hexdigest()
            row["receipt_sha256"] = _digest(row)
            self.receipts.append(row)
        self.lease_events = [lease("WAKE", 0), lease("TUNNEL_RESTORED", 1),
                             lease("HOST_IDLE", 2), lease("EXECUTOR_IDLE", 3),
                             lease("REQUEST", 6, actor="root-a", epoch=1,
                                   lid="lease-a", ttl=30000)]
        self.recovery_events = [
            recovery("WAKE", 0), recovery("TUNNEL_UP", 1),
            recovery("TUNNEL_UP", 2, node="vn1"),
            recovery("TUNNEL_UP", 3, node="vn2"),
            recovery("WORKER_RESUME", 4, actor="worker-shadow", node="vn1"),
            recovery("WORKER_RESUME", 5, actor="worker-shadow", node="vn2"),
            recovery("ACQUIRE", 6, actor="root-a", epoch=1),
            recovery("BEGIN_STEP", 7, actor="root-a", epoch=1, step=1),
            recovery("PARTIAL_WRITE", 8, actor="root-a", epoch=1,
                     step=1, digest=TENSOR),
            recovery("SEAL", 9, actor="root-a", epoch=1,
                     step=1, digest=TENSOR),
            recovery("COMMIT", 10, actor="root-a", epoch=1,
                     step=1, digest=TENSOR),
            recovery("CLAIM_SUCCESS", 11, actor="root-a", epoch=1,
                     step=1, digest=TENSOR),
        ]
        self.ack_events = [ack(r["device"], r["receipt_sha256"], 12 + i)
                           for i, r in enumerate(self.receipts)]

    def verifier(self, data, signature, worker):
        return hmac.compare_digest(hmac.new(self.keys[worker], data,
                                           hashlib.sha256).hexdigest(), signature)

    def assess(self, *, acks=None, leases=None, recovery_rows=None,
               receipts=None, verifier=None):
        return assess_interop(
            RUN, self.job, self.corpus, self.routes,
            self.receipts if receipts is None else receipts,
            now_unix=1001, verify_claim=self.verifier if verifier is None else verifier,
            lease_events=self.lease_events if leases is None else leases,
            recovery_events=self.recovery_events if recovery_rows is None else recovery_rows,
            ack_events=self.ack_events if acks is None else acks,
        )

    def test_clean_three_node_source_chain_remains_hold(self):
        r = self.assess()
        self.assertEqual(r["fault_reasons"], [])
        self.assertEqual(r["accepted_synthetic_ack_nodes"], ["lappy", "vn1", "vn2"])
        self.assertEqual(r["source_level_synchronized_generations"], [1])
        self.assertEqual(r["status"], "SOURCE_ONLY_HOLD")
        self.assertFalse(r["authorizes_optimizer_start"])
        self.assertFalse(r["distributed_gradients_proven"])
        self.assertEqual(r["physical_optimizer_steps_executed"], 0)

    def test_reordered_ack_deliveries_normalize_content_digest(self):
        a = self.assess()
        b = self.assess(acks=list(reversed(self.ack_events)))
        self.assertEqual(a["interop_sha256"], b["interop_sha256"])
        self.assertEqual(a["fault_reasons"], b["fault_reasons"])

    def test_unsolicited_ack_rejected(self):
        extra = ack("vn1", "f" * 64, 15, sequence=2)
        r = self.assess(acks=self.ack_events + [extra])
        self.assertIn("UNSOLICITED_ACK", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_conflicting_generation_epoch_and_step_rejected(self):
        for key, value, reason in [
            ("generation", 2, "GENERATION_NOT_COMMITTED"),
            ("epoch", 2, "FENCED_GENERATION_MISMATCH"),
            ("step", 2, "ACK_STEP_GENERATION_CONFLICT"),
        ]:
            rows = copy.deepcopy(self.ack_events)
            rows[1][key] = value
            with self.subTest(key=key):
                self.assertIn(reason, self.assess(acks=rows)["fault_reasons"])

    def test_future_generation_cannot_reuse_unbound_inference_receipt(self):
        # R25 inference receipts contain no training generation binding.
        # A second generation cannot bootstrap training evidence by replay.
        rows = self.recovery_events + [
            recovery("BEGIN_STEP", 12, actor="root-a", epoch=1, step=2),
            recovery("PARTIAL_WRITE", 13, actor="root-a", epoch=1,
                     step=2, digest="c" * 64),
            recovery("SEAL", 14, actor="root-a", epoch=1,
                     step=2, digest="c" * 64),
            recovery("COMMIT", 15, actor="root-a", epoch=1,
                     step=2, digest="c" * 64),
            recovery("CLAIM_SUCCESS", 16, actor="root-a", epoch=1,
                     step=2, digest="c" * 64),
        ]
        acks = [ack(r["device"], r["receipt_sha256"], 17 + i,
                    generation=2, step=2) for i, r in enumerate(self.receipts)]
        verdict = self.assess(recovery_rows=rows, acks=acks)
        self.assertIn("GENERATION_RECEIPT_UNBOUND", verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_partition_reconnect_without_recovery_cannot_replay_success(self):
        rows = self.recovery_events[:-5] + [
            recovery("TUNNEL_DOWN", 7, node="vn1"),
            recovery("COMMIT", 8, actor="root-a", epoch=1,
                     step=1, digest=TENSOR),
            recovery("WAKE", 9),
            recovery("TUNNEL_UP", 10),
            recovery("TUNNEL_UP", 11, node="vn1"),
            recovery("TUNNEL_UP", 12, node="vn2"),
            recovery("WORKER_RESUME", 13, actor="worker-shadow", node="vn1"),
            recovery("WORKER_RESUME", 14, actor="worker-shadow", node="vn2"),
            recovery("FENCE_ACK", 15, epoch=2),  # old lease unexpired
            recovery("ACQUIRE", 16, actor="root-b", epoch=2),
        ]
        r = self.assess(recovery_rows=rows)
        self.assertIn("RECOVERY_DENIAL", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_expired_lease_cannot_cross_authorize_recovery(self):
        rows = self.lease_events + [lease("RENEW", 40000, actor="root-a",
                                         epoch=1, lid="lease-a", ttl=30000)]
        r = self.assess(leases=rows)
        self.assertIn("LEASE_DENIAL", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_ack_after_shadow_lease_expiry_denied_without_long_delay(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6,
            actor="root-a", epoch=1, lid="lease-a", ttl=4)]
        r = self.assess(leases=leases)
        self.assertIn("ACK_AFTER_LEASE_EXPIRY", r["fault_reasons"])

    def test_ack_before_clean_release_still_valid_on_historical_interval(self):
        # Release at t50 must not retroactively revoke three ACKs at t12..14.
        leases = self.lease_events + [lease("RELEASE", 50, actor="root-a",
                                             epoch=1, lid="lease-a")]
        recovery_rows = self.recovery_events + [recovery("RELEASE", 50,
                                                          actor="root-a", epoch=1)]
        r = self.assess(leases=leases, recovery_rows=recovery_rows)
        self.assertEqual(r["fault_reasons"], [])
        self.assertEqual(r["source_level_synchronized_generations"], [1])

    def test_ack_after_clean_release_rejected_without_retroactive_acceptance(self):
        leases = self.lease_events + [lease("RELEASE", 50, actor="root-a",
                                             epoch=1, lid="lease-a")]
        recovery_rows = self.recovery_events + [recovery("RELEASE", 50,
                                                          actor="root-a", epoch=1)]
        acks = copy.deepcopy(self.ack_events)
        acks[-1]["mono_ms"] = 51
        r = self.assess(leases=leases, recovery_rows=recovery_rows, acks=acks)
        self.assertIn("ACK_AFTER_LEASE_EXPIRY", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_unrestored_node_partition_after_commit_cannot_ack(self):
        rows = self.recovery_events + [
            recovery("TUNNEL_DOWN", 12, node="vn2")]
        r = self.assess(recovery_rows=rows)
        self.assertIn("ACK_WITHOUT_LIVE_RECOVERY_WITNESS", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_standby_after_commit_before_ack_denies_synthetic_success(self):
        rows = self.recovery_events + [recovery("STANDBY", 12)]
        r = self.assess(recovery_rows=rows)
        self.assertIn("ACK_WITHOUT_LIVE_RECOVERY_WITNESS", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_reconnect_cannot_retroactively_attest_buffered_ack(self):
        rows = self.recovery_events + [
            recovery("TUNNEL_DOWN", 12, node="vn2"),
            recovery("WAKE", 13),
            recovery("TUNNEL_UP", 14),
            recovery("TUNNEL_UP", 15, node="vn1"),
            recovery("TUNNEL_UP", 16, node="vn2"),
            recovery("WORKER_RESUME", 17, actor="worker-shadow", node="vn1"),
            recovery("WORKER_RESUME", 18, actor="worker-shadow", node="vn2"),
        ]
        acks = [ack(r["device"], r["receipt_sha256"], 20 + i)
                for i, r in enumerate(self.receipts)]
        r = self.assess(recovery_rows=rows, acks=acks)
        self.assertIn("ACK_SPANS_UNATTESTED_RECOVERY_FAULT", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_r28_wake_witness_stale_at_ack_blocks_source_success(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6,
            actor="root-a", epoch=1, lid="lease-a", ttl=120000)]
        # COMMIT t10, ACK t30009 is within R29's 30s ACK delay, but
        # the R28 host WAKE t0 is already 30009ms old.
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 30009
        verdict = self.assess(leases=leases, acks=acks)
        self.assertIn("ACK_WITHOUT_FRESH_RECOVERY_WITNESS",
                      verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_r28_node_tunnel_witness_stale_despite_new_wake(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6,
            actor="root-a", epoch=1, lid="lease-a", ttl=120000)]
        rows = self.recovery_events + [recovery("WAKE", 20)]
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 30004
        verdict = self.assess(leases=leases, recovery_rows=rows, acks=acks)
        self.assertIn("ACK_WITHOUT_FRESH_RECOVERY_WITNESS",
                      verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_r28_worker_resume_witness_stale_after_tunnel_refresh(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6,
            actor="root-a", epoch=1, lid="lease-a", ttl=120000)]
        rows = self.recovery_events + [
            recovery("WAKE", 20),
            recovery("TUNNEL_UP", 21),
            recovery("TUNNEL_UP", 22, node="vn1"),
            recovery("TUNNEL_UP", 23, node="vn2"),
        ]
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 30006
        verdict = self.assess(leases=leases, recovery_rows=rows, acks=acks)
        self.assertIn("ACK_WITHOUT_FRESH_RECOVERY_WITNESS",
                      verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_exact_r28_30000ms_wake_boundary_remains_admissible_source_only(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6,
            actor="root-a", epoch=1, lid="lease-a", ttl=120000)]
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 30000
        verdict = self.assess(leases=leases, acks=acks)
        self.assertEqual(verdict["fault_reasons"], [])
        self.assertEqual(verdict["source_level_synchronized_generations"], [1])
        self.assertFalse(verdict["host_lease_authenticated"])

    def test_same_timestamp_recovery_witness_cannot_precede_ack_without_order(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6,
            actor="root-a", epoch=1, lid="lease-a", ttl=120000)]
        rows = self.recovery_events + [
            recovery("WAKE", 30009),
            recovery("TUNNEL_UP", 30009),
            recovery("TUNNEL_UP", 30009, node="vn1"),
            recovery("TUNNEL_UP", 30009, node="vn2"),
            recovery("WORKER_RESUME", 30009, actor="worker-shadow", node="vn1"),
            recovery("WORKER_RESUME", 30009, actor="worker-shadow", node="vn2"),
        ]
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 30009
        verdict = self.assess(leases=leases, recovery_rows=rows, acks=acks)
        self.assertIn("ACK_WITHOUT_FRESH_RECOVERY_WITNESS",
                      verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_recovery_witness_one_tick_before_ack_is_source_admissible(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6,
            actor="root-a", epoch=1, lid="lease-a", ttl=120000)]
        rows = self.recovery_events + [
            recovery("WAKE", 30008),
            recovery("TUNNEL_UP", 30008),
            recovery("TUNNEL_UP", 30008, node="vn1"),
            recovery("TUNNEL_UP", 30008, node="vn2"),
            recovery("WORKER_RESUME", 30008, actor="worker-shadow", node="vn1"),
            recovery("WORKER_RESUME", 30008, actor="worker-shadow", node="vn2"),
        ]
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 30009
        verdict = self.assess(leases=leases, recovery_rows=rows, acks=acks)
        self.assertEqual(verdict["fault_reasons"], [])
        self.assertEqual(verdict["source_level_synchronized_generations"], [1])

    def test_ack_at_commit_before_success_claim_never_completes_generation(self):
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 10  # COMMIT t10, accepted CLAIM_SUCCESS t11
        verdict = self.assess(acks=acks)
        self.assertIn("ACK_NOT_AFTER_SUCCESS_CLAIM", verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_ack_same_tick_as_success_claim_has_no_causal_order(self):
        acks = copy.deepcopy(self.ack_events)
        for row in acks:
            row["mono_ms"] = 11  # Same timestamp as CLAIM_SUCCESS
        verdict = self.assess(acks=acks)
        self.assertIn("ACK_NOT_AFTER_SUCCESS_CLAIM", verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_later_success_claim_cannot_retroactively_validate_prior_ack(self):
        rows = self.recovery_events[:-1] + [
            recovery("CLAIM_SUCCESS", 50, actor="root-a", epoch=1,
                     step=1, digest=TENSOR)]
        verdict = self.assess(recovery_rows=rows)
        self.assertIn("ACK_NOT_AFTER_SUCCESS_CLAIM", verdict["fault_reasons"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [])

    def test_nested_dict_subclass_cannot_launder_spoofed_worker(self):
        class Launder(dict):
            def items(self):
                return ((k, v) for k, v in dict.items(self)
                        if k != "spoofed_worker")

        self.job = copy.deepcopy(self.job)
        self.job["workers"] = Launder(self.job["workers"])
        self.job["workers"]["spoofed_worker"] = "intruding-model"
        with self.assertRaises(InteropScenarioError):
            self.assess()

    def test_nested_list_subclass_rejected_before_iteration(self):
        class LaunderList(list):
            def __iter__(self):
                raise AssertionError("custom iterator must never execute")

        self.job = copy.deepcopy(self.job)
        self.job["cases"] = LaunderList(self.job["cases"])
        with self.assertRaises(InteropScenarioError):
            self.assess()

    def test_nested_scalar_subclasses_rejected_across_protocol_planes(self):
        class DeceptiveStr(str):
            def __str__(self):
                raise AssertionError("str conversion hook must never execute")

        receipts = copy.deepcopy(self.receipts)
        receipts[0]["signature"] = DeceptiveStr(receipts[0]["signature"])
        leases = copy.deepcopy(self.lease_events)
        leases[-1]["lease"] = DeceptiveStr("lease-a")
        recovery_rows = copy.deepcopy(self.recovery_events)
        recovery_rows[0]["kind"] = DeceptiveStr("WAKE")
        acks = copy.deepcopy(self.ack_events)
        acks[0]["node"] = DeceptiveStr("lappy")
        for override in ({"receipts": receipts}, {"leases": leases},
                         {"recovery_rows": recovery_rows}, {"acks": acks}):
            with self.subTest(plane=next(iter(override))):
                with self.assertRaises(InteropScenarioError):
                    self.assess(**override)

    def test_nested_caller_mutation_during_first_dump_cannot_touch_snapshot(self):
        original = self.assess()
        actual_dumps = interop_module.json.dumps
        observed = []

        class Launder(dict):
            def items(self):
                raise AssertionError("custom items hook must never execute")

        def mutate_then_dump(value, *args, **kwargs):
            if not observed:
                observed.append(True)
                # Directly after the type check, before the first JSON dump.
                self.job["workers"] = Launder(self.job["workers"])
                self.job["workers"]["spoofed_worker"] = "intruding-model"
                self.assertIsNot(value["job"], self.job)
                self.assertIsNot(value["job"]["workers"], self.job["workers"])
                self.assertIsNot(value["receipts"], self.receipts)
            return actual_dumps(value, *args, **kwargs)

        with patch.object(interop_module.json, "dumps", side_effect=mutate_then_dump):
            verdict = self.assess()
        self.assertTrue(observed)
        self.assertEqual(verdict["interop_sha256"], original["interop_sha256"])
        self.assertEqual(verdict["source_level_synchronized_generations"], [1])

    def test_cross_plane_commit_cannot_precede_claimed_lease_start(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 1000,
            actor="root-a", epoch=1, lid="lease-a", ttl=30000)]
        r = self.assess(leases=leases)
        self.assertIn("COMMIT_PRECEDES_LEASE_START", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_delayed_and_premature_ack_cannot_inflate_progress(self):
        late = copy.deepcopy(self.ack_events)
        late[0]["mono_ms"] = 30_050
        r = self.assess(acks=late)
        self.assertIn("DELAYED_NODE_ACK", r["fault_reasons"])
        early = copy.deepcopy(self.ack_events)
        early[1]["mono_ms"] = 9
        r = self.assess(acks=early)
        self.assertIn("ACK_BEFORE_GENERATION_COMMIT", r["fault_reasons"])

    def test_checkpoint_rollover_without_new_generation_is_denied(self):
        rows = self.recovery_events + [
            recovery("ROLLOVER", 12, actor="root-a", epoch=1,
                     step=1, digest=TENSOR)]
        r = self.assess(recovery_rows=rows)
        self.assertIn("RECOVERY_DENIAL", r["fault_reasons"])

    def test_delayed_worker_and_false_progress_do_not_count(self):
        acks = self.ack_events[:-1]
        r = self.assess(acks=acks)
        self.assertEqual(r["source_level_synchronized_generations"], [])
        self.assertIn("MISSING_NODE_ACK", r["fault_reasons"])
        progress = ack("vn2", self.ack_events[-1]["receipt_sha256"], 100000,
                       kind="PROGRESS")
        r = self.assess(acks=acks + [progress])
        self.assertIn("UNVERIFIED_PROGRESS", r["fault_reasons"])

    def test_duplicate_ack_and_optimizer_claims_are_not_gradient_evidence(self):
        duplicate = copy.deepcopy(self.ack_events[0])
        optimizer = ack("lappy", self.ack_events[0]["receipt_sha256"], 16,
                        kind="OPTIMIZER_CLAIM", sequence=2)
        r = self.assess(acks=self.ack_events + [duplicate, optimizer])
        self.assertIn("REPLAYED_ACK", r["fault_reasons"])
        self.assertIn("UNVERIFIED_OPTIMIZER_CLAIM", r["fault_reasons"])
        self.assertEqual(r["physical_optimizer_steps_executed"], 0)

    def test_conflicting_same_node_sequence_is_rejected(self):
        conflict = copy.deepcopy(self.ack_events[0])
        conflict["generation"] = 2
        r = self.assess(acks=self.ack_events + [conflict])
        self.assertIn("CONFLICTING_ACK_SEQUENCE", r["fault_reasons"])

    def test_cross_module_mismatched_coordinator_owner_is_denied(self):
        leases = self.lease_events[:-1] + [lease("REQUEST", 6, actor="root-b",
                                                  epoch=1, lid="lease-b", ttl=30000)]
        r = self.assess(leases=leases)
        self.assertIn("CROSS_PLANE_OWNER_MISMATCH", r["fault_reasons"])

    def test_receipt_custody_incomplete_denies_interop(self):
        r = self.assess(receipts=self.receipts[:2])
        self.assertIn("CUSTODY_BLOCKER", r["fault_reasons"])
        self.assertEqual(r["source_level_synchronized_generations"], [])

    def test_bad_envelopes_fail_closed(self):
        with self.assertRaises(InteropScenarioError):
            self.assess(acks=[{"wrong": 1}])
        with self.assertRaises(InteropScenarioError):
            self.assess(acks=self.ack_events * 43)
        with self.assertRaises(InteropScenarioError):
            self.assess(acks=[{**self.ack_events[0], "sequence": True}])

    def test_callback_mutation_does_not_change_committed_snapshot(self):
        original = self.assess()
        def mutate(data, signature, worker):
            self.ack_events[0]["generation"] = 99
            return self.verifier(data, signature, worker)
        r = self.assess(verifier=mutate)
        self.assertEqual(original["interop_sha256"], r["interop_sha256"])
        self.assertEqual(original["accepted_synthetic_ack_nodes"],
                         r["accepted_synthetic_ack_nodes"])


if __name__ == "__main__":
    unittest.main()
