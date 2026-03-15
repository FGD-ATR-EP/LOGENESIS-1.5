from __future__ import annotations

from logenesis.schemas.models import ContextPacket, ContextPolicy, DialogueState, MemoryRecord


class ContextCompiler:
    def compile(
        self,
        state: DialogueState,
        constraints: list[str] | None = None,
        retrieval_records: list[MemoryRecord] | None = None,
        drift_detected: bool = False,
        token_budget: int = 1536,
        max_confirmed_facts: int = 6,
        max_unresolved_items: int = 6,
        max_retrieval_items: int = 6,
        turn_window: int = 12,
        policy: ContextPolicy | None = None,
    ) -> ContextPacket:
        retrieval_records = retrieval_records or []
        constraints = constraints or []

        if policy is not None:
            token_budget = policy.token_budget
            max_confirmed_facts = policy.max_confirmed_facts
            max_unresolved_items = policy.max_unresolved_items
            max_retrieval_items = policy.max_retrieval_items
            turn_window = policy.turn_window

        anchor = state.topic.anchor_summary or state.context_anchor_summary or (
            f"topic={state.topic.active_topic}; unresolved={len(state.ledger.unresolved_items)}"
        )

        confirmed_facts = state.ledger.confirmed_facts[-max_confirmed_facts:]
        unresolved_items = state.ledger.unresolved_items[-max_unresolved_items:]
        retrieval_items = [str(r.payload.get("summary", r.payload))[:140] for r in retrieval_records][:max_retrieval_items]

        included_turns = min(state.ledger.turn_index, turn_window)
        excluded_turns = max(0, state.ledger.turn_index - included_turns)

        packet = ContextPacket(
            conversation_id=state.conversation_id,
            active_topic=state.topic.active_topic,
            intent_summary=state.intent.normalized_intent[:220],
            confirmed_facts=confirmed_facts,
            unresolved_items=unresolved_items,
            constraints=constraints[:10],
            max_tokens_budget=token_budget,
            topic_focus_terms=(state.topic.canonical_terms or [state.topic.active_topic])[:12],
            context_anchor_summary=anchor[:320],
            drift_detected=drift_detected,
            retrieval_items=retrieval_items,
            turn_window=included_turns,
            excluded_prior_turns=excluded_turns,
            packet_truncated=excluded_turns > 0,
            ledger_turn_index=state.ledger.turn_index,
            contradiction_count=len(state.ledger.contradictions_detected),
            includes_raw_transcript=False,
            retrieval_filters_applied={
                "topic": state.topic.active_topic,
                "session_scope": state.conversation_id,
                "confidence_floor": 0.6,
                "turn_window": turn_window,
            },
        )
        return packet
