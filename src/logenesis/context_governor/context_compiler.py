from __future__ import annotations

from logenesis.schemas.models import ContextPacket, DialogueState


class ContextCompiler:
    def compile(self, state: DialogueState, constraints: list[str] | None = None) -> ContextPacket:
        return ContextPacket(
            conversation_id=state.conversation_id,
            active_topic=state.topic.active_topic,
            intent_summary=state.intent.normalized_intent[:180],
            confirmed_facts=state.ledger.confirmed_facts[-10:],
            unresolved_items=state.ledger.unresolved_items[-10:],
            constraints=constraints or [],
            max_tokens_budget=2048,
        )
