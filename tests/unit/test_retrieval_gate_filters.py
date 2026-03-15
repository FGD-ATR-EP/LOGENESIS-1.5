import time

from logenesis.context_governor.retrieval_gate import RetrievalGate
from logenesis.schemas.models import MemoryRecord, MemoryTier, TopicFrame


def test_retrieval_gate_topic_time_confidence_session_filters():
    now = time.time()
    recs = [
        MemoryRecord(
            memory_id="1",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "finance", "summary": "finance note", "session_scope": "c1"},
            provenance="turn:c1",
            verified=True,
            stable=True,
            relevance=0.9,
            reuse_likelihood=0.8,
            pollution_risk=0.1,
            created_at=now,
            last_used_at=now,
        ),
        MemoryRecord(
            memory_id="2",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "sports", "summary": "old", "session_scope": "c2"},
            provenance="turn:c2",
            verified=True,
            stable=True,
            relevance=0.4,
            reuse_likelihood=0.3,
            pollution_risk=0.1,
            created_at=now - 60 * 60 * 24 * 60,
            last_used_at=now - 60 * 60 * 24 * 60,
        ),
    ]
    out = RetrievalGate().query(recs, TopicFrame(active_topic="finance"), now_ts=now, session_scope="c1")
    assert len(out) == 1
    assert out[0].memory_id == "1"
