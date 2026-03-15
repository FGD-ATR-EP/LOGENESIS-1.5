from __future__ import annotations

from logenesis.schemas.models import ContextPacket


class ContextVerifier:
    def score(self, answer: str, context: ContextPacket) -> tuple[float, list[str]]:
        factors: list[str] = []
        lower_answer = answer.lower()

        topic_hit = context.active_topic.lower() in lower_answer
        if not topic_hit:
            factors.append("topic_mismatch")

        if context.drift_detected:
            factors.append("context_drift_detected")

        if context.packet_truncated and not context.context_anchor_summary:
            factors.append("missing_context_anchor")

        base = 1.0 if topic_hit else 0.55
        if context.drift_detected:
            base -= 0.2
        if context.packet_truncated:
            base -= 0.05
        return max(0.0, base), factors
