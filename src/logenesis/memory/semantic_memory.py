from __future__ import annotations

import time

from logenesis.schemas.models import MemoryRecord


class SemanticMemory:
    def __init__(self):
        self.records: list[MemoryRecord] = []

    def commit(self, record: MemoryRecord) -> None:
        record.decay_state = "stable"
        record.last_used_at = time.time()
        self.records.append(record)
