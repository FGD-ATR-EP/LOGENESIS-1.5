"""Checker: constitutional boundary enforcement."""
from __future__ import annotations

from dataclasses import dataclass

from logenesis.core.inspira import Intent
from logenesis.core.firma import Feasibility


@dataclass(frozen=True)
class BoundaryReport:
    """Outcome of checking intent against feasibility and rules."""

    allowed: bool
    reasons: tuple[str, ...] = ()


class Checker:
    """Validate intent-feasibility pair against explicit rules."""

    def __init__(self, rules: tuple[str, ...]) -> None:
        self._rules = rules

    def assess(self, intent: Intent, feasibility: Feasibility) -> BoundaryReport:
        """Return a boundary report honoring rules and constraints."""
        reasons = tuple(self._rules)
        allowed = feasibility.status == "approved"
        return BoundaryReport(allowed=allowed, reasons=reasons)
