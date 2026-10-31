"""Offline Rezon ⇄ training provenance gate. NOT a host qualifier.

This source-only fixture checks canonical, role-separated receipts against
independently supplied exact pins. It cannot attest the custody of those pins,
the kernel identity of the signers, or real tensor/gradient execution.

This module never emits QUALIFIED. A complete role-separated HMAC envelope
only establishes a SOURCE_ONLY pin match, recorded separately as an untrusted
source-receipt verification fact. Neural/distributed execution remains UNKNOWN.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import hmac
import json
import re
from typing import Any, Mapping


class QualificationError(ValueError):
    """An offered proof conflicts with an independently pinned identity."""


class EvidenceStatus(str, Enum):
    SOURCE_ONLY = "SOURCE_ONLY"
    UNKNOWN = "UNKNOWN"
    QUALIFIED = "QUALIFIED"


class Claim(str, Enum):
    INDEPENDENT_MODEL_RESPONSES = "INDEPENDENT_MODEL_RESPONSES"
    DISTRIBUTED_SINGLE_MODEL = "DISTRIBUTED_SINGLE_MODEL"
    TENSOR_SHARDING = "TENSOR_SHARDING"
    KV_SHARDING = "KV_SHARDING"
    DISTRIBUTED_GRADIENTS = "DISTRIBUTED_GRADIENTS"


_SHA = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_HEAD = re.compile(r"[0-9a-f]{40}\Z", re.ASCII)
_IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}\Z", re.ASCII)
_ROLES = ("lease", "route", "effect")
_COMMON = frozenset({
    "run_id", "host_id", "owner_id", "authority_head_sha256", "epoch",
    "fence", "episode_sha256", "task_roster_sha256", "checkpoint_sha256",
    "lease_nonce", "rezon_source_head", "labyrinth_source_head",
    "model_training_source_head", "maze_exposure_sha256",
    "control_matrix_sha256", "development_event_sha256",
    "training_program", "bridge_semantics",
})
_FIELDS = {
    "lease": _COMMON | {"lease_expires_at", "authority_sequence", "outcome"},
    "route": _COMMON | {"route_id", "route_generation", "outcome"},
    "effect": _COMMON | {"effect_id", "effect_kind", "effect_sha256", "outcome"},
}
_MAX_PAYLOAD_BYTES = 4096
LABYRINTH_FIVE_ARMS = (
    "correct", "zero_update", "inverted", "zero_lr", "randomized_labels",
)
_CLAIM_EFFECT_KIND = {
    Claim.INDEPENDENT_MODEL_RESPONSES: "WHOLE_MODEL_TEXT",
    Claim.DISTRIBUTED_SINGLE_MODEL: "TENSOR_OPERATION",
    Claim.TENSOR_SHARDING: "TENSOR_OPERATION",
    Claim.KV_SHARDING: "KV_OPERATION",
    Claim.DISTRIBUTED_GRADIENTS: "GRADIENT_OPERATION",
}


def _digest(value: Any, label: str, *, head: bool = False) -> None:
    pattern = _HEAD if head else _SHA
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise QualificationError(f"invalid {label}")


def _identifier(value: Any, label: str) -> None:
    if type(value) is not str or _IDENT.fullmatch(value) is None:
        raise QualificationError(f"invalid {label}")


def _int(value: Any, label: str, *, minimum: int = 0) -> None:
    if type(value) is not int or not minimum <= value < 2**63:
        raise QualificationError(f"invalid {label}")


def _canonical(data: Mapping[str, Any]) -> str:
    if type(data) is not dict or any(type(key) is not str for key in data):
        raise QualificationError("receipt payload must be a dictionary with exact string keys")
    try:
        result = json.dumps(data, ensure_ascii=True, sort_keys=True,
                            allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError, OverflowError) as exc:
        raise QualificationError("receipt payload is not canonical JSON") from exc
    if len(result.encode("utf-8")) > _MAX_PAYLOAD_BYTES:
        raise QualificationError("oversize receipt payload")
    return result


def _parse_canonical(value: str) -> dict[str, Any]:
    if type(value) is not str:
        raise QualificationError("invalid receipt JSON size/type")
    try:
        encoded = value.encode("utf-8")
    except UnicodeError as exc:
        raise QualificationError("invalid receipt JSON encoding") from exc
    if len(encoded) > _MAX_PAYLOAD_BYTES:
        raise QualificationError("invalid receipt JSON size/type")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise QualificationError("duplicate receipt JSON field")
            result[key] = item
        return result

    try:
        parsed = json.loads(value, object_pairs_hook=unique)
    except QualificationError:
        raise
    except (ValueError, TypeError) as exc:
        raise QualificationError("invalid receipt JSON") from exc
    if type(parsed) is not dict or _canonical(parsed) != value:
        raise QualificationError("noncanonical receipt JSON")
    return parsed


@dataclass(frozen=True)
class HostPin:
    host_id: str
    route_id: str
    route_generation: int
    authority_sequence: int

    def validate(self) -> None:
        _identifier(self.host_id, "host ID")
        _identifier(self.route_id, "route ID")
        _int(self.route_generation, "route generation", minimum=1)
        _int(self.authority_sequence, "authority sequence", minimum=1)


@dataclass(frozen=True)
class ExactPins:
    run_id: str
    owner_id: str
    rezon_source_head: str
    labyrinth_source_head: str
    model_training_source_head: str
    episode_sha256: str
    task_roster_sha256: str
    checkpoint_sha256: str
    maze_exposure_sha256: str
    control_matrix_sha256: str
    development_event_sha256: str
    authority_head_sha256: str
    training_program: str
    bridge_semantics: str
    control_arms: tuple[str, ...]
    epoch: int
    fence: int
    now: int
    hosts: tuple[HostPin, ...]

    def validate(self) -> None:
        _identifier(self.run_id, "run ID")
        _identifier(self.owner_id, "owner ID")
        _digest(self.rezon_source_head, "Rezon source head", head=True)
        _digest(self.labyrinth_source_head, "Labyrinth source head", head=True)
        _digest(self.model_training_source_head, "training source head", head=True)
        for label in ("episode_sha256", "task_roster_sha256", "checkpoint_sha256",
                      "maze_exposure_sha256", "control_matrix_sha256",
                      "development_event_sha256", "authority_head_sha256"):
            _digest(getattr(self, label), label)
        # This fixture is for the current MiniLM regenerative five-arm plan.
        # The Qwen R18 MeZO/QLoRA four-control benchmark is separate and its
        # frozen R16 corpus/producer manifest must not be silently replaced.
        if (type(self.training_program) is not str
                or type(self.bridge_semantics) is not str
                or self.training_program != "LABYRINTH_MINILM_FIVE_ARM"
                or self.bridge_semantics != "PROVENANCE_ONLY"
                or type(self.control_arms) is not tuple
                or any(type(arm) is not str for arm in self.control_arms)
                or self.control_arms != LABYRINTH_FIVE_ARMS):
            raise QualificationError("incompatible Labyrinth/model-training plan or controls")
        _int(self.epoch, "authority epoch", minimum=1)
        _int(self.fence, "fence", minimum=1)
        _int(self.now, "current time", minimum=1)
        if type(self.hosts) is not tuple or not self.hosts or len(self.hosts) > 16:
            raise QualificationError("invalid externally pinned host set")
        for host in self.hosts:
            if type(host) is not HostPin:
                raise QualificationError("invalid host pin")
            host.validate()
        if len({h.host_id for h in self.hosts}) != len(self.hosts):
            raise QualificationError("duplicate host pin")
        if len({h.route_id for h in self.hosts}) != len(self.hosts):
            raise QualificationError("duplicate pinned route ID")


@dataclass(frozen=True)
class RoleKeys:
    """Caller-held source verifier secrets; not a host key-custody attestation."""

    lease: bytes
    route: bytes
    effect: bytes

    def validate(self) -> None:
        keys = (self.lease, self.route, self.effect)
        if any(type(key) is not bytes or not 16 <= len(key) <= 128 for key in keys):
            raise QualificationError("invalid role verifier material")
        if len(set(keys)) != 3:
            raise QualificationError("lease/route/effect verifiers must be distinct")

    def for_role(self, role: str) -> bytes:
        self.validate()
        if type(role) is not str or role not in _ROLES:
            raise QualificationError("unknown receipt role")
        return getattr(self, role)


@dataclass(frozen=True)
class SignedReceipt:
    role: str
    payload_json: str
    mac_sha256: str


@dataclass(frozen=True)
class HostReceipts:
    host_id: str
    lease: SignedReceipt
    route: SignedReceipt
    effect: SignedReceipt


@dataclass(frozen=True)
class QualificationVerdict:
    source_envelope: EvidenceStatus
    physical_execution: EvidenceStatus
    distributed_single_model: EvidenceStatus
    claim: Claim
    claim_status: EvidenceStatus
    can_assert_physical_execution: bool
    reasons: tuple[str, ...]
    # Positive source-envelope matching is not a credential, host attestation,
    # replay guarantee, neural observation, or permission to execute effects.
    source_receipts_verified: bool = False
    host_identity_verified: bool = False
    external_monotonic_replay_protected: bool = False
    per_arm_learning_verified: bool = False
    can_authorize_execution: bool = False


def sign_source_receipt(role: str, payload: dict[str, Any], keys: RoleKeys) -> SignedReceipt:
    """For test/protocol fixtures; NOT enrollment or physical attestation."""
    secret = keys.for_role(role)
    if type(payload) is not dict or any(type(key) is not str for key in payload):
        raise QualificationError("invalid signed receipt payload keys")
    if set(payload) != _FIELDS[role]:
        raise QualificationError("receipt field inventory differs from role schema")
    data = _canonical(payload)
    mac = hmac.new(secret, (role + ":" + data).encode("ascii"), sha256).hexdigest()
    return SignedReceipt(role, data, mac)


def _verify(receipt: SignedReceipt, role: str, keys: RoleKeys) -> dict[str, Any]:
    if (type(receipt) is not SignedReceipt or type(receipt.role) is not str
            or receipt.role != role):
        raise QualificationError("receipt role mismatch")
    _digest(receipt.mac_sha256, "receipt MAC")
    data = _parse_canonical(receipt.payload_json)
    if set(data) != _FIELDS[role]:
        raise QualificationError("incorrect receipt field inventory")
    expected = hmac.new(keys.for_role(role), (role + ":" + receipt.payload_json)
                        .encode("ascii"), sha256).hexdigest()
    if not hmac.compare_digest(receipt.mac_sha256, expected):
        raise QualificationError("invalid receipt MAC")
    return data


def _verify_common(data: dict[str, Any], pins: ExactPins, host: HostPin,
                   nonce: str) -> None:
    expected = {
        "run_id": pins.run_id, "host_id": host.host_id,
        "owner_id": pins.owner_id,
        "authority_head_sha256": pins.authority_head_sha256,
        "epoch": pins.epoch, "fence": pins.fence,
        "episode_sha256": pins.episode_sha256,
        "task_roster_sha256": pins.task_roster_sha256,
        "checkpoint_sha256": pins.checkpoint_sha256,
        "lease_nonce": nonce,
        "rezon_source_head": pins.rezon_source_head,
        "labyrinth_source_head": pins.labyrinth_source_head,
        "model_training_source_head": pins.model_training_source_head,
        "maze_exposure_sha256": pins.maze_exposure_sha256,
        "control_matrix_sha256": pins.control_matrix_sha256,
        "development_event_sha256": pins.development_event_sha256,
        "training_program": pins.training_program,
        "bridge_semantics": pins.bridge_semantics,
    }
    for field, pinned in expected.items():
        if type(data[field]) is not type(pinned) or data[field] != pinned:
            raise QualificationError("receipt differs from pinned " + field)


def qualify_source_envelope(pins: ExactPins, keys: RoleKeys,
                            receipts: tuple[HostReceipts, ...],
                            claim: Claim) -> QualificationVerdict:
    """Verify exact signed source custody; NEVER qualify physical inference.

    Host/kernel/key custody must be established *outside* this source-only
    process. Consequently even a cryptographically valid multi-host envelope
    leaves actual tensor/KV/gradient/shared-model execution UNKNOWN.
    """
    if type(pins) is not ExactPins or type(keys) is not RoleKeys or type(claim) is not Claim:
        raise QualificationError("invalid qualification request types")
    pins.validate()
    keys.validate()
    if type(receipts) is not tuple or len(receipts) > len(pins.hosts):
        raise QualificationError("invalid receipt set")
    if not receipts:
        return QualificationVerdict(
            EvidenceStatus.SOURCE_ONLY, EvidenceStatus.UNKNOWN,
            EvidenceStatus.UNKNOWN, claim, EvidenceStatus.SOURCE_ONLY,
            False, ("no independent host receipts presented",))

    pins_by_host = {host.host_id: host for host in pins.hosts}
    observed_hosts: set[str] = set()
    observed_nonces: set[str] = set()
    observed_effects: set[str] = set()
    unresolved = False
    for bundle in receipts:
        if type(bundle) is not HostReceipts:
            raise QualificationError("invalid host receipt bundle")
        if type(bundle.host_id) is not str:
            raise QualificationError("invalid host receipt identity")
        if bundle.host_id not in pins_by_host or bundle.host_id in observed_hosts:
            raise QualificationError("foreign or duplicate host receipt")
        observed_hosts.add(bundle.host_id)
        host = pins_by_host[bundle.host_id]
        lease = _verify(bundle.lease, "lease", keys)
        route = _verify(bundle.route, "route", keys)
        effect = _verify(bundle.effect, "effect", keys)
        nonce = lease["lease_nonce"]
        _identifier(nonce, "lease nonce")
        if nonce in observed_nonces:
            raise QualificationError("replayed cross-host lease nonce")
        observed_nonces.add(nonce)
        for record in (lease, route, effect):
            _verify_common(record, pins, host, nonce)
        _int(lease["lease_expires_at"], "lease expiry", minimum=1)
        if lease["lease_expires_at"] <= pins.now:
            raise QualificationError("stale lease expiry")
        if lease["authority_sequence"] != host.authority_sequence or type(
                lease["authority_sequence"]) is not int:
            raise QualificationError("stale or foreign authority sequence")
        if lease["outcome"] != "AUTHORIZED":
            if lease["outcome"] == "UNKNOWN":
                unresolved = True
            else:
                raise QualificationError("not an authorized lease")
        if (route["route_id"] != host.route_id
                or type(route["route_generation"]) is not int
                or route["route_generation"] != host.route_generation):
            raise QualificationError("stale or foreign route generation")
        if route["outcome"] != "CONNECTED":
            if route["outcome"] == "UNKNOWN":
                unresolved = True
            else:
                raise QualificationError("route is not connected")
        _identifier(effect["effect_id"], "effect ID")
        _digest(effect["effect_sha256"], "effect digest")
        if effect["effect_id"] in observed_effects:
            raise QualificationError("duplicate committed effect ID")
        observed_effects.add(effect["effect_id"])
        if effect["effect_kind"] not in ("WHOLE_MODEL_TEXT", "TENSOR_OPERATION",
                                          "KV_OPERATION", "GRADIENT_OPERATION"):
            raise QualificationError("invalid effect kind")
        if effect["effect_kind"] != _CLAIM_EFFECT_KIND[claim]:
            raise QualificationError("effect kind cannot support requested claim")
        if effect["outcome"] != "COMMITTED":
            if effect["outcome"] == "UNKNOWN":
                unresolved = True
            else:
                raise QualificationError("uncommitted effect")

    if observed_hosts != set(pins_by_host) or unresolved:
        return QualificationVerdict(
            EvidenceStatus.UNKNOWN, EvidenceStatus.UNKNOWN,
            EvidenceStatus.UNKNOWN, claim, EvidenceStatus.UNKNOWN,
            False, ("incomplete or ambiguous host envelope",))
    return QualificationVerdict(
        EvidenceStatus.SOURCE_ONLY, EvidenceStatus.UNKNOWN,
        EvidenceStatus.UNKNOWN, claim,
        EvidenceStatus.SOURCE_ONLY if claim is Claim.INDEPENDENT_MODEL_RESPONSES
        else EvidenceStatus.UNKNOWN,
        False, (
            "source envelope HMACs match caller-supplied exact pins only",
            "HMAC verifier custody is caller asserted; host/runtime proof absent",
            "signed provider effect is not independent tensor/KV/gradient readback",
        ), source_receipts_verified=True)


def require_qualified_distributed_execution(verdict: QualificationVerdict) -> None:
    """Always fail closed for this deliberately offline source fixture."""
    raise QualificationError("physical distributed execution is not qualified")
