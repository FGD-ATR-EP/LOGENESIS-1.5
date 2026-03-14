from __future__ import annotations

from logenesis.schemas.models import ContextPacket, IntentFrame, RoutePath


class ReasoningRouter:
    def __init__(self, policy: dict):
        self.policy = policy

    def route(self, intent: IntentFrame, context: ContextPacket) -> RoutePath:
        risk_weight = self.policy.get("risk_weight", 0.5)
        unresolved_weight = self.policy.get("unresolved_weight", 0.1)
        score = len(intent.risk_flags) * risk_weight + len(context.unresolved_items) * unresolved_weight
        threshold = self.policy.get("deliberative_threshold", 1.0)
        return RoutePath.DELIBERATIVE if score >= threshold else RoutePath.FAST
