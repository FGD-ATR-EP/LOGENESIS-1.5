"""Gems of Wisdom storage primitives for long-term learning."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GemsOfWisdomStorage:
    """In-memory lesson store used as active context during planning."""

    _gems: list[str] = field(default_factory=list)

    def add_gem(self, lesson: str) -> None:
        cleaned = lesson.strip()
        if not cleaned:
            raise ValueError("lesson must not be empty")
        self._gems.append(cleaned)

    def retrieve_active_context(self) -> tuple[str, ...]:
        return tuple(self._gems)
