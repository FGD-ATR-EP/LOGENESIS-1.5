from __future__ import annotations

import re

from logenesis.schemas.models import VerificationResult


class ResponsePlanner:
    def _sanitize(self, text: str) -> str:
        blocked_fragments = [
            "hidden_trace",
            "chain-of-thought",
            "internal reasoning",
            "scratchpad",
            "deliberation tree",
        ]
        cleaned = text
        for frag in blocked_fragments:
            cleaned = cleaned.replace(frag, "")
        return re.sub(r"\s+", " ", cleaned).strip()

    def render(self, model_output: str, verification: VerificationResult) -> str:
        if verification.abstain or not verification.valid_hard:
            reasons = ", ".join(verification.uncertainty_factors[:3]) or "insufficiently verified evidence"
            return (
                "I’m abstaining from a definitive answer because the current evidence is not verified enough "
                f"({reasons}). If you want, I can provide a narrower, explicitly qualified response."
            )

        sanitized = self._sanitize(model_output)
        rationale = "Verified through process/factual/context/commitment checks."

        if verification.aggregate_score < 0.75 or verification.soft_fail:
            factors = ", ".join(verification.uncertainty_factors[:2]) or "limited verification coverage"
            return (
                f"{sanitized}\n\n"
                f"Public rationale: {rationale}\n"
                f"Uncertainty: {factors}.\n"
                f"Confidence: moderate ({verification.aggregate_score:.2f})."
            )

        return f"{sanitized}\n\nPublic rationale: {rationale}\nConfidence: high ({verification.aggregate_score:.2f})."
