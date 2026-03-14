from __future__ import annotations

from logenesis.schemas.models import VerificationResult


class ResponsePlanner:
    def render(self, model_output: str, verification: VerificationResult) -> str:
        if verification.abstain:
            return "I’m not confident enough to answer reliably. Please provide more detail or let me verify further."
        return model_output.replace("hidden_trace", "")
