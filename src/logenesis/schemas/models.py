from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RoutePath(str, Enum):
    FAST = "fast"
    DELIBERATIVE = "deliberative"


class IntentFrame(BaseModel):
    raw_text: str
    normalized_intent: str
    task_type: str = "general"
    risk_flags: list[str] = Field(default_factory=list)
    confidence: float = 0.5


class TopicFrame(BaseModel):
    active_topic: str = "general"
    topic_stack: list[str] = Field(default_factory=list)
    return_anchor: str | None = None


class DialogueLedger(BaseModel):
    confirmed_facts: list[str] = Field(default_factory=list)
    unverified_claims: list[str] = Field(default_factory=list)
    commitments_made: list[str] = Field(default_factory=list)
    commitments_revoked: list[str] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)
    contradictions_detected: list[str] = Field(default_factory=list)


class DialogueState(BaseModel):
    conversation_id: str
    turn_id: str
    intent: IntentFrame
    topic: TopicFrame
    ledger: DialogueLedger
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextPacket(BaseModel):
    conversation_id: str
    active_topic: str
    intent_summary: str
    confirmed_facts: list[str] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    max_tokens_budget: int = 2048


class ThoughtNode(BaseModel):
    node_id: str
    parent_id: str | None = None
    hypothesis: str
    risk_score: float = 0.0
    verified: bool = False
    score: float = 0.0


class VerificationResult(BaseModel):
    process_score: float = 1.0
    factual_score: float = 1.0
    context_score: float = 1.0
    commitment_score: float = 1.0
    aggregate_score: float = 1.0
    failed_checks: list[str] = Field(default_factory=list)
    abstain: bool = False


class MemoryTier(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryRecord(BaseModel):
    memory_id: str
    tier: MemoryTier
    payload: dict[str, Any]
    provenance: str
    verified: bool = False
    stable: bool = False
    policy_tags: list[str] = Field(default_factory=list)
