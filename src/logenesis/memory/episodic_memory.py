from __future__ import annotations

import time

from logenesis.schemas.models import EpisodicEvent, MemoryRecord


class EpisodicMemory:
    def __init__(self):
        self.records: list[MemoryRecord] = []
        self.events: list[EpisodicEvent] = []

    def commit(self, record: MemoryRecord) -> None:
        record.last_used_at = time.time()
        self.records.append(record)

    def record_outcome(self, event: EpisodicEvent) -> None:
        self.events.append(event)
