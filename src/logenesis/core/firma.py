"""Firma: feasibility, constraints, and execution planning."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Feasibility:
    """Represents feasibility assessment for an intent."""

    status: str
    constraints: tuple[str, ...] = ()


class Firma:
    """Assess operational constraints for a given intent."""

    def evaluate(self, intent_statement: str) -> Feasibility:
        """Return a feasibility summary for an intent statement."""
        constraints = ("resource:unknown", "risk:unrated")
        return Feasibility(status="needs-review", constraints=constraints)
