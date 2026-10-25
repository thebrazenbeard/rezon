"""Create and verify a private, non-disruptive VN2 Rezon recovery checkpoint.

This tool never stops a service, writes the source database, or restores data.
It must not be confused with permission to deploy a new Rezon revision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

HEAD_RE = re.compile(r"[0-9a-f]{40}\Z")


class CheckpointError(Exception):
    """Fail closed without promoting partial output to a valid checkpoint."""


def _regular_file(path: Path) -> Path:
    if path.is_symlink() or not path.is_file():
        raise CheckpointError(f"not a regular, non-symlink file: {path}")
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head(checkout: Path) -> str:
    if not checkout.is_dir() or checkout.is_symlink():
        raise CheckpointError("source checkout must be a real directory")

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(checkout), *args],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode:
            raise CheckpointError("source Git command failed")
        return result.stdout.strip()

    if Path(git("rev-parse", "--show-toplevel")).resolve() != checkout.resolve():
        raise CheckpointError("source path is not the repository root")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise CheckpointError("tracked source is dirty")
    return git("rev-parse", "HEAD")


def _private_new_directory(target: Path) -> None:
    if target.exists() or target.is_symlink():
        raise CheckpointError("checkpoint target already exists")
    parent = target.parent
    if not parent.is_dir() or parent.is_symlink():
        raise CheckpointError("checkpoint parent must exist and not be a symlink")
    mode = parent.stat()
    if mode.st_uid != os.getuid() or mode.st_mode & 0o022:
        raise CheckpointError(
            "checkpoint parent must be owned by caller and not group/world-writable"
        )
    target.mkdir(mode=0o700)
    target.chmod(0o700)


def _copy_private(source: Path, dest: Path) -> None:
    _regular_file(source)
    with source.open("rb") as inp, dest.open("xb") as out:
        shutil.copyfileobj(inp, out)
    dest.chmod(0o600)


def _environment_files_in_unit(unit: Path) -> set[Path]:
    """Bind private-file custody to literal EnvironmentFile references."""
    names: list[Path] = []
    for line in unit.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("EnvironmentFile="):
            continue
        try:
            values = shlex.split(stripped.partition("=")[2], posix=True)
        except ValueError as error:
            raise CheckpointError("invalid EnvironmentFile syntax") from error
        for value in values:
            value = value.removeprefix("-")
            if not value.startswith("/") or any(char in value for char in "%*?[]"):
                raise CheckpointError(
                    "nonliteral EnvironmentFile needs manual qualification"
                )
            names.append(Path(value).resolve())
    if not names or len(names) != len(set(names)):
        raise CheckpointError("missing or duplicate EnvironmentFile binding")
    return set(names)


def _check_live_user_unit(name: str, unit: Path, checkout: Path) -> None:
    """Fail if the selected user unit has hidden effective overrides."""
    if not re.fullmatch(r"[A-Za-z0-9_.@-]+\.service", name):
        raise CheckpointError("invalid systemd user service name")
    result = subprocess.run(
        [
            "systemctl",
            "--user",
            "show",
            name,
            (
                "--property=FragmentPath,DropInPaths,"
                "EnvironmentFiles,WorkingDirectory,ActiveState,MainPID"
            ),
            "--no-pager",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if result.returncode:
        raise CheckpointError("cannot verify the effective systemd user unit")
    pairs = dict(
        line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
    )
    if not {
        "FragmentPath",
        "DropInPaths",
        "EnvironmentFiles",
        "WorkingDirectory",
        "ActiveState",
        "MainPID",
    }.issubset(pairs):
        raise CheckpointError("incomplete effective systemd unit metadata")
    if pairs["DropInPaths"].strip():
        raise CheckpointError("unbacked systemd drop-ins are present")
    if (
        pairs["ActiveState"] != "active"
        or not pairs["MainPID"].isdigit()
        or int(pairs["MainPID"]) <= 0
    ):
        raise CheckpointError("selected user unit is not active")
    if (
        Path(pairs["FragmentPath"]).resolve() != unit.resolve()
        or Path(pairs["WorkingDirectory"]).resolve() != checkout.resolve()
    ):
        raise CheckpointError("unit path or effective working directory changed")
    names = re.findall(
        r"([^\s]+) \(ignore_errors=(?:yes|no)\)", pairs["EnvironmentFiles"]
    )
    if len(names) != 1 or {
        Path(name).resolve() for name in names
    } != _environment_files_in_unit(unit):
        raise CheckpointError("effective private environment file differs from unit")


def _check_sqlite(path: Path) -> None:
    uri = f"{path.resolve().as_uri()}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if result != ("ok",):
        raise CheckpointError("checkpoint SQLite integrity check failed")


def _rehearse_restore(snapshot: Path, parent: Path) -> None:
    """Restore into a private disposable location, never the live database."""
    with tempfile.TemporaryDirectory(prefix="rezon-restore-test-", dir=parent) as fresh:
        restored = Path(fresh) / "restored.sqlite3"
        _copy_private(snapshot, restored)
        _check_sqlite(restored)
        if _sha256(restored) != _sha256(snapshot):
            raise CheckpointError("disposable restore bytes differ from checkpoint")


def create_checkpoint(
    *,
    checkout: Path,
    expected_head: str,
    database: Path,
    unit: Path,
    private_files: list[Path],
    target: Path,
    unit_name: str | None = None,
) -> dict:
    if not HEAD_RE.fullmatch(expected_head):
        raise CheckpointError(
            "expected Git head must be exactly forty lowercase hex characters"
        )
    if _git_head(checkout) != expected_head:
        raise CheckpointError("source HEAD differs from pinned expected commit")
    if not private_files:
        raise CheckpointError("VN2 recovery requires a private EnvironmentFile copy")
    _regular_file(database)
    _regular_file(unit)
    for path in private_files:
        _regular_file(path)
        if path.stat().st_mode & 0o077:
            raise CheckpointError(
                "source private environment permissions are too broad"
            )
    if {path.resolve() for path in private_files} != _environment_files_in_unit(unit):
        raise CheckpointError("provided private files do not match the user unit")
    if unit_name is not None:
        _check_live_user_unit(unit_name, unit, checkout)
    if len(
        {str(path.resolve()) for path in [database, unit, *private_files]}
    ) != 2 + len(private_files):
        raise CheckpointError("duplicate source path")

    _private_new_directory(target)
    manifest = {
        "schema": "REZON_VN2_CHECKPOINT_V1",
        "source_head": expected_head,
        "created_utc": datetime.now(UTC).isoformat(),
        "files": {},
        "qualification": "PRIVATE_SNAPSHOT_INTEGRITY_ONLY_NOT_INSTALLED_UPGRADE",
    }
    old_umask = os.umask(0o077)
    try:
        snapshot = target / "episodes.sqlite3"
        # SQLite backup obtains a consistent transaction snapshot while the
        # service may continue writing; copying a live .db file would not.
        with (
            closing(
                sqlite3.connect(
                    f"{database.resolve().as_uri()}?mode=ro", uri=True, timeout=5
                )
            ) as source,
            closing(sqlite3.connect(snapshot, timeout=5)) as dest,
        ):
            source.backup(dest)
        snapshot.chmod(0o600)
        _check_sqlite(snapshot)
        inputs = [("service-unit.conf", unit)] + [
            (f"private-{index}.conf", file)
            for index, file in enumerate(private_files, start=1)
        ]
        for filename, source in inputs:
            _copy_private(source, target / filename)
        for path in [snapshot, *(target / filename for filename, _ in inputs)]:
            manifest["files"][path.name] = {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
        with (target / "manifest.json").open("x", encoding="utf-8") as output:
            json.dump(manifest, output, sort_keys=True, indent=2)
            output.write("\n")
        (target / "manifest.json").chmod(0o600)
        verify_checkpoint(target)
    finally:
        os.umask(old_umask)
    return manifest


def verify_checkpoint(target: Path) -> dict:
    if target.is_symlink() or not target.is_dir():
        raise CheckpointError("checkpoint directory missing or symlinked")
    if target.stat().st_mode & 0o077:
        raise CheckpointError("checkpoint directory permissions are too broad")
    manifest_path = _regular_file(target / "manifest.json")
    if manifest_path.stat().st_mode & 0o077:
        raise CheckpointError("manifest permissions are too broad")

    def reject_nonfinite(_: str) -> object:
        raise CheckpointError("non-finite manifest number")

    data = json.loads(
        manifest_path.read_text(encoding="utf-8"), parse_constant=reject_nonfinite
    )
    if not isinstance(data, dict):
        raise CheckpointError("manifest must be a JSON object")
    source_head = data.get("source_head")
    if (
        data.get("schema") != "REZON_VN2_CHECKPOINT_V1"
        or not isinstance(source_head, str)
        or not HEAD_RE.fullmatch(source_head)
    ):
        raise CheckpointError("invalid manifest schema or source binding")
    files = data.get("files")
    if not isinstance(files, dict) or not {
        "episodes.sqlite3",
        "service-unit.conf",
        "private-1.conf",
    }.issubset(files):
        raise CheckpointError("missing required checkpoint artifacts")
    for name, entry in files.items():
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or name in ("", ".", "..")
        ):
            raise CheckpointError("invalid manifest artifact name")
        path = _regular_file(target / name)
        if path.stat().st_mode & 0o077:
            raise CheckpointError("checkpoint artifact permissions are too broad")
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("sha256"), str)
            or not isinstance(entry.get("bytes"), int)
            or _sha256(path) != entry["sha256"]
            or path.stat().st_size != entry["bytes"]
        ):
            raise CheckpointError("checkpoint checksum/length mismatch")
    _check_sqlite(target / "episodes.sqlite3")
    _rehearse_restore(target / "episodes.sqlite3", target.parent)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("create", "verify"))
    parser.add_argument("--checkpoint-dir", required=True, type=Path)
    parser.add_argument("--source-checkout", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--database", type=Path)
    parser.add_argument("--unit-file", type=Path)
    parser.add_argument("--unit-name")
    parser.add_argument("--private-file", type=Path, action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            data = verify_checkpoint(args.checkpoint_dir)
        else:
            if not all(
                (
                    args.source_checkout,
                    args.expected_head,
                    args.database,
                    args.unit_file,
                    args.unit_name,
                )
            ):
                parser.error(
                    "create needs --source-checkout, --expected-head, --database and --unit-file"
                )
            data = create_checkpoint(
                checkout=args.source_checkout,
                expected_head=args.expected_head,
                database=args.database,
                unit=args.unit_file,
                private_files=args.private_file,
                target=args.checkpoint_dir,
                unit_name=args.unit_name,
            )
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "schema": data["schema"],
                    "source_head": data["source_head"],
                    "file_count": len(data["files"]),
                }
            )
        )
        return 0
    except (
        CheckpointError,
        OSError,
        sqlite3.Error,
        ValueError,
        subprocess.TimeoutExpired,
    ) as error:
        print(f"HOLD: {type(error).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
