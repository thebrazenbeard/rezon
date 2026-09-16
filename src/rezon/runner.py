from __future__ import annotations

from dataclasses import dataclass, replace
from time import perf_counter

from .admission import AdmissionError, admit_execution_result
from .envelopes import TaskEnvelope
from .episode import Episode
from .epistemics import PropositionKind
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
        receipt_source_versions: list[str] = []
        used = 0
        by_id = {node.descriptor.node_id: node for node in self.nodes}

        def add_failure(failure: FailureState) -> None:
            if failure not in failures:
                failures.append(failure)

        def add_preflight_trace(
            execution_id: str,
            runner_node: RunnerNode,
            audit_view,
            failure: FailureState,
        ) -> None:
            records.append(TraceRecord(
                execution_id=execution_id,
                node_id=runner_node.descriptor.node_id,
                episode_version=audit_view.episode_version,
                visible_proposition_ids=tuple(p.proposition_id for p in audit_view.propositions),
                blinded_proposition_ids=audit_view.blinded_proposition_ids,
                visible_relation_ids=tuple(r.relation_id for r in audit_view.relations),
                blinded_relation_ids=audit_view.blinded_relation_ids,
                emitted_proposition_ids=(),
                independence_demonstrated=False,
                task_envelope_digest=task_digest,
                duration_seconds=0.0,
                failures=(failure,),
            ))

        while True:
            decision = self.scheduler.next(
                episode.snapshot(),
                tuple(node.descriptor for node in self.nodes),
                tuple(completed),
                Budget(effective_budget, used),
            )
            if decision.action is ScheduleAction.TERMINATE:
                if decision.failure is not None:
                    add_failure(decision.failure)
                break

            runner_node = by_id[decision.node_id]
            required_authority = set(runner_node.descriptor.required_authority)
            available_authority = set(task_envelope.available_authority if task_envelope else ())
            if required_authority and not required_authority.issubset(available_authority):
                add_failure(FailureState.CONTRACT_VIOLATION)
                unresolved.append(f"authority:{runner_node.descriptor.node_id}")
                break

            if runner_node.executor is None:
                add_failure(FailureState.UNAVAILABLE)
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

            visible_refs = {
                *(p.proposition_id for p in audit_view.propositions),
                *(r.relation_id for r in audit_view.relations),
            }
            if decision.target_id is not None and decision.target_id not in visible_refs:
                add_failure(FailureState.CONTRACT_VIOLATION)
                unresolved.append(f"scheduled_target:{decision.target_id}")
                add_preflight_trace(
                    execution_id,
                    runner_node,
                    audit_view,
                    FailureState.CONTRACT_VIOLATION,
                )
                completed.append(runner_node.descriptor.node_id)
                used += 1
                break

            accepted_input_kinds = set(runner_node.descriptor.accepted_input_kinds)
            if accepted_input_kinds and any(
                proposition.kind not in accepted_input_kinds
                for proposition in audit_view.propositions
            ):
                add_failure(FailureState.CONTRACT_VIOLATION)
                unresolved.append(f"input_contract:{runner_node.descriptor.node_id}")
                add_preflight_trace(
                    execution_id,
                    runner_node,
                    audit_view,
                    FailureState.CONTRACT_VIOLATION,
                )
                completed.append(runner_node.descriptor.node_id)
                used += 1
                break

            independence_ok = False
            if runner_node.descriptor.independence_required:
                independence = runner_node.independence
                pairwise_ok = all(
                    independence.demonstrably_independent_from(previous)
                    for previous in prior_independent
                )
                candidate_blind = not any(
                    proposition.kind is PropositionKind.HYPOTHESIS
                    for proposition in audit_view.propositions
                )
                independence_ok = bool(
                    independence.is_demonstrably_independent
                    and pairwise_ok
                    and candidate_blind
                )
                if not independence_ok:
                    add_failure(FailureState.CONTRACT_VIOLATION)
                    unresolved.append(f"independence:{runner_node.descriptor.node_id}")
                    break

            executor = runner_node.executor
            if decision.target_id is not None and hasattr(executor, "target_hypothesis_id"):
                executor = type(executor)(decision.target_id)

            started = perf_counter()
            try:
                result = executor.execute(executor_view, episode.episode_id)
            except Exception:
                duration = perf_counter() - started
                add_failure(FailureState.ATTEMPTED_UNKNOWN)
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
                    independence_demonstrated=independence_ok,
                    task_envelope_digest=task_digest,
                    duration_seconds=duration,
                    failures=(FailureState.ATTEMPTED_UNKNOWN,),
                ))
                completed.append(runner_node.descriptor.node_id)
                used += 1
                if runner_node.descriptor.mandatory_verification:
                    break
                continue
            duration = perf_counter() - started

            result_source_versions = list(result.source_versions)
            for source_ref in result.source_refs:
                if "@" in source_ref and source_ref not in result_source_versions:
                    result_source_versions.append(source_ref)
            for source_version in result_source_versions:
                if source_version not in receipt_source_versions:
                    receipt_source_versions.append(source_version)

            execution_failures = list(result.failures)
            admitted_ids: tuple[str, ...] = ()
            admission_ok = False
            try:
                admit_execution_result(
                    episode, runner_node.descriptor, result, expected_execution_id=execution_id
                )
                admitted_ids = tuple(p.proposition_id for p in result.emitted_propositions)
                admission_ok = True
            except AdmissionError:
                add_failure(FailureState.CONTRACT_VIOLATION)
                if FailureState.CONTRACT_VIOLATION not in execution_failures:
                    execution_failures.append(FailureState.CONTRACT_VIOLATION)
                unresolved.append(f"admission:{execution_id}")

            for failure in result.failures:
                add_failure(failure)

            if runner_node.descriptor.mandatory_verification and result.failures:
                unresolved.append(f"verification:{execution_id}")

            if (
                admission_ok
                and runner_node.descriptor.mandatory_verification
                and not result.failures
                and not any(
                    proposition.kind is PropositionKind.TEST_RESULT
                    and proposition.proposition_id in admitted_ids
                    for proposition in result.emitted_propositions
                )
            ):
                add_failure(FailureState.INSUFFICIENT_EVIDENCE)
                if FailureState.INSUFFICIENT_EVIDENCE not in execution_failures:
                    execution_failures.append(FailureState.INSUFFICIENT_EVIDENCE)
                unresolved.append(f"verification:{execution_id}")

            records.append(TraceRecord(
                execution_id=execution_id,
                node_id=runner_node.descriptor.node_id,
                episode_version=audit_view.episode_version,
                visible_proposition_ids=tuple(p.proposition_id for p in audit_view.propositions),
                blinded_proposition_ids=audit_view.blinded_proposition_ids,
                visible_relation_ids=tuple(r.relation_id for r in audit_view.relations),
                blinded_relation_ids=audit_view.blinded_relation_ids,
                emitted_proposition_ids=admitted_ids,
                independence_demonstrated=independence_ok,
                task_envelope_digest=task_digest,
                source_refs=result.source_refs,
                source_versions=tuple(result_source_versions),
                duration_seconds=duration,
                failures=tuple(execution_failures),
            ))
            if runner_node.descriptor.independence_required and admission_ok:
                prior_independent.append(runner_node.independence)
            completed.append(runner_node.descriptor.node_id)
            used += 1

        receipt = ResultReceipt(
            task_id=task_id,
            episode_version=episode.snapshot().version_ref,
            unresolved=tuple(unresolved),
            failures=tuple(failures),
            effect_state=EffectState.PLAN,
            source_versions=tuple(receipt_source_versions),
            execution_ids=tuple(record.execution_id for record in records),
            task_envelope_digest=task_digest,
        )
        return RunOutcome(receipt, ExecutionTrace(tuple(records)))
