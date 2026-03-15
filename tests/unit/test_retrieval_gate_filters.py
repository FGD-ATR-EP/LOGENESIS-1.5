import time

from logenesis.context_governor.retrieval_gate import RetrievalGate
from logenesis.schemas.models import MemoryRecord, MemoryTier, RetrievalPolicy, TopicFrame


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
            confidence=0.95,
            relevance=0.9,
            reuse_likelihood=0.8,
            pollution_risk=0.1,
            created_at=now,
            last_used_at=now,
        ),
        MemoryRecord(
            memory_id="2",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "finance", "summary": "wrong session", "session_scope": "c2"},
            provenance="turn:c2",
            verified=True,
            stable=True,
            confidence=0.9,
            relevance=0.9,
            reuse_likelihood=0.7,
            pollution_risk=0.1,
            created_at=now,
            last_used_at=now,
        ),
        MemoryRecord(
            memory_id="3",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "sports", "summary": "topic mismatch", "session_scope": "c1"},
            provenance="turn:c1",
            verified=True,
            stable=True,
            confidence=0.9,
            relevance=0.9,
            reuse_likelihood=0.7,
            pollution_risk=0.1,
            created_at=now,
            last_used_at=now,
        ),
        MemoryRecord(
            memory_id="4",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "finance", "summary": "stale", "session_scope": "c1"},
            provenance="turn:c1",
            verified=True,
            stable=True,
            confidence=0.9,
            relevance=0.9,
            reuse_likelihood=0.3,
            pollution_risk=0.1,
            created_at=now - 60 * 60 * 24 * 60,
            last_used_at=now - 60 * 60 * 24 * 60,
        ),
        MemoryRecord(
            memory_id="5",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "finance", "summary": "low confidence", "session_scope": "c1"},
            provenance="turn:c1",
            verified=True,
            stable=True,
            confidence=0.4,
            relevance=0.4,
            reuse_likelihood=0.9,
            pollution_risk=0.1,
            created_at=now,
            last_used_at=now,
        ),
    ]
    out = RetrievalGate().query(recs, TopicFrame(active_topic="finance"), now_ts=now, session_scope="c1")
    assert [x.memory_id for x in out] == ["1"]


def test_retrieval_gate_respects_explicit_topic_scope_policy():
    now = time.time()
    recs = [
        MemoryRecord(
            memory_id="alpha",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "finance", "summary": "finance", "session_scope": "c1"},
            provenance="turn:c1",
            verified=True,
            stable=True,
            confidence=0.95,
            relevance=0.95,
            reuse_likelihood=0.5,
            pollution_risk=0.1,
            created_at=now,
            last_used_at=now,
        ),
        MemoryRecord(
            memory_id="beta",
            tier=MemoryTier.SEMANTIC,
            payload={"topic": "science", "summary": "science", "session_scope": "c1"},
            provenance="turn:c1",
            verified=True,
            stable=True,
            confidence=0.95,
            relevance=0.95,
            reuse_likelihood=0.5,
            pollution_risk=0.1,
            created_at=now,
            last_used_at=now,
        ),
    ]

    out = RetrievalGate().query(
        recs,
        TopicFrame(active_topic="finance", canonical_terms=["science"]),
        now_ts=now,
        session_scope="c1",
        policy=RetrievalPolicy(topic_scope="science", session_scope="c1"),
    )

    assert [x.memory_id for x in out] == ["beta"]
