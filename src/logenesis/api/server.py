from __future__ import annotations

from fastapi import FastAPI

from logenesis.api.contracts import ConversationTurnRequest, ConversationTurnResponse
from logenesis.runtime.orchestrator import TurnOrchestrator

app = FastAPI(title="Logenesis 1.5 API")

orchestrator = TurnOrchestrator(
    ruleset={"blocked_keywords": ["forbidden"], "forbidden_memory_tags": ["speculative"]},
    routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
)


@app.post("/v1/conversation/turn", response_model=ConversationTurnResponse)
def conversation_turn(req: ConversationTurnRequest) -> ConversationTurnResponse:
    out = orchestrator.run_turn(req.conversation_id, req.text)
    return ConversationTurnResponse(
        conversation_id=req.conversation_id,
        answer=out["answer"],
        route=out["route"],
        abstain=out["abstain"],
        verification_score=out["score"],
    )
