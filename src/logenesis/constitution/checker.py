from __future__ import annotations

from typing import Any


class ConstitutionChecker:
    def __init__(self, ruleset: dict[str, Any]):
        self.ruleset = ruleset

    def check_input(self, text: str) -> tuple[bool, list[str]]:
        blocked = self.ruleset.get("blocked_keywords", [])
        hits = [k for k in blocked if k.lower() in text.lower()]
        return (len(hits) == 0, hits)

    def can_execute(self, action: str) -> bool:
        denied = set(self.ruleset.get("deny_execution_actions", []))
        return action not in denied

    def can_commit_memory(self, tags: list[str]) -> bool:
        forbidden = set(self.ruleset.get("forbidden_memory_tags", []))
        return forbidden.isdisjoint(tags)
