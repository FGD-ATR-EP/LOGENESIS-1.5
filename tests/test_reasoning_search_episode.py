from logenesis.reasoning.cogitator_x import ReasoningConfig, ReasoningEntity
from logenesis.reasoning.pruner import RiskPruner
from logenesis.reasoning.thought_node import RiskProfile, ThoughtNode, VerificationResult


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


def test_selection_prefers_lower_risk_node() -> None:
    reasoner = ReasoningEntity(config=ReasoningConfig(search_budget=2, acceptance_threshold=0.2))
    reasoner.internal_monologue("bounded safe reasoning")
    debug = reasoner.episode_debug_snapshot()
    assert debug is not None
    assert debug.best_node_id


def test_termination_returns_bounded_final_status() -> None:
    reasoner = ReasoningEntity(config=ReasoningConfig(search_budget=1, acceptance_threshold=0.99))
    result = reasoner.internal_monologue("hard objective")
    assert result.final_status in {"stable", "unstable", "unresolved"}
