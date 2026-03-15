from __future__ import annotations

from logenesis.schemas.models import VerificationResult


class ResponsePlanner:
    def _sanitize(self, text: str) -> str:
        blocked_fragments = ["hidden_trace", "chain-of-thought", "internal reasoning", "scratchpad"]
        cleaned = text
        for frag in blocked_fragments:
            cleaned = cleaned.replace(frag, "")
        return cleaned.strip()

    def render(self, model_output: str, verification: VerificationResult) -> str:
        if verification.abstain or not verification.valid_hard:
            reasons = ", ".join(verification.uncertainty_factors[:3]) or "insufficiently verified evidence"
            return f"I'm not confident enough to provide a reliable final answer yet because of {reasons}. Please share more specifics or allow a narrower verified response."

        sanitized = self._sanitize(model_output)
        if verification.aggregate_score < 0.75 and verification.uncertainty_factors:
            return f"{sanitized}\n\nConfidence note: This answer has moderate confidence due to {', '.join(verification.uncertainty_factors[:2])}."
        return sanitized
