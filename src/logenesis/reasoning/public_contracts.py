"""Public-safe output contracts that avoid exposing internal reasoning trees."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicReasoningResult:
    stable_summary: str
    confidence: float
    uncertainty_factors: tuple[str, ...]
    final_status: str
    risk: float
    termination_reason: str


@dataclass(frozen=True)
class InternalEpisodeDebug:
    episode_id: str
    node_count: int
    best_node_id: str
    frontier_size: int
