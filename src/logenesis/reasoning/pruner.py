"""Risk-based pruning policies for search branches."""
from __future__ import annotations

from dataclasses import dataclass

from .thought_node import RiskProfile, ThoughtNode
from .verifier import CRITICAL_FAILURE_MODES


@dataclass(frozen=True)
class RiskPruner:
    critical_modes: tuple[str, ...] = tuple(sorted(CRITICAL_FAILURE_MODES))

    def assess(self, node: ThoughtNode) -> ThoughtNode:
        failures = set(node.verification_result.detected_failure_modes)
        if failures.intersection(self.critical_modes):
            node.terminal_status = "pruned"
            node.aggregated_score = 0.0
            return node

        severity = min(0.95, node.risk_profile.total_risk)
        if severity > 0.6:
            node.aggregated_score *= 1 - severity * 0.5
            node.value_estimate *= 1 - severity * 0.35
        return node

    def post_episode_lessons(self, nodes: list[ThoughtNode]) -> tuple[str, ...]:
        lessons: list[str] = []
        for node in nodes:
            if node.terminal_status != "pruned":
                continue
            if node.verification_result.detected_failure_modes:
                lessons.append(f"avoid:{','.join(node.verification_result.detected_failure_modes)}")
        return tuple(lessons)


def build_risk_profile(content: str, depth: int, uncertainty_count: int) -> RiskProfile:
    lowered = content.lower()
    hallucination = 0.75 if "hallucinate" in lowered else 0.15
    tool_misuse = 0.8 if "unsafe_tool" in lowered or "run shell" in lowered else 0.1
    loop = min(0.7, 0.1 + depth * 0.05)
    memory_pollution = min(0.8, uncertainty_count * 0.2)
    rsi = min(0.8, 0.15 + memory_pollution * 0.5)
    total = min(1.0, (hallucination + tool_misuse + loop + memory_pollution + rsi) / 5)
    return RiskProfile(
        rsi_risk=rsi,
        hallucination_risk=hallucination,
        tool_misuse_risk=tool_misuse,
        loop_risk=loop,
        memory_pollution_risk=memory_pollution,
        total_risk=total,
    )
