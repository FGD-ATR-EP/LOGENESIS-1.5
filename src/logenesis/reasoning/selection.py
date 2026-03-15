from __future__ import annotations

from logenesis.schemas.models import ThoughtNode


def select_node(frontier: list[ThoughtNode]) -> ThoughtNode | None:
    if not frontier:
        return None
    return max(frontier, key=lambda n: (n.aggregated_score or n.local_score or n.score, -n.risk_score))
