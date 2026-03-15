from __future__ import annotations

from typing import Iterable

from logenesis.schemas.models import MemoryRecord, RetrievalPolicy, TopicFrame


class RetrievalGate:
    def allowed(self, risk_flags: list[str], policy: dict) -> bool:
        if "high_stakes" in risk_flags:
            return policy.get("allow_high_stakes_retrieval", True)
        return True

    def query(
        self,
        records: Iterable[MemoryRecord],
        topic: TopicFrame,
        now_ts: float,
        confidence_floor: float = 0.6,
        session_scope: str | None = None,
        max_age_seconds: float = 60 * 60 * 24 * 30,
        packet_limit: int = 8,
        topic_scope: str | None = None,
        policy: RetrievalPolicy | None = None,
    ) -> list[MemoryRecord]:
        if policy is not None:
            confidence_floor = policy.confidence_floor
            max_age_seconds = policy.max_age_seconds
            packet_limit = policy.packet_limit
            session_scope = policy.session_scope if policy.session_scope is not None else session_scope
            topic_scope = policy.topic_scope if policy.topic_scope is not None else topic_scope

        focus_topic = (topic_scope or topic.active_topic).lower()
        focus_terms = {focus_topic, *(t.lower() for t in topic.canonical_terms)}
        items: list[MemoryRecord] = []
        for rec in records:
            if rec.relevance < confidence_floor or rec.confidence < confidence_floor:
                continue
            if rec.pollution_risk > 0.5:
                continue

            if session_scope and rec.payload.get("session_scope") not in {None, session_scope}:
                continue

            age = max(0.0, now_ts - (rec.last_used_at or rec.created_at))
            if age > max_age_seconds:
                continue

            record_topic = str(rec.payload.get("topic", "")).lower()
            if focus_topic and focus_topic != record_topic:
                continue
            provenance = rec.provenance.lower()
            if focus_terms and not any(term and (term in record_topic or term in provenance) for term in focus_terms):
                continue

            items.append(rec)

        return sorted(items, key=lambda r: (r.relevance, r.reuse_likelihood, r.confidence), reverse=True)[:packet_limit]
