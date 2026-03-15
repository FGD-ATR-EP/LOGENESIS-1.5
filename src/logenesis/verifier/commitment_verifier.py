from __future__ import annotations


class CommitmentVerifier:
    def score(self, answer: str, commitments: list[str]) -> tuple[float, list[str]]:
        if not commitments:
            return 1.0, []

        lower_answer = answer.lower()
        missed = [c for c in commitments if c.lower() not in lower_answer]
        score = 1.0 - min(1.0, len(missed) / len(commitments))
        factors = []
        if missed:
            factors.append("commitment_gap")
        if len(missed) > 1:
            factors.append("commitment_consistency_risk")
        return score, factors
