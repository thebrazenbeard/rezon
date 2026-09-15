from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .episode import EpisodeSnapshot
from .epistemics import PropositionKind
from .nodes import NodeDescriptor
from .receipts import FailureState


class ScheduleAction(str, Enum):
    EXECUTE = "execute"
    TERMINATE = "terminate"


@dataclass(frozen=True)
class Budget:
    limit: int
    used: int = 0

    def __post_init__(self) -> None:
        if self.limit < 0 or self.used < 0:
            raise ValueError("budget values cannot be negative")


@dataclass(frozen=True)
class ScheduleDecision:
    action: ScheduleAction
    node_id: str | None = None
    reason: str = ""
    target_id: str | None = None
    failure: FailureState | None = None


class DeterministicScheduler:
    def next(
        self,
        snapshot: EpisodeSnapshot,
        nodes: tuple[NodeDescriptor, ...],
        completed_node_ids: tuple[str, ...],
        budget: Budget,
    ) -> ScheduleDecision:
        if budget.used >= budget.limit:
            return ScheduleDecision(
                ScheduleAction.TERMINATE, reason="budget_exhausted", failure=FailureState.RESOURCE_LIMIT
            )
        completed = set(completed_node_ids)
        by_id = {node.node_id: node for node in nodes}

        for node in nodes:
            if node.mandatory_verification and node.node_id not in completed:
                return ScheduleDecision(ScheduleAction.EXECUTE, node.node_id, "mandatory_verification")

        if "contradiction_scanner" in by_id and "contradiction_scanner" not in completed:
            if any(r.relation_type.lower() == "contradicts" for r in snapshot.current_relations):
                return ScheduleDecision(ScheduleAction.EXECUTE, "contradiction_scanner", "explicit_contradiction")

        generator = by_id.get("echo_hypothesis")
        hypotheses = [p for p in snapshot.current_propositions if p.kind is PropositionKind.HYPOTHESIS]
        if generator and generator.node_id not in completed:
            if generator.independence_required or not hypotheses:
                reason = "independent_hypothesis_generation" if generator.independence_required else "missing_hypothesis"
                return ScheduleDecision(ScheduleAction.EXECUTE, generator.node_id, reason)

        falsifier = by_id.get("falsifier")
        if falsifier and falsifier.node_id not in completed:
            target = next((p for p in hypotheses if (p.confidence or 0.0) >= 0.8), None)
            if target is not None:
                return ScheduleDecision(
                    ScheduleAction.EXECUTE, falsifier.node_id, "falsify_high_confidence_hypothesis", target.proposition_id
                )

        return ScheduleDecision(ScheduleAction.TERMINATE, reason="no_applicable_rule")
