"""Commit gate enforces single-writer memory commits."""
from __future__ import annotations

from dataclasses import dataclass

from logenesis.reasoning.thought_node import ThoughtNode


@dataclass(frozen=True)
class CommitDecision:
    allowed: bool
    reason: str


class CommitGate:
    """Single writer gate for long-term memory commit authorization."""

    def decide(self, node: ThoughtNode, final_status: str) -> CommitDecision:
        if final_status != "stable":
            return CommitDecision(False, "episode_not_stable")
        if node.terminal_status not in {"open", "solved"}:
            return CommitDecision(False, "terminal_state_not_commit_eligible")
        if not node.verification_result.valid_hard:
            return CommitDecision(False, "verification_hard_fail")
        if node.risk_profile.total_risk > 0.35:
            return CommitDecision(False, "risk_too_high")
        return CommitDecision(True, "allow")
