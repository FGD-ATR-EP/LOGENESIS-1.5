from logenesis.context_governor.topic_frame_manager import TopicFrameManager
from logenesis.schemas.models import DialogueLedger, TopicFrame


def test_topic_switch_and_safe_return_without_contradiction():
    mgr = TopicFrameManager()
    topic = TopicFrame(active_topic="alpha")

    topic = mgr.update(topic, "switch topic: beta", ledger=DialogueLedger(turn_index=2))
    assert topic.active_topic == "beta"
    assert topic.topic_stack == ["alpha"]
    assert "topic=beta" in topic.anchor_summary
    assert topic.last_topic_change_turn == 2

    topic = mgr.update(topic, "return topic", ledger=DialogueLedger(turn_index=3))
    assert topic.active_topic == "alpha"
    assert topic.active_status == "active"
    assert topic.contradictory_return_blocked is False
    assert topic.return_guard_reason is None


def test_topic_return_blocked_when_contradiction_detected():
    mgr = TopicFrameManager()
    topic = TopicFrame(active_topic="alpha", topic_stack=["root"])
    ledger = DialogueLedger(contradictions_detected=["x != y"])

    topic = mgr.update(topic, "return topic", ledger=ledger)

    assert topic.active_topic == "alpha"
    assert topic.active_status == "needs_repair"
    assert topic.contradictory_return_blocked is True
    assert topic.return_guard_reason == "contradiction_detected"
