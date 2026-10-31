"""Public synthetic R28 fault/recovery matrix; never controls real hosts."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import rezon.trainingday_r28_recovery_sim as recovery_module

from rezon.trainingday_r28_recovery_sim import (
    MAX_EVENTS, RecoveryScenarioError, simulate_recovery,
)


RUN = "a" * 64
A = "b" * 64
B = "c" * 64


def ev(kind, tick, *, actor="host-shadow", node="lappy", epoch=0,
       step=0, digest="", wall=None):
    return {"kind": kind, "actor": actor, "node": node, "epoch": epoch,
            "step": step, "mono_ms": tick,
            "wall_ms": tick if wall is None else wall, "digest": digest}


def ready(t=0):
    return [
        ev("WAKE", t),
        ev("TUNNEL_UP", t + 1),
        ev("TUNNEL_UP", t + 2, node="vn1"),
        ev("TUNNEL_UP", t + 3, node="vn2"),
        ev("WORKER_RESUME", t + 4, actor="worker-shadow", node="vn1"),
        ev("WORKER_RESUME", t + 5, actor="worker-shadow", node="vn2"),
    ]


def root(kind, t, *, actor="root-a", epoch=1, step=0, digest=""):
    return ev(kind, t, actor=actor, epoch=epoch, step=step, digest=digest)


def step_rows(step, t, digest, *, actor="root-a", epoch=1):
    return [
        root("BEGIN_STEP", t, actor=actor, epoch=epoch, step=step),
        root("PARTIAL_WRITE", t + 1, actor=actor, epoch=epoch,
             step=step, digest=digest),
        root("SEAL", t + 2, actor=actor, epoch=epoch,
             step=step, digest=digest),
        root("COMMIT", t + 3, actor=actor, epoch=epoch,
             step=step, digest=digest),
        root("CLAIM_SUCCESS", t + 4, actor=actor, epoch=epoch,
             step=step, digest=digest),
    ]


class RecoverySimulationTests(unittest.TestCase):
    def assess(self, rows):
        return simulate_recovery(RUN, rows)

    def test_three_node_complete_then_clean_owner_handoff(self):
        rows = ready() + [root("ACQUIRE", 6)] + step_rows(1, 7, A) + [
            root("RELEASE", 12),
            root("ACQUIRE", 13, actor="root-b", epoch=2),
        ] + step_rows(2, 14, B, actor="root-b", epoch=2) + [
            root("ROLLOVER", 19, actor="root-b", epoch=2, step=1,
                 digest=A),
        ]
        result = self.assess(rows)
        self.assertEqual(result["denials"], [])
        self.assertEqual(result["committed_step"], 2)
        self.assertEqual(result["successful_generations"], [1, 2])
        self.assertEqual(result["retired_steps"], [1])
        self.assertEqual(result["final_owner"], "root-b")
        self.assertEqual(result["max_simultaneous_shadow_owners"], 1)
        self.assertEqual(result["physical_optimizer_steps_executed"], 0)
        self.assertFalse(result["host_lease_authenticated"])
        self.assertFalse(result["authorizes_optimizer_start"])
        self.assertFalse(result["checkpoint_bytes_verified"])

    def test_tunnel_drop_partial_write_standby_then_fenced_recovery(self):
        rows = ready() + [root("ACQUIRE", 6)] + step_rows(1, 7, A) + [
            root("BEGIN_STEP", 12, step=2),
            root("PARTIAL_WRITE", 13, step=2, digest=B),
            ev("TUNNEL_DOWN", 14, node="vn1"),
            root("COMMIT", 15, step=2, digest=B),
            ev("STANDBY", 16),
        ] + ready(30_017) + [
            ev("FENCE_ACK", 30_023, epoch=2),
            root("ACQUIRE", 30_024, actor="root-b", epoch=2),
        ] + step_rows(2, 30_025, B, actor="root-b", epoch=2)
        result = self.assess(rows)
        self.assertIn("STEP_WITHOUT_ACTIVE_SYNTHETIC_OWNER",
                      result["denial_reasons"])
        commits = [r["step"] for r in result["receipts"]
                   if r["event"] == "COMMIT"]
        self.assertEqual(commits, [1, 2])
        self.assertEqual(result["successful_generations"], [1, 2])
        self.assertEqual(result["committed_step"], 2)
        self.assertEqual(result["final_owner"], "root-b")
        self.assertIn("FENCE_ACK", {r["event"] for r in result["receipts"]})
        self.assertFalse(result["fencing_host_authenticated"])

    def test_owner_collision_and_wrong_epoch_cannot_commit(self):
        rows = ready() + [
            root("ACQUIRE", 6),
            root("ACQUIRE", 7, actor="root-b", epoch=2),
            root("BEGIN_STEP", 8, actor="root-b", epoch=2, step=1),
            root("COMMIT", 9, actor="root-b", epoch=2, step=1, digest=A),
        ]
        result = self.assess(rows)
        self.assertIn("OWNER_COLLISION", result["denial_reasons"])
        self.assertIn("STEP_WITHOUT_ACTIVE_SYNTHETIC_OWNER",
                      result["denial_reasons"])
        self.assertEqual(result["committed_step"], 0)
        self.assertEqual(result["max_simultaneous_shadow_owners"], 1)

    def test_partial_without_seal_or_mismatched_seal_never_counts(self):
        rows = ready() + [
            root("ACQUIRE", 6), root("BEGIN_STEP", 7, step=1),
            root("PARTIAL_WRITE", 8, step=1, digest=A),
            root("SEAL", 9, step=1, digest=B),
            root("COMMIT", 10, step=1, digest=A),
            root("CLAIM_SUCCESS", 11, step=1, digest=A),
        ]
        r = self.assess(rows)
        self.assertIn("SEAL_WITHOUT_MATCHING_PARTIAL", r["denial_reasons"])
        self.assertIn("COMMIT_WITHOUT_MATCHING_SEAL", r["denial_reasons"])
        self.assertIn("SUCCESS_WITHOUT_DURABLE_COMMIT", r["denial_reasons"])
        self.assertEqual(r["successful_generations"], [])

    def test_replayed_success_and_commit_cannot_double_count(self):
        rows = ready() + [root("ACQUIRE", 6)] + step_rows(1, 7, A) + [
            root("COMMIT", 12, step=1, digest=A),
            root("CLAIM_SUCCESS", 13, step=1, digest=A),
        ]
        r = self.assess(rows)
        self.assertIn("COMMIT_WITHOUT_MATCHING_SEAL", r["denial_reasons"])
        self.assertIn("DUPLICATE_GENERATION_SUCCESS", r["denial_reasons"])
        self.assertEqual(r["successful_generations"], [1])

    def test_rollover_refused_without_newer_claim_or_wrong_digest(self):
        rows = ready() + [root("ACQUIRE", 6)] + step_rows(1, 7, A) + [
            root("ROLLOVER", 12, step=1, digest=A),
            root("ROLLOVER", 13, step=1, digest=B),
        ]
        r = self.assess(rows)
        self.assertEqual(r["retired_steps"], [])
        self.assertEqual(r["denial_reasons"], ("UNSAFE_CHECKPOINT_ROLLOVER",))

    def test_fence_refuses_unexpired_and_without_post_fault_witness(self):
        rows = ready() + [root("ACQUIRE", 6),
                          ev("TUNNEL_DOWN", 7, node="vn2"),
                          ev("FENCE_ACK", 8, epoch=2),
                          ev("FENCE_ACK", 30_007, epoch=2)]
        r = self.assess(rows)
        self.assertIn("UNEXPIRED_OWNER_NOT_FENCED", r["denial_reasons"])
        self.assertIn("FENCE_HOST_WITNESS_UNKNOWN", r["denial_reasons"])
        self.assertEqual(r["final_owner"], "root-a")

    def test_unrequested_fence_and_stale_peer_hold(self):
        rows = ready() + [ev("FENCE_ACK", 6, epoch=1),
                          ev("TUNNEL_DOWN", 7, node="vn1"),
                          root("ACQUIRE", 8)]
        r = self.assess(rows)
        self.assertIn("UNSOLICITED_FAKE_FENCE", r["denial_reasons"])
        self.assertIn("HOST_CUSTODY_UNKNOWN", r["denial_reasons"])
        self.assertEqual(r["committed_step"], 0)

    def test_ancient_host_witness_cannot_grant_new_shadow_owner(self):
        rows = ready() + [root("ACQUIRE", 30_100)]
        r = self.assess(rows)
        self.assertEqual(r["denial_reasons"], ("HOST_CUSTODY_UNKNOWN",))
        self.assertIsNone(r["final_owner"])

    def test_cumulative_wall_monotonic_drift_quarantines_future_steps(self):
        rows = ready() + [root("ACQUIRE", 6),
                          ev("TUNNEL_UP", 7, wall=6_000),
                          {**root("BEGIN_STEP", 8, step=1),
                           "wall_ms": 6_001}]
        r = self.assess(rows)
        self.assertIn("CUMULATIVE_CLOCK_DRIFT", r["denial_reasons"])
        self.assertIn("STEP_WITHOUT_ACTIVE_SYNTHETIC_OWNER",
                      r["denial_reasons"])
        self.assertTrue(r["clock_quarantined"])

    def test_scenario_digest_is_deterministic_and_order_bound(self):
        base = ready() + [root("ACQUIRE", 6)]
        same = self.assess(base)
        self.assertEqual(same["scenario_sha256"], self.assess(base)["scenario_sha256"])
        changed = ready() + [root("ACQUIRE", 6, actor="root-b")]
        self.assertNotEqual(same["scenario_sha256"],
                            self.assess(changed)["scenario_sha256"])
        self.assertEqual(same["schema"],
                         "rezon.trainingday.r28-recovery-simulation.v1.receipt")
        self.assertFalse(same["authorizes_model_release"])
        self.assertFalse(same["distributed_gradient_compute_proven"])

    def test_invalid_adversarial_shape_and_oversized_rejected(self):
        bad_events = [
            {**ev("WAKE", 0), "mono_ms": True},
            {**ev("WAKE", 0), "mono_ms": 2**63},
            {**ev("WAKE", 0), "kind": "OPEN_HOST_SOCKET"},
            {**ev("WAKE", 0), "node": "../lappy"},
            {**ev("WAKE", 0), "actor": "root-a"},
            {**ev("ACQUIRE", 0, actor="root-a", epoch=1), "epoch": True},
            {**ev("PARTIAL_WRITE", 0, actor="root-a", epoch=1,
                  step=1, digest=A), "digest": "f" * 63},
            {**ev("PARTIAL_WRITE", 0, actor="root-a", epoch=1,
                  step=1, digest=A), "digest": "f" * 100_000},
            {**ev("WAKE", 0), "evil": 1},
            {**ev("WAKE", 0), "actor": "host-shadow" * 100_000},
            {**ev("WAKE", 0), "mono_ms": float("nan")},
            {**ev("WAKE", 0), "actor": ["host-shadow"]},
        ]
        for item in bad_events:
            with self.subTest(item=repr(item)):
                with self.assertRaises(RecoveryScenarioError):
                    self.assess([item])
        with self.assertRaises(RecoveryScenarioError):
            self.assess([ev("WAKE", t) for t in range(MAX_EVENTS + 1)])
        with self.assertRaises(RecoveryScenarioError):
            simulate_recovery("x" * 64, ready())
        with self.assertRaises(RecoveryScenarioError):
            simulate_recovery("a" * 100_000, ready())
        with self.assertRaises(RecoveryScenarioError):
            self.assess([ev("WAKE", 1), ev("WAKE", 0)])

    def test_mutation_after_validation_cannot_change_replay_or_digest(self):
        original = ready() + [root("ACQUIRE", 6)]
        expected = self.assess(original)
        real_validate = recovery_module._validate

        def adversary(run_sha, input_events):
            real_validate(run_sha, input_events)
            # Previous version replayed this mutation despite validation.
            original[-1]["actor"] = "root-c"

        with patch.object(recovery_module, "_validate", side_effect=adversary):
            observed = self.assess(original)
        self.assertEqual(original[-1]["actor"], "root-c")
        self.assertEqual(observed["final_owner"], "root-a")
        self.assertEqual(observed["scenario_sha256"], expected["scenario_sha256"])

    def test_internal_validated_snapshot_is_immutable(self):
        original = ready() + [root("ACQUIRE", 6)]
        real_validate = recovery_module._validate

        def adversary(run_sha, snapshot):
            real_validate(run_sha, snapshot)
            with self.assertRaises(TypeError):
                snapshot[-1]["actor"] = "root-c"
            with self.assertRaises(AttributeError):
                snapshot.append(root("ACQUIRE", 7, actor="root-b", epoch=2))

        with patch.object(recovery_module, "_validate", side_effect=adversary):
            observed = self.assess(original)
        self.assertEqual(observed["final_owner"], "root-a")

    def test_mutated_alias_after_snapshot_cannot_rewrite_prior_event(self):
        aliased = ev("WAKE", 0)
        original = [aliased, aliased] + ready(1) + [root("ACQUIRE", 7)]
        expected = self.assess(original)
        real_validate = recovery_module._validate

        def adversary(run_sha, snapshot):
            real_validate(run_sha, snapshot)
            aliased["actor"] = "root-c"

        with patch.object(recovery_module, "_validate", side_effect=adversary):
            observed = self.assess(original)
        self.assertEqual(observed["final_owner"], "root-a")
        self.assertEqual(observed["denials"], [])
        self.assertEqual(observed["scenario_sha256"], expected["scenario_sha256"])


if __name__ == "__main__":
    unittest.main()
