from __future__ import annotations

from itertools import count

from logenesis.schemas.models import ThoughtNode


class MultiPathReasoner:
    def __init__(self, max_nodes: int = 8, risk_threshold: float = 0.7):
        self.max_nodes = max_nodes
        self.risk_threshold = risk_threshold
        self._id = count(1)

    def select_node(self, frontier: list[ThoughtNode]) -> ThoughtNode | None:
        return max(frontier, key=lambda n: n.score, default=None)

    def expand_node(self, node: ThoughtNode) -> list[ThoughtNode]:
        children = [
            ThoughtNode(node_id=f"n{next(self._id)}", parent_id=node.node_id, hypothesis=f"{node.hypothesis} :: branch {i}")
            for i in range(2)
        ]
        return children

    def verify_children(self, children: list[ThoughtNode]) -> list[ThoughtNode]:
        for c in children:
            c.verified = True
            c.score = 0.6
            c.risk_score = 0.4
        return children

    def prune_by_risk(self, nodes: list[ThoughtNode]) -> list[ThoughtNode]:
        return [n for n in nodes if n.risk_score <= self.risk_threshold]

    def backpropagate(self, root: ThoughtNode, candidates: list[ThoughtNode]) -> ThoughtNode:
        if candidates:
            root.score = max(c.score for c in candidates)
        return root

    def check_termination(self, explored_count: int, frontier: list[ThoughtNode]) -> bool:
        return explored_count >= self.max_nodes or not frontier
