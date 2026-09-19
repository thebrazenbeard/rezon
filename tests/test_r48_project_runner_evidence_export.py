import json

from rezon.episode import Episode
from rezon.epistemics import Proposition, PropositionKind
from rezon.interop import RUN_EVIDENCE_SCHEMA, export_run_evidence
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.runner import EpisodeRunner, RunnerNode
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


def _run(input_content, output_content):
    episode = Episode("e1")
    episode.add_proposition(
        Proposition(
            "o1",
            "e1",
            PropositionKind.OBSERVATION,
            input_content,
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
        task_id="t-r48",
    )


def test_exported_run_evidence_is_versioned_json_safe_and_non_promotional():
    evidence = export_run_evidence(_run("input", "output"))

    assert evidence["schema_version"] == RUN_EVIDENCE_SCHEMA
    assert evidence["schema_version"] == "rezon.run-evidence.v1"
    assert evidence["receipt"]["effect_state"] == "plan"
    assert evidence["receipt"]["claim_disposition_complete"] is False
    assert evidence["receipt"]["execution_output_digests"]
    assert evidence["receipt"]["execution_producer_ids"]
    assert evidence["evidence_digest"]

    encoded = json.dumps(
        evidence,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert encoded


def test_run_evidence_digest_is_deterministic_for_same_reasoning_event():
    first = export_run_evidence(_run("same-input", "same-output"))
    second = export_run_evidence(_run("same-input", "same-output"))

    assert first == second


def test_run_evidence_digest_changes_for_different_canonical_output():
    left = export_run_evidence(_run("same-input", "alpha"))
    right = export_run_evidence(_run("same-input", "beta"))

    assert left["evidence_digest"] != right["evidence_digest"]


def test_run_evidence_digest_changes_for_different_canonical_input():
    left = export_run_evidence(_run("input-alpha", "same-output"))
    right = export_run_evidence(_run("input-beta", "same-output"))

    assert left["receipt"]["execution_output_digests"] == right["receipt"]["execution_output_digests"]
    assert left["receipt"]["execution_producer_ids"] != right["receipt"]["execution_producer_ids"]
    assert left["evidence_digest"] != right["evidence_digest"]
