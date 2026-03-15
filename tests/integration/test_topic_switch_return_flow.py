from logenesis.runtime.orchestrator import TurnOrchestrator


def test_topic_switch_and_return_flow():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
    )
    orch.run_turn("c1", "switch topic: memory")
    assert orch.topic.active_topic == "memory"
    orch.run_turn("c1", "return topic")
    assert orch.topic.active_topic == "general"


def test_topic_return_blocked_under_contradiction():
    orch = TurnOrchestrator(
        ruleset={"blocked_keywords": [], "forbidden_memory_tags": []},
        routing_policy={"deliberative_threshold": 1.0, "risk_weight": 0.7, "unresolved_weight": 0.2},
    )
    orch.run_turn("c1", "switch topic: memory")
    orch.ledger_service.ledger.contradictions_detected.append("fact_a != fact_b")
    orch.run_turn("c1", "return topic")
    assert orch.topic.active_topic == "memory"
    assert orch.topic.contradictory_return_blocked is True
