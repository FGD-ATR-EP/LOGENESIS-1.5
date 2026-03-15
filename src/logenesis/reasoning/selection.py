from __future__ import annotations

from logenesis.reasoning.thought_node import ThoughtNode


def node_priority(node: ThoughtNode, verifier_weight: float = 0.6, risk_weight: float = 0.3) -> float:
    """Compute verifier-aware priority for frontier selection."""
    verifier_score = node.verification_result.total_score
    exploitation = node.aggregated_score
    exploration = 1.0 / (1 + node.visit_count)
    risk_penalty = node.risk_profile.total_risk * risk_weight
    return exploitation + verifier_weight * verifier_score + 0.1 * exploration - risk_penalty


def select_node(frontier: list[ThoughtNode]) -> ThoughtNode | None:
    if not frontier:
        return None
    return max(frontier, key=node_priority)
