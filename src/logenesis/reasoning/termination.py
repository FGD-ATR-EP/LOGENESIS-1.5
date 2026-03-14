"""Termination rules for bounded reasoning episodes."""
from __future__ import annotations

from dataclasses import dataclass

from .search_episode import SearchEpisode
from .thought_node import ThoughtNode


@dataclass(frozen=True)
class TerminationPolicy:
    target_confidence: float = 0.75
    risk_threshold: float = 0.35
    coherence_threshold: float = 0.65
    stagnation_epsilon: float = 0.01
    stagnation_window: int = 3

    def check(self, episode: SearchEpisode, node: ThoughtNode) -> str | None:
        if (
            node.aggregated_score >= self.target_confidence
            and node.risk_profile.total_risk <= self.risk_threshold
            and node.verification_result.coherence_score >= self.coherence_threshold
            and node.verification_result.valid_hard
        ):
            return "stable"

        if not episode.budget_available():
            return "unresolved"

        if len(episode.score_history) >= self.stagnation_window:
            window = episode.score_history[-self.stagnation_window :]
            if max(window) - min(window) < self.stagnation_epsilon:
                return "unstable"

        return None
