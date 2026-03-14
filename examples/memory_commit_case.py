from logenesis.constitution.checker import ConstitutionChecker
from logenesis.constitution.constitution_engine import ConstitutionEngine
from logenesis.memory.commit_gate import CommitGate
from logenesis.schemas.models import MemoryRecord, MemoryTier

constitution = ConstitutionEngine(ConstitutionChecker({"forbidden_memory_tags": ["speculative"]}))
gate = CommitGate(constitution, min_score=0.75)
record = MemoryRecord(
    memory_id="m1",
    tier=MemoryTier.EPISODIC,
    payload={"fact": "User prefers concise answers"},
    provenance="turn-1",
    verified=True,
    stable=True,
    policy_tags=["preference"],
)

print(gate.can_commit(record, verification_score=0.9, policy={"allow_long_term_write": True}))
