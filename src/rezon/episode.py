from __future__ import annotations

from dataclasses import dataclass

from .epistemics import Hyperrelation, Proposition


class EpisodeInvariantError(ValueError):
    pass


@dataclass(frozen=True)
class EpisodeEvent:
    event_id: str
    episode_id: str
    event_type: str
    target_id: str
    reason: str | None = None


@dataclass(frozen=True)
class EpisodeSnapshot:
    episode_id: str
    version: int
    current_propositions: tuple[Proposition, ...]
    all_propositions: tuple[Proposition, ...]
    current_relations: tuple[Hyperrelation, ...]
    all_relations: tuple[Hyperrelation, ...]
    events: tuple[EpisodeEvent, ...]

    @property
    def version_ref(self) -> str:
        return f"{self.episode_id}@{self.version}"


class Episode:
    def __init__(self, episode_id: str):
        if not episode_id:
            raise EpisodeInvariantError("episode_id is required")
        self.episode_id = episode_id
        self._propositions: dict[str, Proposition] = {}
        self._relations: dict[str, Hyperrelation] = {}
        self._active_propositions: set[str] = set()
        self._active_relations: set[str] = set()
        self._events: list[EpisodeEvent] = []

    def _event(self, event_type: str, target_id: str, reason: str | None = None) -> None:
        self._events.append(EpisodeEvent(
            event_id=f"{self.episode_id}:event:{len(self._events) + 1}",
            episode_id=self.episode_id,
            event_type=event_type,
            target_id=target_id,
            reason=reason,
        ))

    def add_proposition(self, proposition: Proposition) -> None:
        if proposition.episode_id != self.episode_id:
            raise EpisodeInvariantError("proposition belongs to a different episode")
        previous = self._propositions.get(proposition.proposition_id)
        if previous is not None:
            if previous != proposition:
                raise EpisodeInvariantError("duplicate proposition ID has conflicting content")
            if proposition.proposition_id not in self._active_propositions:
                raise EpisodeInvariantError("retracted proposition ID cannot be silently reactivated")
            return
        self._propositions[proposition.proposition_id] = proposition
        self._active_propositions.add(proposition.proposition_id)
        self._event("proposition_added", proposition.proposition_id)

    def retract_proposition(self, proposition_id: str, reason: str) -> None:
        if proposition_id not in self._propositions:
            raise EpisodeInvariantError("cannot retract unknown proposition")
        if proposition_id not in self._active_propositions:
            raise EpisodeInvariantError("proposition is already retracted")
        self._active_propositions.remove(proposition_id)
        self._event("proposition_retracted", proposition_id, reason)

        invalidated_refs = {proposition_id}
        while True:
            newly_invalidated: list[str] = []

            for current_id in tuple(self._active_propositions):
                proposition = self._propositions[current_id]
                if any(ref in invalidated_refs for ref in proposition.source_refs):
                    self._active_propositions.remove(current_id)
                    self._event(
                        "proposition_invalidated",
                        current_id,
                        f"source_dependency_retracted:{proposition_id}",
                    )
                    newly_invalidated.append(current_id)

            for relation_id in tuple(self._active_relations):
                relation = self._relations[relation_id]
                participant_dependency = any(
                    participant.ref_id in invalidated_refs
                    for participant in relation.participants
                )
                source_dependency = any(
                    ref in invalidated_refs for ref in relation.source_refs
                )
                if participant_dependency or source_dependency:
                    self._active_relations.remove(relation_id)
                    self._event(
                        "relation_invalidated",
                        relation_id,
                        f"dependency_retracted:{proposition_id}",
                    )
                    newly_invalidated.append(relation_id)

            if not newly_invalidated:
                break
            invalidated_refs.update(newly_invalidated)

    def add_relation(self, relation: Hyperrelation) -> None:
        if relation.episode_id != self.episode_id:
            raise EpisodeInvariantError("relation belongs to a different episode")
        active_refs = self._active_propositions | self._active_relations
        unavailable = [p.ref_id for p in relation.participants if p.ref_id not in active_refs]
        if unavailable:
            raise EpisodeInvariantError(
                f"relation references inactive or unknown objects: {unavailable}"
            )
        previous = self._relations.get(relation.relation_id)
        if previous is not None:
            if previous != relation:
                raise EpisodeInvariantError("duplicate relation ID has conflicting content")
            if relation.relation_id not in self._active_relations:
                raise EpisodeInvariantError("invalidated relation ID cannot be silently reactivated")
            return
        self._relations[relation.relation_id] = relation
        self._active_relations.add(relation.relation_id)
        self._event("relation_added", relation.relation_id)

    def snapshot(self) -> EpisodeSnapshot:
        return EpisodeSnapshot(
            episode_id=self.episode_id,
            version=len(self._events),
            current_propositions=tuple(
                p for k, p in self._propositions.items() if k in self._active_propositions
            ),
            all_propositions=tuple(self._propositions.values()),
            current_relations=tuple(
                r for k, r in self._relations.items() if k in self._active_relations
            ),
            all_relations=tuple(self._relations.values()),
            events=tuple(self._events),
        )
