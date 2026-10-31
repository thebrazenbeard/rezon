"""Hostile source-contract tests; NO physical Rezon or MiniLM execution."""

from __future__ import annotations

from dataclasses import replace
import json
import unittest

from experiments.labyrinth_minotaur_receipts.qualification import (
    Claim, EvidenceStatus, ExactPins, HostPin, HostReceipts,
    QualificationError, QualificationVerdict, RoleKeys, SignedReceipt,
    LABYRINTH_FIVE_ARMS, qualify_source_envelope,
    require_qualified_distributed_execution, sign_source_receipt,
)


KEYS = RoleKeys(b"lease-test-only-key-0000000001",
                b"route-test-only-key-0000000002",
                b"effect-test-only-key-000000003")


def pins(**changes) -> ExactPins:
    data = dict(
        run_id="maze.run.1", owner_id="patrick.operator",
        rezon_source_head="b25518b525b8d31c8e8730a3b4d23088d2c66cdc",
        labyrinth_source_head="b698ede24d9a69e551e1cad83dee83a825feb9a6",
        model_training_source_head="a14118e87dbba9fd436ef2ae6ad04293966d4d8b",
        episode_sha256="a" * 64, task_roster_sha256="b" * 64,
        checkpoint_sha256="c" * 64, maze_exposure_sha256="d" * 64,
        control_matrix_sha256="e" * 64, development_event_sha256="f" * 64,
        authority_head_sha256="1" * 64,
        training_program="LABYRINTH_MINILM_FIVE_ARM",
        bridge_semantics="PROVENANCE_ONLY", control_arms=LABYRINTH_FIVE_ARMS,
        epoch=21, fence=8, now=1800000000,
        hosts=(HostPin("Lappy", "route.Lappy", 4, 101),
               HostPin("VN1", "route.VN1", 9, 102)),
    )
    data.update(changes)
    return ExactPins(**data)


def make_bundle(p: ExactPins, host: HostPin, *, effect_kind="WHOLE_MODEL_TEXT",
                outcome="COMMITTED", lease_outcome="AUTHORIZED",
                route_outcome="CONNECTED", expiry=None, nonce=None,
                authority_head=None, authority_sequence=None,
                route_generation=None, run_id=None, effect_id=None,
                signed_keys=KEYS) -> HostReceipts:
    number = p.hosts.index(host)
    common = dict(
        run_id=p.run_id if run_id is None else run_id,
        host_id=host.host_id, owner_id=p.owner_id,
        authority_head_sha256=p.authority_head_sha256
        if authority_head is None else authority_head,
        epoch=p.epoch, fence=p.fence,
        episode_sha256=p.episode_sha256,
        task_roster_sha256=p.task_roster_sha256,
        checkpoint_sha256=p.checkpoint_sha256,
        lease_nonce=nonce if nonce is not None else "lease.nonce." + str(number),
        rezon_source_head=p.rezon_source_head,
        labyrinth_source_head=p.labyrinth_source_head,
        model_training_source_head=p.model_training_source_head,
        maze_exposure_sha256=p.maze_exposure_sha256,
        control_matrix_sha256=p.control_matrix_sha256,
        development_event_sha256=p.development_event_sha256,
        training_program=p.training_program,
        bridge_semantics=p.bridge_semantics,
    )
    lease = dict(common, lease_expires_at=expiry or p.now + 300,
                 authority_sequence=host.authority_sequence
                 if authority_sequence is None else authority_sequence,
                 outcome=lease_outcome)
    route = dict(common, route_id=host.route_id,
                 route_generation=host.route_generation
                 if route_generation is None else route_generation,
                 outcome=route_outcome)
    effect = dict(common, effect_id=effect_id or "effect." + str(number),
                  effect_kind=effect_kind,
                  effect_sha256=str(number + 2) * 64,
                  outcome=outcome)
    return HostReceipts(host.host_id,
                        sign_source_receipt("lease", lease, signed_keys),
                        sign_source_receipt("route", route, signed_keys),
                        sign_source_receipt("effect", effect, signed_keys))


def bundles(p: ExactPins, **kwargs) -> tuple[HostReceipts, ...]:
    return tuple(make_bundle(p, host, **kwargs) for host in p.hosts)


