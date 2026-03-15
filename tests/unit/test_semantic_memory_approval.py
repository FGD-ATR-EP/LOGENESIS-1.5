import pytest

from logenesis.memory.semantic_memory import SemanticMemory
from logenesis.schemas.models import MemoryRecord, MemoryTier


def test_semantic_write_approval_required():
    memory = SemanticMemory()
    denied = MemoryRecord(memory_id="m1", tier=MemoryTier.SEMANTIC, payload={}, provenance="turn:c", verified=True, stable=True)

    with pytest.raises(ValueError, match=r"requires verified\+stable\+policy\+constitution approval"):
        memory.commit(denied)

    allowed = denied.model_copy(update={"policy_approved": True, "constitution_allowed": True})
    memory.commit(allowed)
    assert len(memory.records) == 1
