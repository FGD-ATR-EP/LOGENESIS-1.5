"""Validation agent for auditing intents before execution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidatorAgent:
    """Simple policy validator that enforces source-backed payloads."""

    min_sources: int = 1

    def audit_action(self, intent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        sources = payload.get("source_list", [])
        summary = str(payload.get("summary", ""))
        score = 1.0 if isinstance(sources, list) and len(sources) >= self.min_sources else 0.25

        if score < 0.5:
            return {
                "intent_id": intent_id,
                "status": "FAILED",
                "violating_score": score,
                "data_summary": summary,
            }

        return {
            "intent_id": intent_id,
            "status": "PASSED",
            "score": score,
            "data_summary": summary,
        }
