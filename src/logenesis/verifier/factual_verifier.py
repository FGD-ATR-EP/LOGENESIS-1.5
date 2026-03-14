from __future__ import annotations


class FactualVerifier:
    def score(self, answer: str, confirmed_facts: list[str]) -> float:
        if not confirmed_facts:
            return 0.7
        overlap = sum(1 for f in confirmed_facts if f.lower() in answer.lower())
        return min(1.0, 0.5 + (overlap / max(1, len(confirmed_facts))))
