"""Rezon coordinates evidence workers, not concurrent neural optimizer steps."""

from dataclasses import replace
from pathlib import Path

import pytest

from rezon.collective import CollectiveStore
from rezon.trainingday_coordination import (
    CorpusPins,
    ModelArm,
    WorkerClaim,
    WorkContractError,
    plan_two_model_bakeoff,
    record_cpu_claims,
)


def _sha(char: str) -> str:
    return char * 64


def _arms() -> tuple[ModelArm, ModelArm]:
    return (
        ModelArm("oss4b", "source/model-a", _sha("a"), "GGUF_INFERENCE_ONLY"),
        ModelArm("qwen35", "source/model-b", _sha("b"), "GGUF_INFERENCE_ONLY"),
    )


def _pins() -> CorpusPins:
    return CorpusPins(_sha("1"), _sha("2"), _sha("3"), _sha("4"))


def test_two_gguf_candidates_produce_cpu_fanout_then_serial_single_gpu_bakeoff():
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    cpu = [task for task in plan.tasks if task.phase == "CPU_REVIEW"]
    gpu = [task for task in plan.tasks if task.phase == "BASELINE_EVAL"]
    assert len(cpu) == 4
    assert {task.worker_id for task in cpu} == {"cpu_alpha", "cpu_beta"}
    assert {task.review_role for task in cpu} == {
        "CORPUS_PROVENANCE", "DEDUP_REVIEW", "RIGHTS_CONSENT_REVIEW",
        "PROTECTED_EVAL_CUSTODY",
    }
    assert all(task.review_role is None for task in gpu)
    assert all(task.gpu_slot is None for task in cpu)
    assert len(gpu) == 2 and {task.model_id for task in gpu} == {"oss4b", "qwen35"}
    assert gpu[0].gpu_slot == gpu[1].gpu_slot == "gpu0"
    assert gpu[1].depends_on == (gpu[0].task_id,)
    assert set(gpu[0].depends_on) == {task.task_id for task in cpu}
    assert plan.selection_requires_independent_heldout
    assert plan.requires_trainable_base_after_gguf_bakeoff
    assert not plan.authorizes_gpu_training
    assert not plan.authorizes_data_admission
    assert all(not task.authorizes_effects for task in plan.tasks)
    assert not any(task.phase == "OPTIMIZER_STEP" for task in plan.tasks)


