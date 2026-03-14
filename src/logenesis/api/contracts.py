from __future__ import annotations

from pydantic import BaseModel, Field


class ConversationTurnRequest(BaseModel):
    conversation_id: str
    text: str
    metadata: dict = Field(default_factory=dict)


class ConversationTurnResponse(BaseModel):
    conversation_id: str
    answer: str
    route: str
    abstain: bool
    verification_score: float
