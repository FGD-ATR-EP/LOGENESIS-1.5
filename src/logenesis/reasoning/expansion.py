from __future__ import annotations

from itertools import count

from logenesis.schemas.models import ThoughtNode

_counter = count(1)


def expand_node(node: ThoughtNode, branching_factor: int = 2) -> list[ThoughtNode]:
    return [
        ThoughtNode(
            node_id=f"n{next(_counter)}",
            parent_id=node.node_id,
            hypothesis=f"{node.hypothesis} -> option {i+1}",
            depth=node.depth + 1,
            local_score=max(0.1, node.local_score - 0.05),
            risk_score=min(1.0, node.risk_score + 0.05 * i),
            verification_result="pending",
        )
        for i in range(branching_factor)
    ]
