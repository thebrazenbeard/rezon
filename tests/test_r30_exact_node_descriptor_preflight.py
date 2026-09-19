from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class FlipBool:
    def __init__(self, true_calls=2):
        self.calls = 0
        self.true_calls = true_calls

    def __bool__(self):
        self.calls += 1
        return self.calls <= self.true_calls


class AlwaysEqualStr(str):
    def __new__(cls, value, target):
        obj = str.__new__(cls, value)
        obj.target = target
        return obj

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash(self.target)


class DescriptorSubclass(NodeDescriptor):
    pass


class SpyEmitter:
    node_id = "echo_hypothesis"

    def __init__(self):
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h-spy",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "candidate",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


class PeerReader:
    node_id = "echo_hypothesis"

    def __init__(self):
        self.calls = 0

    def execute(self, view, episode_id):
        self.calls += 1
        peer = next(p for p in view.propositions if p.proposition_id == "peer-h")
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "copied-peer",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    f"copied {peer.content}",
                    source_refs=("peer-h",),
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _run(descriptor, executor, episode=None):
    episode = Episode("e1") if episode is None else episode
    node = RunnerNode(descriptor, executor, VisibilityPolicy())
    outcome = EpisodeRunner((node,), budget_limit=1).run(episode, task_id="t-r30")
    return episode, outcome


def _assert_preflight_rejects(descriptor, executor, episode=None):
    episode, outcome = _run(descriptor, executor, episode)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert executor.calls == 0
    assert "h-spy" not in {p.proposition_id for p in episode.snapshot().current_propositions}


def test_stateful_independence_flag_cannot_downgrade_after_scheduling():
    episode = Episode("e1")
    episode.add_proposition(Proposition("seed", "e1", PropositionKind.OBSERVATION, "seed"))
    episode.add_proposition(
        Proposition(
            "peer-h",
            "e1",
            PropositionKind.HYPOTHESIS,
            "secret peer answer",
            producer_execution_id="peer:exec:1",
        )
    )
    flag = FlipBool(true_calls=2)
    descriptor = NodeDescriptor(
        "echo_hypothesis",
        (PropositionKind.HYPOTHESIS,),
        independence_required=flag,
    )
    executor = PeerReader()
    episode, outcome = _run(descriptor, executor, episode)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert executor.calls == 0
    assert "copied-peer" not in {p.proposition_id for p in episode.snapshot().current_propositions}


def test_stateful_mandatory_verification_flag_cannot_turn_off_after_scheduling():
    flag = FlipBool(true_calls=2)
    descriptor = NodeDescriptor(
        "verifier",
        (PropositionKind.HYPOTHESIS,),
        mandatory_verification=flag,
        verification_target_ids=("target",),
    )
    executor = SpyEmitter()
    episode, outcome = _run(descriptor, executor)
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert executor.calls == 0
    assert "h-spy" not in {p.proposition_id for p in episode.snapshot().current_propositions}


def test_node_descriptor_subclass_is_rejected_before_executor_runs():
    descriptor = DescriptorSubclass("echo_hypothesis", (PropositionKind.HYPOTHESIS,))
    _assert_preflight_rejects(descriptor, SpyEmitter())


def test_custom_node_id_is_rejected_before_executor_runs():
    descriptor = NodeDescriptor(
        AlwaysEqualStr("forged-node", "echo_hypothesis"),
        (PropositionKind.HYPOTHESIS,),
    )
    _assert_preflight_rejects(descriptor, SpyEmitter())


def test_permitted_output_kinds_must_be_exact_tuple_before_execution():
    descriptor = NodeDescriptor("echo_hypothesis", [PropositionKind.HYPOTHESIS])
    _assert_preflight_rejects(descriptor, SpyEmitter())


def test_accepted_input_kinds_must_be_exact_tuple_before_execution():
    episode = Episode("e1")
    episode.add_proposition(Proposition("seed", "e1", PropositionKind.OBSERVATION, "seed"))
    descriptor = NodeDescriptor(
        "echo_hypothesis",
        (PropositionKind.HYPOTHESIS,),
        accepted_input_kinds=[PropositionKind.OBSERVATION],
    )
    _assert_preflight_rejects(descriptor, SpyEmitter(), episode)


def test_required_authority_must_be_exact_tuple_before_execution():
    descriptor = NodeDescriptor(
        "echo_hypothesis",
        (PropositionKind.HYPOTHESIS,),
        required_authority=[],
    )
    _assert_preflight_rejects(descriptor, SpyEmitter())


def test_verification_target_ids_must_be_exact_tuple_before_execution():
    descriptor = NodeDescriptor(
        "echo_hypothesis",
        (PropositionKind.HYPOTHESIS,),
        verification_target_ids=["target"],
    )
    _assert_preflight_rejects(descriptor, SpyEmitter())
