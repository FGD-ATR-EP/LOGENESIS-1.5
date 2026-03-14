"""PRM-style process-aware verifier for reasoning branches."""
from __future__ import annotations

from dataclasses import dataclass

from .thought_node import VerificationResult


CRITICAL_FAILURE_MODES = {
    "policy_violation",
    "impossible_constraint",
    "irreparable_contradiction",
    "critical_hallucination",
    "unsafe_tool_path",
}


@dataclass(frozen=True)
class VerificationWeights:
    process: float = 0.30
    truthfulness: float = 0.25
    coherence: float = 0.20
    gate_compatibility: float = 0.25


class VerificationPolicy:
    """Score reasoning content with hard-fail and soft-fail semantics."""

    def __init__(self, weights: VerificationWeights | None = None) -> None:
        self._weights = weights or VerificationWeights()

    def verify(self, content: str, gate_allowed: bool, constraints: tuple[str, ...]) -> VerificationResult:
        normalized = content.lower()
        failures: list[str] = []
        uncertainty: list[str] = []

        if "policy_violation" in normalized or "bypass gate" in normalized:
            failures.append("policy_violation")
        if "unsafe_tool" in normalized or "run shell" in normalized:
            failures.append("unsafe_tool_path")
        if "hallucinate" in normalized:
            failures.append("critical_hallucination")
        if "impossible" in normalized:
            failures.append("impossible_constraint")
        if "contradiction" in normalized and "repair" not in normalized:
            failures.append("irreparable_contradiction")

        process_score = 0.9 if any(k in normalized for k in ("evidence", "verify", "constraint", "simulate")) else 0.55
        truthfulness_score = 0.9 if "evidence" in normalized else 0.6
        coherence_score = 0.85 if "contradiction" not in normalized else 0.35
        constraint_score = 0.85 if constraints else 0.7

        if "uncertain" in normalized or "maybe" in normalized or "guess" in normalized:
            uncertainty.append("insufficient_evidence")
            process_score -= 0.15
            truthfulness_score -= 0.15

        process_score = _clamp(process_score)
        truthfulness_score = _clamp(truthfulness_score)
        coherence_score = _clamp(coherence_score)
        constraint_score = _clamp(constraint_score)

        gate_score = 1.0 if gate_allowed else 0.0
        valid_hard = gate_allowed and not any(mode in CRITICAL_FAILURE_MODES for mode in failures)
        if not gate_allowed and "policy_violation" not in failures:
            failures.append("policy_violation")

        weighted_score = (
            self._weights.process * process_score
            + self._weights.truthfulness * truthfulness_score
            + self._weights.coherence * coherence_score
            + self._weights.gate_compatibility * gate_score
        )

        if weighted_score < 0.45 and "low_prm_score" not in uncertainty:
            uncertainty.append("low_prm_score")

        return VerificationResult(
            valid_hard=valid_hard,
            process_score=process_score,
            truthfulness_score=truthfulness_score,
            coherence_score=coherence_score,
            constraint_score=constraint_score,
            detected_failure_modes=tuple(failures),
            uncertainty_factors=tuple(uncertainty),
        )


def _clamp(value: float) -> float:
    return max(0.0, min(value, 1.0))
