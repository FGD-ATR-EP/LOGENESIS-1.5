"""Public-safe output contracts that avoid exposing internal reasoning trees."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicReasoningResult:
    final_state: str
    best_node: str
    confidence: float
    risk: float
    uncertainty_factors: tuple[str, ...]
    termination_reason: str
    answer_summary: str


@dataclass(frozen=True)
class InternalEpisodeDebug:
    episode_id: str
    node_count: int
    best_node_id: str
    frontier_size: int
