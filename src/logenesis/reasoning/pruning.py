from __future__ import annotations

from logenesis.reasoning.thought_node import ThoughtNode


def prune_nodes(nodes: list[ThoughtNode], *, risk_threshold: float) -> tuple[list[ThoughtNode], list[ThoughtNode]]:
    """Risk-aware pruning. Hard-invalid and high-risk nodes are removed."""
    kept: list[ThoughtNode] = []
    pruned: list[ThoughtNode] = []

    for node in nodes:
        hard_invalid = not node.verification_result.valid_hard
        too_risky = node.risk_profile.total_risk > risk_threshold
        if hard_invalid or too_risky:
            node.terminal_status = "pruned"
            node.commit_eligible = False
            node.aggregated_score = 0.0
            pruned.append(node)
            continue
        kept.append(node)
    return kept, pruned
