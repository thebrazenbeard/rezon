from __future__ import annotations

from .episode import Episode, EpisodeInvariantError
from .nodes import ExecutionResult, NodeDescriptor


class AdmissionError(ValueError):
    pass


def admit_execution_result(episode: Episode, descriptor: NodeDescriptor, result: ExecutionResult) -> None:
    if result.node_id != descriptor.node_id:
        raise AdmissionError("execution result node does not match descriptor")
    permitted = set(descriptor.permitted_output_kinds)
    for proposition in result.emitted_propositions:
        if proposition.kind not in permitted:
            raise AdmissionError(
                f"node {descriptor.node_id} may not emit {proposition.kind.value}"
            )
        if proposition.producer_execution_id not in (None, result.execution_id):
            raise AdmissionError("proposition producer does not match execution")
        if proposition.episode_id != episode.episode_id:
            raise AdmissionError("proposition belongs to a different episode")
    for relation in result.emitted_relations:
        if relation.producer_execution_id not in (None, result.execution_id):
            raise AdmissionError("relation producer does not match execution")
        if relation.episode_id != episode.episode_id:
            raise AdmissionError("relation belongs to a different episode")

    try:
        for proposition in result.emitted_propositions:
            episode.add_proposition(proposition)
        for relation in result.emitted_relations:
            episode.add_relation(relation)
    except EpisodeInvariantError as exc:
        raise AdmissionError(str(exc)) from exc
