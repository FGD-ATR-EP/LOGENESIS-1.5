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
    topic_id: str = "general"
    user_constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    answer_mode: str = "concise"
    urgency_level: str = "normal"
    safety_class: str = "standard"


class TopicFrame(BaseModel):
    active_topic: str = "general"
    topic_stack: list[str] = Field(default_factory=list)
    return_anchor: str | None = None
    title: str = "General"
    scope: str = "conversation"
    included_subtopics: list[str] = Field(default_factory=list)
    excluded_subtopics: list[str] = Field(default_factory=list)
    canonical_terms: list[str] = Field(default_factory=list)
    active_status: str = "active"
    parent_topic_id: str | None = None
    anchor_summary: str = ""
    switch_count: int = 0
    contradictory_return_blocked: bool = False


class DialogueLedger(BaseModel):
    turn_index: int = 0
    confirmed_facts: list[str] = Field(default_factory=list)
    unverified_claims: list[str] = Field(default_factory=list)
    observed_claims: list[str] = Field(default_factory=list)
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
    current_phase: str = "input_received"
    open_decisions: list[str] = Field(default_factory=list)
    context_anchor_summary: str = ""
    transition_metadata: dict[str, Any] = Field(default_factory=dict)
    retrieval_metadata: dict[str, Any] = Field(default_factory=dict)
    verification_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextPacket(BaseModel):
    conversation_id: str
    active_topic: str
    intent_summary: str
    confirmed_facts: list[str] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    max_tokens_budget: int = 2048
    topic_focus_terms: list[str] = Field(default_factory=list)
    context_anchor_summary: str = ""
    drift_detected: bool = False
    retrieval_items: list[str] = Field(default_factory=list)
    retrieval_count: int = 0
    retrieval_policy_blocked: bool = False
    turn_window: int = 0
    excluded_prior_turns: int = 0
    packet_truncated: bool = False
    retrieval_filters_applied: dict[str, Any] = Field(default_factory=dict)


class ThoughtNode(BaseModel):
    node_id: str
    parent_id: str | None = None
    hypothesis: str
    risk_score: float = 0.0
    verified: bool = False
    score: float = 0.0
    depth: int = 0
    local_score: float = 0.0
    aggregated_score: float = 0.0
    verification_result: str = "unchecked"
    risk_profile: dict[str, float] = Field(default_factory=dict)
    visit_count: int = 0
    value_estimate: float = 0.0
    terminal_status: str = "open"


class VerificationResult(BaseModel):
    process_score: float = 1.0
    factual_score: float = 1.0
    context_score: float = 1.0
    commitment_score: float = 1.0
    aggregate_score: float = 1.0
    failed_checks: list[str] = Field(default_factory=list)
    abstain: bool = False
    valid_hard: bool = True
    soft_fail: bool = False
    detected_failure_modes: list[str] = Field(default_factory=list)
    uncertainty_factors: list[str] = Field(default_factory=list)
    uncertainty_score: float = 0.0
    abstain_threshold_used: float = 0.6
    step_scores: dict[str, float] = Field(default_factory=dict)


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
    confidence: float = 0.5
    relevance: float = 0.5
    reuse_likelihood: float = 0.5
    stability: float = 0.5
    pollution_risk: float = 0.0
    policy_approved: bool = False
    constitution_allowed: bool = False
    created_at: float = 0.0
    last_used_at: float = 0.0
    decay_state: str = "fresh"
    lineage_ref: str | None = None
    commit_candidate: bool = True
    blocked_reasons: list[str] = Field(default_factory=list)


class EpisodicEvent(BaseModel):
    conversation_id: str
    turn_id: str
    event_type: str
    summary: str
    significant: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryImportanceWeights(BaseModel):
    confidence_weight: float = 0.25
    relevance_weight: float = 0.25
    reuse_weight: float = 0.2
    stability_weight: float = 0.2
    pollution_weight: float = 0.1


class MemoryPolicyDecision(BaseModel):
    importance_score: float = 0.0
    verified: bool = False
    stable: bool = False
    policy_approved: bool = False
    constitution_allowed: bool = False
    pollution_risk_bounded: bool = False
    allowed: bool = False
    reasons: list[str] = Field(default_factory=list)
