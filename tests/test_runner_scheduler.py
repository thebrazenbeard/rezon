from rezon.envelopes import TaskEnvelope
from rezon.episode import Episode
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.executors import EchoHypothesisExecutor
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import EffectState, FailureState, IndependenceMetadata
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.scheduler import Budget, DeterministicScheduler, ScheduleAction
from rezon.visibility import VisibilityPolicy


def _p(pid, kind, content=None, confidence=None):
    return Proposition(pid, "e1", kind, content or pid, confidence=confidence)


def test_scheduler_mandatory_verification_is_first():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    scheduler = DeterministicScheduler()
    nodes = (
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        NodeDescriptor("verifier", (PropositionKind.TEST_RESULT,), mandatory_verification=True),
    )
    decision = scheduler.next(ep.snapshot(), nodes, completed_node_ids=(), budget=Budget(5, 0))
    assert decision.action is ScheduleAction.EXECUTE
    assert decision.node_id == "verifier"
    assert decision.reason == "mandatory_verification"


def test_scheduler_budget_exhaustion_is_failure_only_when_work_remains():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    pending = (NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),)
    exhausted = DeterministicScheduler().next(ep.snapshot(), pending, (), Budget(1, 1))
    assert exhausted.action is ScheduleAction.TERMINATE
    assert exhausted.failure is FailureState.RESOURCE_LIMIT

    complete = DeterministicScheduler().next(ep.snapshot(), (), (), Budget(1, 1))
    assert complete.action is ScheduleAction.TERMINATE
    assert complete.reason == "no_applicable_rule"
    assert complete.failure is None


def test_scheduler_routes_explicit_contradiction_before_generation():
    ep = Episode("e1")
    ep.add_proposition(_p("a", PropositionKind.CLAIM))
    ep.add_proposition(_p("b", PropositionKind.CLAIM))
    ep.add_relation(Hyperrelation("r1", "e1", "contradicts", (Participant("a", "left"), Participant("b", "right"))))
    nodes = (
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        NodeDescriptor("contradiction_scanner", (PropositionKind.TEST_RESULT,)),
    )
    decision = DeterministicScheduler().next(ep.snapshot(), nodes, (), Budget(5, 0))
    assert decision.node_id == "contradiction_scanner"
    assert decision.reason == "explicit_contradiction"


def test_scheduler_generates_when_no_hypothesis_then_falsifies_supported_target():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    nodes = (
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        NodeDescriptor("falsifier", (PropositionKind.CLAIM,)),
    )
    first = DeterministicScheduler().next(ep.snapshot(), nodes, (), Budget(5, 0))
    assert first.node_id == "echo_hypothesis"

    ep.add_proposition(_p("h1", PropositionKind.HYPOTHESIS, confidence=0.95))
    second = DeterministicScheduler().next(ep.snapshot(), nodes, ("echo_hypothesis",), Budget(5, 1))
    assert second.node_id == "falsifier"
    assert second.target_id == "h1"


def test_runner_records_blinding_and_does_not_upgrade_effect_state():
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION, "machine stopped"))
    ep.add_proposition(_p("h-existing", PropositionKind.HYPOTHESIS, "old guess"))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,), independence_required=True),
        executor=EchoHypothesisExecutor(),
        visibility=VisibilityPolicy(blind_kinds=(PropositionKind.HYPOTHESIS,)),
        independence=IndependenceMetadata(
            executor_id="echo_hypothesis",
            model_id="test-model",
            provider_id="test-provider",
            prompt_lineage="fresh",
            context_lineage="blinded",
            saw_other_answer=False,
            independence_basis_refs=("policy:blind-hypotheses",),
        ),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t1")
    assert outcome.receipt.effect_state is EffectState.PLAN
    assert outcome.receipt.failures == ()
    assert len(outcome.trace.records) == 1
    record = outcome.trace.records[0]
    assert record.node_id == "echo_hypothesis"
    assert record.visible_proposition_ids == ("o1",)
    assert record.blinded_proposition_ids == ("h-existing",)
    assert record.independence_demonstrated is True


