from __future__ import annotations

from dataclasses import dataclass

from .search_episode import SearchEpisode
from .thought_node import ThoughtNode


@dataclass(frozen=True)
class TerminationPolicy:
    target_confidence: float = 0.82
    max_stagnant_rounds: int = 3

    def check(self, episode: SearchEpisode, best_node: ThoughtNode) -> str | None:
        """Map low-level stop reasons to public-safe final states."""
        reason = should_terminate(
            explored_count=episode.rounds_used,
            budget=episode.budget,
            score_history=episode.score_history,
            target_confidence=self.target_confidence,
            max_stagnant_rounds=self.max_stagnant_rounds,
        )
        if reason == "confidence_reached":
            return "stable"
        if reason in {"budget_exhausted", "stagnation"}:
            return "unstable"
        if best_node.terminal_status == "solved":
            return "stable"
        return None


def should_terminate(
    *,
    explored_count: int,
    budget: int,
    score_history: list[float],
    target_confidence: float,
    max_stagnant_rounds: int,
) -> str | None:
    if explored_count >= budget:
        return "budget_exhausted"
    if score_history and score_history[-1] >= target_confidence:
        return "confidence_reached"
    if len(score_history) >= max_stagnant_rounds:
        tail = score_history[-max_stagnant_rounds:]
        if max(tail) - min(tail) < 0.01:
            return "stagnation"
    return None
