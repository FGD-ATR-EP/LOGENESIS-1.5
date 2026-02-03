"""Inspira: intent, ethics, and guiding principles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Intent:
    """Represents a candidate intent with ethical context."""

    statement: str
    ethical_notes: tuple[str, ...] = ()


class Inspira:
    """Evaluate intent against declared values and context."""

    def __init__(self, values: Iterable[str]) -> None:
        self._values = tuple(values)

    def validate(self, statement: str) -> Intent:
        """Return an intent annotated with value-aligned notes."""
        notes = tuple(f"aligned:{value}" for value in self._values)
        return Intent(statement=statement, ethical_notes=notes)
