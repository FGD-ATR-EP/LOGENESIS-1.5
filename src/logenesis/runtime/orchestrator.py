from __future__ import annotations

import time
from uuid import uuid4

from logenesis.constitution.checker import ConstitutionChecker
from logenesis.constitution.constitution_engine import ConstitutionEngine
from logenesis.context_governor.context_compiler import ContextCompiler
from logenesis.context_governor.drift_detector import DriftDetector
from logenesis.context_governor.intent_normalizer import IntentNormalizer
from logenesis.context_governor.retrieval_gate import RetrievalGate
from logenesis.context_governor.topic_frame_manager import TopicFrameManager
from logenesis.ledger.dialogue_ledger import DialogueLedgerService
from logenesis.llm_core.providers import LLMProvider, MockProvider
from logenesis.memory.commit_gate import CommitGate
from logenesis.memory.diffmem import DiffMem
from logenesis.memory.episodic_memory import EpisodicMemory
from logenesis.memory.rsi import RSI
from logenesis.memory.semantic_memory import SemanticMemory
from logenesis.memory.working_memory import WorkingMemory
from logenesis.reasoning.multipath import MultiPathReasoner
from logenesis.response.response_planner import ResponsePlanner
from logenesis.router.reasoning_router import ReasoningRouter
from logenesis.schemas.models import DialogueLedger, DialogueState, MemoryRecord, MemoryTier, RoutePath, TopicFrame
from logenesis.verifier.commitment_verifier import CommitmentVerifier
from logenesis.verifier.context_verifier import ContextVerifier
from logenesis.verifier.factual_verifier import FactualVerifier
from logenesis.verifier.process_verifier import ProcessVerifier
from logenesis.verifier.scoring_aggregator import ScoringAggregator


