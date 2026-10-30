"""Public-only deterministic tests for two-coordinator GPU lease shadowing."""

from __future__ import annotations

import unittest

from rezon.trainingday_dual_coordinator_shadow import (
    ShadowLeaseError,
    assess_two_coordinator_shadow,
)


RUN_SHA = "a" * 64


def event(kind, t, *, actor="host-shadow", lease="", epoch=0, ttl=0,
          wall=None):
    return {
        "kind": kind,
        "actor": actor,
        "host": "lappy",
        "lease": lease,
        "epoch": epoch,
        "mono_ms": t,
        "wall_ms": t if wall is None else wall,
        "ttl_ms": ttl,
    }


def ready():
    return [
        event("WAKE", 0),
        event("TUNNEL_RESTORED", 1),
        event("HOST_IDLE", 2),
        event("EXECUTOR_IDLE", 3),
    ]


def request(actor, lease, epoch, t, ttl=30000):
    return event("REQUEST", t, actor=actor, lease=lease, epoch=epoch, ttl=ttl)


def renew(actor, lease, epoch, t, ttl=30000):
    return event("RENEW", t, actor=actor, lease=lease, epoch=epoch, ttl=ttl)


def release(actor, lease, epoch, t):
    return event("RELEASE", t, actor=actor, lease=lease, epoch=epoch)


