from __future__ import annotations

from logenesis.schemas.models import ContextPacket


class ContextVerifier:
    def score(self, answer: str, context: ContextPacket) -> float:
        return 1.0 if context.active_topic.lower() in answer.lower() else 0.6
