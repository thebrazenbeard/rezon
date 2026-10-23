"""Portable, no-effect blind/reveal federation for one Rezon reasoning episode.

A GitHub issue, file, or other transport may carry exact JSON envelopes.
Hashes detect ordinary substitution, not independently authenticate workers,
model consumption, chronology, truth custody or host execution.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_NONCE = re.compile(r"[0-9a-f]{32}\Z")
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
_METHODS = ("LOCAL_MODEL", "DETERMINISTIC", "INDEPENDENT_REVIEW")


def _canonical(payload: dict[str, object]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def _digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _identifier(value: str) -> bool:
    return type(value) is str and _NAME.fullmatch(value) is not None


def _text(value: str, maximum: int = 1500) -> bool:
    return type(value) is str and 0 < len(value.strip()) <= maximum


def _digest_string(value: str) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class SharedTopic:
    topic_id: str
    literal_question: str
    constraints: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _identifier(self.topic_id) or not _text(self.literal_question):
            raise ValueError("invalid topic identity/question")
        if (type(self.constraints) is not tuple or len(self.constraints) > 16
                or any(not _text(x, 500) for x in self.constraints)
                or len(set(self.constraints)) != len(self.constraints)):
            raise ValueError("invalid topic constraints")

    @property
    def digest(self) -> str:
        return _digest({
            "schema": "rezon.shared-topic.v1", "topic_id": self.topic_id,
            "literal_question": self.literal_question,
            "constraints": list(self.constraints),
        })


@dataclass(frozen=True, slots=True)
class BlindProposal:
    topic_digest: str
    worker_id: str
    host_id: str
    method: str
    method_identity: str
    input_digest: str
    literal_claim: str
    disconfirming_observation: str
    evidence_refs: tuple[str, ...]
    nonce: str
    peer_answers_visible: bool = False

    def __post_init__(self) -> None:
        if not _digest_string(self.topic_digest) or not _digest_string(self.input_digest):
            raise ValueError("invalid subject/context digest")
        if not _identifier(self.worker_id) or not _identifier(self.host_id):
            raise ValueError("invalid worker/host")
        if self.method not in _METHODS or not _text(self.method_identity, 200):
            raise ValueError("invalid method identity")
        if not _text(self.literal_claim) or not _text(self.disconfirming_observation):
            raise ValueError("claim and falsifier must be explicit")
        if (type(self.evidence_refs) is not tuple or len(self.evidence_refs) > 16
                or any(not _text(x, 200) for x in self.evidence_refs)
                or len(set(self.evidence_refs)) != len(self.evidence_refs)):
            raise ValueError("invalid evidence references")
        if type(self.nonce) is not str or not _NONCE.fullmatch(self.nonce):
            raise ValueError("require unpredictable 16-byte nonce in hex")
        if self.peer_answers_visible is not False:
            raise ValueError("blind proposals must not consume peer answers")

    def subject(self) -> dict[str, object]:
        return {
            "schema": "rezon.blind-proposal.v1",
            "topic_digest": self.topic_digest,
            "worker_id": self.worker_id,
            "host_id": self.host_id,
            "method": self.method,
            "method_identity": self.method_identity,
            "input_digest": self.input_digest,
            "literal_claim": self.literal_claim,
            "disconfirming_observation": self.disconfirming_observation,
            "evidence_refs": list(self.evidence_refs),
            "nonce": self.nonce,
            "peer_answers_visible": self.peer_answers_visible,
        }

    @property
    def digest(self) -> str:
        return _digest(self.subject())


@dataclass(frozen=True, slots=True)
class BlindCommitment:
    topic_digest: str
    worker_id: str
    host_id: str
    proposal_digest: str

    def __post_init__(self) -> None:
        if (not _digest_string(self.topic_digest)
                or not _digest_string(self.proposal_digest)
                or not _identifier(self.worker_id) or not _identifier(self.host_id)):
            raise ValueError("invalid commitment")

    def subject(self) -> dict[str, str]:
        return {
            "schema": "rezon.blind-commitment.v1",
            "topic_digest": self.topic_digest,
            "worker_id": self.worker_id, "host_id": self.host_id,
            "proposal_digest": self.proposal_digest,
        }


def commit(proposal: BlindProposal) -> BlindCommitment:
    if type(proposal) is not BlindProposal:
        raise TypeError("exact BlindProposal required")
    return BlindCommitment(
        proposal.topic_digest, proposal.worker_id,
        proposal.host_id, proposal.digest,
    )


@dataclass(frozen=True, slots=True)
class PeerChallenge:
    topic_digest: str
    challenger_worker_id: str
    target_worker_id: str
    target_proposal_digest: str
    literal_objection: str
    falsification_test: str

    def __post_init__(self) -> None:
        if (not _digest_string(self.topic_digest)
                or not _digest_string(self.target_proposal_digest)
                or not _identifier(self.challenger_worker_id)
                or not _identifier(self.target_worker_id)
                or not _text(self.literal_objection)
                or not _text(self.falsification_test)):
            raise ValueError("invalid challenge")


class SharedEpisode:
    """In-process verifier of portable packets; transport/custody are external."""

    def __init__(self, topic: SharedTopic, participant_hosts: dict[str, str]):
        if type(topic) is not SharedTopic:
            raise TypeError("exact SharedTopic required")
        if (type(participant_hosts) is not dict or len(participant_hosts) < 2
                or len(participant_hosts) > 8
                or any(not _identifier(k) or not _identifier(v)
                       for k, v in participant_hosts.items())
                or len(set(participant_hosts.values())) != len(participant_hosts)):
            raise ValueError("unique worker and host identities required")
        self.topic = topic
        self.participant_hosts = dict(participant_hosts)
        self._commitments: dict[str, BlindCommitment] = {}
        self._reveals: dict[str, BlindProposal] = {}
        self._challenges: list[PeerChallenge] = []

    def submit_commitment(self, receipt: BlindCommitment) -> None:
        if type(receipt) is not BlindCommitment:
            raise TypeError("exact commitment required")
        if (receipt.topic_digest != self.topic.digest
                or self.participant_hosts.get(receipt.worker_id) != receipt.host_id):
            raise ValueError("wrong topic or unassigned host")
        if receipt.worker_id in self._commitments:
            raise ValueError("commitment replay or overwrite")
        if self._reveals:
            raise ValueError("commit phase already closed")
        self._commitments[receipt.worker_id] = receipt

    @property
    def ready_to_reveal(self) -> bool:
        return len(self._commitments) == len(self.participant_hosts)

    @property
    def ready_to_challenge(self) -> bool:
        return len(self._reveals) == len(self.participant_hosts)

    def reveal(self, proposal: BlindProposal) -> None:
        if type(proposal) is not BlindProposal:
            raise TypeError("exact proposal required")
        if not self.ready_to_reveal:
            raise ValueError("do not reveal before every host has committed")
        current = self._commitments.get(proposal.worker_id)
        if current is None or current != commit(proposal):
            raise ValueError("proposal does not match frozen worker commitment")
        if proposal.worker_id in self._reveals:
            raise ValueError("proposal replay")
        self._reveals[proposal.worker_id] = proposal

    def challenge(self, challenge: PeerChallenge) -> None:
        if type(challenge) is not PeerChallenge:
            raise TypeError("exact PeerChallenge required")
        if not self.ready_to_challenge:
            raise ValueError("cannot cross-challenge before full reveal")
        if (challenge.topic_digest != self.topic.digest
                or challenge.challenger_worker_id not in self.participant_hosts
                or challenge.challenger_worker_id == challenge.target_worker_id):
            raise ValueError("invalid challenger/target")
        target = self._reveals.get(challenge.target_worker_id)
        if target is None or target.digest != challenge.target_proposal_digest:
            raise ValueError("challenge must bind exact revealed opponent claim")
        if challenge in self._challenges:
            raise ValueError("duplicate challenge")
        self._challenges.append(challenge)

    def summary(self) -> dict[str, object]:
        return {
            "topic_digest": self.topic.digest,
            "required_workers": sorted(self.participant_hosts),
            "committed_workers": sorted(self._commitments),
            "revealed_workers": sorted(self._reveals),
            "challenge_count": len(self._challenges),
            "status": (
                "CROSS_CHALLENGE" if self.ready_to_challenge
                else "REVEAL" if self.ready_to_reveal
                else "WAITING_FOR_BLIND_COMMITS"
            ),
            "independently_attested": False,
            "consensus_qualified": False,
            "authorization_effect": "NONE",
        }
