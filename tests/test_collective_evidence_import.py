"""A real, externally authored review dossier is not a model simulation."""

import json
from pathlib import Path

import pytest

from rezon.collective import CollectiveStore, CollectiveValidationError
from rezon.collective_evidence import import_dossier
from rezon.collective_cli import main


def _manifest():
    return {
        "provenance": "native-agent-report-import",
        "task": "Investigate Blotter service availability without assuming connectivity",
        "findings": [
            {
                "agent_id": "runtime",
                "evidence_class": "SOURCE_INSPECTION",
                "content": "The client has a read-only list() operation.",
                "source_refs": ["github:thebrazenbeard/blotter@18d23b7ff5b52fdb9d8084a69c69ae2d68a34fac:src/agent_blotter/remote.py"],
            },
            {
                "agent_id": "architect",
                "evidence_class": "INFERENCE",
                "content": "Network connectivity is not proved by source inspection.",
                "source_refs": [],
            },
        ],
        "reviews": [
            {
                "agent_id": "runtime",
                "evidence_class": "MODEL_REVIEW",
                "content": "Architect is correct but the account needs a live probe.",
                "target_ids": ["answer:architect"],
                "source_refs": [],
            },
        ],
    }


def test_import_dossier_preserves_authored_findings_and_review_in_collective_store(tmp_path: Path):
    store = CollectiveStore(tmp_path / "episode.sqlite3")
    episode_id = import_dossier(store, _manifest())
    snapshot = CollectiveStore(tmp_path / "episode.sqlite3").snapshot(episode_id)
    assert snapshot.complete
    assert snapshot.agents == ("architect", "runtime")
    assert snapshot.answers[0].content.startswith("Declared evidence class: INFERENCE (unverified)")
    assert "SOURCE_INSPECTION" in snapshot.answers[1].content
    assert snapshot.answers[1].source_refs[0].startswith("github:thebrazenbeard/blotter@")
    assert snapshot.reviews[0].target_ids == ("answer:architect",)
    assert not snapshot.syntheses
    assert len(snapshot.digest) == 64


@pytest.mark.parametrize("change", [
    lambda m: m["findings"][0].update({"evidence_class": "FORMAL_VERIFY"}),
    lambda m: m["findings"][0].update({"source_refs": []}),
    lambda m: m["findings"][0].update({"source_refs": ["not-version-bound"]}),
    lambda m: m["findings"][1].update({"agent_id": "runtime"}),
    lambda m: m["reviews"][0].update({"target_ids": ["answer:runtime"]}),
    lambda m: m["reviews"][0].update({"target_ids": ["answer:missing"]}),
    lambda m: m["reviews"].append(dict(m["reviews"][0])),
    lambda m: m.update({"provenance": "generated-by-rezon-model"}),
    lambda m: m.update({"spurious": "not allowed"}),
])
def test_invalid_dossier_is_rejected_without_creating_episode(tmp_path: Path, change):
    store = CollectiveStore(tmp_path / "episode.sqlite3")
    manifest = _manifest()
    change(manifest)
    with pytest.raises(CollectiveValidationError):
        import_dossier(store, manifest)
    with store._connect() as conn:
        assert conn.execute("SELECT count(*) FROM episodes").fetchone()[0] == 0


def test_dossier_import_does_not_synthesize_or_claim_network_checks(tmp_path: Path):
    store = CollectiveStore(tmp_path / "episode.sqlite3")
    manifest = _manifest()
    manifest["reviews"] = []
    episode_id = import_dossier(store, manifest)
    snapshot = store.snapshot(episode_id)
    assert snapshot.complete and not snapshot.reviews and not snapshot.syntheses
    assert "unverified" in snapshot.answers[0].content


def test_import_findings_cli_creates_real_durable_episode_without_claiming_model_execution(
    tmp_path: Path, capsys
):
    dossier = tmp_path / "dossier.json"
    dossier.write_text(json.dumps(_manifest()), encoding="utf-8")
    db = tmp_path / "episode.sqlite3"
    assert main(["import-findings", "--db", str(db), "--manifest", str(dossier)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "external_agent_claims_unverified"
    assert result["answers"] == 2 and result["reviews"] == 1
    assert CollectiveStore(db).snapshot(result["episode_id"]).digest == result["input_digest"]
    assert "synthesis" not in result
