from logenesis.context_governor.topic_frame_manager import TopicFrameManager
from logenesis.schemas.models import TopicFrame

manager = TopicFrameManager()
topic = TopicFrame(active_topic="planning")
topic = manager.update(topic, "switch topic: budget")
topic = manager.update(topic, "return topic")
print(topic.model_dump())
