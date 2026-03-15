from __future__ import annotations

from logenesis.schemas.models import ThoughtNode


def prune(nodes: list[ThoughtNode], risk_threshold: float = 0.7) -> list[ThoughtNode]:
    return [n for n in nodes if n.risk_score <= risk_threshold and n.verification_result != "hard_fail"]
