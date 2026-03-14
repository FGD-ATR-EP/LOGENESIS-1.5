"""Core reasoning entities for bounded multi-path search episodes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


TerminalStatus = Literal["open", "solved", "invalid", "pruned", "stalled"]
ActionType = Literal[
    "infer",
    "decompose",
    "verify",
    "simulate",
    "conclude",
    "alternative_hypothesis",
    "constraint_repair",
    "evidence_check",
    "simulation",
    "synthesis",
]


@dataclass(frozen=True)
class IntentFrame:
    intent_id: str
    normalized_goal: str
    constraints: tuple[str, ...]
    success_criteria: tuple[str, ...]
    safety_class: str
    resource_budget: int
    temporal_priority: str


@dataclass(frozen=True)
class CognitiveStateSnapshot:
    state_id: str
    intent_vector: tuple[float, ...]
    coherence: float
    entropy: float
    inertia: float
    activation_potential: float
    stability: float
    load: float
    gate_status: str
    timestamp: float


@dataclass(frozen=True)
class VerificationResult:
    valid_hard: bool
    process_score: float
    truthfulness_score: float
    coherence_score: float
    constraint_score: float
    detected_failure_modes: tuple[str, ...] = ()
    uncertainty_factors: tuple[str, ...] = ()

    @property
    def total_score(self) -> float:
        return (self.process_score + self.truthfulness_score + self.coherence_score + self.constraint_score) / 4


@dataclass(frozen=True)
class RiskProfile:
    rsi_risk: float
    hallucination_risk: float
    tool_misuse_risk: float
    loop_risk: float
    memory_pollution_risk: float
    total_risk: float


@dataclass
class ThoughtNode:
    node_id: str
    parent_id: str | None
    state_snapshot_id: str
    content: str
    action_type: ActionType
    depth: int
    local_score: float
    aggregated_score: float
    verification_result: VerificationResult
    risk_profile: RiskProfile
    visit_count: int = 0
    value_estimate: float = 0.0
    expansion_count: int = 0
    terminal_status: TerminalStatus = "open"
    commit_eligible: bool = False
    child_ids: list[str] = field(default_factory=list)

    def is_open(self) -> bool:
        return self.terminal_status == "open"
