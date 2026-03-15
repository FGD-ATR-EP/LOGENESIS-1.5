from __future__ import annotations

from logenesis.reasoning.search_controller import BoundedSearchController
from logenesis.schemas.models import ThoughtNode


class MultiPathReasoner:
    def __init__(self, max_nodes: int = 8, risk_threshold: float = 0.7):
        self.controller = BoundedSearchController(max_nodes=max_nodes, risk_threshold=risk_threshold)
        self.max_nodes = max_nodes
        self.risk_threshold = risk_threshold

    def run(self, hypothesis: str, enable: bool = True) -> tuple[ThoughtNode, list[ThoughtNode]]:
        return self.controller.run(hypothesis, enable=enable)

    # backward compatible helper methods used by tests/legacy code
    def check_termination(self, explored_count: int, frontier: list[ThoughtNode]) -> bool:
        return explored_count >= self.max_nodes or not frontier
