from __future__ import annotations

from logenesis.schemas.models import MemoryRecord


class EpisodicMemory:
    def __init__(self):
        self.records: list[MemoryRecord] = []

    def commit(self, record: MemoryRecord) -> None:
        self.records.append(record)
