from __future__ import annotations

from logenesis.constitution.constitution_engine import ConstitutionEngine
from logenesis.schemas.models import MemoryRecord


class CommitGate:
    def __init__(self, constitution: ConstitutionEngine, min_score: float = 0.75):
        self.constitution = constitution
        self.min_score = min_score

    def can_commit(self, record: MemoryRecord, verification_score: float, policy: dict) -> bool:
        if not (record.verified and record.stable):
            return False
        if verification_score < self.min_score:
            return False
        if record.tier.value in {"episodic", "semantic"} and not policy.get("allow_long_term_write", False):
            return False
        decision = self.constitution.evaluate_commit(record.policy_tags)
        return decision.allowed
