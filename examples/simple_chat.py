from logenesis.runtime.orchestrator import TurnOrchestrator

orch = TurnOrchestrator(
    ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
    routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
)

print(orch.run_turn("conv-1", "Hello, can you summarize our topic?"))
