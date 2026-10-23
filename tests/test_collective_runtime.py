from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Barrier, Event, Thread

import pytest

from rezon.collective import (
    CollectiveConflict,
    CollectiveStore,
    CollectiveValidationError,
    run_independent_models,
    run_peer_reviews,
    synthesize_with_model,
)
from rezon.epistemics import PropositionKind


def _store(tmp: str) -> CollectiveStore:
    return CollectiveStore(Path(tmp) / "collaboration.sqlite3")


def test_concurrent_agents_share_one_durable_episode_and_cannot_overwrite_each_other():
    with TemporaryDirectory() as tmp:
        store = _store(tmp)
        episode_id = store.create("Why did the motor stop?", ("alpha", "beta"))
        barrier = Barrier(2)

        def submit(agent):
            barrier.wait(timeout=3)
            return store.submit_answer(episode_id, agent, f"Answer from {agent}", ("log:1",))

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(submit, ("alpha", "beta")))

        assert len(set(results)) == 2
        readback = _store(tmp).snapshot(episode_id)
        assert readback.complete is True
        assert {item.agent_id for item in readback.answers} == {"alpha", "beta"}
        assert readback.answers[0].kind == "answer"
        assert store.submit_answer(episode_id, "alpha", "Answer from alpha", ("log:1",)) == results[0]
        with pytest.raises(CollectiveConflict):
            store.submit_answer(episode_id, "alpha", "different answer")
        with pytest.raises(CollectiveValidationError):
            store.submit_answer(episode_id, "stranger", "intrusion")


def test_review_requires_initial_independence_and_targets_real_outputs():
    with TemporaryDirectory() as tmp:
        store = _store(tmp)
        ep = store.create("Question", ("a", "b"))
        a_id = store.submit_answer(ep, "a", "Claim A")
        with pytest.raises(CollectiveConflict):
            store.submit_review(ep, "a", "I disagree", (a_id,))
        store.submit_answer(ep, "b", "Claim B")
        with pytest.raises(CollectiveValidationError):
            store.submit_review(ep, "a", "I disagree", ("unknown",))
        rid = store.submit_review(ep, "a", "B assumes no load", ("answer:b",))
        assert rid == "review:a"
        snapshot = store.snapshot(ep)
        assert snapshot.reviews[0].target_ids == ("answer:b",)
        canonical = store.project_episode(ep).snapshot()
        assert {p.kind for p in canonical.current_propositions} == {
            PropositionKind.QUESTION, PropositionKind.CLAIM,
        }
        assert any(r.relation_type == "challenges" for r in canonical.current_relations)


def test_models_run_concurrently_without_peer_answers_and_synthesis_is_bound_to_state():
    with TemporaryDirectory() as tmp:
        store = _store(tmp)
        ep = store.create("Evaluate the literal claim", ("m1", "m2"))
        entered = Barrier(2)
        seen = {}

        class Model:
            def __init__(self, agent_id):
                self.agent_id = agent_id

            def complete(self, messages):
                seen[self.agent_id] = messages
                entered.wait(timeout=3)
                return f"{self.agent_id} finds uncertainty"

        outcome = run_independent_models(store, ep, (Model("m1"), Model("m2")))
        assert outcome == {"m1": "submitted", "m2": "submitted"}
        assert len(seen) == 2
        assert all("finds uncertainty" not in str(msg) for msg in seen.values())

        begin = Event()
        release = Event()

        class Integrator:
            agent_id = "integrator"

            def complete(self, messages):
                assert "m1 finds uncertainty" in str(messages)
                assert "m2 finds uncertainty" in str(messages)
                begin.set()
                assert release.wait(timeout=3)
                return "Neither answer is independently verified."

        outcome_holder = []

        def do_synthesis():
            try:
                outcome_holder.append(synthesize_with_model(store, ep, Integrator()))
            except Exception as exc:
                outcome_holder.append(exc)

        worker = Thread(target=do_synthesis)
        worker.start()
        assert begin.wait(timeout=3)
        store.submit_review(ep, "m1", "Potential shared assumption", ("answer:m2",))
        release.set()
        worker.join(timeout=3)
        assert len(outcome_holder) == 1
        assert isinstance(outcome_holder[0], CollectiveConflict)  # stale synthesis rejected

        fresh = synthesize_with_model(store, ep, IntegratorNoBarrier())
        assert fresh.status == "unverified_model_synthesis"
        assert store.snapshot(ep).syntheses[-1] == fresh
        assert any(p.kind is PropositionKind.HYPOTHESIS for p in store.project_episode(ep).snapshot().current_propositions)


class IntegratorNoBarrier:
    agent_id = "integrator"

    def complete(self, messages):
        return "Unverified synthesis that cites the two contributions."


def test_failed_worker_does_not_turn_into_a_vote_or_permit_complete_synthesis():
    with TemporaryDirectory() as tmp:
        store = _store(tmp)
        ep = store.create("Task", ("ok", "broken"))

        class Good:
            agent_id = "ok"

            def complete(self, messages):
                return "Supported? Unknown."

        class Bad:
            agent_id = "broken"

            def complete(self, messages):
                raise RuntimeError("do not leak private information")

        outcome = run_independent_models(store, ep, (Good(), Bad()))
        assert outcome["ok"] == "submitted"
        assert outcome["broken"] == "failed:RuntimeError"
        assert store.snapshot(ep).missing_agents == ("broken",)
        assert "private information" not in str(store.snapshot(ep))
        with pytest.raises(CollectiveConflict):
            synthesize_with_model(store, ep, IntegratorNoBarrier())


