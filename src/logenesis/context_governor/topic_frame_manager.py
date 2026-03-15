from __future__ import annotations

from logenesis.schemas.models import DialogueLedger, TopicFrame


class TopicFrameManager:
    def __init__(self, max_stack_depth: int = 6):
        self.max_stack_depth = max_stack_depth

    def _build_anchor(self, topic: TopicFrame, ledger: DialogueLedger) -> str:
        unresolved = len(ledger.unresolved_items)
        contradictions = len(ledger.contradictions_detected)
        terms = ", ".join((topic.canonical_terms or [topic.active_topic])[:4])
        return f"topic={topic.active_topic};terms={terms};unresolved={unresolved};contradictions={contradictions}"

    def update(self, topic: TopicFrame, text: str, ledger: DialogueLedger | None = None) -> TopicFrame:
        lower = text.lower().strip()
        ledger = ledger or DialogueLedger()

        if lower.startswith("switch topic:"):
            new_topic = text.split(":", 1)[1].strip() or "general"
            topic.topic_stack.append(topic.active_topic)
            if len(topic.topic_stack) > self.max_stack_depth:
                topic.topic_stack = topic.topic_stack[-self.max_stack_depth :]
            topic.return_anchor = topic.active_topic
            topic.active_topic = new_topic
            topic.title = new_topic.title()
            topic.canonical_terms = [new_topic]
            topic.active_status = "active"
            topic.switch_count += 1
            topic.last_topic_change_turn = ledger.turn_index
            topic.return_guard_reason = None
            topic.contradictory_return_blocked = False
            topic.anchor_summary = self._build_anchor(topic, ledger)
            return topic

        if "return topic" in lower and topic.topic_stack:
            if ledger.contradictions_detected:
                topic.active_status = "needs_repair"
                topic.contradictory_return_blocked = True
                topic.return_guard_reason = "contradiction_detected"
                topic.anchor_summary = self._build_anchor(topic, ledger)
                return topic
            restored = topic.topic_stack.pop()
            topic.active_topic = restored
            topic.title = restored.title()
            topic.active_status = "active"
            topic.return_anchor = restored
            topic.last_topic_change_turn = ledger.turn_index
            topic.return_guard_reason = None
            topic.contradictory_return_blocked = False
            topic.anchor_summary = self._build_anchor(topic, ledger)
            return topic

        if lower:
            tokens = [tok for tok in lower.split() if len(tok) > 3][:6]
            topic.canonical_terms = sorted(set(topic.canonical_terms + tokens))[-12:]
            topic.anchor_summary = self._build_anchor(topic, ledger)
        return topic
