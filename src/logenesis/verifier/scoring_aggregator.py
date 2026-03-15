from __future__ import annotations

from logenesis.schemas.models import VerificationResult


class ScoringAggregator:
    def __init__(self, weights: dict[str, float] | None = None, abstain_threshold: float = 0.6):
        self.weights = weights or {"process": 0.35, "factual": 0.25, "context": 0.2, "commitment": 0.2}
        self.abstain_threshold = abstain_threshold

    def aggregate(
        self,
        process: tuple[float, list[str], bool],
        factual: tuple[float, list[str]],
        context: tuple[float, list[str]],
        commitment: tuple[float, list[str]],
    ) -> VerificationResult:
        process_score, process_modes, valid_hard = process
        factual_score, factual_factors = factual
        context_score, context_factors = context
        commitment_score, commitment_factors = commitment

        aggregate = (
            process_score * self.weights["process"]
            + factual_score * self.weights["factual"]
            + context_score * self.weights["context"]
            + commitment_score * self.weights["commitment"]
        )

        failure_modes = process_modes + [f"factual:{x}" for x in factual_factors] + [f"context:{x}" for x in context_factors] + [f"commitment:{x}" for x in commitment_factors]
        failed_checks = [m.split(":", 1)[0] for m in failure_modes]
        uncertainty = factual_factors + context_factors + commitment_factors

        abstain = (not valid_hard) or (aggregate < self.abstain_threshold)
        return VerificationResult(
            process_score=process_score,
            factual_score=factual_score,
            context_score=context_score,
            commitment_score=commitment_score,
            aggregate_score=aggregate,
            failed_checks=failed_checks,
            abstain=abstain,
            valid_hard=valid_hard,
            detected_failure_modes=failure_modes,
            uncertainty_factors=uncertainty,
        )
