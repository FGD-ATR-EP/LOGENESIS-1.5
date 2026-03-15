from __future__ import annotations

from logenesis.schemas.models import IntentFrame


class IntentNormalizer:
    def normalize(self, text: str, active_topic: str = "general") -> IntentFrame:
        lower = text.strip().lower()
        task_type = "analysis" if any(k in lower for k in ["why", "explain", "analyze"]) else "general"
        risks = ["high_stakes"] if any(k in lower for k in ["medical", "legal", "finance", "safety"]) else []
        constraints = ["no_cot_exposure", "verified_only"]
        answer_mode = "stepwise" if "step" in lower else "concise"
        urgency = "high" if any(k in lower for k in ["urgent", "asap", "now"]) else "normal"
        safety_class = "restricted" if risks else "standard"
        criteria = ["correctness", "safety"]
        if "cite" in lower:
            criteria.append("traceable")
        return IntentFrame(
            raw_text=text,
            normalized_intent=lower,
            task_type=task_type,
            risk_flags=risks,
            confidence=0.75 if lower else 0.0,
            topic_id=active_topic,
            user_constraints=constraints,
            success_criteria=criteria,
            answer_mode=answer_mode,
            urgency_level=urgency,
            safety_class=safety_class,
        )
