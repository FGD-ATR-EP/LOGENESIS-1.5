"""Pangenes agent for intent generation and recursive self-improvement."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from logenesis.agents.validator_agent import ValidatorAgent
from logenesis.memory.gems_of_wisdom import GemsOfWisdomStorage


@dataclass
class PangenesAgent:
    """Agent that plans, validates, and learns from failed execution."""

    memory_storage: GemsOfWisdomStorage
    validator: ValidatorAgent = field(default_factory=ValidatorAgent)

    def create_intent(self, task_description: str) -> dict[str, Any]:
        _ = self.memory_storage.retrieve_active_context()
        intent_id = f"INTENT-{int(time.time())}"
        payload = {
            "summary": f"Draft content for '{task_description}'",
            "source_list": ["Blog A", "Research Paper Z"],
        }
        return {"intent_id": intent_id, "payload": payload}

    def execute_and_audit(self, intent_data: dict[str, Any]) -> dict[str, Any]:
        intent_id = str(intent_data["intent_id"])
        payload = dict(intent_data["payload"])

        feedback_event = self.validator.audit_action(intent_id, payload)
        if feedback_event["status"] == "FAILED":
            self.learn_from_violation(feedback_event)
        return feedback_event

    def learn_from_violation(self, event_data: dict[str, Any]) -> None:
        lesson = (
            f"GEP VIOLATION: Intent {event_data['intent_id']} failed Principle C "
            f"with score {event_data['violating_score']}. "
            f"Content: '{event_data['data_summary']}'. "
            "Need to verify sources more carefully."
        )
        self.memory_storage.add_gem(lesson)
