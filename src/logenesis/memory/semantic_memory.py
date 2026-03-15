from __future__ import annotations

import time

from logenesis.schemas.models import MemoryRecord


class SemanticMemory:
    def __init__(self):
        self.records: list[MemoryRecord] = []

    def commit(self, record: MemoryRecord) -> None:
        if not (record.verified and record.stable and record.policy_approved and record.constitution_allowed):
            raise ValueError("semantic commit requires verified+stable+policy+constitution approval")
        record.decay_state = "stable"
        record.last_used_at = time.time()
        self.records.append(record)
