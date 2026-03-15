from __future__ import annotations

from logenesis.schemas.models import DialogueLedger, TopicFrame


class DriftDetector:
    def detect(self, topic: TopicFrame, ledger: DialogueLedger, text: str = "") -> bool:
        if ledger.contradictions_detected:
            return True
        if len(topic.topic_stack) > 5:
            return True
        if topic.switch_count >= 3 and ledger.turn_index <= 6:
            return True

        normalized = text.lower().strip()
        if not normalized:
            return False

        stable_focus_terms = {topic.active_topic.lower()}
        if topic.return_anchor:
            stable_focus_terms.add(topic.return_anchor.lower())

        long_turn = len(normalized.split()) > 8
        has_focus_overlap = any(term and term in normalized for term in stable_focus_terms)
        return long_turn and not has_focus_overlap
