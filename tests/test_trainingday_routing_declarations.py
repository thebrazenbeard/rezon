"""Synthetic checks only; no Executor command, lease issuance or GPU scheduling."""

import copy
import unittest

from rezon.trainingday_pool import PoolError, build_job
from rezon.trainingday_routing import assess_routing_declarations


class RoutingDeclarationTests(unittest.TestCase):
    def setUp(self):
        self.job, _ = build_job(
            seed=17, count=2,
            workers={"lappy_worker": "model-a", "vn1_worker": "model-b"},
        )
        self.routes = {"lappy_worker": "lappy", "vn1_worker": "vn1"}
        self.observations = [
            {"device": "lappy", "connected": True, "execution_active": 0,
             "observed_at_unix": 1000},
            {"device": "vn1", "connected": True, "execution_active": 0,
             "observed_at_unix": 1000},
        ]
        self.leases = [
            {"device": "lappy", "worker": "lappy_worker", "lease_id": "lease-1",
             "expires_at_unix": 1050},
            {"device": "vn1", "worker": "vn1_worker", "lease_id": "lease-2",
             "expires_at_unix": 1050},
        ]

    def check(self, routes=None, observations=None, leases=None):
        return assess_routing_declarations(
            self.job, self.routes if routes is None else routes,
            self.observations if observations is None else observations,
            self.leases if leases is None else leases, now_unix=1001,
        )

    def test_consistent_routing_never_authorizes_host_execution(self):
        result = self.check()
        self.assertEqual(result["status"], "DECLARATION_CONSISTENT_NOT_AUTHORIZED")
        self.assertEqual(result["blockers"], [])
        self.assertFalse(result["dispatch_authorized"])
        self.assertFalse(result["host_lease_authenticated"])
        self.assertFalse(result["shared_gradient_computation_proven"])
        self.assertEqual(len(result["assessment_sha256"]), 64)

    def test_identical_status_with_swapped_routes_has_different_evidence_digest(self):
        initial = self.check()
        swapped_routes = {"lappy_worker": "vn1", "vn1_worker": "lappy"}
        swapped_leases = [
            dict(row, device=("vn1" if row["device"] == "lappy" else "lappy"))
            for row in self.leases
        ]
        swapped = self.check(routes=swapped_routes, leases=swapped_leases)
        self.assertEqual(swapped["blockers"], [])
        self.assertEqual(initial["status"], swapped["status"])
        self.assertNotEqual(initial["assessment_sha256"], swapped["assessment_sha256"])
        self.assertFalse(swapped["dispatch_authorized"])
        self.assertFalse(swapped["host_lease_authenticated"])

    def test_same_claims_different_assessment_instant_has_distinct_digest(self):
        early = self.check()
        late = assess_routing_declarations(
            self.job, self.routes, self.observations, self.leases, now_unix=1002,
        )
        self.assertEqual(early["status"], late["status"])
        self.assertNotEqual(early["assessment_sha256"], late["assessment_sha256"])

    def test_input_order_is_not_an_artificial_digest_difference(self):
        initial = self.check()
        reversed_rows = self.check(
            observations=list(reversed(self.observations)),
            leases=list(reversed(self.leases)),
        )
        self.assertEqual(initial["assessment_sha256"], reversed_rows["assessment_sha256"])

    def test_unbounded_lease_lifetime_fails_closed_even_if_host_claims_clean(self):
        leases = copy.deepcopy(self.leases)
        leases[0]["expires_at_unix"] = 2**63 - 1
        response = self.check(leases=leases)
        self.assertIn("LEASE_HORIZON_TOO_LONG", response["blockers"])
        self.assertFalse(response["dispatch_authorized"])
        leases[0]["expires_at_unix"] = 1121  # 120s exactly after assessment now=1001
        self.assertNotIn("LEASE_HORIZON_TOO_LONG", self.check(leases=leases)["blockers"])
        leases[0]["expires_at_unix"] = 1122
        self.assertIn("LEASE_HORIZON_TOO_LONG", self.check(leases=leases)["blockers"])

    def test_caller_cannot_expand_staleness_policy_to_one_hour(self):
        with self.assertRaises(PoolError):
            assess_routing_declarations(
                self.job, self.routes, self.observations, self.leases,
                now_unix=1001, max_age_seconds=3600,
            )

    def test_nonserializable_or_nonfinite_route_values_fail_as_pool_error(self):
        for invalid in (float("nan"), float("inf"), object(), ["lappy"],
                        {"device": "lappy"}, "\ud800", "LAPPY"):
            with self.subTest(value_type=type(invalid).__name__, value_repr=repr(invalid)):
                routes = dict(self.routes, lappy_worker=invalid)
                with self.assertRaisesRegex(PoolError, "routing declaration malformed"):
                    self.check(routes=routes)

    def test_disconnect_stale_occupancy_and_expiry_fail_closed(self):
        for mutation, code in (
            ({"connected": False}, "HOST_DISCONNECTED"),
            ({"observed_at_unix": 960}, "HOST_OBSERVATION_STALE"),
            ({"execution_active": 1}, "HOST_WORKLOAD_OCCUPIED"),
        ):
            with self.subTest(mutation=mutation):
                observations = copy.deepcopy(self.observations)
                observations[0].update(mutation)
                result = self.check(observations=observations)
                self.assertIn(code, result["blockers"])
                self.assertFalse(result["dispatch_authorized"])
        leases = copy.deepcopy(self.leases)
        leases[0]["expires_at_unix"] = 1001
        self.assertIn("LEASE_EXPIRED", self.check(leases=leases)["blockers"])

    def test_colliding_or_misbound_logical_leases_fail_closed(self):
        routes = dict(self.routes, vn1_worker="lappy")
        self.assertIn("DEVICE_ROUTE_COLLISION", self.check(routes=routes)["blockers"])
        leases = copy.deepcopy(self.leases)
        leases[1]["lease_id"] = "lease-1"
        self.assertIn("LEASE_ID_COLLISION", self.check(leases=leases)["blockers"])
        leases = copy.deepcopy(self.leases)
        leases[1]["worker"] = "lappy_worker"
        self.assertIn("LEASE_ROUTE_MISMATCH", self.check(leases=leases)["blockers"])

    def test_missing_worker_and_invalid_job_are_not_scheduled(self):
        self.assertIn("WORKER_ROUTE_INCOMPLETE", self.check(routes={"lappy_worker": "lappy"})["blockers"])
        bad = copy.deepcopy(self.job)
        bad["seed"] += 1
        with self.assertRaises(ValueError):
            assess_routing_declarations(bad, self.routes, self.observations,
                                        self.leases, now_unix=1001)

    def test_disconnect_retry_needs_new_declaration_and_still_cannot_dispatch(self):
        disconnected = copy.deepcopy(self.observations)
        disconnected[1]["connected"] = False
        self.assertEqual(self.check(observations=disconnected)["status"],
                         "HOLD_HOST_DECLARATION_CONFLICT")
        reconnected = copy.deepcopy(self.observations)
        reconnected[1]["observed_at_unix"] = 1020  # future claim is not fresh
        self.assertIn("HOST_OBSERVATION_STALE", self.check(observations=reconnected)["blockers"])
        reconnected[1]["observed_at_unix"] = 1001
        second = self.check(observations=reconnected)
        self.assertEqual(second["status"], "DECLARATION_CONSISTENT_NOT_AUTHORIZED")
        self.assertFalse(second["dispatch_authorized"])
        self.assertFalse(second["host_lease_authenticated"])

    def test_replayed_and_conflicting_host_claims_fail_closed(self):
        observations = copy.deepcopy(self.observations)
        observations.append(copy.deepcopy(observations[0]))
        self.assertIn("HOST_OBSERVATION_DUPLICATE", self.check(observations=observations)["blockers"])
        observations = copy.deepcopy(self.observations)
        observations[0]["device"] = "vn2"  # absent observation for routed Lappy
        self.assertIn("HOST_OBSERVATION_INCOMPLETE", self.check(observations=observations)["blockers"])
        leases = copy.deepcopy(self.leases)
        leases.append(copy.deepcopy(leases[0]))
        result = self.check(leases=leases)
        self.assertIn("LEASE_ROUTE_COLLISION", result["blockers"])
        self.assertIn("LEASE_ID_COLLISION", result["blockers"])

    def test_three_distinct_hosts_are_logically_consistent_but_unattested(self):
        job, _ = build_job(seed=31, count=1, workers={
            "lappy_worker": "model-a", "vn1_worker": "model-b", "vn2_worker": "model-c",
        })
        routes = dict(self.routes, vn2_worker="vn2")
        observations = self.observations + [{
            "device": "vn2", "connected": True, "execution_active": 0,
            "observed_at_unix": 1001,
        }]
        leases = self.leases + [{
            "device": "vn2", "worker": "vn2_worker", "lease_id": "lease-3",
            "expires_at_unix": 1060,
        }]
        result = assess_routing_declarations(
            job, routes, observations, leases, now_unix=1001,
        )
        self.assertEqual(result["blockers"], [])
        self.assertFalse(result["dispatch_authorized"])
        self.assertFalse(result["host_lease_authenticated"])

    def test_malformed_host_claims_are_not_interpreted_as_host_authority(self):
        observations = copy.deepcopy(self.observations)
        observations[0]["connected"] = 1  # Python bool/int equality must not bypass type check
        with self.assertRaises(ValueError):
            self.check(observations=observations)
        leases = copy.deepcopy(self.leases)
        leases[0]["expires_at_unix"] = True
        with self.assertRaises(ValueError):
            self.check(leases=leases)


if __name__ == "__main__":
    unittest.main()
