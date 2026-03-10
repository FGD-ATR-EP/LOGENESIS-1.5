"""Policy simulation sandbox for gate-rule A/B validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class PolicyVariant:
    name: str
    evaluator: Callable[[str], bool]


@dataclass(frozen=True)
class SimulationResult:
    policy_name: str
    allowed_count: int
    blocked_count: int
    allow_rate: float


class PolicySimulationSandbox:
    """Run policy variants on a shared scenario set before rollout."""

    def run(self, scenarios: list[str], policies: list[PolicyVariant]) -> tuple[SimulationResult, ...]:
        if not scenarios:
            return tuple()

        results: list[SimulationResult] = []
        for policy in policies:
            allowed_count = sum(1 for scenario in scenarios if policy.evaluator(scenario))
            blocked_count = len(scenarios) - allowed_count
            results.append(
                SimulationResult(
                    policy_name=policy.name,
                    allowed_count=allowed_count,
                    blocked_count=blocked_count,
                    allow_rate=allowed_count / len(scenarios),
                )
            )
        return tuple(results)
