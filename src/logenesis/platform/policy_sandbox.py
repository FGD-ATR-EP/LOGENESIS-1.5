"""Policy simulation sandbox for gate-rule A/B validation."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PolicyVariant:
    name: str
    evaluator: Callable[[str], bool]


@dataclass(frozen=True)
class SimulationResult:
    policy_name: str
    allowed_count: int
    blocked_count: int
    errored_count: int
    allow_rate: float


class PolicySimulationSandbox:
    """Run policy variants on a shared scenario set before rollout."""

    def run(self, scenarios: list[str], policies: list[PolicyVariant]) -> tuple[SimulationResult, ...]:
        if not scenarios:
            return tuple()

        results: list[SimulationResult] = []
        for policy in policies:
            allowed_count = 0
            blocked_count = 0
            errored_count = 0

            for scenario in scenarios:
                try:
                    allowed = policy.evaluator(scenario)
                except Exception:
                    logger.exception(
                        "Policy evaluation failed for policy=%s scenario=%r",
                        policy.name,
                        scenario,
                    )
                    errored_count += 1
                    blocked_count += 1
                    continue

                if allowed:
                    allowed_count += 1
                else:
                    blocked_count += 1

            results.append(
                SimulationResult(
                    policy_name=policy.name,
                    allowed_count=allowed_count,
                    blocked_count=blocked_count,
                    errored_count=errored_count,
                    allow_rate=allowed_count / len(scenarios),
                )
            )
        return tuple(results)
