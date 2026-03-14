from logenesis.runtime.orchestrator import TurnOrchestrator


def test_constitution_blocking():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": ["forbidden"], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
    )
    out = orch.run_turn("c1", "this is forbidden")
    assert out["route"] == "blocked"
