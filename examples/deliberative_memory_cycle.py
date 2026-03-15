from logenesis.runtime.orchestrator import TurnOrchestrator

orch = TurnOrchestrator(
    ruleset={"blocked_keywords": [], "forbidden_memory_tags": ["speculative"]},
    routing_policy={"deliberative_threshold": 0.5, "risk_weight": 1.0, "unresolved_weight": 0.2},
)

result = orch.run_turn("conv-risk", "medical safety question: explain possible dosage risks")
print(result)
print("working", len(orch.working_memory.records), "episodic", len(orch.episodic_memory.records), "semantic", len(orch.semantic_memory.records))