def test_missing_mandatory_executor_is_visible_failure_not_clean_success():
    ep = Episode("e1")
    node = RunnerNode(
        descriptor=NodeDescriptor("verifier", (PropositionKind.TEST_RESULT,), mandatory_verification=True),
        executor=None,
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=2).run(ep, task_id="t1")
    assert FailureState.UNAVAILABLE in outcome.receipt.failures
    assert outcome.receipt.effect_state is EffectState.PLAN
    assert "mandatory:verifier" in outcome.receipt.unresolved


def test_task_envelope_is_bound_to_executor_trace_receipt_and_authority():
    class CapturingExecutor:
        node_id = "echo_hypothesis"

        def __init__(self):
            self.seen = None

        def execute(self, view, episode_id):
            self.seen = view
            return ExecutionResult(view.execution_id, self.node_id)

    executor = CapturingExecutor()
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    envelope = TaskEnvelope(
        task_id="t-bound",
        literal_request="Evaluate the literal proposition A without substituting it",
        available_authority=("read:policy",),
        resource_budget=2,
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            required_authority=("read:policy",),
        ),
        executor=executor,
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=8).run(
        ep, task_id="t-bound", task_envelope=envelope
    )
    assert outcome.receipt.failures == ()
    assert executor.seen.task_envelope == envelope
    assert outcome.receipt.task_envelope_digest == envelope.digest
    assert outcome.trace.records[0].task_envelope_digest == envelope.digest


def test_required_authority_fails_closed_before_worker_execution():
    class ShouldNotRun:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            raise AssertionError("worker should not run")

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    envelope = TaskEnvelope("t-auth", "Read protected state", available_authority=("read:public",))
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            required_authority=("read:protected",),
        ),
        executor=ShouldNotRun(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=2).run(
        ep, task_id="t-auth", task_envelope=envelope
    )
    assert outcome.receipt.failures == (FailureState.CONTRACT_VIOLATION,)
    assert outcome.receipt.unresolved == ("authority:echo_hypothesis",)
    assert outcome.trace.records == ()


def test_executor_cannot_see_blinded_ids_but_audit_trace_can():
    class CapturingExecutor:
        node_id = "echo_hypothesis"

        def __init__(self):
            self.blinded = None

        def execute(self, view, episode_id):
            self.blinded = (view.blinded_proposition_ids, view.blinded_relation_ids)
            return ExecutionResult(view.execution_id, self.node_id)

    executor = CapturingExecutor()
    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    ep.add_proposition(_p("h-secret", PropositionKind.HYPOTHESIS))
    independence = IndependenceMetadata(
        executor_id="independent-generator",
        model_id="test-model",
        provider_id="test-provider",
        prompt_lineage="fresh-prompt",
        context_lineage="fresh-context",
        saw_other_answer=False,
        independence_basis_refs=("policy:blind-hypotheses",),
    )
    node = RunnerNode(
        descriptor=NodeDescriptor(
            "echo_hypothesis", (PropositionKind.HYPOTHESIS,), independence_required=True
        ),
        executor=executor,
        visibility=VisibilityPolicy(blind_kinds=(PropositionKind.HYPOTHESIS,)),
        independence=independence,
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-blind")
    assert executor.blinded == ((), ())
    assert outcome.trace.records[0].blinded_proposition_ids == ("h-secret",)


def test_admission_failure_is_consistent_between_receipt_and_trace():
    class EvidenceLaunderingExecutor:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            proposition = Proposition(
                "ev-bad",
                episode_id,
                PropositionKind.EVIDENCE,
                "unsupported evidence",
                producer_execution_id=view.execution_id,
            )
            return ExecutionResult(view.execution_id, self.node_id, (proposition,))

    ep = Episode("e1")
    ep.add_proposition(_p("o1", PropositionKind.OBSERVATION))
    node = RunnerNode(
        descriptor=NodeDescriptor("echo_hypothesis", (PropositionKind.EVIDENCE,)),
        executor=EvidenceLaunderingExecutor(),
        visibility=VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(ep, task_id="t-trace")
    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert outcome.trace.records[0].failures == (FailureState.CONTRACT_VIOLATION,)
    assert outcome.trace.records[0].emitted_proposition_ids == ()
