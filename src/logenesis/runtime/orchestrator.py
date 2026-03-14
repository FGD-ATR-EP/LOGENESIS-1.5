from __future__ import annotations

from uuid import uuid4

from logenesis.constitution.checker import ConstitutionChecker
from logenesis.constitution.constitution_engine import ConstitutionEngine
from logenesis.context_governor.context_compiler import ContextCompiler
from logenesis.context_governor.intent_normalizer import IntentNormalizer
from logenesis.context_governor.topic_frame_manager import TopicFrameManager
from logenesis.ledger.dialogue_ledger import DialogueLedgerService
from logenesis.llm_core.providers import LLMProvider, MockProvider
from logenesis.router.reasoning_router import ReasoningRouter
from logenesis.schemas.models import DialogueLedger, DialogueState, RoutePath, TopicFrame
from logenesis.verifier.commitment_verifier import CommitmentVerifier
from logenesis.verifier.context_verifier import ContextVerifier
from logenesis.verifier.factual_verifier import FactualVerifier
from logenesis.verifier.process_verifier import ProcessVerifier
from logenesis.verifier.scoring_aggregator import ScoringAggregator
from logenesis.response.response_planner import ResponsePlanner


class TurnOrchestrator:
    def __init__(self, ruleset: dict, routing_policy: dict, provider: LLMProvider | None = None):
        self.constitution = ConstitutionEngine(ConstitutionChecker(ruleset))
        self.intent_normalizer = IntentNormalizer()
        self.topic_manager = TopicFrameManager()
        self.context_compiler = ContextCompiler()
        self.router = ReasoningRouter(routing_policy)
        self.provider = provider or MockProvider()
        self.process_verifier = ProcessVerifier()
        self.factual_verifier = FactualVerifier()
        self.context_verifier = ContextVerifier()
        self.commitment_verifier = CommitmentVerifier()
        self.aggregator = ScoringAggregator()
        self.response_planner = ResponsePlanner()
        self.ledger_service = DialogueLedgerService(DialogueLedger())
        self.topic = TopicFrame()

    def run_turn(self, conversation_id: str, text: str) -> dict:
        decision = self.constitution.evaluate_input(text)
        if not decision.allowed:
            return {"answer": "Request blocked by constitution policy.", "route": "blocked", "abstain": True, "score": 0.0}

        intent = self.intent_normalizer.normalize(text)
        self.topic = self.topic_manager.update(self.topic, text)
        state = DialogueState(
            conversation_id=conversation_id,
            turn_id=str(uuid4()),
            intent=intent,
            topic=self.topic,
            ledger=self.ledger_service.ledger,
        )
        context = self.context_compiler.compile(state, constraints=["no_cot_exposure"])
        route = self.router.route(intent, context)

        model_output = self.provider.generate(text, context)
        process = self.process_verifier.score({"policy_ok": True})
        factual = self.factual_verifier.score(model_output, self.ledger_service.ledger.confirmed_facts)
        context_score = self.context_verifier.score(model_output, context)
        commitment = self.commitment_verifier.score(model_output, self.ledger_service.ledger.commitments_made)
        verification = self.aggregator.aggregate(process, factual, context_score, commitment)

        answer = self.response_planner.render(model_output, verification)
        return {
            "answer": answer,
            "route": RoutePath(route).value,
            "abstain": verification.abstain,
            "score": verification.aggregate_score,
        }
