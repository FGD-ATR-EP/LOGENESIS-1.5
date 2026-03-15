from __future__ import annotations

from typing import Iterable

from logenesis.schemas.models import MemoryRecord, TopicFrame


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
    ) -> list[MemoryRecord]:
        items: list[MemoryRecord] = []
        for rec in records:
            if rec.relevance < confidence_floor:
                continue
            if rec.pollution_risk > 0.5:
                continue
            record_topic = str(rec.payload.get("topic", "")).lower()
            if topic.active_topic.lower() not in record_topic and topic.active_topic.lower() not in rec.provenance.lower():
                continue
            if session_scope and rec.payload.get("session_scope") not in {None, session_scope}:
                continue
            age = max(0.0, now_ts - (rec.last_used_at or rec.created_at))
            if age > 60 * 60 * 24 * 30:
                continue
            items.append(rec)
        return sorted(items, key=lambda r: (r.relevance, r.reuse_likelihood), reverse=True)[:8]
