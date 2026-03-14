"""Search episode container for append-only reasoning tree."""
from __future__ import annotations

from dataclasses import dataclass, field

from .thought_node import CognitiveStateSnapshot, IntentFrame, ThoughtNode


@dataclass
class SearchEpisode:
    episode_id: str
    root_intent: IntentFrame
    root_state: CognitiveStateSnapshot
    tree: dict[str, ThoughtNode]
    frontier: list[str]
    budget: int
    best_node_id: str
    best_stable_node_id: str | None = None
    final_status: str = "unresolved"
    rounds_used: int = 0
    stagnation_rounds: int = 0
    score_history: list[float] = field(default_factory=list)

    def budget_available(self) -> bool:
        return self.rounds_used < self.budget

    def append_child(self, parent_id: str, child: ThoughtNode) -> None:
        self.tree[child.node_id] = child
        self.tree[parent_id].child_ids.append(child.node_id)

    def mark_pruned(self, node_id: str) -> None:
        self.tree[node_id].terminal_status = "pruned"

    def mark_terminal(self, node_id: str, status: str) -> None:
        self.tree[node_id].terminal_status = status
