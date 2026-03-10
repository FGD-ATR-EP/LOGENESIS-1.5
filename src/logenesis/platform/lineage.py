"""State lineage graphing utilities."""
from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass(frozen=True)
class StateNode:
    """Graph node for a cognitive snapshot."""

    state_id: str
    timestamp: float
    coherence_score: float


class StateLineageGraph:
    """Track causality and replay paths across state snapshots."""

    def __init__(self) -> None:
        self._nodes: dict[str, StateNode] = {}
        self._children: dict[str, set[str]] = defaultdict(set)
        self._parents: dict[str, set[str]] = defaultdict(set)

    def add_node(self, node: StateNode) -> None:
        self._nodes[node.state_id] = node

    def add_edge(self, parent_state_id: str, child_state_id: str) -> None:
        self._children[parent_state_id].add(child_state_id)
        self._parents[child_state_id].add(parent_state_id)

    def trace_path(self, origin_state_id: str, target_state_id: str) -> tuple[str, ...]:
        queue: deque[tuple[str, tuple[str, ...]]] = deque([(origin_state_id, (origin_state_id,))])
        visited: set[str] = set()

        while queue:
            state_id, path = queue.popleft()
            if state_id == target_state_id:
                return path
            if state_id in visited:
                continue
            visited.add(state_id)
            for child in sorted(self._children.get(state_id, set())):
                queue.append((child, (*path, child)))

        return tuple()

    def causality_score(self, state_id: str) -> float:
        node = self._nodes[state_id]
        downstream_count = len(self._children.get(state_id, set()))
        return round(node.coherence_score * (1 + downstream_count / 10), 4)
