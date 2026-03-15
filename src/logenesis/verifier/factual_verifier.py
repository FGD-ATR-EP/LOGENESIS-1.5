from __future__ import annotations


class FactualVerifier:
    def score(self, answer: str, confirmed_facts: list[str]) -> tuple[float, list[str]]:
        if not confirmed_facts:
            return 0.7, ["limited_fact_support"]
        overlap = sum(1 for f in confirmed_facts if f.lower() in answer.lower())
        score = min(1.0, overlap / max(1, len(confirmed_facts)))
        factors: list[str] = []
        if score < 0.5:
            factors.append("low_fact_overlap")
        return max(0.2, score), factors
