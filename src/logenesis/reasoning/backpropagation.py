from __future__ import annotations

from logenesis.reasoning.thought_node import ThoughtNode


def backpropagate(root: ThoughtNode, explored: list[ThoughtNode]) -> ThoughtNode:
    if not explored:
        root.terminal_status = "stalled"
        root.commit_eligible = False
        return root

    best = max(explored, key=lambda n: n.aggregated_score * n.verification_result.total_score)
    root.value_estimate = best.aggregated_score
    root.aggregated_score = best.aggregated_score
    root.visit_count += len(explored)
    return root
