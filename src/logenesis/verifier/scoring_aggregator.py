from __future__ import annotations

from logenesis.schemas.models import VerificationResult


class ScoringAggregator:
    def aggregate(
        self,
        process: float,
        factual: float,
        context: float,
        commitment: float,
        abstain_threshold: float = 0.55,
    ) -> VerificationResult:
        aggregate = (process + factual + context + commitment) / 4.0
        failed = []
        if process < 0.5:
            failed.append("process")
        if factual < 0.5:
            failed.append("factual")
        if context < 0.5:
            failed.append("context")
        if commitment < 0.5:
            failed.append("commitment")
        return VerificationResult(
            process_score=process,
            factual_score=factual,
            context_score=context,
            commitment_score=commitment,
            aggregate_score=aggregate,
            failed_checks=failed,
            abstain=aggregate < abstain_threshold,
        )
