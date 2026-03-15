from __future__ import annotations

from logenesis.schemas.models import ContextPacket, DialogueState, MemoryRecord


class ContextCompiler:
    def compile(
        self,
        state: DialogueState,
        constraints: list[str] | None = None,
        retrieval_records: list[MemoryRecord] | None = None,
        drift_detected: bool = False,
    ) -> ContextPacket:
        retrieval_records = retrieval_records or []
        anchor = state.context_anchor_summary or f"topic={state.topic.active_topic}; unresolved={len(state.ledger.unresolved_items)}"
        return ContextPacket(
            conversation_id=state.conversation_id,
            active_topic=state.topic.active_topic,
            intent_summary=state.intent.normalized_intent[:180],
            confirmed_facts=state.ledger.confirmed_facts[-6:],
            unresolved_items=state.ledger.unresolved_items[-6:],
            constraints=(constraints or [])[:10],
            max_tokens_budget=1536,
            topic_focus_terms=(state.topic.canonical_terms or [state.topic.active_topic])[:10],
            context_anchor_summary=anchor[:280],
            drift_detected=drift_detected,
            retrieval_items=[str(r.payload.get("summary", r.payload))[:120] for r in retrieval_records][:6],
        )
