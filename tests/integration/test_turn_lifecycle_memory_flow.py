from logenesis.runtime.orchestrator import TurnOrchestrator


def test_turn_lifecycle_updates_memory_and_ledger():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
    )
    out = orch.run_turn("c1", "medical question about dosage")
    assert "confidence" in out
    assert len(orch.working_memory.records) == 1
    assert len(orch.episodic_memory.records) == 1
    assert len(orch.ledger_service.ledger.unverified_claims) >= 1