@pytest.mark.parametrize("arms", [
    (ModelArm("same", "source/a", _sha("a"), "GGUF_INFERENCE_ONLY"),
     ModelArm("same", "source/b", _sha("b"), "GGUF_INFERENCE_ONLY")),
    (ModelArm("one", "source/a", _sha("a"), "GGUF_INFERENCE_ONLY"),
     ModelArm("two", "source/b", _sha("a"), "GGUF_INFERENCE_ONLY")),
])
def test_reject_ambiguous_two_model_roster(arms):
    with pytest.raises(WorkContractError):
        plan_two_model_bakeoff(arms, _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")


@pytest.mark.parametrize("workers", [(), ("same", "same"), ("solo",), ("a", "b", "a")])
def test_require_distinct_parallel_cpu_reviewers(workers):
    with pytest.raises(WorkContractError):
        plan_two_model_bakeoff(_arms(), _pins(), workers, "gpu0")


def test_reject_split_overlap_and_unbounded_gpu_parallelism():
    with pytest.raises(WorkContractError):
        plan_two_model_bakeoff(_arms(), CorpusPins(_sha("1"), _sha("1"), _sha("3"), _sha("4")),
                               ("a", "b"), "gpu0")
    with pytest.raises(WorkContractError):
        plan_two_model_bakeoff(_arms(), _pins(), ("a", "b"), "gpu0", gpu_parallelism=2)
    with pytest.raises(WorkContractError):
        plan_two_model_bakeoff(_arms(), _pins(), ("a", "b"), "gpu0", zero_cost=False)


def test_different_candidate_formats_do_not_create_a_weight_merge_or_training_grant():
    arms = (ModelArm("hf", "source/hf", _sha("a"), "HF_TRAINABLE"),
            ModelArm("gguf", "source/gguf", _sha("b"), "GGUF_INFERENCE_ONLY"))
    plan = plan_two_model_bakeoff(arms, _pins(), ("a", "b"), "gpu0")
    assert not plan.authorizes_gpu_training
    assert not hasattr(plan, "aggregated_gradient")
    assert not hasattr(plan, "merged_weights")


def test_structured_cpu_claims_are_saved_as_unverified_rezon_episode(tmp_path: Path):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    reviews = [task for task in plan.tasks if task.phase == "CPU_REVIEW"]
    claims = [WorkerClaim(task.task_id, task.worker_id,
                          "SOURCE_CHECKED" if index % 2 == 0 else "REJECTED",
                          _sha(str(index + 5)))
              for index, task in enumerate(reviews)]
    store = CollectiveStore(tmp_path / "rezon.sqlite3")
    episode = record_cpu_claims(store, plan, tuple(claims))
    snapshot = CollectiveStore(tmp_path / "rezon.sqlite3").snapshot(episode)
    assert snapshot.complete
    assert len(snapshot.answers) == 2
    assert sum(len(answer.source_refs) for answer in snapshot.answers) == 4
    assert snapshot.syntheses == ()
    assert all("unverified" in answer.content.lower() for answer in snapshot.answers)
    assert all(ref.startswith("artifact:sha256:") for answer in snapshot.answers for ref in answer.source_refs)
    assert not plan.authorizes_gpu_training


def test_reject_unbound_and_duplicate_claims_without_creating_episode(tmp_path: Path):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    work = next(task for task in plan.tasks if task.phase == "CPU_REVIEW")
    store = CollectiveStore(tmp_path / "rezon.sqlite3")
    for claims in (
        (WorkerClaim(work.task_id, "wrong", "SOURCE_CHECKED", _sha("5")),),
        (WorkerClaim(work.task_id, work.worker_id, "SOURCE_CHECKED", _sha("5")),) * 2,
        (WorkerClaim("baseline-eval-oss4b", work.worker_id, "SOURCE_CHECKED", _sha("5")),),
    ):
        with pytest.raises(WorkContractError):
            record_cpu_claims(store, plan, claims)
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_reject_private_freeform_claim_content_and_malformed_digests():
    with pytest.raises(WorkContractError):
        WorkerClaim("cpu-review-1", "cpu_alpha", "gold=A", _sha("a"))
    with pytest.raises(WorkContractError):
        WorkerClaim("cpu-review-1", "cpu_alpha", "SOURCE_CHECKED", "bad")


def test_cpu_evidence_import_is_deterministic_over_claim_arrival_order(tmp_path: Path):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    claims = tuple(WorkerClaim(task.task_id, task.worker_id, "UNKNOWN", _sha(str(index + 5)))
                   for index, task in enumerate(plan.tasks[:4]))
    answers = []
    for filename, ordered in (("forward.sqlite3", claims),
                              ("reverse.sqlite3", tuple(reversed(claims)))):
        store = CollectiveStore(tmp_path / filename)
        episode = record_cpu_claims(store, plan, ordered)
        snap = store.snapshot(episode)
        answers.append(tuple((answer.agent_id, answer.content, answer.source_refs)
                             for answer in snap.answers))
    assert answers[0] == answers[1]


def test_forged_plan_role_must_not_leak_to_collective_episode(tmp_path: Path):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    poisoned = replace(plan, tasks=(
        replace(plan.tasks[0], review_role="private_gold_answer=LEAK"),
        *plan.tasks[1:],
    ))
    claims = tuple(WorkerClaim(task.task_id, task.worker_id, "UNKNOWN", _sha(str(index + 5)))
                   for index, task in enumerate(poisoned.tasks[:2]))
    store = CollectiveStore(tmp_path / "poisoned.sqlite3")
    with pytest.raises(WorkContractError):
        record_cpu_claims(store, poisoned, claims)
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_duplicate_same_worker_evidence_rejected_before_any_episode(tmp_path: Path):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    claims = tuple(WorkerClaim(task.task_id, task.worker_id, "SOURCE_CHECKED",
                               _sha("5" if index in (0, 2) else str(index + 5)))
                   for index, task in enumerate(plan.tasks[:4]))
    store = CollectiveStore(tmp_path / "duplicate.sqlite3")
    with pytest.raises(WorkContractError):
        record_cpu_claims(store, plan, claims)
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_forged_gpu_dependency_and_authority_flag_fail_closed(tmp_path: Path):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    claims = tuple(WorkerClaim(task.task_id, task.worker_id, "UNKNOWN", _sha(str(index + 5)))
                   for index, task in enumerate(plan.tasks[:2]))
    poisoned_gpu = replace(plan, tasks=(*plan.tasks[:4],
                                        replace(plan.tasks[4], depends_on=()),
                                        plan.tasks[5]))
    poisoned_flag = replace(plan)
    object.__setattr__(poisoned_flag, "authorizes_gpu_training", True)
    store = CollectiveStore(tmp_path / "forged.sqlite3")
    for poisoned in (poisoned_gpu, poisoned_flag):
        with pytest.raises(WorkContractError):
            record_cpu_claims(store, poisoned, claims)
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_mutated_claim_status_and_source_ref_never_leak(tmp_path: Path):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    two = plan.tasks[:2]
    store = CollectiveStore(tmp_path / "mutated.sqlite3")
    for field, value in (("status", "private_gold_answer=LEAK"),
                         ("artifact_sha256", "private_gold_answer=LEAK")):
        first = WorkerClaim(two[0].task_id, two[0].worker_id, "UNKNOWN", _sha("5"))
        object.__setattr__(first, field, value)
        second = WorkerClaim(two[1].task_id, two[1].worker_id, "UNKNOWN", _sha("6"))
        with pytest.raises(WorkContractError):
            record_cpu_claims(store, plan, (first, second))
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_equal_spoofed_role_objects_do_not_cross_persistence_boundary(tmp_path: Path):
    class EvilEqual:
        def __eq__(self, other):
            return True

        def __str__(self):
            return "private_gold_answer=LEAK"

    class EvilStr(str):
        def __str__(self):
            return "private_gold_answer=LEAK"

    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    claims = tuple(WorkerClaim(task.task_id, task.worker_id, "UNKNOWN", _sha(str(index + 5)))
                   for index, task in enumerate(plan.tasks[:2]))
    store = CollectiveStore(tmp_path / "spoof.sqlite3")
    for role in (EvilEqual(), EvilStr("CORPUS_PROVENANCE")):
        poisoned = replace(plan, tasks=(replace(plan.tasks[0], review_role=role),
                                        *plan.tasks[1:]))
        assert poisoned == plan  # Dataclass equality alone is not a schema gate.
        with pytest.raises(WorkContractError):
            record_cpu_claims(store, poisoned, claims)
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_equal_spoofed_gpu_dependency_tuple_rejected(tmp_path: Path):
    class EvilTuple(tuple):
        def __eq__(self, other):
            return True

    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    tampered = replace(plan, tasks=(*plan.tasks[:4],
                                    replace(plan.tasks[4], depends_on=EvilTuple(())),
                                    plan.tasks[5]))
    assert tampered == plan
    store = CollectiveStore(tmp_path / "evil-tuple.sqlite3")
    claims = tuple(WorkerClaim(task.task_id, task.worker_id, "UNKNOWN", _sha(str(index + 5)))
                   for index, task in enumerate(plan.tasks[:2]))
    with pytest.raises(WorkContractError):
        record_cpu_claims(store, tampered, claims)
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_worker_claims_are_snapshotted_before_persistence_side_effect(tmp_path: Path, monkeypatch):
    plan = plan_two_model_bakeoff(_arms(), _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")
    claims = tuple(WorkerClaim(task.task_id, task.worker_id, "UNKNOWN", _sha(str(index + 5)))
                   for index, task in enumerate(plan.tasks[:2]))
    store = CollectiveStore(tmp_path / "mutable-claims.sqlite3")
    original = CollectiveStore.create

    def mutate_during_create(self, prompt, agents):
        object.__setattr__(claims[0], "status", "private_gold_answer=LEAK")
        return original(self, prompt, agents)

    monkeypatch.setattr(CollectiveStore, "create", mutate_during_create)
    episode = record_cpu_claims(store, plan, claims)
    snapshot = store.snapshot(episode)
    assert snapshot.complete
    assert all("private_gold_answer" not in answer.content for answer in snapshot.answers)


def test_planner_revalidates_frozen_model_artifact_after_caller_mutation():
    arms = _arms()
    object.__setattr__(arms[0], "artifact_format", "NOT_A_MODEL_FORMAT")
    with pytest.raises(WorkContractError):
        plan_two_model_bakeoff(arms, _pins(), ("cpu_alpha", "cpu_beta"), "gpu0")


def test_planner_revalidates_frozen_corpus_pins_after_caller_mutation():
    pins = _pins()
    object.__setattr__(pins, "protected_eval_roster_sha256", "bad")
    with pytest.raises(WorkContractError):
        plan_two_model_bakeoff(_arms(), pins, ("cpu_alpha", "cpu_beta"), "gpu0")
