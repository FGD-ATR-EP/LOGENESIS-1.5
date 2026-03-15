from __future__ import annotations


class CommitmentVerifier:
    def score(self, answer: str, commitments: list[str]) -> tuple[float, list[str]]:
        if not commitments:
            return 1.0, []
        missed = [c for c in commitments if c.lower() not in answer.lower()]
        score = 1.0 - min(1.0, len(missed) / len(commitments))
        factors = ["commitment_gap"] if missed else []
        return score, factors
