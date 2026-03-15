from __future__ import annotations

from logenesis.schemas.models import ContextPacket


class ContextVerifier:
    def score(self, answer: str, context: ContextPacket) -> tuple[float, list[str]]:
        factors: list[str] = []
        topic_hit = context.active_topic.lower() in answer.lower()
        if not topic_hit:
            factors.append("topic_mismatch")
        if context.drift_detected:
            factors.append("context_drift_detected")
        base = 1.0 if topic_hit else 0.55
        if context.drift_detected:
            base -= 0.2
        return max(0.0, base), factors