class RezonLabyrinthSourceFixtureTests(unittest.TestCase):
    def test_hostile_python_string_subclasses_cannot_spoof_pinned_identity(self):
        class GhostStr(str):
            def __eq__(self, other):
                return True

            def __ne__(self, other):
                return False

            def __hash__(self):
                return hash("Lappy")

        p = pins()
        first, second = bundles(p)
        # These compare equal in deliberately hostile Python; their underlying
        # string values do not satisfy the signed role / host / plan identity.
        mutations = (
            (replace(first, lease=replace(first.lease, role=GhostStr("WRONG"))), second),
            (replace(first, host_id=GhostStr("NONEXISTENT")), second),
        )
        for attempted in mutations:
            with self.subTest(attempted=repr(attempted[0])[:70]):
                with self.assertRaises(QualificationError):
                    qualify_source_envelope(p, KEYS, attempted,
                                            Claim.INDEPENDENT_MODEL_RESPONSES)
        for malformed_pins in (
            replace(p, training_program=GhostStr("NOT_FIVE_ARM")),
            replace(p, bridge_semantics=GhostStr("EXECUTION_ALLOWED")),
            replace(p, control_arms=tuple(GhostStr("ANY") for _ in range(5))),
        ):
            with self.subTest(malformed=repr(malformed_pins)[:80]):
                with self.assertRaises(QualificationError):
                    malformed_pins.validate()

    def test_source_signer_rejects_hostile_role_and_dictionary_key_objects(self):
        class GhostRole(str):
            def __eq__(self, other):
                return True

            def __ne__(self, other):
                return False

            def __hash__(self):
                return hash("lease")

        p = pins()
        first = make_bundle(p, p.hosts[0])
        with self.assertRaises(QualificationError):
            KEYS.for_role(GhostRole("WRONG"))
        with self.assertRaises(QualificationError):
            sign_source_receipt(GhostRole("WRONG"), {}, KEYS)
        # A valid signer role with a forged key still must fail before hashing.
        forged = {GhostRole("run_id"): p.run_id}
        with self.assertRaises(QualificationError):
            sign_source_receipt("lease", forged, KEYS)
        self.assertEqual(first.lease.role, "lease")

    def test_full_two_host_source_envelope_still_is_not_physical_qualification(self):
        p = pins()
        result = qualify_source_envelope(
            p, KEYS, bundles(p), Claim.INDEPENDENT_MODEL_RESPONSES)
        self.assertEqual(result.source_envelope, EvidenceStatus.SOURCE_ONLY)
        self.assertTrue(result.source_receipts_verified)
        self.assertFalse(result.can_authorize_execution)
        self.assertEqual(result.claim_status, EvidenceStatus.SOURCE_ONLY)
        self.assertEqual(result.physical_execution, EvidenceStatus.UNKNOWN)
        self.assertEqual(result.distributed_single_model, EvidenceStatus.UNKNOWN)
        self.assertFalse(result.can_assert_physical_execution)
        with self.assertRaises(QualificationError):
            require_qualified_distributed_execution(result)

    def test_missing_or_partial_receipts_do_not_promote_a_physical_claim(self):
        p = pins()
        empty = qualify_source_envelope(p, KEYS, (), Claim.DISTRIBUTED_SINGLE_MODEL)
        self.assertEqual(empty.source_envelope, EvidenceStatus.SOURCE_ONLY)
        self.assertFalse(empty.source_receipts_verified)
        partial = qualify_source_envelope(p, KEYS, bundles(p)[:1],
                                          Claim.INDEPENDENT_MODEL_RESPONSES)
        self.assertEqual(partial.source_envelope, EvidenceStatus.UNKNOWN)
        self.assertFalse(partial.source_receipts_verified)
        self.assertFalse(partial.can_assert_physical_execution)

    def test_valid_signed_tensor_claim_also_stays_unknown_physical(self):
        p = pins()
        test_records = bundles(p, effect_kind="TENSOR_OPERATION")
        result = qualify_source_envelope(
            p, KEYS, test_records, Claim.DISTRIBUTED_SINGLE_MODEL)
        self.assertEqual(result.source_envelope, EvidenceStatus.SOURCE_ONLY)
        self.assertTrue(result.source_receipts_verified)
        self.assertEqual(result.claim_status, EvidenceStatus.UNKNOWN)
        self.assertEqual(result.physical_execution, EvidenceStatus.UNKNOWN)
        with self.assertRaises(QualificationError):
            require_qualified_distributed_execution(result)

    def test_whole_model_text_cannot_be_relabelled_gradient_or_tensor_shard(self):
        p = pins()
        for claim in (Claim.DISTRIBUTED_SINGLE_MODEL, Claim.TENSOR_SHARDING,
                      Claim.KV_SHARDING, Claim.DISTRIBUTED_GRADIENTS):
            with self.subTest(claim=claim), self.assertRaisesRegex(
                    QualificationError, "effect kind"):
                qualify_source_envelope(p, KEYS, bundles(p), claim)

    def test_ambiguous_ack_and_unknown_route_never_replayed_as_success(self):
        p = pins()
        for data in (dict(outcome="UNKNOWN"), dict(lease_outcome="UNKNOWN"),
                     dict(route_outcome="UNKNOWN")):
            result = qualify_source_envelope(
                p, KEYS, bundles(p, **data), Claim.INDEPENDENT_MODEL_RESPONSES)
            self.assertEqual(result.source_envelope, EvidenceStatus.UNKNOWN)
            self.assertFalse(result.can_assert_physical_execution)

    def test_expired_lease_stale_route_and_authority_sequence_rejected(self):
        p = pins()
        for mutation in (dict(expiry=p.now), dict(route_generation=1),
                         dict(authority_sequence=1)):
            with self.subTest(mutation=mutation), self.assertRaises(QualificationError):
                qualify_source_envelope(
                    p, KEYS, bundles(p, **mutation), Claim.INDEPENDENT_MODEL_RESPONSES)

    def test_split_brain_head_and_foreign_run_rejected(self):
        p = pins()
        for mutation in (dict(authority_head="9" * 64),
                         dict(run_id="foreign.run")):
            with self.subTest(mutation=mutation), self.assertRaises(QualificationError):
                qualify_source_envelope(
                    p, KEYS, bundles(p, **mutation), Claim.INDEPENDENT_MODEL_RESPONSES)

    def test_duplicate_host_and_cloned_nonce_rejected(self):
        p = pins()
        records = bundles(p)
        with self.assertRaisesRegex(QualificationError, "duplicate host"):
            qualify_source_envelope(
                p, KEYS, (records[0], records[0]), Claim.INDEPENDENT_MODEL_RESPONSES)
        with self.assertRaisesRegex(QualificationError, "nonce"):
            qualify_source_envelope(
                p, KEYS, bundles(p, nonce="shared.nonce"),
                Claim.INDEPENDENT_MODEL_RESPONSES)

    def test_signature_tampering_and_cross_role_reuse_rejected(self):
        p = pins()
        first, second = bundles(p)
        bad = replace(first.lease, mac_sha256="0" * 64)
        with self.assertRaisesRegex(QualificationError, "MAC"):
            qualify_source_envelope(
                p, KEYS, (replace(first, lease=bad), second),
                Claim.INDEPENDENT_MODEL_RESPONSES)
        with self.assertRaisesRegex(QualificationError, "role"):
            qualify_source_envelope(
                p, KEYS, (replace(first, route=first.lease), second),
                Claim.INDEPENDENT_MODEL_RESPONSES)

    def test_missing_role_key_separation_rejected(self):
        p = pins()
        bad_keys = RoleKeys(KEYS.lease, KEYS.lease, KEYS.effect)
        with self.assertRaisesRegex(QualificationError, "distinct"):
            qualify_source_envelope(p, bad_keys, bundles(p),
                                    Claim.INDEPENDENT_MODEL_RESPONSES)

    def test_signer_custody_and_cloned_external_state_cannot_be_proven_offline(self):
        p = pins()
        record = bundles(p)
        # Two independent *process invocations* with cloned source keys/head
        # both verify. This deliberately preserves the no-global-monotonicity
        # falsifier instead of pretending an HMAC makes a host trustworthy.
        first = qualify_source_envelope(p, KEYS, record,
                                        Claim.INDEPENDENT_MODEL_RESPONSES)
        second = qualify_source_envelope(p, KEYS, record,
                                         Claim.INDEPENDENT_MODEL_RESPONSES)
        self.assertEqual((first.source_envelope, second.source_envelope),
                         (EvidenceStatus.SOURCE_ONLY, EvidenceStatus.SOURCE_ONLY))
        self.assertTrue(first.source_receipts_verified)
        self.assertTrue(second.source_receipts_verified)
        self.assertFalse(first.can_authorize_execution)
        self.assertFalse(second.can_authorize_execution)
        self.assertFalse(first.can_assert_physical_execution)
        self.assertFalse(second.can_assert_physical_execution)

    def test_labyrinth_five_arm_controls_and_provenance_only_bridge_pinned(self):
        base = pins()
        for changed in (
            replace(base, control_arms=("MeZO", "QLoRA")),
            replace(base, training_program="MODEL_TRAINING_R18_FOUR_ARM"),
            replace(base, bridge_semantics="SHARED_MODEL_WEIGHTS"),
            replace(base, maze_exposure_sha256="wrong"),
            replace(base, development_event_sha256="wrong"),
        ):
            with self.subTest(changed=str(changed)[:90]), self.assertRaises(
                    QualificationError):
                changed.validate()

    def test_rezon_and_training_head_must_be_exact_git_digests(self):
        for changed in (replace(pins(), rezon_source_head="1" * 64),
                        replace(pins(), labyrinth_source_head="1" * 64),
                        replace(pins(), model_training_source_head="BAD")):
            with self.assertRaises(QualificationError):
                changed.validate()

    def test_duplicate_fields_and_noncanonical_json_rejected_even_if_mac_present(self):
        p = pins()
        first, second = bundles(p)
        raw = first.lease.payload_json
        duplicate = raw[:-1] + ',"run_id":"another.run"}'
        with self.assertRaisesRegex(QualificationError, "duplicate"):
            # Canonical parser refuses before any MAC comparison.
            mutated = replace(first.lease, payload_json=duplicate)
            qualify_source_envelope(
                p, KEYS, (replace(first, lease=mutated), second),
                Claim.INDEPENDENT_MODEL_RESPONSES)
        noncanonical = json.dumps(json.loads(raw), indent=2)
        with self.assertRaisesRegex(QualificationError, "noncanonical"):
            mutated = replace(first.lease, payload_json=noncanonical)
            qualify_source_envelope(
                p, KEYS, (replace(first, lease=mutated), second),
                Claim.INDEPENDENT_MODEL_RESPONSES)

    def test_no_escalation_by_constructing_forged_qualified_verdict(self):
        forged = QualificationVerdict(
            EvidenceStatus.QUALIFIED, EvidenceStatus.QUALIFIED,
            EvidenceStatus.QUALIFIED, Claim.DISTRIBUTED_SINGLE_MODEL,
            EvidenceStatus.QUALIFIED, True, ())
        with self.assertRaises(QualificationError):
            require_qualified_distributed_execution(forged)

    def test_fictional_host_and_local_signatures_cannot_claim_qualification(self):
        # A local producer can invent a provider and its HMAC evidence.
        fictitious = HostPin("NONEXISTENT", "route.fiction", 1, 1)
        p = pins(hosts=(fictitious,))
        forged = make_bundle(p, fictitious, effect_kind="TENSOR_OPERATION")
        verdict = qualify_source_envelope(
            p, KEYS, (forged,), Claim.DISTRIBUTED_SINGLE_MODEL)
        self.assertTrue(verdict.source_receipts_verified)
        self.assertEqual(verdict.source_envelope, EvidenceStatus.SOURCE_ONLY)
        self.assertEqual(verdict.claim_status, EvidenceStatus.UNKNOWN)
        self.assertFalse(verdict.can_assert_physical_execution)
        self.assertFalse(verdict.can_authorize_execution)
        with self.assertRaises(QualificationError):
            require_qualified_distributed_execution(verdict)

    def test_source_pin_match_is_not_per_arm_learning_or_host_authority(self):
        p = pins()
        verdict = qualify_source_envelope(
            p, KEYS, bundles(p), Claim.INDEPENDENT_MODEL_RESPONSES)
        self.assertTrue(verdict.source_receipts_verified)
        self.assertFalse(verdict.host_identity_verified)
        self.assertFalse(verdict.external_monotonic_replay_protected)
        self.assertFalse(verdict.per_arm_learning_verified)
        self.assertFalse(verdict.can_authorize_execution)

    def test_malformed_unicode_and_oversize_payload_fail_closed(self):
        p = pins()
        first, second = bundles(p)
        for bad_json in ("\ud800", "z" * 5000):
            with self.subTest(payload=repr(bad_json)[:20]), self.assertRaises(
                    QualificationError):
                qualify_source_envelope(
                    p, KEYS,
                    (replace(first, lease=replace(first.lease, payload_json=bad_json)),
                     second),
                    Claim.INDEPENDENT_MODEL_RESPONSES)


if __name__ == "__main__":
    unittest.main()
