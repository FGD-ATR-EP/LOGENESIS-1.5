from logenesis.runtime.orchestrator import TurnOrchestrator


def test_turn_lifecycle_updates_memory_and_ledger():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
        memory_policy={
            "allow_long_term_write": True,
            "allow_high_stakes_retrieval": False,
            "importance_threshold": 0.6,
            "max_pollution_risk": 0.45,
            "stability_threshold": 0.7,
        },
    )
    out = orch.run_turn("c1", "medical question about dosage")
    assert "confidence" in out
    assert len(orch.working_memory.records) == 1
    assert len(orch.episodic_memory.records) == 1
    assert len(orch.episodic_memory.events) == 1
    assert len(orch.ledger_service.ledger.unverified_claims) >= 1
    assert orch.ledger_service.ledger.turn_index == 1
    assert orch.ledger_service.ledger.observed_claims[-1] == "medical question about dosage"
    assert out["retrieval"]["allowed"] is False
    assert out["retrieval"]["count"] == 0


def test_memory_candidate_flow_exposes_commit_gate_result():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 0.0, "risk_weight": 0.1, "unresolved_weight": 0.1},
        memory_policy={
            "allow_long_term_write": False,
            "allow_high_stakes_retrieval": True,
            "importance_threshold": 0.99,
            "max_pollution_risk": 0.01,
            "stability_threshold": 0.95,
        },
    )
    out = orch.run_turn("c2", "general update about project status and planning details")
    assert out["memory_candidate"]["commit_candidate"] is False
    assert len(out["memory_candidate"]["blocked_reasons"]) >= 1
    assert len(orch.semantic_memory.records) == 0
    assert len(orch.ledger_service.ledger.unresolved_items) >= 1



def test_invalid_reasoning_branch_blocks_long_term_commit():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 0.0, "risk_weight": 1.0, "unresolved_weight": 0.2},
        memory_policy={
            "allow_long_term_write": True,
            "allow_high_stakes_retrieval": True,
            "importance_threshold": 0.1,
            "max_pollution_risk": 1.0,
            "stability_threshold": 0.1,
        },
    )
    orch.reasoner = orch.reasoner.__class__(max_nodes=4, risk_threshold=0.05, branching_limit=2)

    out = orch.run_turn("c3", "medical plan with uncertainty")

    assert out["memory_candidate"]["commit_candidate"] is False
    assert out["memory_candidate"]["blocked_reasons"] == ["invalid_reasoning_branch"]
    assert len(orch.semantic_memory.records) == 0


def test_diffmem_lineage_created_on_allowed_commit():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.2, "unresolved_weight": 0.1},
        memory_policy={
            "allow_long_term_write": True,
            "allow_high_stakes_retrieval": True,
            "importance_threshold": 0.1,
            "max_pollution_risk": 1.0,
            "stability_threshold": 0.1,
        },
    )
    _ = orch.run_turn("c6", "project planning update for architecture")

    assert len(orch.semantic_memory.records) == 1
    assert len(orch.diffmem.changes) == 1
    assert orch.diffmem.changes[0]["lineage_ref"] == "c6"
