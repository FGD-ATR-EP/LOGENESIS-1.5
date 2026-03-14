from __future__ import annotations

from logenesis.schemas.models import IntentFrame


class IntentNormalizer:
    def normalize(self, text: str) -> IntentFrame:
        task_type = "analysis" if "why" in text.lower() else "general"
        risks = ["high_stakes"] if any(k in text.lower() for k in ["medical", "legal", "finance"]) else []
        return IntentFrame(
            raw_text=text,
            normalized_intent=text.strip().lower(),
            task_type=task_type,
            risk_flags=risks,
            confidence=0.7 if text.strip() else 0.0,
        )
