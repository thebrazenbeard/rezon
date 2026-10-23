"""A shared Rezon topic is not proof of independent model reasoning."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import unittest

from rezon.federation import (
    SharedTopic, BlindProposal, BlindCommitment, PeerChallenge,
    SharedEpisode, commit,
)


TOPIC = SharedTopic(
    "goal1-four-host-20261023",
    "What minimum observation would distinguish feedback-caused learning in "
    "QualifiedVeraRuntime from prompt conditioning, retrieval, or memorization "
    "across a cold restart?",
    ("same literal proposition", "no secret evaluator labels",
     "no privileged effects"),
)
HOSTS = {
    "vera-lappy": "Lappy",
    "vera-vn1": "VERA-NODE-1",
    "vera-vn2": "VN2",
    "malaphor": "MT-262029",
}


def proposal(worker: str, answer: str = "Measure new-task improvement") -> BlindProposal:
    return BlindProposal(
        topic_digest=TOPIC.digest,
        worker_id=worker,
        host_id=HOSTS[worker],
        method="LOCAL_MODEL" if worker == "vera-lappy" else "DETERMINISTIC",
        method_identity="test-method-v1",
        input_digest=hashlib.sha256(b"unchanged context").hexdigest(),
        literal_claim=answer,
        disconfirming_observation="Frozen control equals revised performance",
        evidence_refs=("source@head",), nonce=("a" * 28 + str(list(HOSTS).index(worker)).zfill(4)),
    )


class SharedEpisodeTests(unittest.TestCase):
    def test_full_blind_commit_reveal_and_cross_challenge(self):
        board = SharedEpisode(TOPIC, HOSTS)
        proposals = [proposal(worker) for worker in HOSTS]
        with self.assertRaisesRegex(ValueError, "before every host"):
            board.reveal(proposals[0])
        for item in proposals:
            board.submit_commitment(commit(item))
        self.assertTrue(board.ready_to_reveal)
        with self.assertRaisesRegex(ValueError, "replay"):
            board.submit_commitment(commit(proposals[0]))
        for item in proposals:
            board.reveal(item)
        self.assertTrue(board.ready_to_challenge)
        ref = proposals[0]
        board.challenge(PeerChallenge(
            topic_digest=TOPIC.digest,
            challenger_worker_id="malaphor",
            target_worker_id=ref.worker_id,
            target_proposal_digest=ref.digest,
            literal_objection="What if the gain was from longer context?",
            falsification_test="Repeat with exact matched context length.",
        ))
        self.assertEqual(board.summary()["challenge_count"], 1)
        self.assertFalse(board.summary()["independently_attested"])
        self.assertFalse(board.summary()["consensus_qualified"])
        self.assertEqual(board.summary()["authorization_effect"], "NONE")

    def test_rejects_unknown_host_reused_commit_and_cross_topic(self):
        board = SharedEpisode(TOPIC, HOSTS)
        item = proposal("vera-lappy")
        with self.assertRaisesRegex(ValueError, "unassigned host"):
            board.submit_commitment(replace(commit(item), host_id="wrong-host"))
        with self.assertRaisesRegex(ValueError, "wrong topic"):
            board.submit_commitment(replace(commit(item), topic_digest="b" * 64))
        board.submit_commitment(commit(item))
        with self.assertRaisesRegex(ValueError, "replay"):
            board.submit_commitment(commit(item))

    def test_rejects_changed_proposal_after_commit(self):
        board = SharedEpisode(TOPIC, HOSTS)
        proposals = [proposal(w) for w in HOSTS]
        for p in proposals:
            board.submit_commitment(commit(p))
        with self.assertRaisesRegex(ValueError, "does not match"):
            board.reveal(replace(proposals[0], literal_claim="posthoc different answer"))
        board.reveal(proposals[0])

    def test_early_or_self_challenge_denied(self):
        board = SharedEpisode(TOPIC, HOSTS)
        proposals = [proposal(w) for w in HOSTS]
        for p in proposals:
            board.submit_commitment(commit(p))
        c = PeerChallenge(
            TOPIC.digest, "vera-vn1", "vera-lappy", proposals[0].digest,
            "Consider prompt leakage", "Use new cases with a blinded label",
        )
        with self.assertRaisesRegex(ValueError, "full reveal"):
            board.challenge(c)
        for p in proposals:
            board.reveal(p)
        with self.assertRaisesRegex(ValueError, "challenger/target"):
            board.challenge(replace(c, target_worker_id="vera-vn1"))
        board.challenge(c)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            board.challenge(c)

    def test_no_peer_answers_or_forged_nonce(self):
        with self.assertRaisesRegex(ValueError, "peer answers"):
            replace(proposal("vera-vn1"), peer_answers_visible=True)
        with self.assertRaisesRegex(ValueError, "nonce"):
            replace(proposal("vera-vn1"), nonce="guess")
        with self.assertRaisesRegex(ValueError, "unique worker"):
            SharedEpisode(TOPIC, {"w1": "host1", "w2": "host1"})

    def test_portable_canonical_hash_matches_json_roundtrip(self):
        p = proposal("vera-vn2")
        subject = p.subject()
        self.assertEqual(subject["topic_digest"], TOPIC.digest)
        self.assertEqual(json.loads(json.dumps(subject)), subject)
        self.assertEqual(p.digest, commit(p).proposal_digest)
        self.assertEqual(
            hashlib.sha256(json.dumps(
                subject, sort_keys=True, separators=(",", ":"),
                ensure_ascii=False, allow_nan=False,
            ).encode()).hexdigest(), p.digest,
        )


if __name__ == "__main__":
    unittest.main()
