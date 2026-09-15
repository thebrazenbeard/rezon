from __future__ import annotations

from dataclasses import dataclass

from .admission import AdmissionError, admit_execution_result
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

    def run(self, episode: Episode, task_id: str) -> RunOutcome:
        completed: list[str] = []
        failures: list[FailureState] = []
        unresolved: list[str] = []
        records: list[TraceRecord] = []
        used = 0
        by_id = {node.descriptor.node_id: node for node in self.nodes}

        while True:
            decision = self.scheduler.next(
                episode.snapshot(),
                tuple(node.descriptor for node in self.nodes),
                tuple(completed),
                Budget(self.budget_limit, used),
            )
            if decision.action is ScheduleAction.TERMINATE:
                if decision.failure is not None and decision.failure not in failures:
                    failures.append(decision.failure)
                break

            runner_node = by_id[decision.node_id]
            if runner_node.executor is None:
                if FailureState.UNAVAILABLE not in failures:
                    failures.append(FailureState.UNAVAILABLE)
                unresolved.append(f"mandatory:{runner_node.descriptor.node_id}" if runner_node.descriptor.mandatory_verification else f"node:{runner_node.descriptor.node_id}")
                completed.append(runner_node.descriptor.node_id)
                if runner_node.descriptor.mandatory_verification:
                    break
                continue

            execution_id = f"{task_id}:exec:{len(records) + 1}:{runner_node.descriptor.node_id}"
            view = build_execution_view(
                execution_id, episode.snapshot(), runner_node.visibility, runner_node.independence
            )
            executor = runner_node.executor
            # Falsifiers need an explicit scheduler target; instantiate through a small adapter contract when supported.
            if decision.target_id is not None and hasattr(executor, "target_hypothesis_id"):
                executor = type(executor)(decision.target_id)
            result = executor.execute(view, episode.episode_id)
            try:
                admit_execution_result(episode, runner_node.descriptor, result)
            except AdmissionError:
                failures.append(FailureState.CONTRACT_VIOLATION)
                unresolved.append(f"admission:{execution_id}")
            for failure in result.failures:
                if failure not in failures:
                    failures.append(failure)
            records.append(TraceRecord(
                execution_id=execution_id,
                node_id=runner_node.descriptor.node_id,
                episode_version=view.episode_version,
                visible_proposition_ids=tuple(p.proposition_id for p in view.propositions),
                blinded_proposition_ids=view.blinded_proposition_ids,
                visible_relation_ids=tuple(r.relation_id for r in view.relations),
                blinded_relation_ids=view.blinded_relation_ids,
                emitted_proposition_ids=tuple(p.proposition_id for p in result.emitted_propositions),
                independence_demonstrated=view.independence.is_demonstrably_independent,
                failures=result.failures,
            ))
            completed.append(runner_node.descriptor.node_id)
            used += 1

        receipt = ResultReceipt(
            task_id=task_id,
            episode_version=episode.snapshot().version_ref,
            unresolved=tuple(unresolved),
            failures=tuple(failures),
            effect_state=EffectState.PLAN,
            execution_ids=tuple(record.execution_id for record in records),
        )
        return RunOutcome(receipt, ExecutionTrace(tuple(records)))
