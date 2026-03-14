from __future__ import annotations

from logenesis.schemas.models import TopicFrame


class TopicFrameManager:
    def update(self, topic: TopicFrame, text: str) -> TopicFrame:
        lower = text.lower()
        if lower.startswith("switch topic:"):
            new_topic = text.split(":", 1)[1].strip() or "general"
            topic.topic_stack.append(topic.active_topic)
            topic.return_anchor = topic.active_topic
            topic.active_topic = new_topic
        elif "return topic" in lower and topic.topic_stack:
            topic.active_topic = topic.topic_stack.pop()
        return topic
