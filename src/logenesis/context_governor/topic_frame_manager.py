from __future__ import annotations

from logenesis.schemas.models import DialogueLedger, TopicFrame


class TopicFrameManager:
    def update(self, topic: TopicFrame, text: str, ledger: DialogueLedger | None = None) -> TopicFrame:
        lower = text.lower().strip()
        ledger = ledger or DialogueLedger()

        if lower.startswith("switch topic:"):
            new_topic = text.split(":", 1)[1].strip() or "general"
            topic.topic_stack.append(topic.active_topic)
            topic.return_anchor = topic.active_topic
            topic.active_topic = new_topic
            topic.title = new_topic.title()
            topic.canonical_terms = [new_topic]
            topic.active_status = "active"
            return topic

        if "return topic" in lower and topic.topic_stack:
            if ledger.contradictions_detected:
                topic.active_status = "needs_repair"
                return topic
            restored = topic.topic_stack.pop()
            topic.active_topic = restored
            topic.title = restored.title()
            topic.active_status = "active"
            topic.return_anchor = restored
            return topic

        if lower:
            tokens = [tok for tok in lower.split() if len(tok) > 3][:5]
            topic.canonical_terms = sorted(set(topic.canonical_terms + tokens))[-10:]
        return topic
