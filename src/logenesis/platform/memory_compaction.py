"""Adaptive memory compaction with salience-aware retention."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryRecord:
    key: str
    age_hours: int
    salience: float


class AdaptiveMemoryCompactor:
    """Compact memory by retaining high-salience and fresh records."""

    def compact(self, records: list[MemoryRecord], max_items: int) -> tuple[MemoryRecord, ...]:
        if max_items <= 0:
            return tuple()

        ranked = sorted(
            records,
            key=lambda record: (record.salience, -record.age_hours),
            reverse=True,
        )
        return tuple(ranked[:max_items])
