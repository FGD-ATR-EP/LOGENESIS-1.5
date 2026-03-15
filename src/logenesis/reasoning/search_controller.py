from __future__ import annotations

from logenesis.reasoning.backpropagation import backpropagate
from logenesis.reasoning.expansion import expand_node
from logenesis.reasoning.pruning import prune
from logenesis.reasoning.selection import select_node
from logenesis.reasoning.termination import should_terminate
from logenesis.schemas.models import ThoughtNode


class BoundedSearchController:
    def __init__(self, max_nodes: int = 10, max_depth: int = 3, risk_threshold: float = 0.7):
        self.max_nodes = max_nodes
        self.max_depth = max_depth
        self.risk_threshold = risk_threshold

    def run(self, hypothesis: str, enable: bool = True) -> tuple[ThoughtNode, list[ThoughtNode]]:
        root = ThoughtNode(node_id="root", hypothesis=hypothesis, local_score=0.7, aggregated_score=0.7)
        if not enable:
            root.terminal_status = "skipped"
            return root, []

        frontier: list[ThoughtNode] = [root]
        explored: list[ThoughtNode] = []

        while frontier:
            current = select_node(frontier)
            if current is None:
                break
            frontier.remove(current)
            current.visit_count += 1
            explored.append(current)
            max_depth_reached = current.depth >= self.max_depth
            if should_terminate(len(explored), len(frontier), self.max_nodes, max_depth_reached):
                break
            children = expand_node(current)
            for child in children:
                child.local_score = max(0.1, current.local_score - 0.1)
                child.verification_result = "soft_pass" if child.risk_score < 0.6 else "hard_fail"
            frontier.extend(prune(children, self.risk_threshold))

        root = backpropagate(root, explored)
        return root, explored
