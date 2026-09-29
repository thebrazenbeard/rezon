from threading import Event, Thread

import rezon.admission as admission_module
from rezon.admission import admit_execution_result
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.provenance import canonical_episode_snapshot_digest


def test_concurrent_episode_mutation_cannot_interleave_inside_admission(monkeypatch):
    episode = Episode("r19-race")
    captured_digest = canonical_episode_snapshot_digest(episode.snapshot())

    descriptor = NodeDescriptor(
        "generator",
        (PropositionKind.HYPOTHESIS,),
    )
    result = ExecutionResult(
        execution_id="attempt-r19",
        node_id="generator",
        emitted_propositions=(
            Proposition(
                proposition_id="admitted-output",
                episode_id=episode.episode_id,
                kind=PropositionKind.HYPOTHESIS,
                content="computed from captured state",
                producer_execution_id="attempt-r19",
            ),
        ),
    )

    entered_prevalidate = Event()
    mutator_attempting = Event()
    mutator_completed = Event()
    interleaved = []

    original_prevalidate = admission_module._prevalidate_episode_mutation

    def wrapped_prevalidate(ep, execution_result):
        entered_prevalidate.set()
        assert mutator_attempting.wait(2)
        mutator_completed.wait(0.2)
        interleaved.append(mutator_completed.is_set())
        return original_prevalidate(ep, execution_result)

    monkeypatch.setattr(
        admission_module,
        "_prevalidate_episode_mutation",
        wrapped_prevalidate,
    )

    def mutate_concurrently():
        assert entered_prevalidate.wait(2)
        mutator_attempting.set()
        episode.add_proposition(
            Proposition(
                proposition_id="concurrent-input",
                episode_id=episode.episode_id,
                kind=PropositionKind.OBSERVATION,
                content="concurrent state change",
            )
        )
        mutator_completed.set()

    thread = Thread(target=mutate_concurrently)
    thread.start()

    receipt = admit_execution_result(
        episode,
        descriptor,
        result,
        expected_episode_snapshot_digest=captured_digest,
        expected_execution_id="attempt-r19",
    )
    thread.join(timeout=2)

    assert receipt.canonical_producer_execution_id is not None
    assert mutator_completed.is_set()
    assert interleaved == [False]

    snapshot = episode.snapshot()
    assert tuple(event.target_id for event in snapshot.events) == (
        "admitted-output",
        "concurrent-input",
    )
    assert tuple(
        proposition.proposition_id
        for proposition in snapshot.current_propositions
    ) == (
        "admitted-output",
        "concurrent-input",
    )
