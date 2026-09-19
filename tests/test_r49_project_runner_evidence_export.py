import json
from dataclasses import replace

import pytest

from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.interop import RUN_EVIDENCE_SCHEMA, RunEvidenceError, export_run_evidence
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState
from rezon.runner import EpisodeRunner, RunnerNode, RunOutcome
from rezon.visibility import VisibilityPolicy


class Echo:
    node_id = "echo_hypothesis"

    def __init__(self, output):
        self.output = output

    def execute(self, view, episode_id):
        return ExecutionResult(
            execution_id=view.execution_id,
            node_id=self.node_id,
            emitted_propositions=(
                Proposition(
                    "h1",
                    episode_id,
                    PropositionKind.HYPOTHESIS,
                    self.output,
                    producer_execution_id=view.execution_id,
                ),
            ),
        )


def _run(input_content, output_content, *, source_versions=()):
    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            "o1",
            "e1",
            PropositionKind.OBSERVATION,
            input_content,
            source_versions=source_versions,
        )
    )
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
        ),
        Echo(output_content),
        VisibilityPolicy(),
    )
    return EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r49",
    )


def test_export_is_versioned_json_safe_non_promotional_and_deterministic():
    first = export_run_evidence(_run("same-input", "same-output"))
    second = export_run_evidence(_run("same-input", "same-output"))

    assert first == second
    assert first["schema_version"] == RUN_EVIDENCE_SCHEMA
    assert first["schema_version"] == "rezon.run-evidence.v1"
    assert first["receipt"]["effect_state"] == "plan"
    assert first["receipt"]["claim_disposition_complete"] is False
    assert first["receipt"]["execution_output_digests"]
    assert first["receipt"]["execution_producer_ids"]
    assert first["executions"]
    assert first["evidence_digest"]

    assert json.dumps(first, sort_keys=True, separators=(",", ":"))


def test_export_digest_changes_for_different_canonical_output():
    left = export_run_evidence(_run("same-input", "alpha"))
    right = export_run_evidence(_run("same-input", "beta"))

    assert left["evidence_digest"] != right["evidence_digest"]


def test_export_digest_changes_for_different_canonical_input():
    left = export_run_evidence(_run("input-alpha", "same-output"))
    right = export_run_evidence(_run("input-beta", "same-output"))

    assert left["receipt"]["execution_output_digests"] == right["receipt"]["execution_output_digests"]
    assert left["receipt"]["execution_producer_ids"] != right["receipt"]["execution_producer_ids"]
    assert left["evidence_digest"] != right["evidence_digest"]


def test_export_binds_receipt_source_versions_to_trace_ordered_dedupe():
    outcome = _run(
        "input",
        "output",
        source_versions=("source:A@v1", "source:B@v2"),
    )

    evidence = export_run_evidence(outcome)

    assert evidence["receipt"]["source_versions"] == ["source:A@v1", "source:B@v2"]
    assert evidence["executions"][0]["source_versions"] == ["source:A@v1", "source:B@v2"]


def test_export_rejects_forged_receipt_source_versions():
    outcome = _run("input", "output", source_versions=("source:A@v1",))
    forged = RunOutcome(
        replace(
            outcome.receipt,
            source_versions=("source:FORGED@v9",),
        ),
        outcome.trace,
    )

    with pytest.raises(RunEvidenceError, match="source versions"):
        export_run_evidence(forged)


def test_export_rejects_receipt_that_conceals_trace_failure():
    class InvalidResultExecutor:
        node_id = "echo_hypothesis"

        def execute(self, view, episode_id):
            return object()

    episode = Episode("e1")
    episode.add_proposition(
        Proposition("o1", "e1", PropositionKind.OBSERVATION, "input")
    )
    node = RunnerNode(
        NodeDescriptor("echo_hypothesis", (PropositionKind.HYPOTHESIS,)),
        InvalidResultExecutor(),
        VisibilityPolicy(),
    )
    outcome = EpisodeRunner((node,), budget_limit=1).run(
        episode,
        task_id="t-r51-failure-binding",
    )

    assert outcome.receipt.failures == (FailureState.CONTRACT_VIOLATION,)
    assert outcome.trace.records[0].failures == (FailureState.CONTRACT_VIOLATION,)

    forged = RunOutcome(
        replace(outcome.receipt, failures=()),
        outcome.trace,
    )

    with pytest.raises(RunEvidenceError, match="failure"):
        export_run_evidence(forged)


def test_export_rejects_forged_receipt_output_binding():
    outcome = _run("input", "real-output")
    execution_id = outcome.receipt.execution_ids[0]
    forged = RunOutcome(
        replace(
            outcome.receipt,
            execution_output_digests=((execution_id, "0" * 64),),
        ),
        outcome.trace,
    )

    with pytest.raises(RunEvidenceError, match="output"):
        export_run_evidence(forged)


def test_export_rejects_forged_receipt_producer_binding():
    outcome = _run("input", "output")
    execution_id = outcome.receipt.execution_ids[0]
    forged = RunOutcome(
        replace(
            outcome.receipt,
            execution_producer_ids=((execution_id, "forged-producer"),),
        ),
        outcome.trace,
    )

    with pytest.raises(RunEvidenceError, match="producer"):
        export_run_evidence(forged)


def test_export_rejects_missing_receipt_execution_coverage():
    outcome = _run("input", "output")
    forged = RunOutcome(
        replace(
            outcome.receipt,
            execution_ids=(),
            execution_output_digests=(),
            execution_producer_ids=(),
        ),
        outcome.trace,
    )

    with pytest.raises(RunEvidenceError, match="execution"):
        export_run_evidence(forged)
