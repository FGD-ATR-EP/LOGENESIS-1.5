from __future__ import annotations

from dataclasses import dataclass

from .checker import ConstitutionChecker


@dataclass
class ConstitutionDecision:
    allowed: bool
    reasons: list[str]


class ConstitutionEngine:
    def __init__(self, checker: ConstitutionChecker):
        self.checker = checker

    def evaluate_input(self, text: str) -> ConstitutionDecision:
        ok, hits = self.checker.check_input(text)
        if ok:
            return ConstitutionDecision(True, [])
        return ConstitutionDecision(False, [f"blocked_keyword:{h}" for h in hits])

    def evaluate_commit(self, tags: list[str]) -> ConstitutionDecision:
        ok = self.checker.can_commit_memory(tags)
        return ConstitutionDecision(ok, [] if ok else ["forbidden_memory_tag"])

    def evaluate_execution(self, action: str) -> ConstitutionDecision:
        ok = self.checker.can_execute(action)
        return ConstitutionDecision(ok, [] if ok else [f"execution_denied:{action}"])
