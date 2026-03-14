from logenesis.constitution.checker import ConstitutionChecker
from logenesis.constitution.constitution_engine import ConstitutionEngine
from logenesis.memory.commit_gate import CommitGate
from logenesis.schemas.models import MemoryRecord, MemoryTier


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
