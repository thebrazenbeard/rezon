import json
from pathlib import Path
import subprocess
import sys


FIXTURES = (
    Path("tests/fixtures/benchmark_v1.json"),
    Path("tests/fixtures/benchmark_v1_clean_controls.json"),
)
SCRIPT = Path("scripts/run_benchmark_v1.py")


def _run(seed: int = 20260916, code_version: str = "test-code-version") -> dict:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            *(str(path) for path in FIXTURES),
            "--seed",
            str(seed),
            "--code-version",
            code_version,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def test_reference_runner_emits_auditable_metric_report():
    report = _run()

    assert report["benchmark"] == "rezon-benchmark-v1-layer1"
    assert report["fixture_version"] == "benchmark-v1.0"
    assert len(report["fixture_sha256"]) == 64
    assert len(report["fixture_files"]) == 2
    assert {entry["path"] for entry in report["fixture_files"]} == {
        str(path) for path in FIXTURES
    }
    assert all(len(entry["sha256"]) == 64 for entry in report["fixture_files"])
    assert report["code_version"] == "test-code-version"
    assert report["case_count"] == 24

    assert set(report["strategies"]) == {
        "single_pass",
        "fixed_multipass",
        "rezon_guarded",
    }
    for metrics in report["strategies"].values():
        assert "semantic" in metrics
        assert "cost" in metrics
        assert "disposition_accuracy" in metrics["semantic"]
        assert "false_accepts" in metrics["semantic"]
        assert "operation_count" in metrics["cost"]
        assert metrics["cost"]["wall_clock_seconds"] is None

    assert report["pairwise_deltas"]
    assert all(
        entry["deltas"]["wall_clock_seconds"] is None
        for entry in report["pairwise_deltas"]
    )
    assert {entry["removed_guard"] for entry in report["guard_ablation"]} == {
        "proposition_fidelity",
        "provenance_currentness",
        "admission_integrity",
        "independence_contamination",
        "failure_visibility",
        "authority_effect_boundary",
    }
    assert report["order_permutations"]
    assert all(entry["permutation_id"] for entry in report["order_permutations"])
    assert report["label_permutation"]["seed"] == 20260916
    assert report["label_permutation"]["permutation_id"]
    assert (
        report["label_permutation"]["before_strategy_input_digest"]
        == report["label_permutation"]["after_strategy_input_digest"]
    )
    assert report["does_not_prove"] == [
        "live end-to-end reasoning superiority",
        "provider or model quality",
        "deployment, installation, activation, or runtime effect",
        "general reasoning improvement outside this frozen replay population",
    ]
    assert "best_strategy" not in report
    assert "score" not in report


def test_reference_runner_is_deterministic_for_same_inputs():
    first = _run(seed=123)
    second = _run(seed=123)
    assert first == second


def test_reference_runner_changes_permutation_identity_with_seed_not_fixture_digest():
    first = _run(seed=1)
    second = _run(seed=2)

    assert first["fixture_sha256"] == second["fixture_sha256"]
    assert first["fixture_files"] == second["fixture_files"]
    assert first["strategy_input_digest"] == second["strategy_input_digest"]
    assert first["label_permutation"]["permutation_id"] != second["label_permutation"]["permutation_id"]
