from __future__ import annotations

from logenesis.schemas.models import DialogueLedger, TopicFrame


class DriftDetector:
    def detect(self, topic: TopicFrame, ledger: DialogueLedger) -> bool:
        return bool(ledger.contradictions_detected) or len(topic.topic_stack) > 5
