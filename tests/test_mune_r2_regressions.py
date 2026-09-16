import pytest

from rezon.admission import AdmissionError, admit_execution_result
from rezon.episode import Episode, EpisodeInvariantError
from rezon.epistemics import Hyperrelation, Participant, Proposition, PropositionKind
from rezon.executors import ContradictionScannerExecutor
from rezon.nodes import ExecutionResult, NodeDescriptor
from rezon.receipts import FailureState, IndependenceMetadata
from rezon.runner import EpisodeRunner, RunnerNode
from rezon.visibility import VisibilityPolicy


def _p(pid, kind, producer=None):
    return Proposition(
        pid,
        "e1",
        kind,
        pid,
        producer_execution_id=producer,
    )


def test_retracted_dependency_cannot_be_resurrected_by_new_current_relation():
    episode = Episode("e1")
    episode.add_proposition(_p("p1", PropositionKind.CLAIM))
    episode.retract_proposition("p1", "stale")

    with pytest.raises(EpisodeInvariantError):
        episode.add_relation(
            Hyperrelation(
                "r1",
                "e1",
                "supports",
                (Participant("p1", "claim"),),
            )
        )


def test_admission_rejects_relation_against_retracted_dependency():
    episode = Episode("e1")
    episode.add_proposition(_p("p1", PropositionKind.CLAIM))
    episode.retract_proposition("p1", "stale")
    descriptor = NodeDescriptor("generator", (PropositionKind.CLAIM,))
    relation = Hyperrelation(
        "r1",
        "e1",
        "supports",
        (Participant("p1", "claim"),),
        producer_execution_id="x1",
    )

    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            descriptor,
            ExecutionResult(
                "x1",
                "generator",
                emitted_relations=(relation,),
            ),
        )


def test_blinded_scheduler_target_fails_closed_instead_of_clean_noop():
    episode = Episode("e1")
    episode.add_proposition(_p("a", PropositionKind.CLAIM))
    episode.add_proposition(_p("b", PropositionKind.CLAIM))
    episode.add_relation(
        Hyperrelation(
            "r1",
            "e1",
            "contradicts",
            (
                Participant("a", "left"),
                Participant("b", "right"),
            ),
        )
    )
    node = RunnerNode(
        NodeDescriptor(
            "contradiction_scanner",
            (PropositionKind.TEST_RESULT,),
        ),
        ContradictionScannerExecutor(),
        VisibilityPolicy(blind_ids=("b",)),
    )

    outcome = EpisodeRunner((node,), 2).run(episode, "t")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "visibility:contradiction_scanner:r1" in outcome.receipt.unresolved


def test_strong_independence_requires_known_model_and_provider():
    metadata = IndependenceMetadata(
        executor_id="x",
        prompt_lineage="p",
        context_lineage="c",
        saw_other_answer=False,
        independence_basis_refs=("policy:blind-hypotheses",),
    )

    assert not metadata.is_demonstrably_independent


def test_independence_metadata_cannot_override_visible_prior_hypothesis():
    class ShouldNotRun:
        def execute(self, *args):
            raise AssertionError("must fail before worker")

    episode = Episode("e1")
    episode.add_proposition(_p("h1", PropositionKind.HYPOTHESIS))
    independence = IndependenceMetadata(
        executor_id="x",
        model_id="m1",
        provider_id="p1",
        prompt_lineage="fresh",
        context_lineage="fresh",
        saw_other_answer=False,
        independence_basis_refs=("policy:blind-hypotheses",),
    )
    node = RunnerNode(
        NodeDescriptor(
            "echo_hypothesis",
            (PropositionKind.HYPOTHESIS,),
            independence_required=True,
        ),
        ShouldNotRun(),
        VisibilityPolicy(),
        independence,
    )

    outcome = EpisodeRunner((node,), 1).run(episode, "t")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "independence_exposure:echo_hypothesis" in outcome.receipt.unresolved


