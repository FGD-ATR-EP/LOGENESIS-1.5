"""Cross-run analytics for intent and coherence trend diagnosis."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunMetric:
    run_id: str
    intent_strength: float
    coherence_score: float


class CrossRunAnalyticsDashboard:
    """Compute trend summaries across runs without a UI dependency."""

    def summarize(self, metrics: list[RunMetric]) -> dict[str, float]:
        if not metrics:
            return {"avg_intent_strength": 0.0, "avg_coherence_score": 0.0}

        avg_intent = sum(item.intent_strength for item in metrics) / len(metrics)
        avg_coherence = sum(item.coherence_score for item in metrics) / len(metrics)
        return {
            "avg_intent_strength": round(avg_intent, 4),
            "avg_coherence_score": round(avg_coherence, 4),
        }
