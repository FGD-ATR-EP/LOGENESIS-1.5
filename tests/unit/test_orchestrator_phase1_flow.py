from logenesis.runtime.orchestrator import TurnOrchestrator


def test_retrieval_gate_allowed_for_non_high_stakes():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
    )
    out = orch.run_turn("c3", "hello")
    assert out["retrieval"]["allowed"] is True


def test_drift_detector_signal_propagates_in_response():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
    )
    out = orch.run_turn(
        "c4",
        "this statement is intentionally long and unrelated to baseline topic to trigger detector",
    )
    assert out["retrieval"]["drift_detected"] is True
