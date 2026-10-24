"""A reproducible real-HTTP isolated hearing is not production enrollment."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from rezon.qualify_isolated import qualify, QualificationError


class ModelFixture:
    def __init__(self, *args, **kwargs):
        assert kwargs["max_tokens"] == 120
    def complete(self, messages):
        assert messages[-1]["role"] == "user"
        return "MODEL_FIXTURE: hypothesis unsupported without preregistered controlled comparison"


def test_full_http_tkal_qualification_and_persistent_readback():
    with TemporaryDirectory() as tmp:
        output = Path(tmp) / "isolated"
        with patch("rezon.worker_client.OpenAICompatibleModel", ModelFixture):
            report = qualify(output, model="fixture-test", model_url="http://127.0.0.1:11435/v1",
                             max_tokens=120)
        assert report["qualification"] == "ISOLATED_TKAL_REFINE"
        assert report["answer_count"] == report["review_count"] == 4
        assert report["challenges"] == report["defenses"] == 3
        assert report["verdict"] == "REFINE"
        assert report["live_model_calls"] == 1
        assert report["persisted_reopen"] is True
        assert report["unauthenticated_denied"] is True
        assert report["self_review_denied"] is True
        assert report["self_challenge_denied"] is True
        assert report["premature_verdict_denied"] is True
        assert report["unanswered_resolution_denied"] is True
        assert report["closed_hearing_denied"] is True
        assert report["host_attestation"] is False
        assert report["production_credential_access"] is False
        serialized = (output / "report.json").read_text()
        assert "Bearer " not in serialized
        assert "REZON_COLLECTIVE_ADMIN_TOKEN" not in serialized
        assert "REZON_WORKER_TOKEN" not in serialized
        assert (output / "qual.sqlite3").is_file()


def test_nonloopback_model_is_rejected_before_files_written():
    with TemporaryDirectory() as tmp:
        target = Path(tmp) / "probe"
        with pytest.raises(QualificationError):
            qualify(target, model="test", model_url="http://outside.example/v1")
        assert not target.exists()


def test_existing_output_is_not_overwritten():
    with TemporaryDirectory() as tmp:
        target = Path(tmp) / "already-exists"
        target.mkdir()
        with pytest.raises(QualificationError):
            qualify(target)


def test_python_optimized_mode_cannot_skip_qualification_assertions():
    with TemporaryDirectory() as tmp:
        output = Path(tmp) / "must-not-run-optimized"
        result = subprocess.run(
            [sys.executable, "-O", "-m", "rezon.qualify_isolated",
             "--output", str(output)],
            capture_output=True, text=True, timeout=20,
        )
        assert result.returncode != 0
        assert not output.exists()