class TurnOrchestrator:
    def __init__(self, ruleset: dict, routing_policy: dict, provider: LLMProvider | None = None, memory_policy: dict | None = None):
        self.constitution = ConstitutionEngine(ConstitutionChecker(ruleset))
        self.intent_normalizer = IntentNormalizer()
        self.topic_manager = TopicFrameManager()
        self.retrieval_gate = RetrievalGate()
        self.drift_detector = DriftDetector()
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
        self.reasoner = MultiPathReasoner(max_nodes=10)

        self.memory_policy = memory_policy or {
            "allow_long_term_write": True,
            "allow_high_stakes_retrieval": True,
            "importance_threshold": 0.6,
            "max_pollution_risk": 0.45,
        }
        self.commit_gate = CommitGate(self.constitution)
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.diffmem = DiffMem()
        self.rsi = RSI()

    def _memory_candidate(self, conversation_id: str, text: str, verification_score: float) -> MemoryRecord:
        now = time.time()
        return MemoryRecord(
            memory_id=str(uuid4()),
            tier=MemoryTier.SEMANTIC,
            payload={"summary": text[:180], "topic": self.topic.active_topic, "session_scope": conversation_id},
            provenance=f"turn:{conversation_id}",
            verified=verification_score >= 0.6,
            stable=verification_score >= 0.75,
            policy_tags=[],
            relevance=verification_score,
            reuse_likelihood=min(1.0, 0.4 + verification_score / 2),
            pollution_risk=max(0.0, 1 - verification_score),
            created_at=now,
            last_used_at=now,
            lineage_ref=conversation_id,
        )

    def run_turn(self, conversation_id: str, text: str) -> dict:
        # 1-2 receive input and constitution check
        decision = self.constitution.evaluate_input(text)
        if not decision.allowed:
            return {
                "answer": "Request blocked by constitution policy.",
                "route": "blocked",
                "abstain": True,
                "score": 0.0,
                "confidence": 0.0,
                "uncertainty_factors": ["constitution_block"],
            }

        # 3-4 intent and topic update
        intent = self.intent_normalizer.normalize(text, active_topic=self.topic.active_topic)
        self.topic = self.topic_manager.update(self.topic, text, ledger=self.ledger_service.ledger)

        # 5 retrieval and drift detector integrated into turn behavior
        retrieval_allowed = self.retrieval_gate.allowed(intent.risk_flags, self.memory_policy)
        retrieved = []
        if retrieval_allowed:
            retrieved = self.retrieval_gate.query(
                self.semantic_memory.records,
                self.topic,
                now_ts=time.time(),
                session_scope=conversation_id,
            )
        drift_detected = self.drift_detector.detect(self.topic, self.ledger_service.ledger, text=text)

        # 6 dialogue state and context compilation
        state = DialogueState(
            conversation_id=conversation_id,
            turn_id=str(uuid4()),
            intent=intent,
            topic=self.topic,
            ledger=self.ledger_service.ledger,
            current_phase="context_compiled",
            context_anchor_summary=f"topic:{self.topic.active_topic};claims:{len(self.ledger_service.ledger.unverified_claims)}",
            transition_metadata={"drift_detected": drift_detected},
            retrieval_metadata={"allowed": retrieval_allowed, "retrieved": len(retrieved)},
        )
        context = self.context_compiler.compile(state, constraints=intent.user_constraints, retrieval_records=retrieved, drift_detected=drift_detected)
        context.retrieval_count = len(retrieved)
        context.retrieval_policy_blocked = not retrieval_allowed

        # 7 ledger update pre-generation
        self.ledger_service.ledger.turn_index += 1
        self.ledger_service.ledger.observed_claims.append(text[:160])
        self.ledger_service.add_unverified_claim(text[:160])

        # 8 route
        route = self.router.route(intent, context)

        # 9 optional bounded multipath
        if route == RoutePath.DELIBERATIVE and (intent.risk_flags or drift_detected):
            root, explored = self.reasoner.run(text, enable=True, route=route)
            reasoning_meta = {
                "explored": len(explored),
                "root_score": root.aggregated_score,
                "commit_eligible": root.commit_eligible,
            }
        else:
            reasoning_meta = {"explored": 0, "root_score": 0.0, "commit_eligible": True}

        model_output = self.provider.generate(text, context)

        # 10-11 verifier stack + aggregation
        process = self.process_verifier.score({"policy_ok": True, "cot_leak_risk": "hidden_trace" in model_output})
        factual = self.factual_verifier.score(model_output, self.ledger_service.ledger.confirmed_facts)
        context_score = self.context_verifier.score(model_output, context)
        commitment = self.commitment_verifier.score(model_output, self.ledger_service.ledger.commitments_made)
        verification = self.aggregator.aggregate(process, factual, context_score, commitment)

        # 12 response planner
        answer = self.response_planner.render(model_output, verification)

        # 13 memory candidate creation + 14 commit gate
        candidate = self._memory_candidate(conversation_id, answer, verification.aggregate_score)

        # 15 memory updates flow
        self.working_memory.add(candidate.model_copy(update={"tier": MemoryTier.WORKING}))
        self.episodic_memory.commit(candidate.model_copy(update={"tier": MemoryTier.EPISODIC, "stable": True}))

        can_commit = self.commit_gate.can_commit(candidate, verification.aggregate_score, self.memory_policy)
        if not reasoning_meta["commit_eligible"]:
            can_commit = False
        if can_commit:
            self.semantic_memory.commit(candidate)
            self.diffmem.record(diff=f"commit:{candidate.memory_id}", lineage_ref=candidate.lineage_ref)
            self.ledger_service.confirm_fact(answer[:120])
        else:
            candidate.commit_candidate = False
            candidate.blocked_reasons.append("commit_gate_denied")
            self.ledger_service.add_unresolved(text[:120])

        self.ledger_service.update_from_turn(text, answer)
        rsi_summary = self.rsi.summarize_episode([answer], episode_closed=False)

        # 16 structured response
        return {
            "answer": answer,
            "route": RoutePath(route).value,
            "abstain": verification.abstain,
            "score": verification.aggregate_score,
            "confidence": verification.aggregate_score,
            "uncertainty_factors": verification.uncertainty_factors,
            "valid_hard": verification.valid_hard,
            "reasoning": reasoning_meta,
            "retrieval": {
                "allowed": retrieval_allowed,
                "count": len(retrieved),
                "drift_detected": drift_detected,
            },
            "memory_candidate": {
                "commit_candidate": can_commit,
                "blocked_reasons": [] if can_commit else ["invalid_reasoning_branch" if not reasoning_meta["commit_eligible"] else "commit_gate_denied"],
            },
            "rsi": rsi_summary,
        }
