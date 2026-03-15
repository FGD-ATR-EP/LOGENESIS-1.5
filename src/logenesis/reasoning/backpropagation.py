from __future__ import annotations

from logenesis.schemas.models import ThoughtNode


def backpropagate(root: ThoughtNode, explored: list[ThoughtNode]) -> ThoughtNode:
    if not explored:
        return root
    best = max(explored, key=lambda n: n.local_score - n.risk_score * 0.3)
    root.aggregated_score = best.local_score
    root.value_estimate = best.local_score
    root.visit_count += len(explored)
    root.terminal_status = "bounded_complete"
    return root
