"""Opt-in T'Kal-in-ket hearing over a Rezon CollectiveStore episode.

Protocol inspired by the *documented* t-kal-in-ket deliberation pattern,
not derived from or importing its unlicensed implementation. This is a
virtual, durable shared workspace, NOT physical network transport, model
identity authentication, independent verification, or a decision authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3

from .collective import (
    CollectiveConflict, CollectiveStore, CollectiveValidationError,
    _agent, _digest, _text,
)

LENSES = ("purist_logic", "pragmatism", "bridge")
RESOLUTIONS = ("ANSWERED", "CONCEDED", "WAIVED", "PARTLY_ANSWERED", "UNRESOLVED")
VERDICTS = ("SUSTAIN", "REFINE", "WITHDRAW")


@dataclass(frozen=True)
class HearingView:
    episode_id: str
    input_digest: str
    hypothesis: str
    falsifier: str
    proposer: str
    lenses: dict[str, str]
    challenges: tuple[dict, ...]
    verdict: str | None
    rationale: str | None
    stale: bool

    def to_dict(self) -> dict:
        return {
            "episode_id": self.episode_id, "input_digest": self.input_digest,
            "hypothesis": self.hypothesis, "falsifier": self.falsifier,
            "proposer": self.proposer, "lenses": dict(self.lenses),
            "challenges": list(self.challenges), "verdict": self.verdict,
            "rationale": self.rationale, "stale": self.stale,
            "authority": "NONE", "independence_verified": False,
        }


class TkalVirtualNetwork:
    """Shared, append-only hearing rounds persisted beside CollectiveStore.

    The caller must authenticate a participant BEFORE supplying agent_id;
    direct Python callers and tokens do not prove independent model execution.
    """

    def __init__(self, store: CollectiveStore):
        if type(store) is not CollectiveStore:
            raise TypeError("existing Rezon CollectiveStore required")
        self.store = store
        with store._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tkal_hearings(
                    episode_id TEXT PRIMARY KEY,
                    input_digest TEXT NOT NULL,
                    hypothesis TEXT NOT NULL,
                    falsifier TEXT NOT NULL,
                    proposer TEXT NOT NULL,
                    lenses_json TEXT NOT NULL,
                    verdict TEXT, rationale TEXT
                );
                CREATE TABLE IF NOT EXISTS tkal_challenges(
                    episode_id TEXT NOT NULL,
                    challenge_id TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    lens TEXT NOT NULL,
                    target TEXT NOT NULL,
                    question TEXT NOT NULL,
                    response TEXT,
                    response_ref TEXT,
                    disposition TEXT,
                    rationale TEXT,
                    PRIMARY KEY(episode_id, challenge_id)
                );
            """)

    def _view(self, conn: sqlite3.Connection, episode_id: str) -> HearingView:
        row = conn.execute(
            "SELECT input_digest,hypothesis,falsifier,proposer,lenses_json,verdict,rationale "
            "FROM tkal_hearings WHERE episode_id=?", (episode_id,),
        ).fetchone()
        if row is None:
            raise CollectiveConflict("hearing not opened")
        challenges = tuple({
            "challenge_id": c[0], "reviewer": c[1], "lens": c[2],
            "target": c[3], "question": c[4], "response": c[5],
            "response_ref": c[6], "disposition": c[7], "rationale": c[8],
        } for c in conn.execute(
            "SELECT challenge_id,reviewer,lens,target,question,response,"
            "response_ref,disposition,rationale FROM tkal_challenges "
            "WHERE episode_id=? ORDER BY rowid", (episode_id,),
        ))
        snap = self.store._snapshot(conn, episode_id)
        return HearingView(episode_id, row[0], row[1], row[2], row[3],
                           json.loads(row[4]), challenges, row[5], row[6],
                           row[0] != snap.digest)

    def snapshot(self, episode_id: str) -> HearingView:
        with self.store._connect() as conn:
            conn.execute("BEGIN")
            try:
                result = self._view(conn, episode_id)
                conn.commit()
                return result
            except BaseException:
                conn.rollback()
                raise

    def _mutate(self, episode_id: str, operation):
        with self.store._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                view = self._view(conn, episode_id)
                if view.stale or view.verdict is not None:
                    raise CollectiveConflict("hearing stale or closed")
                result = operation(conn, view)
                conn.commit()
                return result
            except BaseException:
                conn.rollback()
                raise

    def open(self, episode_id: str, *, expected_digest: str,
             proposer: str, lenses: dict[str, str],
             hypothesis: str, falsifier: str) -> HearingView:
        _agent(proposer)
        _text(hypothesis, 4096, "hypothesis")
        _text(falsifier, 4096, "falsifier")
        if (type(lenses) is not dict or set(lenses) != set(LENSES)
                or any(type(v) is not str for v in lenses.values())):
            raise CollectiveValidationError("exact three peer lenses required")
        for agent in lenses.values():
            _agent(agent)
        if len(set(lenses.values())) != 3 or proposer in lenses.values():
            raise CollectiveValidationError("four distinct worker identities required")
        if type(expected_digest) is not str or len(expected_digest) != 64:
            raise CollectiveValidationError("frozen input digest required")
        with self.store._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                snap = self.store._snapshot(conn, episode_id)
                if (not snap.complete or snap.digest != expected_digest
                        or set(snap.agents) != {proposer, *lenses.values()}):
                    raise CollectiveConflict("incomplete or stale four-worker episode")
                actual_reviewers = {r.agent_id for r in snap.reviews}
                if not set(lenses.values()).issubset(actual_reviewers):
                    raise CollectiveConflict("three peer first reviews required")
                if conn.execute("SELECT 1 FROM tkal_hearings WHERE episode_id=?",
                                (episode_id,)).fetchone():
                    raise CollectiveConflict("hearing already exists")
                conn.execute(
                    "INSERT INTO tkal_hearings VALUES (?,?,?,?,?,?,NULL,NULL)",
                    (episode_id, snap.digest, hypothesis, falsifier,
                     proposer, json.dumps(lenses, sort_keys=True)),
                )
                result = self._view(conn, episode_id)
                conn.commit()
                return result
            except BaseException:
                conn.rollback()
                raise

    def challenge(self, episode_id: str, *, reviewer: str,
                  challenge_id: str, target: str, question: str) -> HearingView:
        _agent(reviewer); _agent(challenge_id); _agent(target)
        _text(question, 4096, "question")

        def apply(conn, view):
            matches = [lens for lens, agent in view.lenses.items() if agent == reviewer]
            if not matches or target == reviewer or target not in {view.proposer, *view.lenses.values()}:
                raise CollectiveValidationError("reviewer/target identity mismatch")
            if any(c["disposition"] is None for c in view.challenges):
                raise CollectiveConflict("only one unresolved challenge at a time")
            if any(c["challenge_id"] == challenge_id for c in view.challenges):
                raise CollectiveConflict("challenge ID replay")
            conn.execute(
                "INSERT INTO tkal_challenges VALUES (?,?,?,?,?,?,NULL,NULL,NULL,NULL)",
                (episode_id, challenge_id, reviewer, matches[0], target, question),
            )
            return self._view(conn, episode_id)

        return self._mutate(episode_id, apply)

    def defend(self, episode_id: str, *, challenge_id: str,
               defender: str, response: str, evidence_ref: str) -> HearingView:
        _agent(challenge_id); _agent(defender)
        _text(response, 8192, "defense")
        _text(evidence_ref, 1024, "evidence reference")

        def apply(conn, view):
            matches = [c for c in view.challenges if c["challenge_id"] == challenge_id]
            if not matches or matches[0]["target"] != defender:
                raise CollectiveValidationError("only challenged worker may defend")
            c = matches[0]
            if c["response"] is not None or c["disposition"] is not None:
                raise CollectiveConflict("defense already provided or resolved")
            conn.execute(
                "UPDATE tkal_challenges SET response=?,response_ref=? "
                "WHERE episode_id=? AND challenge_id=?",
                (response, evidence_ref, episode_id, challenge_id),
            )
            return self._view(conn, episode_id)

        return self._mutate(episode_id, apply)

    def resolve(self, episode_id: str, *, challenge_id: str,
                disposition: str, rationale: str) -> HearingView:
        _agent(challenge_id); _text(rationale, 4096, "rationale")
        if disposition not in RESOLUTIONS or type(disposition) is not str:
            raise CollectiveValidationError("invalid disposition")

        def apply(conn, view):
            matches = [c for c in view.challenges if c["challenge_id"] == challenge_id]
            if not matches or matches[0]["disposition"] is not None:
                raise CollectiveConflict("missing/already resolved challenge")
            c = matches[0]
            if disposition == "ANSWERED" and not c["response"]:
                raise CollectiveConflict("answer must exist before answered disposition")
            conn.execute(
                "UPDATE tkal_challenges SET disposition=?,rationale=? "
                "WHERE episode_id=? AND challenge_id=?",
                (disposition, rationale, episode_id, challenge_id),
            )
            return self._view(conn, episode_id)

        return self._mutate(episode_id, apply)

    def determine(self, episode_id: str, *, verdict: str,
                  rationale: str) -> HearingView:
        _text(rationale, 4096, "rationale")
        if type(verdict) is not str or verdict not in VERDICTS:
            raise CollectiveValidationError("invalid verdict")

        def apply(conn, view):
            challenged = {c["lens"] for c in view.challenges}
            if not set(LENSES).issubset(challenged):
                raise CollectiveConflict("each lens must cross-examine before determination")
            if any(c["disposition"] not in ("ANSWERED", "CONCEDED", "WAIVED")
                   for c in view.challenges):
                raise CollectiveConflict("unanswered/partial/unresolved challenge")
            if verdict == "SUSTAIN":
                # A chair's unilateral WAIVED resolution (or three
                # proposer-only answers) cannot stand in for reciprocal
                # peer examination. Required: all three lenses challenge
                # and all three peer lenses supply attributable responses.
                answered = [c for c in view.challenges
                            if c["disposition"] in ("ANSWERED", "CONCEDED")
                            and c["response"] and c["response_ref"]
                            and c["target"] in view.lenses.values()
                            and c["reviewer"] != c["target"]]
                challengers = {c["lens"] for c in answered}
                respondents = {
                    lens for c in answered for lens, peer in view.lenses.items()
                    if peer == c["target"]
                }
                if challengers != set(LENSES) or respondents != set(LENSES):
                    raise CollectiveConflict(
                        "SUSTAIN requires directed, attributed peer exchanges across all lenses"
                    )
            conn.execute(
                "UPDATE tkal_hearings SET verdict=?,rationale=? WHERE episode_id=?",
                (verdict, rationale, episode_id),
            )
            return self._view(conn, episode_id)

        return self._mutate(episode_id, apply)
