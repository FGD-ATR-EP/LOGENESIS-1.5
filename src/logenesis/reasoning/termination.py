from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TerminationPolicy:
    target_confidence: float = 0.7
    max_rounds_without_gain: int = 3

    def check(self, episode, best_node) -> str | None:
        if best_node.aggregated_score >= self.target_confidence and best_node.risk_profile.total_risk <= 0.5:
            return "stable"
        if len(episode.score_history) >= self.max_rounds_without_gain:
            tail = episode.score_history[-self.max_rounds_without_gain :]
            if max(tail) - min(tail) < 0.02:
                return "stalled"
        return None


def should_terminate(explored_count: int, frontier_size: int, max_nodes: int, max_depth_reached: bool) -> bool:
    return explored_count >= max_nodes or frontier_size == 0 or max_depth_reached
