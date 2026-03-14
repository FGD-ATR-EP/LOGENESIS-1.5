from logenesis.router.reasoning_router import ReasoningRouter
from logenesis.schemas.models import ContextPacket, IntentFrame, RoutePath


def test_fast_deep_path_routing():
    router = ReasoningRouter({"deliberative_threshold": 0.5, "risk_weight": 1.0, "unresolved_weight": 0.2})
    intent = IntentFrame(raw_text="medical question", normalized_intent="medical question", risk_flags=["high_stakes"])
    context = ContextPacket(conversation_id="c", active_topic="t", intent_summary="i")
    assert router.route(intent, context) == RoutePath.DELIBERATIVE
