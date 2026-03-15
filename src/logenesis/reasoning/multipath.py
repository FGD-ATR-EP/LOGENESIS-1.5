from __future__ import annotations

from logenesis.reasoning.search_controller import BoundedSearchController, SearchConfig
from logenesis.reasoning.thought_node import ThoughtNode
from logenesis.schemas.models import RoutePath


class MultiPathReasoner:
    def __init__(
        self,
        max_nodes: int = 8,
        risk_threshold: float = 0.7,
        branching_limit: int = 2,
        deliberative_only: bool = True,
        target_confidence: float = 0.82,
        max_stagnant_rounds: int = 3,
    ):
        self.controller = BoundedSearchController(
            SearchConfig(
                search_budget=max_nodes,
                risk_threshold=risk_threshold,
                branching_limit=branching_limit,
                deliberative_only=deliberative_only,
                target_confidence=target_confidence,
                max_stagnant_rounds=max_stagnant_rounds,
            )
        )
        self.max_nodes = max_nodes

    def run(self, hypothesis: str, enable: bool = True, route: RoutePath | str | None = None) -> tuple[ThoughtNode, list[ThoughtNode]]:
        return self.controller.run(hypothesis, enable=enable, route=route)

    def check_termination(self, explored_count: int, frontier: list[ThoughtNode]) -> bool:
        return explored_count >= self.max_nodes or not frontier