def test_noop_mandatory_verifier_is_not_clean_success():
    class NoopVerifier:
        def execute(self, view, episode_id):
            return ExecutionResult(view.execution_id, "verifier")

    episode = Episode("e1")
    node = RunnerNode(
        NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
        ),
        NoopVerifier(),
        VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), 1).run(episode, "t")

    assert FailureState.INSUFFICIENT_EVIDENCE in outcome.receipt.failures
    assert "verification:verifier" in outcome.receipt.unresolved


def test_visible_input_kind_must_match_descriptor_contract():
    class ShouldNotRun:
        def execute(self, *args):
            raise AssertionError("must fail before worker")

    episode = Episode("e1")
    episode.add_proposition(_p("h1", PropositionKind.HYPOTHESIS))
    node = RunnerNode(
        NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            accepted_input_kinds=(PropositionKind.OBSERVATION,),
            mandatory_verification=True,
        ),
        ShouldNotRun(),
        VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), 1).run(episode, "t")

    assert FailureState.CONTRACT_VIOLATION in outcome.receipt.failures
    assert "input_kind:verifier" in outcome.receipt.unresolved


def test_mandatory_verifier_can_explicitly_satisfy_postcondition():
    class Verifier:
        def execute(self, view, episode_id):
            return ExecutionResult(
                view.execution_id,
                "verifier",
                verification_satisfied=True,
            )

    episode = Episode("e1")
    node = RunnerNode(
        NodeDescriptor(
            "verifier",
            (PropositionKind.TEST_RESULT,),
            mandatory_verification=True,
        ),
        Verifier(),
        VisibilityPolicy(),
    )

    outcome = EpisodeRunner((node,), 1).run(episode, "t")

    assert outcome.receipt.failures == ()
    assert outcome.receipt.unresolved == ()


def test_invalidated_relation_cannot_be_used_as_new_current_dependency():
    episode = Episode("e1")
    episode.add_proposition(_p("p1", PropositionKind.CLAIM))
    episode.add_proposition(_p("p2", PropositionKind.CLAIM))
    episode.add_relation(
        Hyperrelation(
            "r-old",
            "e1",
            "supports",
            (
                Participant("p1", "premise"),
                Participant("p2", "claim"),
            ),
        )
    )
    episode.retract_proposition("p1", "stale")

    with pytest.raises(EpisodeInvariantError):
        episode.add_relation(
            Hyperrelation(
                "r-new",
                "e1",
                "supports",
                (
                    Participant("r-old", "premise"),
                    Participant("p2", "claim"),
                ),
            )
        )


def test_worker_proposition_requires_exact_producer_execution_id():
    episode = Episode("e1")
    descriptor = NodeDescriptor("generator", (PropositionKind.HYPOTHESIS,))
    proposition = Proposition("h-no-producer", "e1", PropositionKind.HYPOTHESIS, "guess")
    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            descriptor,
            ExecutionResult("x1", "generator", emitted_propositions=(proposition,)),
            expected_execution_id="x1",
        )


def test_worker_relation_requires_exact_producer_execution_id():
    episode = Episode("e1")
    episode.add_proposition(_p("p1", PropositionKind.CLAIM))
    descriptor = NodeDescriptor("generator", (PropositionKind.CLAIM,))
    relation = Hyperrelation(
        "r-no-producer",
        "e1",
        "supports",
        (Participant("p1", "claim"),),
    )
    with pytest.raises(AdmissionError):
        admit_execution_result(
            episode,
            descriptor,
            ExecutionResult("x1", "generator", emitted_relations=(relation,)),
            expected_execution_id="x1",
        )


def test_same_executor_cannot_claim_pairwise_independence():
    left = IndependenceMetadata(
        executor_id="same",
        model_id="m1",
        provider_id="p1",
        prompt_lineage="prompt-a",
        context_lineage="context-a",
        saw_other_answer=False,
        independence_basis_refs=("policy:left",),
    )
    right = IndependenceMetadata(
        executor_id="same",
        model_id="m2",
        provider_id="p2",
        prompt_lineage="prompt-b",
        context_lineage="context-b",
        saw_other_answer=False,
        independence_basis_refs=("policy:right",),
    )

    assert not left.demonstrably_independent_from(right)