class DualCoordinatorShadowTests(unittest.TestCase):
    def assess(self, rows):
        return assess_two_coordinator_shadow(RUN_SHA, rows)

    def test_two_roots_never_simultaneously_claim_one_gpu(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5),
            request("root-b", "lease-b", 2, 6),
            renew("root-a", "lease-a", 1, 10000),
            release("root-a", "lease-a", 1, 11000),
            request("root-b", "lease-b", 2, 12000),
        ]
        outcome = self.assess(rows)
        self.assertEqual([r["actor"] for r in outcome["accepted_requests"]],
                         ["root-a", "root-b"])
        self.assertIn("UNEXPIRED_OWNER_COLLISION", outcome["denials"])
        self.assertEqual(outcome["final_owner"], "root-b")
        self.assertEqual(outcome["max_concurrent_claims"], 1)
        self.assertFalse(outcome["authorizes_optimizer_start"])
        self.assertFalse(outcome["host_lease_authenticated"])

    def test_without_initial_wake_tunnel_host_executor_observations_hold(self):
        rows = [request("root-a", "lease-a", 1, 5)]
        outcome = self.assess(rows)
        self.assertEqual(outcome["accepted_requests"], [])
        self.assertIn("HOST_CUSTODY_UNKNOWN", outcome["denials"])

    def test_disconnect_and_expiry_require_new_fencing_claim(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5),
            event("TUNNEL_LOST", 10000),
            event("TUNNEL_RESTORED", 10001),
            event("WAKE", 10001),
            event("HOST_IDLE", 10002),
            event("EXECUTOR_IDLE", 10003),
            request("root-b", "lease-b", 2, 10004),
            event("FENCE_ACK", 10005, epoch=2),  # original still unexpired
            request("root-b", "lease-b", 2, 30005),
            event("FENCE_ACK", 30006, epoch=2),
            request("root-b", "lease-b", 2, 30007),
        ]
        outcome = self.assess(rows)
        self.assertEqual(outcome["final_owner"], "root-b")
        self.assertEqual(len(outcome["accepted_requests"]), 2)
        self.assertIn("FENCE_REJECTED_ACTIVE_LEASE", outcome["denials"])
        self.assertIn("EXPIRED_OWNER_NOT_FENCED", outcome["denials"])
        self.assertFalse(outcome["authorizes_optimizer_start"])

    def test_host_standby_ambiguous_custody_never_second_start(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5, ttl=120000),
            event("SUSPEND", 12000),
            event("WAKE", 13000),
            request("root-b", "lease-b", 2, 14000),
        ]
        outcome = self.assess(rows)
        self.assertEqual(len(outcome["accepted_requests"]), 1)
        self.assertIn("UNEXPIRED_OWNER_COLLISION", outcome["denials"])
        self.assertFalse(outcome["host_lease_authenticated"])

    def test_executor_queued_work_prevents_new_shadow_owner(self):
        rows = ready() + [event("EXECUTOR_BUSY", 4),
                          request("root-a", "lease-a", 1, 5)]
        self.assertIn("HOST_CUSTODY_UNKNOWN", self.assess(rows)["denials"])

    def test_late_owner_renewal_requires_fence_even_before_ttl(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5, ttl=120000),
            renew("root-a", "lease-a", 1, 30006),
            request("root-b", "lease-b", 2, 30007),
        ]
        outcome = self.assess(rows)
        self.assertEqual(outcome["final_owner"], "root-a")
        self.assertIn("STALE_RENEWAL_HEARTBEAT", outcome["denials"])
        self.assertIn("UNEXPIRED_OWNER_COLLISION", outcome["denials"])

    def test_unverified_second_root_release_cannot_evict_owner(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5, ttl=120000),
            release("root-b", "lease-a", 1, 6),
            request("root-b", "lease-b", 2, 7),
        ]
        outcome = self.assess(rows)
        self.assertIn("RELEASE_NOT_CURRENT_OWNER", outcome["denials"])
        self.assertIn("UNEXPIRED_OWNER_COLLISION", outcome["denials"])
        self.assertEqual(outcome["final_owner"], "root-a")

    def test_expired_release_does_not_skip_fencing(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5),
            release("root-a", "lease-a", 1, 30005),
            request("root-b", "lease-b", 2, 30006),
        ]
        outcome = self.assess(rows)
        self.assertEqual(len(outcome["accepted_requests"]), 1)
        self.assertIn("EXPIRED_RELEASE_NEEDS_FENCE", outcome["denials"])
        self.assertIn("EXPIRED_OWNER_NOT_FENCED", outcome["denials"])

    def test_fence_requires_post_disconnect_independent_observation_claims(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5),
            event("TUNNEL_LOST", 10000),
            event("TUNNEL_RESTORED", 10001),
            event("FENCE_ACK", 30005, epoch=2),
            request("root-b", "lease-b", 2, 30006),
        ]
        outcome = self.assess(rows)
        self.assertIn("FENCE_REJECTED_FRESH_POST_FAULT_WITNESS_MISSING", outcome["denials"])
        self.assertEqual(len(outcome["accepted_requests"]), 1)

    def test_fence_epoch_cannot_jump_over_ledger_generation(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5),
            event("HOST_IDLE", 30005), event("EXECUTOR_IDLE", 30005),
            event("TUNNEL_RESTORED", 30005),
            event("FENCE_ACK", 30006, epoch=99),
            request("root-b", "lease-b", 2, 30007),
        ]
        outcome = self.assess(rows)
        self.assertIn("NONSEQUENTIAL_FENCE_EPOCH", outcome["denials"])
        self.assertEqual(len(outcome["accepted_requests"]), 1)

    def test_unsolicited_fence_without_holder_or_fault_rejected(self):
        rows = ready() + [
            event("FENCE_ACK", 4, epoch=1),
            request("root-a", "lease-a", 1, 5),
        ]
        outcome = self.assess(rows)
        self.assertIn("UNSOLICITED_FENCE_ACK", outcome["denials"])
        self.assertFalse(outcome["synthetic_fencing_claimed"])
        # The real first shadow request does not depend on bogus fencing.
        self.assertEqual(len(outcome["accepted_requests"]), 1)

    def test_old_host_witness_cannot_extend_active_lease(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5, ttl=120000),
            renew("root-a", "lease-a", 1, 20000, ttl=120000),
            renew("root-a", "lease-a", 1, 40000, ttl=120000),
            request("root-b", "lease-b", 2, 40001),
        ]
        outcome = self.assess(rows)
        self.assertIn("RENEW_DURING_AMBIGUOUS_CUSTODY", outcome["denials"])
        self.assertIn("UNEXPIRED_OWNER_COLLISION", outcome["denials"])
        self.assertEqual(outcome["final_owner"], "root-a")

    def test_cumulative_clock_drift_rejected_even_when_each_gap_small(self):
        rows = ready() + [
            request("root-a", "lease-a", 1, 5),
            event("HOST_IDLE", 7000, wall=6500),
            event("HOST_IDLE", 14000, wall=13000),
            event("HOST_IDLE", 21000, wall=19500),
            event("HOST_IDLE", 28000, wall=26000),
            event("HOST_IDLE", 35000, wall=32500),
            event("HOST_IDLE", 42000, wall=39000),
            event("HOST_IDLE", 49000, wall=45500),
            event("HOST_IDLE", 56000, wall=52000),
            event("HOST_IDLE", 63000, wall=58500),
            event("HOST_IDLE", 70000, wall=65000),
            event("HOST_IDLE", 77000, wall=71500),
        ]
        outcome = self.assess(rows)
        self.assertIn("CUMULATIVE_CLOCK_DIVERGENCE", outcome["denials"])
        self.assertFalse(outcome["authorizes_optimizer_start"])

    def test_overly_long_lease_and_event_list_rejected_before_hash(self):
        with self.assertRaises(ShadowLeaseError):
            self.assess(ready() + [request("root-a", "lease-a", 1, 5, ttl=120001)])
        with self.assertRaises(ShadowLeaseError):
            self.assess([event("HOST_IDLE", i) for i in range(129)])

    def test_invalid_coordinator_unicode_and_epoch_bool_fail_closed(self):
        for bad in (
            event("REQUEST", 5, actor="root-\ud800", lease="lease-a", epoch=1, ttl=10),
            event("REQUEST", 5, actor="root-a", lease="lease-a", epoch=True, ttl=10),
            event("REQUEST", 5, actor="root-a", lease="lease-a", epoch=1, ttl=10, wall=float("nan")),
            {**event("HOST_IDLE", 5), "ttl_ms": False},
            {**event("HOST_IDLE", 5), "host": object()},
        ):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ShadowLeaseError):
                    self.assess(ready() + [bad])

    def test_content_digest_binding_and_order_sensitivity(self):
        a = self.assess(ready() + [request("root-a", "lease-a", 1, 5)])
        b = self.assess(ready() + [request("root-a", "lease-z", 1, 5)])
        self.assertNotEqual(a["scenario_sha256"], b["scenario_sha256"])
        self.assertEqual(len(a["scenario_sha256"]), 64)
        self.assertEqual(a["status"], "SOURCE_ONLY_HOLD")


if __name__ == "__main__":
    unittest.main()
