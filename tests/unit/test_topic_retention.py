from logenesis.context_governor.topic_frame_manager import TopicFrameManager
from logenesis.schemas.models import TopicFrame


def test_topic_switch_and_return():
    mgr = TopicFrameManager()
    topic = TopicFrame(active_topic="alpha")
    topic = mgr.update(topic, "switch topic: beta")
    assert topic.active_topic == "beta"
    topic = mgr.update(topic, "return topic")
    assert topic.active_topic == "alpha"
