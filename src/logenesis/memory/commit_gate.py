from __future__ import annotations

from logenesis.constitution.constitution_engine import ConstitutionEngine
from logenesis.schemas.models import MemoryImportanceWeights, MemoryPolicyDecision, MemoryRecord


class CommitGate:
    def __init__(self, constitution: ConstitutionEngine, min_score: float = 0.75, weights: MemoryImportanceWeights | None = None):
        self.constitution = constitution
        self.min_score = min_score
        self.weights = weights or MemoryImportanceWeights()

    def importance(self, record: MemoryRecord) -> float:
        score = (
            self.weights.confidence_weight * record.confidence
            + self.weights.relevance_weight * record.relevance
            + self.weights.reuse_weight * record.reuse_likelihood
            + self.weights.stability_weight * record.stability
            - self.weights.pollution_weight * record.pollution_risk
        )
        return max(0.0, min(1.0, score))

    def evaluate_policy(self, record: MemoryRecord, verification_score: float, policy: dict) -> MemoryPolicyDecision:
        reasons: list[str] = []

        verified = bool(record.verified and verification_score >= self.min_score)
        if not verified:
            reasons.append("verification_failed")

        stable = bool(record.stable and record.stability >= policy.get("stability_threshold", 0.7))
        if not stable:
            reasons.append("stability_failed")

        policy_approved = bool(policy.get("allow_long_term_write", False) or record.tier.value == "working")
        if not policy_approved:
            reasons.append("policy_long_term_write_denied")

        constitution_decision = self.constitution.evaluate_commit(record.policy_tags)
        constitution_allowed = constitution_decision.allowed
        if not constitution_allowed:
            reasons.extend(constitution_decision.reasons or ["constitution_denied"])

        has_contradiction = bool(record.payload.get("has_unresolved_contradiction", False))
        if has_contradiction:
            reasons.append("unresolved_contradiction")

        pollution_limit = policy.get("max_pollution_risk", 0.45)
        pollution_risk_bounded = record.pollution_risk <= pollution_limit
        if not pollution_risk_bounded:
            reasons.append("pollution_risk_too_high")

        importance_score = self.importance(record)
        threshold = policy.get("importance_threshold", 0.6)
        if importance_score < threshold:
            reasons.append("importance_below_threshold")

        allowed = (
            verified
            and stable
            and policy_approved
            and constitution_allowed
            and pollution_risk_bounded
            and not has_contradiction
            and importance_score >= threshold
        )

        return MemoryPolicyDecision(
            importance_score=importance_score,
            verified=verified,
            stable=stable,
            policy_approved=policy_approved,
            constitution_allowed=constitution_allowed,
            pollution_risk_bounded=pollution_risk_bounded,
            allowed=allowed,
            reasons=reasons,
        )

    def can_commit(self, record: MemoryRecord, verification_score: float, policy: dict) -> bool:
        return self.evaluate_policy(record, verification_score, policy).allowed
