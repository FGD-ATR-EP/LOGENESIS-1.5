from __future__ import annotations

from logenesis.schemas.models import MemoryRecord


class WorkingMemory:
    def __init__(self):
        self.records: list[MemoryRecord] = []

    def add(self, record: MemoryRecord) -> None:
        self.records.append(record)
