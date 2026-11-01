"""Source-only coordination for two-model TRAININGDAY evidence.

Rezon can distribute *reasoning and review* work to enrolled workers. It does
not run an optimizer, pool VRAM, grant a GPU lease, or admit training data.
The ordered GPU evaluation declarations below must be executed by a separate,
host-authorized runtime; they are never launch requests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from .collective import CollectiveStore


_SHA = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[a-z][a-z0-9_-]{0,39}\Z")
_MODEL_FORMATS = frozenset({"GGUF_INFERENCE_ONLY", "HF_TRAINABLE"})
_CPU_ROLES = (
    "CORPUS_PROVENANCE", "DEDUP_REVIEW", "RIGHTS_CONSENT_REVIEW",
    "PROTECTED_EVAL_CUSTODY",
)
_CPU_STATUSES = frozenset({"SOURCE_CHECKED", "REJECTED", "UNKNOWN"})


class WorkContractError(ValueError):
    """An untrusted source-only training coordination declaration is invalid."""


def _id(value: object, label: str) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise WorkContractError(f"invalid {label}")
    return value


def _sha(value: object, label: str) -> str:
    if type(value) is not str or not _SHA.fullmatch(value):
        raise WorkContractError(f"invalid {label} SHA-256")
    return value


@dataclass(frozen=True)
class ModelArm:
    """Immutable identity of a candidate artifact, not model-weight custody."""

    model_id: str
    source_ref: str
    artifact_sha256: str
    artifact_format: str

    def __post_init__(self) -> None:
        _id(self.model_id, "model id")
        if (type(self.source_ref) is not str or not 1 <= len(self.source_ref) <= 160
                or any(ord(ch) < 33 or ord(ch) > 126 for ch in self.source_ref)):
            raise WorkContractError("invalid model source reference")
        _sha(self.artifact_sha256, "model artifact")
        if type(self.artifact_format) is not str or self.artifact_format not in _MODEL_FORMATS:
            raise WorkContractError("unsupported model artifact format")


@dataclass(frozen=True)
class CorpusPins:
    """Whole-artifact pins; do not use/publicize low-entropy per-answer hashes."""

    train_sha256: str
    dev_sha256: str
    protected_eval_roster_sha256: str
    provenance_manifest_sha256: str

    def __post_init__(self) -> None:
        vals = (self.train_sha256, self.dev_sha256,
                self.protected_eval_roster_sha256, self.provenance_manifest_sha256)
        for key, value in zip(("TRAIN", "DEV", "evaluation roster", "provenance"), vals):
            _sha(value, key)
        if len(set(vals)) != len(vals):
            raise WorkContractError("split and provenance artifact pins must be distinct")


@dataclass(frozen=True)
class WorkItem:
    task_id: str
    phase: str
    worker_id: str
    model_id: str | None
    depends_on: tuple[str, ...]
    gpu_slot: str | None
    review_role: str | None = None
    authorizes_effects: bool = field(default=False, init=False)


@dataclass(frozen=True)
class TrainingDayPlan:
    """A non-executable plan; no positive authority can be constructed here."""

    arms: tuple[ModelArm, ModelArm]
    corpus: CorpusPins
    tasks: tuple[WorkItem, ...]
    gpu_slot: str
    selection_requires_independent_heldout: bool = field(default=True, init=False)
    requires_trainable_base_after_gguf_bakeoff: bool = field(default=False, init=False)
    authorizes_gpu_training: bool = field(default=False, init=False)
    authorizes_data_admission: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "requires_trainable_base_after_gguf_bakeoff",
                           any(arm.artifact_format == "GGUF_INFERENCE_ONLY" for arm in self.arms))


@dataclass(frozen=True)
class WorkerClaim:
    """Deliberately no freeform text/labels or claim of authenticated worker."""

    task_id: str
    worker_id: str
    status: str
    artifact_sha256: str

    def __post_init__(self) -> None:
        _id(self.task_id, "task id")
        _id(self.worker_id, "worker id")
        if type(self.status) is not str or self.status not in _CPU_STATUSES:
            raise WorkContractError("invalid declared CPU work status")
        _sha(self.artifact_sha256, "CPU work evidence")


def plan_two_model_bakeoff(
    arms: tuple[ModelArm, ModelArm],
    corpus: CorpusPins,
    cpu_workers: tuple[str, ...],
    gpu_slot: str,
    *,
    gpu_parallelism: int = 1,
    zero_cost: bool = True,
) -> TrainingDayPlan:
    """Fan out CPU reviews; serialize baseline GPU tests; NEVER launch training.

    Scores, gold answers and true worker/host identities are intentionally not
    parameters. An independent evaluator must choose the winner externally,
    then a distinct host-owned authority must approve any optimizer execution.
    """
    if (type(arms) is not tuple or len(arms) != 2
            or any(type(arm) is not ModelArm for arm in arms)):
        raise WorkContractError("two distinct immutable model artifacts required")
    # Caller-owned frozen dataclasses may have been mutated via
    # object.__setattr__. Validate their *current* fields in the planner as
    # well as in the evidence-import gate.
    for arm in arms:
        arm.__post_init__()
    if (arms[0].model_id == arms[1].model_id
            or arms[0].artifact_sha256 == arms[1].artifact_sha256):
        raise WorkContractError("two distinct immutable model artifacts required")
    if type(corpus) is not CorpusPins:
        raise WorkContractError("typed corpus pins required")
    corpus.__post_init__()
    if (type(cpu_workers) is not tuple or not 2 <= len(cpu_workers) <= 8
            or any(type(worker) is not str or not _ID.fullmatch(worker) for worker in cpu_workers)
            or len(set(cpu_workers)) != len(cpu_workers)):
        raise WorkContractError("2-8 distinct CPU evidence workers required")
    _id(gpu_slot, "GPU slot")
    if type(gpu_parallelism) is not int or gpu_parallelism != 1:
        raise WorkContractError("one GPU slot can run at most one model at a time")
    if zero_cost is not True:
        raise WorkContractError("TRAININGDAY has a zero-cost constraint")

    cpu_tasks = tuple(
        WorkItem(f"cpu-review-{index + 1}", "CPU_REVIEW",
                 cpu_workers[index % len(cpu_workers)], None, (), None, role)
        for index, role in enumerate(_CPU_ROLES)
    )
    # Ordering is an explicit resource-conflict contract, not a GPU lock.
    gpu_first = WorkItem(f"baseline-eval-{arms[0].model_id}", "BASELINE_EVAL",
                         "host_evaluator", arms[0].model_id,
                         tuple(task.task_id for task in cpu_tasks), gpu_slot)
    gpu_second = WorkItem(f"baseline-eval-{arms[1].model_id}", "BASELINE_EVAL",
                          "host_evaluator", arms[1].model_id, (gpu_first.task_id,), gpu_slot)
    return TrainingDayPlan(arms, corpus, cpu_tasks + (gpu_first, gpu_second), gpu_slot)


def _same_builtin_literal(actual: object, expected: object) -> bool:
    """Compare schema literals only; never call custom equality or rendering."""
    if type(actual) is not type(expected):
        return False
    if type(expected) is tuple:
        return (len(actual) == len(expected)
                and all(type(item) is str and item == wanted
                        for item, wanted in zip(actual, expected)))
    if type(expected) in (str, bool, type(None)):
        return actual == expected
    return False


def _validate_canonical_plan(plan: TrainingDayPlan) -> TrainingDayPlan:
    """Recheck input shape at the persistence boundary, not only at planning.

    Callers can construct frozen dataclasses directly (or use ``replace``),
    so a TrainingDayPlan's type is NOT evidence it came from the planner.
    Never render mutable/untrusted WorkItem text into CollectiveStore.
    """
    if (type(plan.arms) is not tuple or len(plan.arms) != 2
            or any(type(arm) is not ModelArm for arm in plan.arms)
            or type(plan.corpus) is not CorpusPins
            or type(plan.tasks) is not tuple or len(plan.tasks) != 6
            or any(type(task) is not WorkItem for task in plan.tasks)):
        raise WorkContractError("noncanonical TRAININGDAY plan shape")
    for arm in plan.arms:
        arm.__post_init__()
    plan.corpus.__post_init__()
    cpu_tasks = plan.tasks[:len(_CPU_ROLES)]
    if any(type(task.worker_id) is not str for task in cpu_tasks):
        raise WorkContractError("noncanonical TRAININGDAY worker binding")
    workers = tuple(dict.fromkeys(task.worker_id for task in cpu_tasks))
    expected = plan_two_model_bakeoff(plan.arms, plan.corpus, workers, plan.gpu_slot)
    # Dataclass equality is *not* schema validation: a field can be an object
    # with __eq__ always True and __str__ exposing private data. Validate every
    # field's exact built-in type before comparing values, including nested
    # dependency tuple elements and the false authority flags.
    for actual, canonical in zip(plan.tasks, expected.tasks):
        for field_name in WorkItem.__dataclass_fields__:
            if not _same_builtin_literal(getattr(actual, field_name),
                                         getattr(canonical, field_name)):
                raise WorkContractError("noncanonical TRAININGDAY task or role binding")
    for field_name in ("gpu_slot", "selection_requires_independent_heldout",
                       "requires_trainable_base_after_gguf_bakeoff",
                       "authorizes_gpu_training", "authorizes_data_admission"):
        if not _same_builtin_literal(getattr(plan, field_name),
                                     getattr(expected, field_name)):
            raise WorkContractError("noncanonical TRAININGDAY authority binding")
    # From this point forward render only trusted planner literals, never
    # caller-owned WorkItems, even if a future field is added to the dataclass.
    return expected


def record_cpu_claims(
    store: CollectiveStore,
    plan: TrainingDayPlan,
    claims: tuple[WorkerClaim, ...],
) -> str:
    """Store self-declared CPU review evidence in existing Rezon Collective.

    Nothing here authenticates worker identity or source content. Validation
    finishes before opening a new episode, and no private corpus digests,
    prompts, labels or answers are embedded in the episode prompt.
    """
    if type(store) is not CollectiveStore or type(plan) is not TrainingDayPlan:
        raise WorkContractError("typed Rezon collective store and plan required")
    canonical_plan = _validate_canonical_plan(plan)
    if type(claims) is not tuple or not 2 <= len(claims) <= 8:
        raise WorkContractError("two or more independent CPU work claims required")
    allowed = {task.task_id: task for task in canonical_plan.tasks
               if task.phase == "CPU_REVIEW"}
    seen_tasks: set[str] = set()
    by_worker: dict[str, list[WorkerClaim]] = {}
    for claim in claims:
        if type(claim) is not WorkerClaim:
            raise WorkContractError("typed CPU claim required")
        # Frozen dataclasses are not a trust boundary: ``object.__setattr__``
        # could mutate a caller-owned claim after this loop. Rebuild a private
        # canonical snapshot, validating exact primitive field types, and use
        # ONLY that snapshot during the later persistence side effects.
        safe_claim = WorkerClaim(claim.task_id, claim.worker_id,
                                 claim.status, claim.artifact_sha256)
        task = allowed.get(safe_claim.task_id)
        if (task is None or task.worker_id != safe_claim.worker_id
                or safe_claim.task_id in seen_tasks):
            raise WorkContractError("duplicate or unbound CPU work claim")
        seen_tasks.add(safe_claim.task_id)
        by_worker.setdefault(safe_claim.worker_id, []).append(safe_claim)
    if len(by_worker) < 2:
        raise WorkContractError("independently attributed CPU claims require two workers")
    for worker_claims in by_worker.values():
        refs = tuple(item.artifact_sha256 for item in worker_claims)
        if len(refs) != len(set(refs)):
            raise WorkContractError("duplicate CPU source reference for one worker")

    episode = store.create(
        "TRAININGDAY source-only CPU worker reports. Authors, artifacts, model "
        "identity, corpus admission and physical effects are UNVERIFIED; this "
        "episode does not contain protected evaluation material or any training grant.",
        tuple(sorted(by_worker)),
    )
    for worker_id, worker_claims in sorted(by_worker.items()):
        ordered = sorted(worker_claims, key=lambda item: item.task_id)
        store.submit_answer(
            episode, worker_id,
            "Unverified CPU work claims: "
            + "; ".join(f"{item.task_id} / {allowed[item.task_id].review_role} / {item.status}"
                        for item in ordered)
            + ". This is not legal/data admission, model qualification or a host grant.",
            tuple(f"artifact:sha256:{item.artifact_sha256}" for item in ordered),
        )
    return episode
