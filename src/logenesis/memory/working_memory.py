from __future__ import annotations

import time

from logenesis.schemas.models import MemoryRecord


class WorkingMemory:
    def __init__(self):
        self.records: list[MemoryRecord] = []

    def add(self, record: MemoryRecord) -> None:
        now = time.time()
        record.last_used_at = now
        if not record.created_at:
            record.created_at = now
        self.records.append(record)

    def recent(self, limit: int = 10) -> list[MemoryRecord]:
        return self.records[-limit:]
