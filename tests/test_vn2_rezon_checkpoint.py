"""Adversarial source-only tests for VN2 recovery checkpoint custody."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import vn2_rezon_checkpoint as checkpoint
from scripts.vn2_rezon_checkpoint import (
    CheckpointError,
    create_checkpoint,
    verify_checkpoint,
)


@pytest.fixture
def inputs(tmp_path: Path):
    checkout = tmp_path / "source"
    checkout.mkdir()
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    (checkout / "VERSION").write_text("one", encoding="utf-8")
    subprocess.run(["git", "-C", str(checkout), "add", "VERSION"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(checkout),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "pinned source",
        ],
        check=True,
    )
    head = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()

    database = tmp_path / "live.sqlite3"
    with closing(sqlite3.connect(database)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE episodes(id INTEGER PRIMARY KEY, text TEXT)")
        conn.execute("INSERT INTO episodes(text) VALUES ('existing-private-record')")
        conn.commit()
    env = tmp_path / "rezon.env"
    env.write_text("PRIVATE_TOKEN=do-not-leak\n", encoding="utf-8")
    env.chmod(0o600)
    unit = tmp_path / "rezon.service"
    unit.write_text(f"[Service]\nEnvironmentFile={env}\n", encoding="utf-8")
    target = tmp_path / "checkpoint"
    return {
        "checkout": checkout,
        "expected_head": head,
        "database": database,
        "unit": unit,
        "private_files": [env],
        "target": target,
    }


def test_online_sqlite_backup_private_custody_and_immutable_source(inputs):
    before = inputs["database"].read_bytes()
    manifest = create_checkpoint(**inputs)
    assert manifest["source_head"] == inputs["expected_head"]
    assert set(manifest["files"]) == {
        "episodes.sqlite3",
        "service-unit.conf",
        "private-1.conf",
    }
    assert verify_checkpoint(inputs["target"]) == manifest
    assert inputs["database"].read_bytes() == before
    with sqlite3.connect(inputs["target"] / "episodes.sqlite3") as conn:
        assert conn.execute("SELECT text FROM episodes").fetchone() == (
            "existing-private-record",
        )
    assert inputs["target"].stat().st_mode & 0o077 == 0
    assert all(p.stat().st_mode & 0o077 == 0 for p in inputs["target"].iterdir())
    assert "do-not-leak" not in (inputs["target"] / "manifest.json").read_text()


def test_reject_wrong_source_revision_without_creating_backup(inputs):
    inputs["expected_head"] = "0" * 40
    with pytest.raises(CheckpointError, match="differs"):
        create_checkpoint(**inputs)
    assert not inputs["target"].exists()


def test_reject_missing_private_environment_file(inputs):
    inputs["private_files"] = []
    with pytest.raises(CheckpointError, match="EnvironmentFile"):
        create_checkpoint(**inputs)
    assert not inputs["target"].exists()


def test_reject_wrong_or_dynamic_unit_private_file_reference(inputs, tmp_path):
    alternate = tmp_path / "wrong.env"
    alternate.write_text("OTHER=1\n", encoding="utf-8")
    alternate.chmod(0o600)
    inputs["private_files"] = [alternate]
    with pytest.raises(CheckpointError, match="do not match"):
        create_checkpoint(**inputs)
    inputs["unit"].write_text(
        "[Service]\nEnvironmentFile=%h/secrets.env\n", encoding="utf-8"
    )
    with pytest.raises(CheckpointError, match="nonliteral"):
        create_checkpoint(**inputs)
    assert not inputs["target"].exists()


def test_reject_world_readable_private_source_file(inputs):
    inputs["private_files"][0].chmod(0o644)
    with pytest.raises(CheckpointError, match="permissions"):
        create_checkpoint(**inputs)
    assert not inputs["target"].exists()


def test_active_user_unit_binding_rejects_dropins_and_mismatched_environment(
    inputs, monkeypatch
):
    unit = inputs["unit"]
    checkout = inputs["checkout"]
    env = inputs["private_files"][0]

    def fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=(
                f"FragmentPath={unit}\nDropInPaths={fake_run.dropins}\n"
                f"EnvironmentFiles={fake_run.environment} (ignore_errors=no)\n"
                f"WorkingDirectory={checkout}\nActiveState=active\nMainPID=51321\n"
            ),
        )

    fake_run.dropins = ""
    fake_run.environment = str(env)
    monkeypatch.setattr(checkpoint.subprocess, "run", fake_run)
    checkpoint._check_live_user_unit("rezon-tkik.service", unit, checkout)
    fake_run.dropins = (
        "/home/patrick/.config/systemd/user/rezon-tkik.service.d/override.conf"
    )
    with pytest.raises(CheckpointError, match="drop-ins"):
        checkpoint._check_live_user_unit("rezon-tkik.service", unit, checkout)
    fake_run.dropins = ""
    fake_run.environment = "/other/hidden.env"
    with pytest.raises(CheckpointError, match="effective private environment"):
        checkpoint._check_live_user_unit("rezon-tkik.service", unit, checkout)


def test_reject_dirty_tracked_source_without_snapshot(inputs):
    (inputs["checkout"] / "VERSION").write_text("changed", encoding="utf-8")
    with pytest.raises(CheckpointError, match="dirty"):
        create_checkpoint(**inputs)
    assert not inputs["target"].exists()


def test_detect_tampered_artifact_and_reject_destination_overwrite(inputs):
    create_checkpoint(**inputs)
    with pytest.raises(CheckpointError, match="already exists"):
        create_checkpoint(**inputs)
    (inputs["target"] / "private-1.conf").write_text("mutated", encoding="utf-8")
    with pytest.raises(CheckpointError, match="checksum"):
        verify_checkpoint(inputs["target"])


def test_reject_symlinked_credential_file_and_parent(inputs, tmp_path):
    alias = tmp_path / "alias.env"
    alias.symlink_to(inputs["private_files"][0])
    inputs["private_files"] = [alias]
    with pytest.raises(CheckpointError, match="symlink"):
        create_checkpoint(**inputs)
    assert not inputs["target"].exists()


def test_reject_world_writable_checkpoint_parent(inputs, tmp_path):
    parent = tmp_path / "unsafe"
    parent.mkdir(mode=0o777)
    parent.chmod(0o777)
    inputs["target"] = parent / "checkpoint"
    with pytest.raises(CheckpointError, match="group/world-writable"):
        create_checkpoint(**inputs)
    assert not inputs["target"].exists()


def test_reject_manifest_path_traversal(inputs):
    create_checkpoint(**inputs)
    path = inputs["target"] / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["files"]["../outside"] = {"sha256": "0" * 64, "bytes": 0}
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(CheckpointError, match="artifact name"):
        verify_checkpoint(inputs["target"])


@pytest.mark.parametrize(
    "payload", ["[]", '{"source_head": null}', '{"source_head": NaN}']
)
def test_malformed_manifest_never_promoted(inputs, payload):
    create_checkpoint(**inputs)
    (inputs["target"] / "manifest.json").write_text(payload, encoding="utf-8")
    with pytest.raises(CheckpointError):
        verify_checkpoint(inputs["target"])


def test_invalid_database_never_writes_valid_manifest(inputs, tmp_path):
    invalid = tmp_path / "corrupt.sqlite3"
    invalid.write_bytes(b"not a SQLite database")
    inputs["database"] = invalid
    with pytest.raises(sqlite3.DatabaseError):
        create_checkpoint(**inputs)
    assert not (inputs["target"] / "manifest.json").exists()


def test_checkpoint_verifier_rejects_broad_file_permissions(inputs):
    create_checkpoint(**inputs)
    (inputs["target"] / "episodes.sqlite3").chmod(0o644)
    with pytest.raises(CheckpointError, match="permissions"):
        verify_checkpoint(inputs["target"])
