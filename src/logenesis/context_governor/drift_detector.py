from __future__ import annotations

from logenesis.schemas.models import DialogueLedger, TopicFrame


class DriftDetector:
    def detect(self, topic: TopicFrame, ledger: DialogueLedger, text: str = "") -> bool:
        if ledger.contradictions_detected:
            return True
        if len(topic.topic_stack) > 5:
            return True
        return bool(text and topic.active_topic not in text.lower() and len(text.split()) > 8)
