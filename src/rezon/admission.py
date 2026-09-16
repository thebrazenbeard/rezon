from __future__ import annotations

from .episode import Episode, EpisodeInvariantError
from .epistemics import PropositionKind
from .nodes import ExecutionResult, NodeDescriptor


class AdmissionError(ValueError):
    pass


def _prevalidate_episode_mutation(episode: Episode, result: ExecutionResult) -> None:
    snapshot = episode.snapshot()
    existing_props = {p.proposition_id: p for p in snapshot.all_propositions}
    active_props = {p.proposition_id for p in snapshot.current_propositions}
    existing_relations = {r.relation_id: r for r in snapshot.all_relations}
    active_relations = {r.relation_id for r in snapshot.current_relations}

    staged_props = {}
    for proposition in result.emitted_propositions:
        previous = staged_props.get(proposition.proposition_id, existing_props.get(proposition.proposition_id))
        if previous is not None and previous != proposition:
            raise AdmissionError("duplicate proposition ID has conflicting content")
        if proposition.proposition_id in existing_props and proposition.proposition_id not in active_props:
            raise AdmissionError("retracted proposition ID cannot be silently reactivated")
        staged_props[proposition.proposition_id] = proposition

    known = set(active_props) | set(active_relations) | set(staged_props)
    staged_relations = {}
    for relation in result.emitted_relations:
        previous = staged_relations.get(relation.relation_id, existing_relations.get(relation.relation_id))
        if previous is not None and previous != relation:
            raise AdmissionError("duplicate relation ID has conflicting content")
        if relation.relation_id in existing_relations and relation.relation_id not in active_relations:
            raise AdmissionError("invalidated relation ID cannot be silently reactivated")
        missing = [participant.ref_id for participant in relation.participants if participant.ref_id not in known]
        if missing:
            raise AdmissionError(f"relation references inactive or unknown current objects: {missing}")
        staged_relations[relation.relation_id] = relation
        known.add(relation.relation_id)


def admit_execution_result(
    episode: Episode,
    descriptor: NodeDescriptor,
    result: ExecutionResult,
    *,
    expected_execution_id: str | None = None,
) -> None:
    if result.node_id != descriptor.node_id:
        raise AdmissionError("execution result node does not match descriptor")
    if expected_execution_id is not None and result.execution_id != expected_execution_id:
        raise AdmissionError("execution result identity does not match runner-issued execution")
    permitted = set(descriptor.permitted_output_kinds)
    for proposition in result.emitted_propositions:
        if proposition.kind not in permitted:
            raise AdmissionError(f"node {descriptor.node_id} may not emit {proposition.kind.value}")
        if proposition.kind is PropositionKind.EVIDENCE:
            raise AdmissionError("worker output cannot self-promote to evidence")
        required_execution_id = expected_execution_id or result.execution_id
        if proposition.producer_execution_id != required_execution_id:
            raise AdmissionError("proposition producer must match execution exactly")
        if proposition.episode_id != episode.episode_id:
            raise AdmissionError("proposition belongs to a different episode")
    for relation in result.emitted_relations:
        required_execution_id = expected_execution_id or result.execution_id
        if relation.producer_execution_id != required_execution_id:
            raise AdmissionError("relation producer must match execution exactly")
        if relation.episode_id != episode.episode_id:
            raise AdmissionError("relation belongs to a different episode")

    _prevalidate_episode_mutation(episode, result)
    try:
        for proposition in result.emitted_propositions:
            episode.add_proposition(proposition)
        for relation in result.emitted_relations:
            episode.add_relation(relation)
    except EpisodeInvariantError as exc:
        raise AdmissionError(str(exc)) from exc
