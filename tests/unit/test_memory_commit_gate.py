from logenesis.constitution.checker import ConstitutionChecker
from logenesis.constitution.constitution_engine import ConstitutionEngine
from logenesis.memory.commit_gate import CommitGate
from logenesis.schemas.models import MemoryRecord, MemoryTier


def _record(**kwargs) -> MemoryRecord:
    base = dict(
        memory_id="x",
        tier=MemoryTier.SEMANTIC,
        payload={"k": "v"},
        provenance="turn",
        verified=True,
        stable=True,
        confidence=0.9,
        relevance=0.9,
        reuse_likelihood=0.9,
        stability=0.9,
        pollution_risk=0.1,
        policy_tags=[],
    )
    base.update(kwargs)
    return MemoryRecord(**base)


def test_allowed_commit_when_gate_requirements_are_met():
    gate = CommitGate(ConstitutionEngine(ConstitutionChecker({"forbidden_memory_tags": []})))
    decision = gate.evaluate_policy(
        _record(),
        0.95,
        {"allow_long_term_write": True, "importance_threshold": 0.5, "max_pollution_risk": 0.4, "stability_threshold": 0.7},
    )
    assert decision.allowed is True


def test_blocked_speculative_commit():
    gate = CommitGate(ConstitutionEngine(ConstitutionChecker({"forbidden_memory_tags": []})))
    decision = gate.evaluate_policy(
        _record(verified=False, stable=False, confidence=0.3, stability=0.4),
        0.3,
        {"allow_long_term_write": True, "importance_threshold": 0.6, "max_pollution_risk": 0.45, "stability_threshold": 0.7},
    )
    assert decision.allowed is False
    assert "verification_failed" in decision.reasons


def test_blocked_unresolved_contradiction_commit():
    gate = CommitGate(ConstitutionEngine(ConstitutionChecker({"forbidden_memory_tags": []})))
    decision = gate.evaluate_policy(
        _record(payload={"has_unresolved_contradiction": True}),
        0.95,
        {"allow_long_term_write": True, "importance_threshold": 0.5, "max_pollution_risk": 0.4, "stability_threshold": 0.7},
    )
    assert decision.allowed is False
    assert "unresolved_contradiction" in decision.reasons


def test_no_memory_write_from_unverified_branch():
    gate = CommitGate(ConstitutionEngine(ConstitutionChecker({"forbidden_memory_tags": []})))
    record = MemoryRecord(
        memory_id="x",
        tier=MemoryTier.SEMANTIC,
        payload={"k": "v"},
        provenance="turn",
        verified=False,
        stable=True,
        policy_tags=[],
    )
    assert not gate.can_commit(record, 0.99, {"allow_long_term_write": True})
