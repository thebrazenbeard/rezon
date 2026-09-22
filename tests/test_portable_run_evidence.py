import hashlib
import json

import pytest

from rezon.audit import verify_run_evidence
from rezon.cli import main
from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.interop import RunEvidenceError, export_run_evidence
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


class Echo:
    node_id = "echo_hypothesis"

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h1",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    "portable output",
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _evidence():
    episode = Episode("portable")
    episode.add_proposition(
        Proposition(
            "o1",
            "portable",
            PropositionKind.OBSERVATION,
            "portable input",
            source_versions=("source:portable@v1",),
        )
    )
    node = RunnerNode(
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        Echo(),
        VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="portable-task",
    )
    return export_run_evidence(outcome)


def _redigest(evidence):
    body = {
        "schema_version": evidence["schema_version"],
        "receipt": evidence["receipt"],
        "executions": evidence["executions"],
    }
    encoded = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    evidence["evidence_digest"] = hashlib.sha256(encoded).hexdigest()


def test_exported_evidence_verifies_without_reexecution():
    report = verify_run_evidence(_evidence())

    assert report["valid"] is True
    assert report["schema_version"] == "rezon.run-evidence.v1"
    assert report["execution_count"] == 1
    assert report["effect_state"] == "plan"


def test_digest_tampering_is_rejected():
    evidence = _evidence()
    evidence["evidence_digest"] = "0" * 64

    with pytest.raises(RunEvidenceError, match="digest"):
        verify_run_evidence(evidence)


def test_redigested_receipt_trace_mismatch_is_rejected():
    evidence = _evidence()
    evidence["receipt"]["execution_ids"] = []
    evidence["receipt"]["execution_output_digests"] = []
    evidence["receipt"]["execution_producer_ids"] = []
    _redigest(evidence)

    with pytest.raises(RunEvidenceError, match="execution"):
        verify_run_evidence(evidence)


def test_redigested_producer_forgery_is_rejected():
    evidence = _evidence()
    evidence["executions"][0]["canonical_producer_execution_id"] = "canonical:exec:forged"
    execution_id = evidence["receipt"]["execution_ids"][0]
    evidence["receipt"]["execution_producer_ids"] = [
        [execution_id, "canonical:exec:forged"]
    ]
    _redigest(evidence)

    with pytest.raises(RunEvidenceError, match="producer"):
        verify_run_evidence(evidence)


def test_cli_verifies_file(tmp_path, capsys):
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(_evidence()), encoding="utf-8")

    assert main(["verify-evidence", str(path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["valid"] is True


def test_cli_fails_closed_for_invalid_file(tmp_path, capsys):
    path = tmp_path / "evidence.json"
    path.write_text('{"not":"evidence"}', encoding="utf-8")

    assert main(["verify-evidence", str(path)]) == 2
    report = json.loads(capsys.readouterr().err)
    assert report["valid"] is False
