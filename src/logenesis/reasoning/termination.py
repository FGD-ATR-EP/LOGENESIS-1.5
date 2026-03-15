from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TerminationPolicy:
    target_confidence: float = 0.82
    max_stagnant_rounds: int = 3


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
