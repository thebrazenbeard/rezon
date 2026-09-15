from __future__ import annotations

from dataclasses import dataclass, replace

from .admission import AdmissionError, admit_execution_result
from .envelopes import TaskEnvelope
from .episode import Episode
from .nodes import NodeDescriptor
from .receipts import EffectState, FailureState, IndependenceMetadata, ResultReceipt
from .scheduler import Budget, DeterministicScheduler, ScheduleAction
from .trace import ExecutionTrace, TraceRecord
from .visibility import VisibilityPolicy, build_execution_view


@dataclass(frozen=True)
class RunnerNode:
    descriptor: NodeDescriptor
    executor: object | None
    visibility: VisibilityPolicy
    independence: IndependenceMetadata = IndependenceMetadata()


@dataclass(frozen=True)
class RunOutcome:
    receipt: ResultReceipt
    trace: ExecutionTrace


class EpisodeRunner:
    def __init__(self, nodes: tuple[RunnerNode, ...], budget_limit: int = 8):
        self.nodes = nodes
        self.budget_limit = budget_limit
        self.scheduler = DeterministicScheduler()

    def run(
        self,
        episode: Episode,
        task_id: str,
        *,
        task_envelope: TaskEnvelope | None = None,
    ) -> RunOutcome:
        task_digest = task_envelope.digest if task_envelope is not None else None
        if task_envelope is not None and task_envelope.task_id != task_id:
            receipt = ResultReceipt(
                task_id=task_id,
                episode_version=episode.snapshot().version_ref,
                unresolved=("task_envelope:mismatched_task_id",),
                failures=(FailureState.CONTRACT_VIOLATION,),
                effect_state=EffectState.PLAN,
                task_envelope_digest=task_digest,
            )
            return RunOutcome(receipt, ExecutionTrace())

        effective_budget = self.budget_limit
        if task_envelope is not None and task_envelope.resource_budget is not None:
            effective_budget = min(effective_budget, task_envelope.resource_budget)

        completed: list[str] = []
        failures: list[FailureState] = []
        unresolved: list[str] = []
        records: list[TraceRecord] = []
        prior_independent: list[IndependenceMetadata] = []
        used = 0
        by_id = {node.descriptor.node_id: node for node in self.nodes}

        while True:
            decision = self.scheduler.next(
                episode.snapshot(),
                tuple(node.descriptor for node in self.nodes),
                tuple(completed),
                Budget(effective_budget, used),
            )
            if decision.action is ScheduleAction.TERMINATE:
                if decision.failure is not None and decision.failure not in failures:
                    failures.append(decision.failure)
                break

            runner_node = by_id[decision.node_id]
            required_authority = set(runner_node.descriptor.required_authority)
            available_authority = set(task_envelope.available_authority if task_envelope else ())
            if required_authority and not required_authority.issubset(available_authority):
                if FailureState.CONTRACT_VIOLATION not in failures:
                    failures.append(FailureState.CONTRACT_VIOLATION)
                unresolved.append(f"authority:{runner_node.descriptor.node_id}")
                break

            if runner_node.descriptor.independence_required:
                independence = runner_node.independence
                pairwise_ok = all(
                    independence.demonstrably_independent_from(previous)
                    for previous in prior_independent
                )
                if not independence.is_demonstrably_independent or not pairwise_ok:
                    if FailureState.CONTRACT_VIOLATION not in failures:
                        failures.append(FailureState.CONTRACT_VIOLATION)
                    unresolved.append(f"independence:{runner_node.descriptor.node_id}")
                    break

            if runner_node.executor is None:
                if FailureState.UNAVAILABLE not in failures:
                    failures.append(FailureState.UNAVAILABLE)
                unresolved.append(
                    f"mandatory:{runner_node.descriptor.node_id}"
                    if runner_node.descriptor.mandatory_verification
                    else f"node:{runner_node.descriptor.node_id}"
                )
                completed.append(runner_node.descriptor.node_id)
                if runner_node.descriptor.mandatory_verification:
                    break
                continue

            execution_id = f"{task_id}:exec:{len(records) + 1}:{runner_node.descriptor.node_id}"
            audit_view = build_execution_view(
                execution_id,
                episode.snapshot(),
                runner_node.visibility,
                runner_node.independence,
                task_envelope,
            )
            executor_view = replace(
                audit_view,
                blinded_proposition_ids=(),
                blinded_relation_ids=(),
            )
            executor = runner_node.executor
            if decision.target_id is not None and hasattr(executor, "target_hypothesis_id"):
                executor = type(executor)(decision.target_id)

            try:
                result = executor.execute(executor_view, episode.episode_id)
            except Exception:
                if FailureState.ATTEMPTED_UNKNOWN not in failures:
                    failures.append(FailureState.ATTEMPTED_UNKNOWN)
                unresolved.append(f"execution:{execution_id}")
                records.append(TraceRecord(
                    execution_id=execution_id,
                    node_id=runner_node.descriptor.node_id,
                    episode_version=audit_view.episode_version,
                    visible_proposition_ids=tuple(p.proposition_id for p in audit_view.propositions),
                    blinded_proposition_ids=audit_view.blinded_proposition_ids,
                    visible_relation_ids=tuple(r.relation_id for r in audit_view.relations),
                    blinded_relation_ids=audit_view.blinded_relation_ids,
                    emitted_proposition_ids=(),
                    independence_demonstrated=audit_view.independence.is_demonstrably_independent,
                    task_envelope_digest=task_digest,
                    failures=(FailureState.ATTEMPTED_UNKNOWN,),
                ))
                completed.append(runner_node.descriptor.node_id)
                used += 1
                if runner_node.descriptor.mandatory_verification:
                    break
                continue

            execution_failures = list(result.failures)
            admitted_ids: tuple[str, ...] = ()
            try:
                admit_execution_result(
                    episode, runner_node.descriptor, result, expected_execution_id=execution_id
                )
                admitted_ids = tuple(p.proposition_id for p in result.emitted_propositions)
            except AdmissionError:
                if FailureState.CONTRACT_VIOLATION not in failures:
                    failures.append(FailureState.CONTRACT_VIOLATION)
                if FailureState.CONTRACT_VIOLATION not in execution_failures:
                    execution_failures.append(FailureState.CONTRACT_VIOLATION)
                unresolved.append(f"admission:{execution_id}")
            for failure in result.failures:
                if failure not in failures:
                    failures.append(failure)
            records.append(TraceRecord(
                execution_id=execution_id,
                node_id=runner_node.descriptor.node_id,
                episode_version=audit_view.episode_version,
                visible_proposition_ids=tuple(p.proposition_id for p in audit_view.propositions),
                blinded_proposition_ids=audit_view.blinded_proposition_ids,
                visible_relation_ids=tuple(r.relation_id for r in audit_view.relations),
                blinded_relation_ids=audit_view.blinded_relation_ids,
                emitted_proposition_ids=admitted_ids,
                independence_demonstrated=audit_view.independence.is_demonstrably_independent,
                task_envelope_digest=task_digest,
                failures=tuple(execution_failures),
            ))
            if runner_node.descriptor.independence_required:
                prior_independent.append(runner_node.independence)
            completed.append(runner_node.descriptor.node_id)
            used += 1

        receipt = ResultReceipt(
            task_id=task_id,
            episode_version=episode.snapshot().version_ref,
            unresolved=tuple(unresolved),
            failures=tuple(failures),
            effect_state=EffectState.PLAN,
            execution_ids=tuple(record.execution_id for record in records),
            task_envelope_digest=task_digest,
        )
        return RunOutcome(receipt, ExecutionTrace(tuple(records)))