def test_read_snapshot_is_atomic_during_concurrent_write():
    with TemporaryDirectory() as tmp:
        reader = _store(tmp)
        writer = _store(tmp)
        ep = reader.create("Task", ("one", "two"))
        writer.submit_answer(ep, "one", "First")
        paused = Event()
        resume = Event()
        original_snapshot = reader._snapshot

        def controlled_read(connection, episode_id):
            # Pin the WAL read snapshot before a concurrent writer commits.
            assert connection.execute("SELECT prompt FROM episodes WHERE episode_id=?",
                                      (episode_id,)).fetchone()
            paused.set()
            assert resume.wait(timeout=3)
            return original_snapshot(connection, episode_id)

        reader._snapshot = controlled_read
        result = []
        thread = Thread(target=lambda: result.append(reader.snapshot(ep)))
        thread.start()
        assert paused.wait(timeout=3)
        try:
            writer.submit_answer(ep, "two", "Second")
        finally:
            resume.set()
        thread.join(timeout=3)
        assert len(result) == 1
        assert result[0].missing_agents == ("two",)
        assert writer.snapshot(ep).complete


def test_old_syntheses_remain_auditable_but_not_current_claims():
    with TemporaryDirectory() as tmp:
        store = _store(tmp)
        ep = store.create("Task", ("one", "two"))
        store.submit_answer(ep, "one", "Observation 1")
        store.submit_answer(ep, "two", "Observation 2")
        first = synthesize_with_model(store, ep, IntegratorNoBarrier())
        assert store.snapshot(ep).to_dict()["syntheses"][0]["is_current"]
        store.submit_review(ep, "one", "Observation 2 may be wrong", ("answer:two",))
        stale = store.snapshot(ep)
        assert stale.syntheses == (first,)
        assert not stale.to_dict()["syntheses"][0]["is_current"]
        assert all(p.kind is not PropositionKind.HYPOTHESIS for p in
                   store.project_episode(ep).snapshot().current_propositions)
        second = synthesize_with_model(store, ep, IntegratorNoBarrier())
        assert second.input_digest != first.input_digest
        assert [s["is_current"] for s in store.snapshot(ep).to_dict()["syntheses"]] == [False, True]
        assert sum(p.kind is PropositionKind.HYPOTHESIS for p in
                   store.project_episode(ep).snapshot().current_propositions) == 1


def test_separate_processes_submit_to_one_durable_episode():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "multi-process.sqlite3"
        store = CollectiveStore(db)
        ep = store.create("Independent process check", ("one", "two"))
        script = (
            "import sys; from rezon.collective import CollectiveStore; "
            "CollectiveStore(sys.argv[1]).submit_answer(sys.argv[2], "
            "sys.argv[3], 'Message from ' + sys.argv[3])"
        )
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
        workers = [subprocess.Popen((sys.executable, "-c", script, str(db), ep, agent),
                                    env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                   for agent in ("one", "two")]
        for worker in workers:
            _stdout, stderr = worker.communicate(timeout=10)
            assert worker.returncode == 0, stderr.decode()
        assert [c.agent_id for c in store.snapshot(ep).answers] == ["one", "two"]


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission semantics")
def test_fresh_episode_database_is_owner_only():
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "private.sqlite3"
        CollectiveStore(path)
        assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_models_challenge_one_another_only_after_initial_answers_finish():
    with TemporaryDirectory() as tmp:
        store = _store(tmp)
        ep = store.create("Evaluate tradeoffs", ("alpha", "beta"))
        seen = {}

        class Model:
            def __init__(self, agent_id):
                self.agent_id = agent_id
                self.rounds = 0

            def complete(self, messages):
                self.rounds += 1
                if self.rounds == 1:
                    assert "peer_claims_unverified" not in str(messages)
                    return f"Initial answer {self.agent_id}"
                assert "peer_claims_unverified" in str(messages)
                assert "answer:" in str(messages)
                assert "review:" not in str(messages)
                seen[self.agent_id] = messages
                return f"Critique from {self.agent_id}"

        models = (Model("alpha"), Model("beta"))
        with pytest.raises(CollectiveConflict):
            run_peer_reviews(store, ep, models)
        assert run_independent_models(store, ep, models) == {
            "alpha": "submitted", "beta": "submitted",
        }
        assert run_peer_reviews(store, ep, models) == {
            "alpha": "submitted", "beta": "submitted",
        }
        snap = store.snapshot(ep)
        assert len(seen) == 2 and len(snap.reviews) == 2
        assert {(r.agent_id, r.target_ids) for r in snap.reviews} == {
            ("alpha", ("answer:beta",)), ("beta", ("answer:alpha",)),
        }
        assert len(store.project_episode(ep).snapshot().current_relations) == 2
        assert synthesize_with_model(store, ep, IntegratorNoBarrier()).input_digest == snap.digest


def test_review_cannot_challenge_own_answer_even_alongside_peer_target():
    with TemporaryDirectory() as tmp:
        store = _store(tmp)
        ep = store.create("Independent peer challenge", ("alice", "bob"))
        store.submit_answer(ep, "alice", "Alice's initial claim")
        store.submit_answer(ep, "bob", "Bob's initial claim")

        for targets in (("answer:alice",), ("answer:bob", "answer:alice")):
            with pytest.raises(CollectiveValidationError):
                store.submit_review(ep, "alice", "Claimed peer review", targets)
        assert store.snapshot(ep).reviews == ()

        assert store.submit_review(ep, "alice", "Bob's claim needs evidence",
                                   ("answer:bob",)) == "review:alice"
        assert store.snapshot(ep).reviews[0].target_ids == ("answer:bob",)
