from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class TaskEnvelope:
    task_id: str
    literal_request: str
    subject_refs: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    available_authority: tuple[str, ...] = ()
    privacy_scope: str | None = None
    resource_budget: int | None = None
    context_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id or not self.literal_request:
            raise ValueError("task_id and literal_request are required")
        if self.resource_budget is not None and self.resource_budget < 0:
            raise ValueError("resource_budget cannot be negative")

    @property
    def digest(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()
