from logenesis.reasoning.cogitator_x import ReasoningConfig, ReasoningEntity
from logenesis.reasoning.pruner import RiskPruner
from logenesis.reasoning.search_episode import SearchEpisode
from logenesis.reasoning.thought_node import (
    CognitiveStateSnapshot,
    IntentFrame,
    RiskProfile,
    ThoughtNode,
    VerificationResult,
)


def test_episode_remains_bounded_by_budget() -> None:
    reasoner = ReasoningEntity(config=ReasoningConfig(search_budget=3, acceptance_threshold=0.3))
    result = reasoner.internal_monologue("Design a safe rollout plan")

    assert result.explored_steps <= 3


def test_hard_failures_are_pruned() -> None:
    node = ThoughtNode(
        node_id="n1",
        parent_id="root",
        state_snapshot_id="s1",
        content="unsafe",
        action_type="verify",
        depth=1,
        local_score=0.1,
        aggregated_score=0.2,
        verification_result=VerificationResult(
            valid_hard=False,
            process_score=0.1,
            truthfulness_score=0.1,
            coherence_score=0.1,
            constraint_score=0.1,
            detected_failure_modes=("policy_violation",),
        ),
        risk_profile=RiskProfile(0.8, 0.8, 0.8, 0.8, 0.8, 0.8),
    )

    pruned = RiskPruner().assess(node)
    assert pruned.terminal_status == "pruned"
    assert pruned.aggregated_score == 0.0


def test_append_only_tree_rejects_node_rewrite() -> None:
    root = ThoughtNode(
        node_id="root",
        parent_id=None,
        state_snapshot_id="s0",
        content="goal",
        action_type="infer",
        depth=0,
        local_score=0.9,
        aggregated_score=0.8,
        verification_result=VerificationResult(True, 0.8, 0.8, 0.8, 0.8),
        risk_profile=RiskProfile(0.1, 0.1, 0.1, 0.1, 0.1, 0.1),
    )
    episode = SearchEpisode(
        episode_id="ep1",
        root_intent=IntentFrame("i1", "goal", (), ("ok",), "constitutional", 4, "normal"),
        root_state=CognitiveStateSnapshot("s0", (1.0,), 0.8, 0.2, 0.1, 0.8, 0.9, 0.2, "allow", 0.0),
        tree={"root": root},
        frontier=["root"],
        budget=4,
        best_node_id="root",
    )

    child = ThoughtNode(
        node_id="c1",
        parent_id="root",
        state_snapshot_id="s1",
        content="child",
        action_type="decompose",
        depth=1,
        local_score=0.7,
        aggregated_score=0.7,
        verification_result=VerificationResult(True, 0.7, 0.7, 0.7, 0.7),
        risk_profile=RiskProfile(0.1, 0.1, 0.1, 0.1, 0.1, 0.1),
    )
    episode.append_child("root", child)

    try:
        episode.append_child("root", child)
    except ValueError as exc:
        assert "append-only violation" in str(exc)
    else:
        raise AssertionError("Expected append-only guard to reject duplicate child")


def test_termination_returns_bounded_final_status() -> None:
    reasoner = ReasoningEntity(config=ReasoningConfig(search_budget=1, acceptance_threshold=0.99))
    result = reasoner.internal_monologue("hard objective")
    assert result.final_status in {"stable", "unstable", "unresolved"}


def test_rsi_lessons_are_post_episode_only() -> None:
    reasoner = ReasoningEntity(config=ReasoningConfig(search_budget=2, acceptance_threshold=0.2))
    reasoner.run_public_episode("unsafe_tool rollout")
    debug = reasoner.episode_debug_snapshot()

    assert debug is not None
    assert reasoner._last_episode is not None
    assert isinstance(reasoner._last_episode.rsi_lessons, list)
